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


import os.path
import re


# Sort function use to sort files in a natural order, by lowering
# characters, and manage multi levels of integers (tome 1/ page 1.jpg, etc etc)
# cf: See http://www.codinghorror.com/blog/archives/001018.html
def natural_key(string_):
    l = []
    for s in re.split(r'(\d+)', string_):
        if s.isdigit():
            l.append(int(s))
        else:
            l.append(s.lower())
    return l

def get_ui_path(relative):
    my_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_dir, relative)
