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
import random
import re
import time
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
        
        parameters.load_previous_parameters()
        
        self._set_device(parameters.get_device(), parameters.get_device_index())
    
    
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
        self._set_title(text)
    
    
    def _set_title(self, text):
        parameters.set_title(text)
        
        self._components['title_input'].set_value(text)
        
        self._check_for_convert_ready()
    
    
    @staticmethod
    def __get_file_extension(filename):
        # type: (LiteralString | str| bytes) -> str
        return os.path.splitext(filename)[1].lower()
    
    
    def __is_image_file(self, filename):
        # type: (LiteralString | str | bytes) -> bool
        image_exts = ('.jpeg', '.jpg', '.gif', '.png', '.webp')
        file_extension = self.__get_file_extension(filename)
        return file_extension in image_exts
    
    
    def start_converting(self):
        for component in self._components.values():
            component.disable_interaction()
        
        # But enable the progress bar
        self._components['progress_bar'].enable()
    
    
    @pyqtSlot(str)
    def on_files_dropped(self, file_url_str):
        start = time.time()
        print(f"File dropped: ZZ{file_url_str}ZZ  {type(file_url_str)}")
        
        paths = []
        file_paths = file_url_str.split("\n")
        for file_path in file_paths:
            file_path = file_path.strip().replace("file:///", "", 1)
            print(f'onFilesDropped::File path: {file_path}')
            if not file_path:
                continue
            paths.append(file_path)
        
        # For chapters, we cannot use the given directory if there is only one directory
        is_only_main_title_dir = len(paths) == 1
        
        paths.sort()
        print(f'Loading Paths: {paths}')
        for file_path in paths:
            chapter_name = os.path.basename(file_path)
            if not is_only_main_title_dir:  # real chapter/tome name
                parameters.add_chapter(chapter_name)
            if self.__is_image_file(file_path):
                self._file_path_model.add_file_path(file_path, chapter_name, 0.33)
            elif os.path.isdir(file_path):
                if is_only_main_title_dir:
                    self.__add_main_directory(file_path)
                else: # real chapter/tome name
                    self.__add_directory(file_path, chapter_name)
        
        if len(parameters.get_images()):
            self.__enable_other_cols()
        
        self._drop_done()
        print(f'End of onFilesDropped in {time.time() - start:.3f}s')
    
    
    def _drop_done(self):
        # Let the UI know we have all the images so it can sort it and update display
        self._file_path_model.finish_add_files()
        
        if not self._first_drop_done:
            self._guess_parameters()
            self._first_drop_done = True
        
        # In all case, look if we have all parameters and can convert
        self._check_for_convert_ready()
    
    
    def _send_message_to_manga_webtoon_row(self, message):
        # type: (str) -> None
        manga_or_webtoon_text = self._find_dom_id('manga_or_webtoon_text')
        manga_or_webtoon_text.setProperty("text", message)
    
    
    def _send_message_to_manga_split_row(self, message):
        # type: (str) -> None
        split_row_text = self._find_dom_id('split_manga_row_text')
        split_row_text.setProperty("text", message)
    
    
    def _send_message_to_webtoon_split_row(self, message):
        # type: (str) -> None
        split_row_text = self._find_dom_id('split_webtoon_row_text')
        split_row_text.setProperty("text", message)
    
    
    # We are looking for the most less level directory that is common to ALL image paths
    # and this will give us the title
    def _guess_title(self):
        print(f'UIController::_guess_title')
        
        image_paths = parameters.get_images()
        
        if not image_paths:
            return
        
        # Get the common path
        common_path = os.path.commonpath(image_paths)
        print(f'Common path: {common_path}')
        
        # Get the title
        raw_title = os.path.basename(common_path)
        print(f'raw_title: {raw_title}')
        
        # Clean all that is between [] and () in this string
        title = re.sub(r'\[.*?\]', '', raw_title)
        title = re.sub(r'\(.*?\)', '', title)
        title = title.strip()
        
        print(f'Final title: {title}')
        self._set_title(title)
    
    
    def _guess_parameters(self):
        print(f'UIController::_guess_parameters')
        
        self._guess_title()
        
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
            self._send_message_to_manga_webtoon_row('Webtoon was detected')
            self._send_message_to_webtoon_split_row('Automatic split for Webtoon')
            return
        
        # Not a webtoon so a manga
        self._enable_manga_display()
        self._send_message_to_manga_webtoon_row('Manga detected')
        
        # If more than half of the images can be split, then we set one split
        if nb_should_split > quorum_size:
            self._enable_split_left_then_right()
            self._send_message_to_manga_split_row('Double pages detected: choose between split LEFT then RIGHT or RIGHT then LEFT')
        else:
            self._enable_no_split()
            self._send_message_to_manga_split_row('Simple pages detected, no split need')
    
    
    def __enable_other_cols(self):
        self._col_parameters.setProperty("visible", True)
        self._col_convert.setProperty("visible", True)
        
        for component in self._components.values():
            component.enable()
        
        # Now it's ready, we can load the output directory from the parameters
        # can be the default ~ or the last one saved
        self._set_output_directory(parameters.get_output_directory())
    
    def __add_main_directory(self, directory):
        # type: (str) -> None
        
        main_chapter = os.path.basename(directory)
        was_main_chapter_added = False
        
        file_names = os.listdir(directory)
        for filename in file_names:
            file_path = os.path.join(directory, filename)
            if self.__is_image_file(file_path):
                if not was_main_chapter_added:  # don't add chapters more than once!
                    parameters.add_chapter(main_chapter)
                    was_main_chapter_added = True
                print(f'UIController::__add_main_directory:: found an IMAGE {filename=} so in main chapter {main_chapter=}')
                self._file_path_model.add_file_path(file_path, main_chapter, 0.33)
            elif os.path.isdir(file_path):
                chapter_name = filename  # this is a direct sub-dir, so use it as chapter name
                print(f'UIController::__add_main_directory:: found a CHAPTER {chapter_name=}')
                self.__add_directory(file_path, chapter_name)
    
    
    def __add_directory(self, directory, chapter_name):
        # type: (str, str) -> None
        print(f'UIController::__add_directory {directory=} {chapter_name=}')
        
        for root, _, subfiles in os.walk(directory):
            for filename in subfiles:
                file_path = os.path.join(root, filename)
                if self.__is_image_file(file_path):
                    self._file_path_model.add_file_path(file_path, chapter_name, 0.33)
    
    
    @pyqtSlot()
    def on_button_manga(self):
        print(f"onButtonManga clicked")
        if not parameters.is_webtoon():
            return
        parameters.set_is_webtoon(False)
        self._enable_manga_display()
        self._send_message_to_manga_webtoon_row('Switch to Manga')
        self._send_message_to_manga_split_row('You must choose your split mode')
    
    
    def _enable_manga_display(self):
        # Switch display
        self._components['webtoon_rectangle'].set_not_active()
        self._components['manga_rectangle'].set_active()
        
        self._enable_manga_split_display()
    
    
    @pyqtSlot()
    def on_button_webtoon(self):
        print(f"onButtonWebtoon clicked")
        if parameters.is_webtoon():
            return  # already is
        parameters.set_is_webtoon(True)
        self._enable_webtoon_display()
        self._send_message_to_manga_webtoon_row('Switch to Webtoon')
        self._send_message_to_webtoon_split_row('Automatic split for Webtoon')
    
    
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
        self._send_message_to_manga_split_row('No image split')
    
    
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
        self._send_message_to_manga_split_row('Split page right, then left')
    
    
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
        self._send_message_to_manga_split_row('Split page left, then right')
    
    
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
        self.worker.add_ui_controller(self)
        self.worker.add_progress_text(self._find_dom_id('progress_text'))
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
    
    
    @pyqtSlot(str, int)
    def on_device_changed(self, str_value, index):
        print(f"Selected value: {str_value} {index}")
        self._set_device(str_value, index)
    
    
    def _set_device(self, value, index):
        parameters.set_device(value, index)
        
        self._components['device_combo_box'].set_value(value, index)
    
    
    directorySelected = pyqtSignal(str)
    
    
    @pyqtSlot()
    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(None, "Select Directory", parameters.get_output_directory(),
                                                     options=QFileDialog.Option.ShowDirsOnly)
        self._set_output_directory(directory)
    
    
    def _set_output_directory(self, directory):
        if not directory or not os.path.exists(directory) or not os.path.isdir(directory):
            print(f'Wrong output directory: {directory}')
            return
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
