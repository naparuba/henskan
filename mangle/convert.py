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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parameters import Parameters


class DialogConvert(QtWidgets.QProgressDialog):
    def __init__(self, parent, book, directory):
        # type: (QtWidgets.QWidget, Parameters, str) -> None
        super().__init__(parent)
        
        self.book = parameters
        self.bookPath = os.path.join(str(directory), str(self.book.title))
        
        self.timer = None
        self.setWindowTitle('Exporting book...')
        self.setMaximum(len(self.book.images))
        self.setValue(0)
        self.increment = 0
        
        self.archive = None
        if 'CBZ' in self.book.outputFormat:
            self.archive = ArchiveCBZ(self.bookPath)
        
        self.pdf = None
        if "PDF" in self.book.outputFormat:
            self.pdf = ArchivePDF(self.bookPath, str(self.book.title), str(self.book.device))
    
    
    def showEvent(self, event):
        # type: (QtWidgets.QShowEvent) -> None
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self._on_timer)
            self.timer.start(0)
    
    
    # Called when the dialog finishes processing.
    def hideEvent(self, event):
        # type: (QtWidgets.QHideEvent) -> None
        
        # Close the archive if we created a CBZ file
        if self.archive is not None:
            self.archive.close()
        # Close and generate the PDF File
        if self.pdf is not None:
            self.pdf.close()
        
        # Remove image directory if the user didn't wish for images
        if 'Image' not in self.book.outputFormat:
            shutil.rmtree(self.bookPath)
    
    
    def convertAndSave(self, source, target, device, flags, archive, pdf):
        # type: (str, str, str, int, ArchiveCBZ, ArchivePDF) -> None
        begin = time.time()
        converted_images = convert_image(source, target, device, flags)
        print(f"* convert for {target} => {len(converted_images)}")
        
        # If we have only one image, we can directly use the target
        if len(converted_images) == 1:
            try:
                save_image(converted_images[0], target)
            except:
                print('convertAndSave:: ERROR in saveImage: %s' % traceback.format_exc())
                return
            if archive is not None:
                archive.add(target)
            if pdf is not None:
                pdf.add(target)
        else:
            print("* convert2 for %s => %s" % (target, converted_images))
            base_target = target.replace('.png', '')
            for (idx, converted_image) in enumerate(converted_images):
                n_target = '%s_%04d.png' % (base_target, idx)
                print("Want to saves %s with target: %s" % (converted_image, n_target))
                try:
                    save_image(converted_image, n_target)
                except:
                    print('convertAndSave:: ERROR in saveImage: %s' % traceback.format_exc())
                    return
                if archive is not None:
                    archive.add(n_target)
                if pdf is not None:
                    pdf.add(n_target)
        
        print(f" * Convert & save in {time.time() - begin:.3f}s for {target}")
    
    
    def _on_timer(self):
        index = self.value()
        pages_split = self.increment
        target = os.path.join(self.bookPath, '%05d.png' % (index + pages_split))
        source = self.book.images[index]
        
        if index == 0:
            try:
                if not os.path.isdir(self.bookPath):
                    os.makedirs(self.bookPath)
            except OSError:
                QtWidgets.QMessageBox.critical(self, 'Mangle', 'Cannot create directory %s' % self.bookPath)
                self.close()
                return
        
        self.setLabelText('Processing %s...' % os.path.split(source)[1])
        
        try:
            if self.book.overwrite or not os.path.isfile(target):
                device = str(self.book.device)
                flags = self.book.imageFlags
                archive = self.archive
                pdf = self.pdf
                
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
                    self.convertAndSave(source, target, device,
                                        flags ^ ImageFlags.SplitRightLeft | ImageFlags.SplitRight,
                                        archive, pdf)
                    
                    # Change target for left page
                    target = os.path.join(self.bookPath, '%05d.png' % (index + pages_split + 1))
                    self.increment += 1
                
                # For right page (if requested), but in inverted mode
                if flags & ImageFlags.SplitLeftRight:
                    self.convertAndSave(source, target, device,
                                        flags ^ ImageFlags.SplitLeftRight | ImageFlags.SplitLeft,
                                        archive, pdf)
                    
                    # Change target for left page
                    target = os.path.join(self.bookPath, '%05d.png' % (index + pages_split + 1))
                    self.increment += 1
                
                # Convert page
                self.convertAndSave(source, target, device, flags, archive, pdf)
        
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
