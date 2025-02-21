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

import json
import os
import time
from pathlib import Path

from .util import natural_key

if os.name == 'nt':
    BASE_HENSKAN_DIR = os.path.join(str(Path.home()), 'Documents', 'henskan')
else:
    BASE_HENSKAN_DIR = os.path.join(str(Path.home()), 'henskan')

if not os.path.exists(BASE_HENSKAN_DIR):
    os.mkdir(BASE_HENSKAN_DIR)

UNWANTED = os.path.join(BASE_HENSKAN_DIR, 'unwanted_images')
if not os.path.exists(UNWANTED):
    os.mkdir(UNWANTED)

unwanted_doc = os.path.join(UNWANTED, 'readme.txt')
if not os.path.exists(unwanted_doc):
    with open(unwanted_doc, 'w') as f:
        f.write(
            'Put in this directory images you don\'t want. Images split will be automatically compared to theses images, and if one is "similar" then it will be removed\n')

DELETED = os.path.join(BASE_HENSKAN_DIR, 'deleted_images')
if not os.path.exists(DELETED):
    os.mkdir(DELETED)


class Parameters(object):
    DefaultDevice = 'Kobo Libra H2O'
    DefaultTitle = 'Untitled'
    
    _chapters: list[str]
    
    _images_by_chapter: dict[str, list[str]]
    
    _images: list[str]
    
    _title: str
    _device: str
    _device_index: int
    
    _is_webtoon: bool
    
    _split_right_then_left = False
    _split_left_then_right = False
    
    _output_directory: str
    _default_document_directory: str
    
    
    def __init__(self):
        self.clean()
    
    
    def clean(self):
        self._images = []
        self._chapters = []
        self._images_by_chapter = {}
        
        self._title = self.DefaultTitle
        self._device = self.DefaultDevice
        self._device_index = 12
        
        self._split_left_then_right = False
        self._split_left_then_right = False
        self._is_webtoon = False
        
        self._default_document_directory = BASE_HENSKAN_DIR
        self._output_directory = self._default_document_directory  # value used only at first launch, or if saved directory is missing
    
    
    def __get_previous_parameter_path(self):
        return os.path.join(self._default_document_directory, 'henskan_parameters.json')
    
    
    def load_previous_parameters(self):
        from .image import EReaderData  # Avoid circular import
        
        previous_parameter_path = self.__get_previous_parameter_path()
        try:
            if os.path.exists(previous_parameter_path):
                with open(previous_parameter_path, 'r') as f:
                    data = json.load(f)
                    output_directory = data.get('output_directory', None)
                    # Accept only if the directory still exists
                    if output_directory and os.path.exists(output_directory) and os.path.isdir(output_directory):
                        self._output_directory = output_directory
                        print(f'Loaded previous output directory: {output_directory}')
                    device = data.get('device', None)
                    device_index = data.get('device_index', None)
                    if device and EReaderData.is_device_exists(device) and device_index is not None:
                        self._device = device
                        self._device_index = device_index
                        print(f'Loaded previous device: {device} {device_index}')
        except Exception as exp:
            print(f'Error in loading previous parameters: {exp}')
    
    
    def save_parameters(self):
        previous_parameter_path = self.__get_previous_parameter_path()
        print(f'Saving parameters to {previous_parameter_path}')
        try:
            with open(previous_parameter_path, 'w') as f:
                data = {
                    'output_directory': self._output_directory,
                    'device':           self._device,
                    'device_index':     self._device_index,
                }
                json.dump(data, f)
                print(f'Saved parameters to {previous_parameter_path}')
        except Exception as exp:
            print(f'Error in saving parameters: {exp}')
    
    
    def is_ready_for_convert(self):
        return len(self._images) > 0 and self._output_directory != '' and self.is_title_set()
    
    
    def get_output_directory(self):
        return self._output_directory
    
    
    def set_output_directory(self, output_directory):
        self._output_directory = output_directory
    
    
    def set_title(self, title):
        self._title = title
    
    
    def get_title(self):
        return self._title
    
    
    def is_title_set(self):
        return self._title != self.DefaultTitle
    
    
    def is_webtoon(self):
        return self._is_webtoon
    
    
    def set_is_webtoon(self, is_webtoon):
        self._is_webtoon = is_webtoon
    
    
    def get_device(self):
        return self._device
    
    
    def get_device_index(self):
        return self._device_index
    
    
    def set_device(self, device, index):
        self._device = device
        self._device_index = index
    
    
    def is_split_left_then_right(self):
        return self._split_left_then_right
    
    
    def set_split_left_then_right(self, b):
        # type: (bool) -> None
        self._split_left_then_right = b
    
    
    def is_split_right_then_left(self):
        return self._split_right_then_left
    
    
    def set_split_right_then_left(self, b):
        # type: (bool) -> None
        self._split_right_then_left = b
    
    
    def add_image(self, image_path, chapter_name):
        # type: (str, str) -> None
        t0 = time.time()
        self._images.append(image_path)
        if chapter_name not in self._images_by_chapter:
            self._images_by_chapter[chapter_name] = []
        self._images_by_chapter[chapter_name].append(image_path)
        print(f'[{time.time() - t0:.3f}s] Parameters:: Added image: {image_path} (current size: {len(self._images)})')
    
    
    def remove_images(self, images_to_delete):
        print(f'Cleaning images : {images_to_delete=}')
        update = {}
        for chapter_name, images in self._images_by_chapter.items():
            nb_start = len(images)
            images = [image for image in images if image not in images_to_delete]
            update[chapter_name] = images
            nb_after_clean = len(images)
            if nb_start != nb_after_clean:
                print(f'Cleaned {nb_start - nb_after_clean} images in chapter {chapter_name}')
        
        self._images_by_chapter.update(update)
    
    
    def add_chapter(self, chapter):
        # type: (str) -> None
        self._chapters.append(chapter)
        print(f'Parameters:: Added chapter: {chapter} (current size: {len(self._chapters)})')
    
    
    def get_images(self):
        # type: () -> list[str]
        return self._images
    
    
    def get_images_by_chapter(self):
        # type: () -> dict[str, list[str]]
        return self._images_by_chapter
    
    
    def get_chapters(self):
        # type: () -> list[str]
        return self._chapters
    
    
    # Sort images by natural key (so that 2.jpg comes before 10.jpg), after remove duplicates
    def sort_images(self):
        # type: () -> None
        
        sorted_images = sorted(set(self._images), key=natural_key)
        self._images = sorted_images
        print(f'Parameters:: Sorted images: {self._images}')
        
        # also sort in the chapters
        for chapter in self._chapters:
            self._images_by_chapter[chapter] = sorted(set(self._images_by_chapter[chapter]), key=natural_key)
            print(f'Parameters:: Sorted images for chapter {chapter}: {self._images_by_chapter[chapter]}')

        # Also sort chapters
        self._chapters = sorted(set(self._chapters), key=natural_key)
        print(f'Parameters:: Sorted chapters: {self._chapters}')

parameters = Parameters()
