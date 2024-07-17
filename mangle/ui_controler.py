import os
import sys
from typing import LiteralString

from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal, QAbstractListModel, pyqtProperty, QModelIndex, QStringListModel, QThread
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import Qt

from mangle.parameters import parameters
from mangle.worker import Worker


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
    
    
    @staticmethod
    def __get_file_extension(filename):
        # type: (LiteralString | str| bytes) -> str
        return os.path.splitext(filename)[1].lower()
    
    
    def _is_image_file(self, filename):
        # type: (LiteralString | str | bytes) -> bool
        image_exts = ('.jpeg', '.jpg', '.gif', '.png')
        
        return os.path.isfile(filename) and self.__get_file_extension(filename) in image_exts
    
    
    @pyqtSlot(str)
    def onFilesDropped(self, file_url_str):
        print(f"File dropped: ZZ{file_url_str}ZZ  {type(file_url_str)}")
        
        file_paths = file_url_str.split("\n")
        for file_path in file_paths:
            file_path = file_path.strip().replace("file:///", "", 1)
            print(f'onFilesDropped::File path: {file_path}')
            if not file_path:
                continue
            if self._is_image_file(file_path):
                self.add_file_path(file_path, 0.33)
            elif os.path.isdir(file_path):
                self._add_directory(file_path)
                
        print(f"onFilesDropped::Finished adding files")

    
    
    def _add_directory(self, directory):
        for root, _, subfiles in os.walk(directory):
            for filename in subfiles:
                file_path = os.path.join(root, filename)
                if self._is_image_file(file_path):
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
        
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.updateProgress.connect(self.updateProgressBar)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    
    
    @pyqtSlot(int)
    def updateProgressBar(self, value):
        print(f'Backend::updateProgressBar:: Progress: {value}')
        # Find the ProgressBar QML object by its objectName
        progressBar = self._find_child(self.engine.rootObjects()[0], "progress_bar")
        if progressBar:
            # Update the value of the ProgressBar
            progressBar.setProperty("value", value)
        # root_objects = self.engine.rootObjects()
        # if root_objects:
        #     root_object = root_objects[0]
        #     title_input = root_object.findChild(QObject, "titleInput")
        #     if title_input:
        #         title_input.setProperty("enabled", False)
    
    
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
