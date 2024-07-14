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


class Parameters(object):
    DefaultDevice = 'Kobo Libra H2O'
    DefaultTitle = 'Untitled'
    
    images: list[str]
    
    _title: str
    _device: str
    
    _is_webtoon: bool
    
    _split_right_then_left = False
    _split_left_then_right = False
    
    
    def __init__(self):
        self.clean()
    
    
    def clean(self):
        self.images = []
        
        self._title = self.DefaultTitle
        self._device = self.DefaultDevice
        
        self._split_left_then_right = False
        self._split_left_then_right = False
        self._is_webtoon = False
    
    
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
    
    
    def set_device(self, device):
        self._device = device
    
    
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


parameters = Parameters()
