# -*- coding: utf-8 -*-
#
#    Timetra is a time tracking application and library.
#    Copyright © 2010-2014  Andrey Mikhaylenko
#
#    This file is part of Timetra.
#
#    Timetra is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Timetra is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with Timer.  If not, see <http://gnu.org/licenses/>.
#
"""
===============
Terminal colors
===============
"""
from functools import partial
import sys

from blessings import Terminal


PY3 = sys.version_info >= (3,)
if PY3:
    unicode = str


t = Terminal()


def colored(text, wrapper):
    return wrapper(unicode(text))


success = partial(colored, wrapper=t.green)
warning = partial(colored, wrapper=t.yellow)
failure = partial(colored, wrapper=t.red)
