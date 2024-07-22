import os
import sys


from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QStringListModel, QAbstractListModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine

from mangle.ui_controller import UIController
from mangle.file_path_model import FilePathModel
import mangle

if __name__ == "__main__":
    lib_dir = os.path.dirname(mangle.__file__)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(lib_dir, 'img', 'splash.jpg')))
    
    # Create the QML application engine
    engine = QQmlApplicationEngine()
    print(f"engine: {engine}")
    
    # File list elements display
    file_path_model = FilePathModel()
    
    
    # Create the backend object
    ui_controller = UIController(engine, file_path_model)
    print(f"UI Controller: {ui_controller}")
    
    # Expose the backend object to QML
    engine.rootContext().setContextProperty("ui_controller", ui_controller)
    engine.rootContext().setContextProperty("file_path_model", file_path_model)
    print(f"Backend is set")
    
    # Load the QML file
    
    ui_file = os.path.join(lib_dir, 'ui', 'main.qml')
    engine.load(QUrl.fromLocalFile(ui_file))
    print(f"engine loaded")
    
    # Get the controller know about parameters controllers, and disabled them all
    ui_controller.load_components()
    
    if not engine.rootObjects():
        print("Error: No root objects")
        sys.exit(-1)
    
    sys.exit(app.exec())
