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
import time
import shutil
import traceback

from PyQt6 import QtWidgets, QtCore

from .image import ImageFlags, convert_image, save_image, is_splitable
from .archive_cbz import ArchiveCBZ
from .archive_pdf import ArchivePDF
from .parameters import parameters


class DialogConvert(QtWidgets.QProgressDialog):
    def __init__(self, parent, directory):
        # type: (QtWidgets.QWidget, str) -> None
        super().__init__(parent)
        
        self.book = parameters
        self._book_path = os.path.join(directory, self.book.title)
        
        self.timer = None
        self.setWindowTitle('Exporting book...')
        self.setMaximum(len(self.book.images))
        self.setValue(0)
        self.increment = 0
        
        self._archive = None
        if 'CBZ' in self.book.outputFormat:
            self._archive = ArchiveCBZ(self._book_path)
        elif "PDF" in self.book.outputFormat:
            self._archive = ArchivePDF(self._book_path, str(self.book.title), str(self.book.device))
    
    
    def showEvent(self, event):
        # type: (QtWidgets.QShowEvent) -> None
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self._on_timer)
            self.timer.start(0)
    
    
    # Called when the dialog finishes processing.
    def hideEvent(self, event):
        # type: (QtWidgets.QHideEvent) -> None
        
        # Close the CBZ/PDF
        if self._archive is not None:
            self._archive.close()
        
        print(f'Cleaning temporary directory {self._book_path}')
        shutil.rmtree(self._book_path)
    
    
    def _convert_and_save(self, source, target, flags):
        # type: (str, str, int) -> None
        begin = time.time()
        device = str(self.book.device)
        converted_images = convert_image(source, target, device, flags)
        print(f"* convert for {target} => {len(converted_images)}")
        
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
    
    
    def _on_timer(self):
        index = self.value()
        pages_split = self.increment
        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split))
        source = self.book.images[index]
        
        if index == 0:
            try:
                if not os.path.isdir(self._book_path):
                    os.makedirs(self._book_path)
            except OSError:
                QtWidgets.QMessageBox.critical(self, 'Mangle', f'Cannot create directory {self._book_path}')
                self.close()
                return
        
        self.setLabelText(f'Processing {os.path.split(source)[1]}...')
        
        try:
            flags = self.book.imageFlags
            
            # Check if page wide enough to split
            if (flags & ImageFlags.SplitRightLeft) or (flags & ImageFlags.SplitLeftRight):
                if not is_splitable(source):
                    # remove split flags
                    split_flags = [ImageFlags.SplitRightLeft, ImageFlags.SplitLeftRight, ImageFlags.SplitRight,
                                   ImageFlags.SplitLeft]
                    for f in split_flags:
                        flags &= ~f
            
            # For right page (if requested in options and need for this image)
            if flags & ImageFlags.SplitRightLeft:
                self._convert_and_save(source, target, flags ^ ImageFlags.SplitRightLeft | ImageFlags.SplitRight)
                
                # Change target for left page
                target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                self.increment += 1
            
            # For right page (if requested), but in inverted mode
            if flags & ImageFlags.SplitLeftRight:
                self._convert_and_save(source, target, flags ^ ImageFlags.SplitLeftRight | ImageFlags.SplitLeft)
                
                # Change target for left page
                target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                self.increment += 1
            
            # Convert page
            self._convert_and_save(source, target, flags)
        
        except RuntimeError as error:
            result = QtWidgets.QMessageBox.critical(
                    self,
                    'Mangle',
                    str(error),
                    QtWidgets.QMessageBox.Abort | QtWidgets.QMessageBox.Ignore,
                    QtWidgets.QMessageBox.Ignore
            )
            if result == QtWidgets.QMessageBox.Abort:
                self.close()
                return
        
        self.setValue(index + 1)
