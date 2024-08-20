# Copyright (C) 2012  Cristian Lizana <cristian@lizana.in>
# Copyright 2011-2019 Alex Yatskov
# Copyright 2020+     Gabès Jean (naparuba@gmail.com)
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
from uuid import uuid4

from reportlab.pdfgen import canvas

from .archive import Archive
from .image import EReaderData


class ArchivePDF(Archive):
    def __init__(self, path, title, device):
        # type: (str, str, str) -> None
        output_directory = os.path.dirname(path)
        output_file_name = '%s.pdf' % os.path.basename(path)
        self._output_path = os.path.join(output_directory, output_file_name)
        # self._current_device = device
        # self.bookTitle = title
        self._page_size = EReaderData.Profiles[device][0]
        # pagesize could be letter or A4 for standardization, but we need to control some image sizes
        self._canvas = canvas.Canvas(self._output_path, pagesize=self._page_size)
        self._canvas.setAuthor("Henskan")
        self._canvas.setTitle(title)
        self._canvas.setSubject("Created by Henskan for " + device)
        
        print(f'[PDF] file: {self._output_path} open for writing')
    
    
    def add(self, filename):
        # type: (str) -> None
        self._canvas.drawImage(filename, 0, 0, width=self._page_size[0], height=self._page_size[1], preserveAspectRatio=True, anchor='c')
        self._canvas.showPage()  # close page
    
    
    # create a chapter in the reportlab pdf, so it can be added to the table of contents
    # NOTE: key in pdf must be unique, so using a uuid4, duplicated title are not a problem
    def add_chapter(self, title):
        # type: (str) -> None
        key = uuid4().hex  # so it's unique
        self._canvas.bookmarkPage(key)
        self._canvas.addOutlineEntry(title, key, 0, 0)
    
    
    def close(self):
        t0 = time.time()
        self._canvas.save()
        print(f"[PDF] file: {self._output_path} generation time: {time.time() - t0:.3f}s")
