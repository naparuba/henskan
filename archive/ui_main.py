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

from os.path import basename
import os.path
import tempfile
from zipfile import ZipFile
import hashlib

from PyQt6 import QtGui, QtWidgets, QtCore, uic
from PyQt6.QtCore import Qt

from .parameters import parameters
from .ui_about import DialogAbout
from .convert import DialogConvert
from .ui_options import DialogOptions
from .util import get_ui_path, natural_key


class MainWindowBook(QtWidgets.QMainWindow):
    widget_list_files: QtWidgets.QListWidget
    actionFileNew: QtGui.QAction
    actionBookOptions: QtGui.QAction
    actionBookShiftUp: QtGui.QAction
    actionBookShiftDown: QtGui.QAction
    actionBookRemove: QtGui.QAction
    actionBookExport: QtGui.QAction
    actionHelpAbout: QtGui.QAction
    actionHelpHomepage: QtGui.QAction
    export_button: QtWidgets.QPushButton
    
    # Parameters
    edit_line: QtWidgets.QLineEdit
    checkbox_webtoon: QtWidgets.QCheckBox
    checkbox_split_right_left: QtWidgets.QCheckBox
    checkbox_split_left_right: QtWidgets.QCheckBox
    device_select: QtWidgets.QComboBox
    
    
    def __init__(self):
        super().__init__()
        
        uic.loadUi(get_ui_path('ui/book.ui'), self)
        # self.widget_list_files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.actionFileNew.triggered.connect(self.onFileNew)
        self.actionBookOptions.triggered.connect(self._show_options)
        self.actionBookShiftUp.triggered.connect(self._shift_up)
        self.actionBookShiftDown.triggered.connect(self._shift_down)
        self.actionBookRemove.triggered.connect(self._delete_items)
        self.actionBookExport.triggered.connect(self._do_export)
        self.export_button.clicked.connect(self._do_export)
        self.actionHelpAbout.triggered.connect(self._show_about)
        self.actionHelpHomepage.triggered.connect(self._open_homepage)
        
        self.widget_list_files.itemDoubleClicked.connect(self._on_double_click)
        
        # Read parameters
        # Title
        self.edit_line.setPlaceholderText("Set the title here")
        self.edit_line.textChanged.connect(self._on_title_change)
        # Webtoon
        self.checkbox_webtoon.stateChanged.connect(self._on_webtoon_change)
        # Split
        self.checkbox_split_right_left.stateChanged.connect(self._on_split_right_left_change)
        self.checkbox_split_left_right.stateChanged.connect(self._on_split_left_right_change)
        # Device
        self.device_select.currentIndexChanged.connect(self._on_device_change)
    
    
    def _on_title_change(self, new_title):
        parameters.set_title(new_title)
    
    
    def _on_webtoon_change(self, state):
        print(f'_on_webtoon_change:: {state=}')
        parameters.set_is_webtoon(state == Qt.CheckState.Checked)
    
    
    def _on_split_right_left_change(self, state):
        print(f'_on_split_right_left_change:: {state=}')
        parameters.set_split_right_then_left(state == Qt.CheckState.Checked)
    
    
    def _on_split_left_right_change(self, state):
        print(f'_on_split_left_right_change:: {state=}')
        parameters.set_split_left_then_right(state == Qt.CheckState.Checked)
    
    
    def _on_device_change(self, index):
        print(f'_on_device_change:: {index=} {self.device_select.currentText()}')
        parameters.set_device(self.device_select.currentText())
    
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    
    def dropEvent(self, event):
        print('dropEvent')
        directories = []
        filenames = []
        
        for url in event.mimeData().urls():
            print(f'dropEvent:: {url=}')
            filename = url.toLocalFile()
            print(f'dropEvent:: {filename=}')
            if self._is_image_file(filename):
                filenames.append(filename)
            elif os.path.isdir(filename):
                directories.append(filename)
        
        if directories:
            self._add_image_dirs(directories)
        if filenames:
            self._add_image_files(filenames)
    
    
    def onFileNew(self):
        parameters.clean()
        self.widget_list_files.clear()
    
    
    def _on_double_click(self, item):
        services = QtGui.QDesktopServices()
        services.openUrl(QtCore.QUrl.fromLocalFile(item.text()))
    
    
    def _shift_up(self):
        self._shift_image_files(-1)
    
    
    def _shift_down(self):
        self._shift_image_files(1)
    
    
    def _delete_items(self):
        for item in self.widget_list_files.selectedItems():
            row = self.widget_list_files.row(item)
            self.widget_list_files.takeItem(row)
            parameters._images.remove(item.text())
    
    
    def _show_options(self):
        dialog = DialogOptions(self)
        dialog.exec()
    
    
    def _do_export(self):
        if len(parameters._images) == 0:
            QtWidgets.QMessageBox.warning(self, 'Mangle', 'This book has no images to export')
            return
        
        if not parameters.is_title_set():
            dialog = DialogOptions(self)
            dialog.exec()
            if not parameters.is_title_set():
                return
        
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a directory to export book to')
        if directory:
            dialog = DialogConvert(self, directory)
            dialog.exec()
    
    
    @staticmethod
    def _open_homepage():
        services = QtGui.QDesktopServices()
        services.openUrl(QtCore.QUrl('https://github.com/naparuba/mangle'))
    
    
    def _show_about(self):
        dialog = DialogAbout(self)
        dialog.exec()
    
    
    def _shift_image_file(self, row, delta):
        # type: (int, int) -> None
        _valid_shift = (
                (delta > 0 and row < self.widget_list_files.count() - delta) or
                (delta < 0 and row >= abs(delta))
        )
        if not _valid_shift:
            return
        
        item = self.widget_list_files.takeItem(row)
        
        self.widget_list_files.insertItem(row + delta, item)
        self.widget_list_files.setCurrentItem(item)
        
        parameters._images[row], parameters._images[row + delta] = (
            parameters._images[row + delta], parameters._images[row]
        )
    
    
    def _shift_image_files(self, delta):
        # type: (int) -> None
        items = self.widget_list_files.selectedItems()
        rows = sorted([self.widget_list_files.row(item) for item in items])
        
        for row in rows if delta < 0 else reversed(rows):
            self._shift_image_file(row, delta)
    
    
    # We will look at duplicate images, and remove them
    # NOTE: we cannot hash all files, so first look at size duplicate, and then for same size, we can compute
    #       the hash.
    def _clean_duplicates(self):
        file_by_sizes = {}
        _idx_to_delete = []
        
        # First look at same size
        for idx, filename in enumerate(parameters._images):
            size = os.path.getsize(filename)
            # print "File: %s => %s " % (filename, size)
            if size not in file_by_sizes:
                file_by_sizes[size] = []
            file_by_sizes[size].append((idx, filename))
        
        # For same size, compute hash
        sizes = list(file_by_sizes.keys())
        sizes.sort()
        for size in sizes:
            nb_elements = len(file_by_sizes[size])
            if nb_elements == 1:
                continue
            _hashs = {}
            for idx, filename in file_by_sizes[size]:
                with open(filename, 'rb') as f:
                    buf = f.read()
                    _hash = hashlib.sha1(buf).hexdigest()
                    if _hash not in _hashs:
                        _hashs[_hash] = []
                    _hashs[_hash].append(idx)
            for idxs in _hashs.values():
                if len(idxs) == 1:
                    continue
                _idx_to_delete.extend(idxs)
        
        # Now clean duplicate images
        if _idx_to_delete:
            print("We will clean a total of %s of %s images" % (len(_idx_to_delete), len(parameters._images)))
            # We need to remove by the end
            _idx_to_delete.sort()
            _idx_to_delete.reverse()
            for idx in _idx_to_delete:
                parameters._images.pop(idx)
                self.widget_list_files.takeItem(idx)
    
    
    def _add_image_files(self, filenames):
        # type: (list[str]) -> None
        filenames_listed = []
        for i in range(0, self.widget_list_files.count()):
            filenames_listed.append(self.widget_list_files.item(i).text())
        
        print(f'addImageFiles:: filenames: {filenames}')
        # Get files but in a natural sorted order
        for filename in sorted(filenames, key=natural_key):
            if filename not in filenames_listed:
                self.widget_list_files.addItem(filename)
                parameters._images.append(filename)
        
        self._clean_duplicates()
    
    
    def _add_image_dirs(self, directories):
        # type: (list[str]) -> None
        filenames = []
        
        for directory in directories:
            for root, _, subfiles in os.walk(directory):
                for filename in subfiles:
                    path = os.path.join(root, filename)
                    if self._is_image_file(path):
                        filenames.append(path)
        
        self._add_image_files(filenames)
    
    
    def _add_cbz_files(self, filenames):
        directories = []
        temp_dir = tempfile.gettempdir()
        filenames.sort()
        
        filenames_listed = []
        for i in range(0, self.widget_list_files.count()):
            filenames_listed.append(self.widget_list_files.item(i).text())
        
        for filename in filenames:
            folder_name = os.path.splitext(basename(filename))[0]
            path = temp_dir + "/" + folder_name + "/"
            cbz_file = ZipFile(filename)
            for f in cbz_file.namelist():
                if f.endswith('/'):
                    try:
                        os.makedirs(path + f)
                    except:
                        pass  # the dir exists, so we are going to extract the images only.
                else:
                    cbz_file.extract(f, path)
            if os.path.isdir(path):  # Add the directories
                directories.append(path)
        
        self._add_image_dirs(directories)  # Add the files
    
    
    @staticmethod
    def __get_file_extension(filename):
        # type: (str) -> str
        return os.path.splitext(filename)[1].lower()
    
    
    def _is_image_file(self, filename):
        # type: (str) -> bool
        image_exts = ('.jpeg', '.jpg', '.gif', '.png')
        
        return os.path.isfile(filename) and self.__get_file_extension(filename) in image_exts
    
    
    def contains_cbz_file(self, filenames):
        cbz_exts = ['.cbz']
        for filename in filenames:
            is_cbz = os.path.isfile(filename) and self.__get_file_extension(filename) in cbz_exts
            if is_cbz:
                return True
        return False
