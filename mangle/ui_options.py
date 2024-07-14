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

from .image import ImageFlags
from .util import get_ui_path
from .parameters import parameters


class DialogOptions(QtWidgets.QDialog):
    lineEditTitle: QtWidgets.QLineEdit
    comboBoxDevice: QtWidgets.QComboBox
    checkboxWebtoon: QtWidgets.QCheckBox
    
    
    def __init__(self, parent):
        super().__init__(parent)
        
        uic.loadUi(get_ui_path('ui/options.ui'), self)
        self.accepted.connect(self.onAccept)
        
        self.moveOptionsToDialog()
    
    
    def onAccept(self):
        self.moveDialogToOptions()
    
    
    # Get options from current book (like a loaded one) and set the dialog values
    def moveOptionsToDialog(self):
        self.lineEditTitle.setText(parameters.title or 'Untitled')
        self.comboBoxDevice.setCurrentIndex(max(self.comboBoxDevice.findText(parameters.device), 0))
        self.checkboxWebtoon.setChecked(parameters.imageFlags & ImageFlags.Webtoon)
    
    
    # Save parameters set on the dialogs to the book object
    def moveDialogToOptions(self):
        # First get dialog values
        title = self.lineEditTitle.text()
        device = self.comboBoxDevice.currentText()
        
        # Now compute flags
        image_flags = 0
        
        if self.checkboxSplit.isChecked():
            image_flags |= ImageFlags.SplitRightLeft
        if self.checkboxSplitInverse.isChecked():
            image_flags |= ImageFlags.SplitLeftRight
        
        if self.checkboxWebtoon.isChecked():
            image_flags |= ImageFlags.Webtoon
        
        parameters.title = title
        parameters.device = device
        parameters.imageFlags = image_flags
