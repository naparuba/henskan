# Copyright 2011-2019 Alex Yatskov
# Copyright 2020+     Gabès Jean (naparuba@gmail.com)
# Copyright (C) 2011  Marek Kubica <marek@xivilization.net>
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
import time
import traceback
from zipfile import ZipFile, ZIP_STORED


class ArchiveCBZ(object):
    def __init__(self, path):
        # type: (str) -> None
        output_directory = os.path.dirname(path)
        output_file_name = '%s.cbz' % os.path.basename(path)
        output_path = os.path.join(output_directory, output_file_name)
        self._zipfile = ZipFile(output_path, 'w', ZIP_STORED)
    
    
    def add(self, filename):
        # type: (str) -> None
        arcname = os.path.basename(filename)
        self._zipfile.write(filename, arcname)
    
    
    def close(self):
        t0 = time.time()
        self._zipfile.close()
        print(f"CBZ generation time: {time.time() - t0:.3f}s")
