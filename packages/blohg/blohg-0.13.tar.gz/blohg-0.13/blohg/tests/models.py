# -*- coding: utf-8 -*-
"""
    blohg.tests.models
    ~~~~~~~~~~~~~~~~~~

    Module with tests for blohg models.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import time
import unittest
import os
from datetime import datetime
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg.vcs_backends.hg.changectx import ChangeCtxDefault
from blohg.vcs_backends.hg.filectx import FileCtx
from blohg.models import Blog, Page, Post


SAMPLE_PAGE = """\
My sample page
==============

First paragraph.

This is my abstract.

.. read_more

This is the content of the page

"""

SAMPLE_POST = """\
My sample post
==============

.. tags: xd, lol,hehe

First paragraph.

This is my post abstract.

.. read_more

This is the content of the post

"""


class PageTestCase(unittest.TestCase):

    content = SAMPLE_PAGE
    model = Page

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def _get_model(self, content):
        file_dir = os.path.join(self.repo_path, 'content')
        file_path = os.path.join(file_dir, 'stub.rst')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        with codecs.open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(content)
        commands.commit(self.ui, self.repo, file_path, message='foo',
                        user='foo <foo@bar.com>', addremove=True)
        ctx = FileCtx(self.repo, self.repo[None], 'content/stub.rst')
        return self.model(ctx, 'content', '.rst', 2)

    def test_abstract(self):
        obj = self._get_model(self.content)
        search_abstract = 'abstract.'
        search_full = 'This is the content of the'
        self.assertTrue(search_abstract in obj.abstract)
        self.assertTrue(search_abstract in obj.abstract_html)
        self.assertTrue(search_abstract in obj.abstract_raw_html)
        self.assertFalse(search_full in obj.abstract)
        self.assertFalse(search_full in obj.abstract_html)
        self.assertFalse(search_full in obj.abstract_raw_html)

    def test_fulltext(self):
        obj = self._get_model(self.content)
        search_abstract = 'abstract.'
        search_full = 'This is the content of the'
        self.assertTrue(search_abstract in obj.abstract)
        self.assertTrue(search_abstract in obj.abstract_html)
        self.assertTrue(search_abstract in obj.abstract_raw_html)
        self.assertTrue(search_full in obj.full)
        self.assertTrue(search_full in obj.full_html)
        self.assertTrue(search_full in obj.full_raw_html)

    def test_date_and_mdate(self):
        obj = self._get_model(self.content)
        self.assertTrue(obj.date <= time.time())
        self.assertTrue(obj.datetime <= datetime.utcnow())
        self.assertTrue(obj.mdate is None)
        self.assertTrue(obj.mdatetime is None)
        self.assertTrue(isinstance(obj.date, int))
        self.assertTrue(isinstance(obj.datetime, datetime))

        old_date = obj.date
        old_datetime = obj.datetime

        # force date
        content = self.content + """\
.. date: 1234567890
"""
        obj = self._get_model(content)
        self.assertEqual(obj.date, 1234567890)
        self.assertEqual(obj.datetime, datetime(2009, 2, 13, 23, 31, 30))
        self.assertTrue(obj.mdate >= old_date)
        self.assertTrue(obj.mdatetime >= old_datetime)

        # force date and mdate
        content = self.content + """\
.. date: 1234567890
.. mdate: 1234567891
"""
        obj = self._get_model(content)
        self.assertEqual(obj.mdate, 1234567891)
        self.assertEqual(obj.mdatetime, datetime(2009, 2, 13, 23, 31, 31))

    def test_author_default(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.author_name, 'foo')
        self.assertEqual(obj.author_email, 'foo@bar.com')

    def test_author_without_email(self):
        content = self.content + """\
.. author: john
"""
        obj = self._get_model(content)
        self.assertEqual(obj.author_name, 'john')
        self.assertTrue(obj.author_email is None)

    def test_author_explicit(self):
        content = self.content + """\
.. author: john <example@example.org>
"""
        obj = self._get_model(content)
        self.assertEqual(obj.author_name, 'john')
        self.assertEqual(obj.author_email, 'example@example.org')

    def test_path(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.path, 'content/stub.rst')

    def test_slug(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.slug, 'stub')

    def test_title(self):
        obj = self._get_model(self.content)
        self.assertTrue(obj.title.startswith('My sample '))

    def test_description(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.description, 'First paragraph.')

    def test_aliases(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.aliases, [])

    def test_aliases_explicit(self):
        content = self.content + """\
