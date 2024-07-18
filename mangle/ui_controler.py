import os
from typing import LiteralString

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
from PyQt6.QtWidgets import QFileDialog

from .parameters import parameters
from .ui_component import UIInput, UIRectButton, UIComboBox, UIButton, UIProgressBar
from .worker import Worker

COMPONENTS = {
    'title_input':                UIInput,
    'webtoon_rectangle':          UIRectButton,
    'manga_rectangle':            UIRectButton,
    'no_split_rectangle':         UIRectButton,
    'split_left_right_rectangle': UIRectButton,
    'split_right_left_rectangle': UIRectButton,
    'device_combo_box':           UIComboBox,
    
    'output_directory_button':    UIButton,
    'output_directory_input':     UIInput,
    
    'convert_rect_button':        UIRectButton,
    'progress_bar':               UIProgressBar,
}


class UIController(QObject):
    def __init__(self, engine, file_path_model):
        super().__init__()
        self.engine = engine
        self._file_path_model = file_path_model
        
        self._components = {}
        
        self._col_parameters = None
        self._col_convert = None
    
    
    def load_components(self):
        for component_id, ui_component_klass in COMPONENTS.items():
            dom_element = self._find_dom_id(component_id)
            if not dom_element:
                raise ValueError(f"Component {dom_element=} not found")
            component = ui_component_klass(component_id, dom_element)
            component.disable()
            self._components[component_id] = component
        
        # hide col2 & 3
        self._col_parameters = self._find_dom_id('col_parameters')
        self._col_parameters.setProperty("visible", False)
        self._col_convert = self._find_dom_id('col_convert')
        self._col_convert.setProperty("visible", False)
    
    
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
    
    
    def _find_dom_id(self, dom_id):
        root_objects = self.engine.rootObjects()
        if root_objects:
            return self._find_child(root_objects[0], dom_id)
        return None
    
    
    @pyqtSlot(str)
    def onTitleChanged(self, text):
        print(f"Title changed: {text}")
        parameters.set_title(text)
        
        color = 'red' if not text else 'green'
        self._set_placeholder_color('title_input', color)
    
    
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
        
        if len(parameters.get_images()):
            self._enable_other_cols()
        
    def _enable_other_cols(self):
        self._col_parameters.setProperty("visible", True)
        self._col_convert.setProperty("visible", True)
        
        for component in self._components.values():
            component.enable()
    
    
    def _add_directory(self, directory):
        for root, _, subfiles in os.walk(directory):
            for filename in subfiles:
                file_path = os.path.join(root, filename)
                if self._is_image_file(file_path):
                    self.add_file_path(file_path, 0.33)
    
    
    def _set_color(self, dom_id, color):
        # type: (str, str) -> None
        obj = self._find_dom_id(dom_id)
        if obj:
            obj.setProperty("color", color)
    
    
    def _set_placeholder_color(self, dom_id, color):
        # type: (str, str) -> None
        obj = self._find_dom_id(dom_id)
        if obj:
            obj.setProperty("placeholderTextColor", color)
    
    
    @pyqtSlot()
    def onButtonManga(self):
        print(f"onButtonManga clicked")
        parameters.set_is_webtoon(False)
        
        # Switch display
        self._set_color('webtoon_rectangle', 'grey')
        self._set_color('manga_rectangle', 'green')
    
    
    @pyqtSlot()
    def onButtonWebtoon(self):
        print(f"onButtonWebtoon clicked")
        parameters.set_is_webtoon(True)
        
        # Switch display
        self._set_color('webtoon_rectangle', 'green')
        self._set_color('manga_rectangle', 'grey')
    
    
    @pyqtSlot()
    def onButtonNoSplit(self):
        print(f"onButtonNoSplit clicked")
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(False)
        
        self._set_color('no_split_rectangle', 'green')
        self._set_color('split_right_left_rectangle', 'grey')
        self._set_color('split_left_right_rectangle', 'grey')
    
    
    @pyqtSlot()
    def onButtonSplitRightThenLeft(self):
        print(f"onButtonSplitRightThenLeft clicked")
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(True)
        
        self._set_color('no_split_rectangle', 'grey')
        self._set_color('split_right_left_rectangle', 'green')
        self._set_color('split_left_right_rectangle', 'grey')
    
    
    @pyqtSlot()
    def onButtonSplitLeftThenRight(self):
        print(f"onButtonSplitLeftThenRight clicked")
        parameters.set_split_left_then_right(True)
        parameters.set_split_right_then_left(False)
        
        self._set_color('no_split_rectangle', 'grey')
        self._set_color('split_right_left_rectangle', 'grey')
        self._set_color('split_left_right_rectangle', 'green')
    
    
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
            parameters.set_output_directory(directory)
            output_directory_input = self._find_dom_id('output_directory_input')
            if output_directory_input:
                output_directory_input.setProperty("text", directory)
            self._set_placeholder_color('output_directory_input', 'green')
        else:
            self._set_placeholder_color('output_directory_input', 'red')
