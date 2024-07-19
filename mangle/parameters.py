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
from pathlib import Path


class Parameters(object):
    DefaultDevice = 'Kobo Libra H2O'
    DefaultTitle = 'Untitled'
    
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
        
        self._title = self.DefaultTitle
        self._device = self.DefaultDevice
        self._device_index = 12
        
        self._split_left_then_right = False
        self._split_left_then_right = False
        self._is_webtoon = False
        
        self._default_document_directory = str(Path.home())  # ~ on Linux
        if os.name == 'nt':
            self._default_document_directory = os.path.join(self._default_document_directory, 'Documents')
        self._output_directory = self._default_document_directory  # value used only at first launch, or if saved directory is missing
    
    
    def __get_previous_parameter_path(self):
        return os.path.join(self._default_document_directory, '.mangle_parameters.json')
    
    
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
    
    
    def add_image(self, image_path):
        self._images.append(image_path)
        print(f'Parameters:: Added image: {image_path} (current size: {len(self._images)})')
    
    
    def get_images(self):
        return self._images


parameters = Parameters()
