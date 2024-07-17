import sys

from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QAbstractListModel, pyqtProperty, QModelIndex, QStringListModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import Qt

from mangle.parameters import parameters


class Backend(QObject):
    def __init__(self, engine, file_path_model):
        super().__init__()
        self.engine = engine
        self._file_path_model = file_path_model
    
    
    @pyqtSlot()
    def add_file_path(self, file_path, size):
        
        self._file_path_model.add_file_path(file_path, size)
    
    
    def _find_child(self, obj, look_name):
        if obj.objectName() == look_name:
            return obj
        for child in obj.children():
            result = self._find_child(child, look_name)
            if result:
                return result
        return None
    
    
    @pyqtSlot(str)
    def onTitleChanged(self, text):
        print(f"Title changed: {text}")
        parameters.set_title(text)
    
    
    @pyqtSlot(str)
    def onFilesDropped(self, file_url_str):
        print(f"File dropped: ZZ{file_url_str}ZZ")
        
        file_paths = file_url_str.split("\n")
        for file_path in file_paths:
            if file_path:
                self.add_file_path(file_path, 0.33)
    
    
    @pyqtSlot()
    def onButtonManga(self):
        print(f"onButtonManga clicked")
        parameters.set_is_webtoon(False)
    
    
    @pyqtSlot()
    def onButtonWebtoon(self):
        print(f"onButtonWebtoon clicked")
        parameters.set_is_webtoon(True)
    
    
    @pyqtSlot()
    def onButtonNoSplit(self):
        print(f"onButtonNoSplit clicked")
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(False)
    
    
    @pyqtSlot()
    def onButtonSplitRightThenLeft(self):
        print(f"onButtonSplitRightThenLeft clicked")
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(True)
    
    
    @pyqtSlot()
    def onButtonSplitLeftThenRight(self):
        print(f"onButtonSplitLeftThenRight clicked")
        parameters.set_split_left_then_right(True)
        parameters.set_split_right_then_left(False)
    
    
    @pyqtSlot()
    def onConvertClicked(self):
        print("Submit button clicked")
        root_objects = self.engine.rootObjects()
        if root_objects:
            root_object = root_objects[0]
            title_input = root_object.findChild(QObject, "titleInput")
            if title_input:
                title_input.setProperty("enabled", False)
    
    
    @pyqtSlot(str)
    def onDeviceChanged(self, value):
        print(f"Selected value: {value}")
        parameters.set_device(value)
    
    
    directorySelected = pyqtSignal(str)
    
    
    @pyqtSlot()
    def selectOutputDirectory(self):
        directory = QFileDialog.getExistingDirectory(None, "Select Directory", "", options=QFileDialog.Option.ShowDirsOnly)
        if directory:
            print(f"Selected directory: {directory}")
