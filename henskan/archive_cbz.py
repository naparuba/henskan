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
from zipfile import ZipFile, ZIP_STORED

from henskan.archive import Archive


class ArchiveCBZ(Archive):
    DEFAULT_MAX_SIZE = 1500 * 1024 * 1024  # 1.5GB
    
    
    def __init__(self, path, max_size=None):
        # type: (str, int) -> None
        self._base_output_directory = os.path.dirname(path)
        self._base_output_name = os.path.basename(path)
        self._max_size = max_size if max_size is not None else self.DEFAULT_MAX_SIZE
        self._current_part = 1
        self._all_output_paths = []
        
        self._create_new_part()
        print(f"[CBZ] Split mode enabled: max size per file = {self._max_size / (1024 ** 3):.2f}GB")
    
    
    def _create_new_part(self):
        if self._current_part == 1:
            output_file_name = '%s.cbz' % self._base_output_name
        else:
            output_file_name = '%s_part%d.cbz' % (self._base_output_name, self._current_part)
        
        self._cbz_path = os.path.join(self._base_output_directory, output_file_name)
        self._zipfile = ZipFile(self._cbz_path, 'w', ZIP_STORED)
        self._all_output_paths.append(self._cbz_path)
        print(f"[CBZ] file: {self._cbz_path} open for writing (part {self._current_part})")
    
    
    def _get_current_size(self):
        try:
            return os.path.getsize(self._cbz_path)
        except OSError:
            return 0
    
    
    def _should_split(self, new_file_size):
        current_size = self._get_current_size()
        return (current_size + new_file_size) > self._max_size
    
    
    def add(self, filename):
        # type: (str) -> None
        file_size = os.path.getsize(filename)
        
        # If too much, close and create a new part
        if self._should_split(file_size):
            print(f"[CBZ] Size limit reached ({self._get_current_size() / (1024 ** 3):.2f}GB), creating new part...")
            self._zipfile.close()
            self._current_part += 1
            self._create_new_part()
        
        arcname = os.path.basename(filename)
        self._zipfile.write(filename, arcname)
    
    
    # Not managed for CBZ
    def add_chapter(self, title):
        # type: (str) -> None
        pass
    
    
    def close(self):
        t0 = time.time()
        self._zipfile.close()
        print(f"[CBZ] file: {self._cbz_path} generation time: {time.time() - t0:.3f}s")
        
        if len(self._all_output_paths) > 1:
            print(f"[CBZ] Total parts created: {len(self._all_output_paths)}")
            for i, path in enumerate(self._all_output_paths, 1):
                size_mb = os.path.getsize(path) / (1024 ** 2)
                print(f"[CBZ]   Part {i}: {path} ({size_mb:.2f}MB)")
