# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import logging


def reset():
    # Reset loggers.
    for name in logging.Logger.manager.loggerDict.keys():
        logger = logging.getLogger(name)
        map(logger.removeHandler, logger.handlers[:])
        map(logger.removeFilter, logger.filters[:])

    # Reset root logger.
    root = logging.getLogger()
    map(root.removeHandler, root.handlers[:])
    map(root.removeFilter, root.filters[:])
