# -*- coding: utf-8 -*-
"""
    blohg.vcs_backends.hg.changectx
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Model with classes to represent Mercurial change context.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import time
from flask.helpers import locked_cached_property
from mercurial import error, hg, ui
from zlib import adler32

from blohg.vcs_backends.hg.filectx import FileCtx
from blohg.vcs import ChangeCtx


class ChangeCtxBase(ChangeCtx):
    """Base class that represents a change context."""

    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._ui = ui.ui()
        self._repo = hg.repository(self._ui, self._repo_path)
        self._ctx = self._repo[self.revision_id]
        self.revno = self._ctx.rev()

    @locked_cached_property
    def files(self):
        files = set(self._ctx.manifest().keys())
        try:
            files = files.union(set(self._extra_files))
        except:
            pass
        return sorted(files)

    def get_filectx(self, path):
        return FileCtx(self._repo, self._ctx, path)


class ChangeCtxDefault(ChangeCtxBase):
    """Class with the specific implementation details for the change context
    of the default revision state of the repository. It inherits the common
    implementation from the class :class:`ChangeCtxBase`.
    """

    def __init__(self, repo_path):
        ChangeCtxBase.__init__(self, repo_path)
        if self.revno is None:
            raise RuntimeError('No commits found in the repository!')

    @property
    def revision_id(self):
        try:
            return self._repo.branchtip('default')
        except error.RepoLookupError:
            return None

    def needs_reload(self):
        if self.revno is None:
            return True
        repo = hg.repository(self._ui, self._repo_path)
        try:
            revision_id = repo.branchtip('default')
        except error.RepoLookupError:
            return True
        revision = repo[revision_id]
        return revision.rev() > self.revno

    def filectx_needs_reload(self, filectx):
        filelog = filectx._ctx.filelog()
        changesets = list(filelog)
        new_filectx = self.get_filectx(filectx._path)
        new_filelog = new_filectx._ctx.filelog()
        new_changesets = list(new_filelog)
        return len(changesets) != len(new_changesets)

    def published(self, date, now):
        return date <= now

    def etag(self, filectx):
        return 'blohg-%i-%i-%s' % (filectx.mdate or filectx.date,
                                   len(filectx.data), adler32(filectx.path)
                                   & 0xffffffff)


class ChangeCtxWorkingDir(ChangeCtxBase):
    """Class with the specific implementation details for the change context
    of the working dir of the repository. It inherits the common implementation
    from the class :class:`ChangeCtxBase`.
    """

    revision_id = None

    @property
    def _extra_files(self):
        return self._repo.status(unknown=True)[4]

    def needs_reload(self):
        """This change context is mainly used by the command-line tool, and
        didn't provides any reliable way to evaluate its "freshness". Always
        reload.
        """
        return True

    def filectx_needs_reload(self, filectx):
        return True

    def published(self, date, now):
        return True

    def etag(self, filectx):
        return 'blohg-%i-%i-%s' % (time.time(), len(filectx.data),
                                   adler32(filectx.path)& 0xffffffff)
