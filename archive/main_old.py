#!/usr/bin/env python

# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

my_dir = os.path.dirname(__file__)
mangle_dir = os.path.join(my_dir, 'mangle')
sys.path.insert(0, my_dir)
sys.path.insert(0, mangle_dir)

from PyQt6 import QtWidgets

from mangle.ui_main import MainWindowBook

application = QtWidgets.QApplication(sys.argv)

# filename = sys.argv[1] if len(sys.argv) > 1 else None
window = MainWindowBook()
window.show()

application.exec()
