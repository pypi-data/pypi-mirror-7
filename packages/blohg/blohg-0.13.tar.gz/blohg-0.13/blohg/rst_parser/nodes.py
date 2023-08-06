# -*- coding: utf-8 -*-
"""
    blohg.rst_parser.nodes
    ~~~~~~~~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText doctree nodes.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.nodes import General, Element, Invisible, Special


class iframe_flash_video(General, Element):
    pass


class opengraph_image(Special, Invisible, Element):
    pass