.. aliases: 301:/my-old-post-location/,/another-old-location/
"""
        obj = self._get_model(content)
        self.assertEqual(obj.aliases, [(301, '/my-old-post-location/'),
                                       (302, '/another-old-location/')])


class PostTestCase(PageTestCase):

    content = SAMPLE_POST
    model = Post

    def test_tags(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.tags, ['xd', 'lol', 'hehe'])


class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'username', 'foo <foo@bar.com>')
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_path)
        file_dir = os.path.join(self.repo_path, 'content')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        for i in range(3):
            file_path = os.path.join(file_dir, 'page-%i.rst' % i)
            with codecs.open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(SAMPLE_PAGE)
            commands.add(self.ui, self.repo, file_path)
        file_path = os.path.join(file_dir, 'about.rst')
        with codecs.open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(SAMPLE_PAGE + """
.. aliases: 301:/my-old-post-location/,/another-old-location/""")
        commands.add(self.ui, self.repo, file_path)
        file_dir = os.path.join(self.repo_path, 'content', 'post')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        for i in range(3):
            file_path = os.path.join(file_dir, 'post-%i.rst' % i)
            with codecs.open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(SAMPLE_POST)
            commands.add(self.ui, self.repo, file_path)
        file_path = os.path.join(file_dir, 'foo.rst')
        with codecs.open(file_path, 'w', encoding='utf-8') as fp:
            # using the page template, because we want to set tags manually
            fp.write(SAMPLE_PAGE + """
.. tags: foo, bar, lol""")
        commands.add(self.ui, self.repo, file_path)
        commands.commit(self.ui, self.repo, message='foo', user='foo')

    def get_model(self):
        ctx = ChangeCtxDefault(self.repo_path)
        return Blog(ctx, 'content', '.rst', 3)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_tags(self):
        self.assertEqual(sorted(self.get_model().tags),
                         sorted(['bar', 'foo', 'hehe', 'lol', 'xd']))

    def test_aliases(self):
        self.assertEqual(self.get_model().aliases,
                         {'/my-old-post-location/': (301, u'about'),
                          '/another-old-location/': (302, u'about')})

    def test_get(self):
        self.assertEqual(self.get_model().get('about').slug, 'about')

    def test_get_all(self):
        self.assertEqual(sorted([i.slug for i in self.get_model().get_all()]),
                         sorted(['page-%i' % i for i in range(3)] + \
                                ['post/post-%i' % i for i in range(3)] + \
                                ['about', 'post/foo']))

    def test_get_all_only_posts(self):
        self.assertEqual(sorted([i.slug for i in \
                                 self.get_model().get_all(True)]),
                         sorted(['post/post-%i' % i for i in range(3)] + \
                                ['post/foo']))

    def test_get_by_tag(self):
        model = self.get_model()
        self.assertEqual(sorted([i.slug for i in model.get_by_tag('lol')]),
                         sorted(['post/post-%i' % i for i in range(3)] + \
                                ['post/foo']))
        self.assertEqual(sorted([i.slug for i in \
                                 model.get_by_tag('foo')]), ['post/foo'])

    def test_get_from_archive(self):
        file_dir = os.path.join(self.repo_path, 'content', 'post')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        for i in range(1, 4):
            file_path = os.path.join(file_dir, 'archive-%i.rst' % i)
            with codecs.open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(SAMPLE_POST + """
.. date: 2010-%02i-01 12:00:00""" % i)
        commands.commit(self.ui, self.repo, user='foo', message='foo',
                        addremove=True)
        model = self.get_model()
        now = datetime.utcnow()
        self.assertEqual(model.archives, [(now.year, now.month), (2010, 3),
                                          (2010, 2), (2010, 1)])
        jan_2010 = model.get_from_archive(2010, 1)
        self.assertEqual(jan_2010[0].slug, 'post/archive-1')
        feb_2010 = model.get_from_archive(2010, 2)
        self.assertEqual(feb_2010[0].slug, 'post/archive-2')
        mar_2010 = model.get_from_archive(2010, 3)
        self.assertEqual(mar_2010[0].slug, 'post/archive-3')
        apr_2010 = model.get_from_archive(2010, 4)
        self.assertEqual(len(apr_2010), 0)

    def test_self(self):
        self.assertEqual(sorted([i.slug for i in self.get_model().published]),
                         sorted(['page-%i' % i for i in range(3)] + \
                                ['post/post-%i' % i for i in range(3)] + \
                                ['about', 'post/foo']))

    def test_scheduled(self):
        file_dir = os.path.join(self.repo_path, 'content', 'post')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        file_path = os.path.join(file_dir, 'scheduled.rst')
        with codecs.open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(SAMPLE_POST + """
.. date: """ + str(int(time.time()) + 2))
        commands.commit(self.ui, self.repo, file_path, user='foo',
                        message='foo', addremove=True)
        model = self.get_model()
        self.assertEqual(model.get('post/scheduled'), None)
        time.sleep(2)
        self.assertEqual(model.get('post/scheduled').slug, 'post/scheduled')
