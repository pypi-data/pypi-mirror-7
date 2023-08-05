# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2014 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of msgcheck.
#
# Msgcheck is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Msgcheck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with msgcheck.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Perform various checks on gettext files:
* compilation (with command `msgfmt -c`)
* for each translation:
  * number of lines in translated strings
  * whitespace at beginning/end of strings
  * trailing whitespace at end of lines inside strings
  * punctuation at end of strings
  * spelling
"""

from . import msgcheck
from . import po
