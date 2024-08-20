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
import time

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

from .parameters import parameters


class FilePathModel(QAbstractListModel):
    FullPathRole = Qt.ItemDataRole.UserRole + 1
    SizeRole = Qt.ItemDataRole.UserRole + 2
    
    
    def __init__(self, *args, **kwargs):
        super(FilePathModel, self).__init__(*args, **kwargs)
        self._items = []
    
    
    def __get_common_part_with_previous(self, current, previous):
        prefix = os.path.commonpath([previous, current])
        return prefix
    
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        current_idx = index.row()
        item = self._items[current_idx]
        
        if role == FilePathModel.FullPathRole:
            current_path = item["full_path"]
            current_path = current_path.replace('\\', '/')  # go unix mode
            if current_idx == 0:
                if len(current_path) > 60:
                    current_path = "..." + current_path[-60:]
                return current_path
            previous_path = self._items[current_idx - 1]["full_path"]
            common_prefix = self.__get_common_part_with_previous(current_path, previous_path).replace('\\', '/')
            # replace common_prefix by spaces
            new_value = current_path.replace(common_prefix, " " * len(common_prefix), 1)
            if len(new_value) > 60:
                new_value = "..." + new_value[-60:]
            return new_value
            # return item["full_path"]
        elif role == FilePathModel.SizeRole:
            return item["size"]
        
        return QVariant()
    
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)
    
    
    def roleNames(self):
        return {
            FilePathModel.FullPathRole: b"full_path",
            FilePathModel.SizeRole:     b"size",
        }
    
    
    def add_file_path(self, full_path, chapter_name, size):
        # type: (str, str, int) -> None
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append({"full_path": full_path, "size": size})
        parameters.add_image(full_path, chapter_name)
        self.endInsertRows()
    
    
    # When we did finish to add files, then we can sort and display them
    def finish_add_files(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.sort(key=lambda item: item["full_path"])
        self.endInsertRows()
