import os
import random
from typing import LiteralString

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
from PyQt6.QtWidgets import QFileDialog

from .image import guess_manga_or_webtoon_image, is_splitable
from .parameters import parameters
from .ui_component import UIInput, UIRectButton, UIComboBox, UIProgressBar, UIRectButtonConvert
from .worker import Worker

COMPONENTS = {
    'title_input':                UIInput,
    'webtoon_rectangle':          UIRectButton,
    'manga_rectangle':            UIRectButton,
    'no_split_rectangle':         UIRectButton,
    'split_left_right_rectangle': UIRectButton,
    'split_right_left_rectangle': UIRectButton,
    'device_combo_box':           UIComboBox,
    
    'output_directory_input':     UIInput,
    
    'convert_rect_button':        UIRectButtonConvert,
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
        
        self._first_drop_done = False
    
    
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
    def on_title_changed(self, text):
        print(f"Title changed: {text}")
        parameters.set_title(text)
        
        self._components['title_input'].set_value(text)
        
        self._check_for_convert_ready()
    
    
    @staticmethod
    def __get_file_extension(filename):
        # type: (LiteralString | str| bytes) -> str
        return os.path.splitext(filename)[1].lower()
    
    
    def __is_image_file(self, filename):
        # type: (LiteralString | str | bytes) -> bool
        image_exts = ('.jpeg', '.jpg', '.gif', '.png')
        
        return os.path.isfile(filename) and self.__get_file_extension(filename) in image_exts
    
    
    @pyqtSlot(str)
    def on_files_dropped(self, file_url_str):
        print(f"File dropped: ZZ{file_url_str}ZZ  {type(file_url_str)}")
        
        file_paths = file_url_str.split("\n")
        for file_path in file_paths:
            file_path = file_path.strip().replace("file:///", "", 1)
            print(f'onFilesDropped::File path: {file_path}')
            if not file_path:
                continue
            if self.__is_image_file(file_path):
                self.add_file_path(file_path, 0.33)
            elif os.path.isdir(file_path):
                self.__add_directory(file_path)
        
        if len(parameters.get_images()):
            self.__enable_other_cols()
        
        self._drop_done()
    
    
    def _drop_done(self):
        if not self._first_drop_done:
            self._guess_parameters()
            self._first_drop_done = True
        
        # In all case, look if we have all parameters and can convert
        self._check_for_convert_ready()
    
    
    def _guess_parameters(self):
        print(f'UIController::_guess_parameters')
        
        nb_random_need = 20
        
        # Get 20 random images to guess: manga or webtoon, and can split or not
        images = parameters.get_images()
        if len(images) < nb_random_need:
            return
        
        sampled_images = random.sample(images, min(nb_random_need, len(images)))
        quorum_size = (len(sampled_images) // 2) + 1
        
        nb_webtoon = 0
        nb_should_split = 0
        
        for image_path in sampled_images:
            print(f'Guessing {image_path}')
            image_guess = guess_manga_or_webtoon_image(image_path)
            if image_guess == 'webtoon':
                nb_webtoon += 1
                print(f'''{image_path} is a webtoon''')
                continue
            print(f'''{image_path} is a manga''')
            splitable = is_splitable(image_path)
            if splitable:
                nb_should_split += 1
                print(f'''{image_path} can be split''')
            else:
                print(f'''{image_path} can't be split''')
        
        print(f'nb_webtoon: {nb_webtoon}  nb_should_split: {nb_should_split}')
        
        # If more than half of the images are webtoon, then we set webtoon
        if nb_webtoon > quorum_size:
            parameters.set_is_webtoon(True)
            self._enable_webtoon_display()
            return
        
        # Not a webtoon so a manga
        self._enable_manga_display()
        
        # If more than half of the images can be split, then we set one split
        if nb_should_split > quorum_size:
            self._enable_split_left_then_right()
        else:
            self._enable_no_split()
    
    
    def __enable_other_cols(self):
        self._col_parameters.setProperty("visible", True)
        self._col_convert.setProperty("visible", True)
        
        for component in self._components.values():
            component.enable()
    
    
    def __add_directory(self, directory):
        for root, _, subfiles in os.walk(directory):
            for filename in subfiles:
                file_path = os.path.join(root, filename)
                if self.__is_image_file(file_path):
                    self.add_file_path(file_path, 0.33)
    
    
    @pyqtSlot()
    def on_button_manga(self):
        print(f"onButtonManga clicked")
        parameters.set_is_webtoon(False)
        self._enable_manga_display()
    
    
    def _enable_manga_display(self):
        # Switch display
        self._components['webtoon_rectangle'].set_not_active()
        self._components['manga_rectangle'].set_active()
        
        self._enable_manga_split_display()
    
    
    @pyqtSlot()
    def on_button_webtoon(self):
        print(f"onButtonWebtoon clicked")
        parameters.set_is_webtoon(True)
        self._enable_webtoon_display()
    
    
    def _enable_webtoon_display(self):
        # Switch display
        self._components['webtoon_rectangle'].set_active()
        self._components['manga_rectangle'].set_not_active()
        
        self._enable_webtoon_split_display()
    
    
    def _enable_manga_split_display(self):
        print(f'UIController::_enable_manga_split_display')
        self._find_dom_id('split_webtoon_row').setProperty("visible", False)
        self._find_dom_id('split_manga_row').setProperty("visible", True)
    
    
    def _enable_webtoon_split_display(self):
        print(f'UIController::_enable_webtoon_split_display')
        self._find_dom_id('split_webtoon_row').setProperty("visible", True)
        self._find_dom_id('split_manga_row').setProperty("visible", False)
    
    
    @pyqtSlot()
    def on_button_no_split(self):
        print(f"onButtonNoSplit clicked")
        self._enable_no_split()
    
    
    def _enable_no_split(self):
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(False)
        
        self._components['split_right_left_rectangle'].set_not_active()
        self._components['split_left_right_rectangle'].set_not_active()
        self._components['no_split_rectangle'].set_active()
    
    
    @pyqtSlot()
    def on_button_split_right_then_left(self):
        print(f"onButtonSplitRightThenLeft clicked")
        self._enable_split_right_then_left()
    
    
    def _enable_split_right_then_left(self):
        parameters.set_split_left_then_right(False)
        parameters.set_split_right_then_left(True)
        
        self._components['split_right_left_rectangle'].set_active()
        self._components['split_left_right_rectangle'].set_not_active()
        self._components['no_split_rectangle'].set_not_active()
    
    
    @pyqtSlot()
    def on_button_split_left_then_right(self):
        print(f"onButtonSplitLeftThenRight clicked")
        self._enable_split_left_then_right()
    
    
    def _enable_split_left_then_right(self):
        parameters.set_split_left_then_right(True)
        parameters.set_split_right_then_left(False)
        
        self._components['split_right_left_rectangle'].set_not_active()
        self._components['split_left_right_rectangle'].set_active()
        self._components['no_split_rectangle'].set_not_active()
    
    
    @pyqtSlot()
    def on_convert_clicked(self):
        print("Submit button clicked")
        
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.updateProgress.connect(self.update_progress_bar)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    
    
    @pyqtSlot(int)
    def update_progress_bar(self, value):
        print(f'Backend::updateProgressBar:: Progress: {value}')
        # Find the ProgressBar QML object by its objectName
        progress_bar = self._find_child(self.engine.rootObjects()[0], "progress_bar")
        if progress_bar:
            # Update the value of the ProgressBar
            progress_bar.setProperty("value", value)
    
    
    @pyqtSlot(str)
    def on_device_changed(self, value):
        print(f"Selected value: {value}")
        parameters.set_device(value)
    
    
    directorySelected = pyqtSignal(str)
    
    
    @pyqtSlot()
    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(None, "Select Directory", "", options=QFileDialog.Option.ShowDirsOnly)
        if directory:
            print(f"Selected directory: {directory}")
            parameters.set_output_directory(directory)
        # Update the UI
        self._components['output_directory_input'].set_value(directory)
        
        self._check_for_convert_ready()
    
    
    def _check_for_convert_ready(self):
        if parameters.is_ready_for_convert():
            self._enable_convert()
        else:
            self._disable_convert()
    
    
    def _enable_convert(self):
        print('UIController::_enable_convert')
        self._components['convert_rect_button'].enable()
        self._components['progress_bar'].enable()
    
    
    def _disable_convert(self):
        print('UIController::_disable_convert')
        self._components['convert_rect_button'].disable()
        self._components['progress_bar'].disable()
