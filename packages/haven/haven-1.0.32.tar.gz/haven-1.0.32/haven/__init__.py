# -*- coding: utf-8 -*-

__version__ = '1.0.32'

from .log import logger

try:
    from gevent_impl import GHaven, GBlueprint, GLater
except:
    GHaven = GLater = GBlueprint = None

from thread_impl import THaven, TBlueprint, TLater
