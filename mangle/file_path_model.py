import sys

from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QStringListModel, QAbstractListModel, QModelIndex, Qt, QVariant
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine

from .parameters import parameters


class FilePathModel(QAbstractListModel):
    FullPathRole = Qt.ItemDataRole.UserRole + 1
    SizeRole = Qt.ItemDataRole.UserRole + 2
    
    
    def __init__(self, *args, **kwargs):
        super(FilePathModel, self).__init__(*args, **kwargs)
        self._items = []
    
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        item = self._items[index.row()]
        if role == FilePathModel.FullPathRole:
            return item["full_path"]
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
    
    
    def add_file_path(self, full_path, size):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append({"full_path": full_path, "size": size})
        self._items.sort(key=lambda item: item["full_path"])
        parameters.add_image(full_path)
        self.endInsertRows()
