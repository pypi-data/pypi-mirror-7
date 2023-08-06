# -*- coding: utf-8 -*-
"""
dmc
~~~~~~~~

:copyright: (c) 2014 by Rhett Garber.
:license: ISC, see LICENSE for more details.

"""

__title__ = 'dmc'
__version__ = '0.0.1'
__description__ = 'Date and Time handling, the right way.'
__url__ = 'https://github.com/rhettg/dmc'
__build__ = 0
__author__ = 'Rhett Garber'
__license__ = 'ISC'
__copyright__ = 'Copyright 2014 Rhett Garber'


from .testing import MockNow, set_mock_now, get_mock_now, clear_mock_now
from .time import Time, TimeInterval, TimeSpan, TimeIterator, TimeSpanIterator
from .date import Date, DateInterval, DateSpan, DateIterator, DateSpanIterator
from .errors import Error
