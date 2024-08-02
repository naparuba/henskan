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


from PyQt6 import QtWidgets, uic

from .util import get_ui_path
from .parameters import parameters


class DialogOptions(QtWidgets.QDialog):
    lineEditTitle: QtWidgets.QLineEdit
    comboBoxDevice: QtWidgets.QComboBox
    checkboxWebtoon: QtWidgets.QCheckBox
    checkboxSplit: QtWidgets.QCheckBox
    checkboxSplitInverse: QtWidgets.QCheckBox
    
    
    def __init__(self, parent):
        super().__init__(parent)
        
        uic.loadUi(get_ui_path('ui/options.ui'), self)
        self.accepted.connect(self.onAccept)
        
        self._move_options_to_dialog()
    
    
    def onAccept(self):
        self._move_dialog_to_options()
    
    
    # Get options from current book (like a loaded one) and set the dialog values
    def _move_options_to_dialog(self):
        self.lineEditTitle.setText(parameters.get_title())
        self.comboBoxDevice.setCurrentIndex(max(self.comboBoxDevice.findText(parameters.get_device()), 0))
        self.checkboxWebtoon.setChecked(parameters.is_webtoon())
    
    
    # Save parameters set on the dialogs to the book object
    def _move_dialog_to_options(self):
        parameters.set_split_right_then_left(self.checkboxSplit.isChecked())
        parameters.set_split_left_then_right(self.checkboxSplitInverse.isChecked())
        parameters.set_is_webtoon(self.checkboxWebtoon.isChecked())
        parameters.set_title(self.lineEditTitle.text())
        parameters.set_device(self.comboBoxDevice.currentText())
