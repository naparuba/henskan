import sys

from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QStringListModel, QAbstractListModel, QModelIndex, Qt, QVariant
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine

from mangle.ui_controler import Backend
from mangle.file_path_model import FilePathModel

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create the QML application engine
    engine = QQmlApplicationEngine()
    print(f"engine: {engine}")
    
    # File list elements display
    file_path_model = FilePathModel()
    
    # Create the backend object
    backend = Backend(engine, file_path_model)
    print(f"backend: {backend}")
    
    # Expose the backend object to QML
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("file_path_model", file_path_model)
    print(f"Backend is set")
    
    # Load the QML file
    engine.load(QUrl.fromLocalFile('main.qml'))
    print(f"engine loaded")
    
    if not engine.rootObjects():
        print("Error: No root objects")
        sys.exit(-1)
    
    sys.exit(app.exec())
