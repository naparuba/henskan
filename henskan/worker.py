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

import os
import shutil
import time
import traceback
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QDesktopServices

from .archive import ARCHIVE_FORMATS
from .archive_cbz import ArchiveCBZ
from .archive_pdf import ArchivePDF
from .image import EReaderData, convert_image, save_image, is_splitable
from .parameters import parameters, UNWANTED, DELETED


class Worker(QObject):
    updateProgress = pyqtSignal(int)  # will be called
    
    _progress_text: Any
    _ui_controller: Any
    
    
    def add_ui_controller(self, ui_controller):
        self._ui_controller = ui_controller
    
    
    def add_progress_text(self, progress_text_dom):
        self._progress_text = progress_text_dom
    
    
    def set_progress_text(self, text):
        self._progress_text.setProperty("text", text)
    
    
    def _convert_and_save(self, source, target, split_right=False, split_left=False):
        # type: (str, str, bool, bool) -> None
        begin = time.time()
        
        converted_images = convert_image(source, split_right=split_right, split_left=split_left)
        
        if split_right:
            print(f"  - Split right {source}")
        if split_left:
            print(f"  - Split left  {source}")
        
        print(f"* convert for {source} => {target}({len(converted_images)})")
        
        # If we have only one image, we can directly use the target
        if len(converted_images) == 1:
            try:
                save_image(converted_images[0], target)
            except:
                print(f'convertAndSave:: ERROR in saveImage: {traceback.format_exc()}')
                return
            if self._archive is not None:
                self._archive.add(target)
        
        else:
            print(f"* convert2 for {target} => {converted_images}")
            base_target = target.replace('.png', '')
            for (idx, converted_image) in enumerate(converted_images):
                n_target = '%s_%04d.png' % (base_target, idx)
                print(f"Want to saves {converted_image} with target: {n_target}")
                try:
                    save_image(converted_image, n_target)
                except:
                    print(f'convertAndSave:: ERROR in saveImage: {traceback.format_exc()}')
                    return
                if self._archive is not None:
                    self._archive.add(n_target)
        
        print(f" * Convert & save in {time.time() - begin:.3f}s for {target}")
    
    
    def _tick(self, image_path):
        index = self._index_value
        pages_split = self._split_page_offset
        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split))
        source = image_path  # parameters._images[index]
        
        if index == 0:
            try:
                if not os.path.isdir(self._book_path):
                    os.makedirs(self._book_path)
            except OSError:
                print(f'Cannot create directory {self._book_path} {traceback.format_exc()}')
                raise
        
        print(f'Processing {os.path.split(source)[1]}...')
        
        try:
            # Asked for split: maybe we cannot
            if parameters.is_split_left_then_right() or parameters.is_split_right_then_left():
                can_be_split = is_splitable(source)  # is image large enough to be split?
                if can_be_split:
                    # Generate 2 images: right, then left
                    if parameters.is_split_right_then_left():
                        self._convert_and_save(source, target, split_right=True)
                        
                        # Change target for left page
                        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                        self._split_page_offset += 1
                        self._convert_and_save(source, target, split_left=True)
                    
                    # just the other order
                    else:
                        self._convert_and_save(source, target, split_left=True)
                        
                        # Change target for left page
                        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                        self._split_page_offset += 1
                        self._convert_and_save(source, target, split_right=True)
                
                else:  # simple page (un-splitable) on a split manga
                    self._convert_and_save(source, target)
            else:
                # Convert page
                self._convert_and_save(source, target)
        
        except RuntimeError:
            raise RuntimeError(f'Error while processing {source} {traceback.format_exc()}')
        
        self._index_value += 1
    
    
    def _display_sec_into_humain(self, sec):
        # type: (float) -> str
        if sec < 60:
            return f'{sec:.0f}s'
        elif sec < 3600:
            return f'{sec / 60:.0f}m'
        else:
            return f'{sec / 3600:.0f}h'
    
    
    def run(self):
        self._index_value = 0
        self._split_page_offset = 0
        
        directory = parameters.get_output_directory()
        self._split_page_offset = 0
        self._book_path = os.path.join(directory, parameters.get_title())
        self._archive = None
        device = parameters.get_device()
        output_format = EReaderData.get_archive_format(device)
        if ARCHIVE_FORMATS.CBZ == output_format:
            self._archive = ArchiveCBZ(self._book_path)
        elif ARCHIVE_FORMATS.PDF == output_format:
            self._archive = ArchivePDF(self._book_path, parameters.get_title(), parameters.get_device())
        
        # We did finish the setup, we can now save the parameters
        parameters.save_parameters()
        self._ui_controller.start_converting()
        
        # sort images before processing
        parameters.sort_images()
        
        print(f'Chapter & images: {parameters._images_by_chapter}')
        
        nb_images = len(parameters.get_images())
        images_by_chapter = parameters.get_images_by_chapter()
        start = time.time()
        # Now work!
        i = 0
        
        for chapter in parameters.get_chapters():  # note: already sorted
            images_in_chapter = images_by_chapter[chapter]  # already sorted too
            self._archive.add_chapter(chapter)  # let the archive know we have a new chapter/tome
            for image_path in images_in_chapter:
                print(f' SAVING:: {chapter} => {image_path}')
                i += 1
                self._tick(image_path)
                pct_float = float(i) / len(parameters.get_images())
                pct = min(100, int(pct_float * 100))
                self.updateProgress.emit(pct)
                elapsed = time.time() - start
                if i >= 5:
                    estimated_time = elapsed / pct_float
                    print(f'Estimated time: {estimated_time} = {elapsed} / {pct_float}')
                    remaining_time_float = max(0.0, estimated_time - elapsed)
                    estimated_time_str = f'Estimated time: {self._display_sec_into_humain(remaining_time_float)}'
                else:
                    estimated_time_str = ''
                
                self.set_progress_text(f'Processing {i + 1}/{nb_images}<br/>{estimated_time_str}')
                QThread.msleep(1)
        print(f'Worker::run::Finished processing images')
        
        # Close the CBZ/PDF
        if self._archive is not None:
            self._archive.close()
        
        if os.path.exists(self._book_path):
            print(f'Cleaning temporary directory {self._book_path}')
            shutil.rmtree(self._book_path)
        
        self.updateProgress.emit(100)  # Be sure to round to 100 the update
        self.set_progress_text(f'Finish after {self._display_sec_into_humain(time.time() - start)}')
        
        # Show the output directory so the user can quickly access it
        QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
        
        # If webtoon, also show useful directory to analyse the splits
        if parameters.is_webtoon():
            QDesktopServices.openUrl(QUrl.fromLocalFile(UNWANTED))
            QDesktopServices.openUrl(QUrl.fromLocalFile(DELETED))
        
        print(f'Worker::run::Exiting')
