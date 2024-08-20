import sys

from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QStringListModel, QAbstractListModel, QModelIndex, Qt, QVariant
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine

#from mangle.ui_controler import Backend

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
            FilePathModel.SizeRole: b"size",
        }

    def add_file_path(self, full_path, size):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append({"full_path": full_path, "size": size})
        self.endInsertRows()

class Backend(QObject):
    def __init__(self, engine, fruit_model,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fruit_model = fruit_model

    @pyqtSlot()
    def add_file_path(self):
        for i in range(1000):
            self._fruit_model._add_file_path("c:\\mangle\\toto.py", 4.00)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create the QML application engine
    engine = QQmlApplicationEngine()
    print(f"engine: {engine}")
    
    file_path_model = FilePathModel()
    
    # Create the backend object
    backend = Backend(engine, file_path_model)
    print(f"backend: {backend}")
    
    
    # Expose the backend object to QML
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("file_path_model", file_path_model)
    print(f"Backend is set")
    
    
    # Load the QML file
    engine.load(QUrl.fromLocalFile('toto.qml'))
    print(f"engine loaded")
    
    #fruitModel = engine.rootObjects()[0].findChild(QObject, "fruitModel")  # type: QAbstractListModel
    #print(f'fruitModel: {fruitModel}')
    #entry = fruitModel.index(0, 0)
    #print(f'Entry: {entry} {type(entry)} {dir(entry)}')
    
    if not engine.rootObjects():
        print("Error: No root objects")
        sys.exit(-1)
        
    
    sys.exit(app.exec())
