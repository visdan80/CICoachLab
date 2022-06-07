"""!
This class defines the gui-dialog for the input of the user data.


Copyright (C) 2019-2022 Daniel Leander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

GPL-3.0-or-later
"""

from PyQt5 import QtWidgets
from UserDataDialog import Ui_UserDataDialog



class UserDataDialogCall(QtWidgets.QDialog):
    def __init__(self, parHandle=None):
        """Initializing the dialog window for the input of the user data.

        The gui is imported as Ui_Dialog which is defined in UserData.py and UserData.ui. UserData.ui is converted into
        the pyhon file with the command line 'pyuic5 UserData.ui -o UserData.py'.

        The data of self.parHandle.user is loaded into the gui and can be changed and saved or reset. parHandle defines
        the handle to the CICoachLab-class.
        """
        QtWidgets.QDialog.__init__(self, parHandle)
        self.uiUser = Ui_UserDataDialog()
        self.uiUser.setupUi(self)
        # Your own init stuff

        self.parHandle = parHandle

        self.uiUser.pbSave.clicked.connect(self.save)
        self.uiUser.pbCancel.clicked.connect(self.cancel)
        self.uiUser.pbClear.clicked.connect(self.clear)
        # fill fields with the data found in self.parHandle.user
        self.readUserGui()

    def save(self):
        """
        This function saves the data of the gui in self.parHandle.user.
        """

        for item in list(self.parHandle.user):
            #ignoring 'left' and 'right' which contain the attributes describing the hearings status
            if not (item == 'left' or item == 'right'):
                # writing the values into the different types of widgets
                if isinstance(getattr(self.uiUser, item), QtWidgets.QDateEdit):
                    if getattr(self.uiUser, item).date():
                        self.parHandle.user[item] = getattr(self.uiUser, item).date().toString('dd.MM.yyyy')
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QLineEdit):
                    self.parHandle.user[item] = getattr(self.uiUser, item).text()
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QTextEdit):
                    self.parHandle.user[item] = getattr(self.uiUser, item).toPlainText()
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QComboBox):
                    self.parHandle.user[item] = getattr(self.uiUser, item).currentText()
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QCheckBox):
                    if getattr(self.uiUser, item).isChecked():
                        self.parHandle.user[item] = 'checked'
                    else:
                        self.parHandle.user[item] = 'unchecked'
                else:
                    print(f"We got some problem: Cannot save field data {item}")
        for side in ['left', 'right']:
            # assumption: left and right have the same attributes
            for item in list(self.parHandle.user['left']):
                # all fields are dropdown boxex
                if isinstance(getattr(self.uiUser, side + '_' + item), QtWidgets.QComboBox):
                    self.parHandle.user[side][item] = getattr(self.uiUser, side + '_' + item).currentText()
                else:
                    print(f"We got some problem: Cannot save field data: {item}")
        self.close()

    def cancel(self):
        self.close()

    def clear(self):
        # delete user data
        self.parHandle.initializeToDefaults(mode='user')
        # refilling the gui with the default values
        self.readUserGui()

    def readUserGui(self):
        """This function reads the data of self.parHandle.user into the gui dialog."""

        for item in list(self.parHandle.user):
            # ignoring 'left' and 'right' which contain the attributes describing the hearings status
            if not( item == 'left' or item == 'right' ):
                # writing the values into the different types of widgets
                if isinstance(getattr(self.uiUser, item), QtWidgets.QDateEdit):
                    getattr(self.uiUser, item).setDateTime(getattr(self.uiUser, item).dateTimeFromText(self.parHandle.user[item]))
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QLineEdit):
                    getattr(self.uiUser, item).setText(self.parHandle.user[item])
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QTextEdit):
                    getattr(self.uiUser, item).setText(self.parHandle.user[item])
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QComboBox):
                    idx = getattr(self.uiUser, item).findText(self.parHandle.user[item])
                    getattr(self.uiUser, item).setCurrentIndex(idx)
                elif isinstance(getattr(self.uiUser, item), QtWidgets.QCheckBox):
                    if self.parHandle.user[item] == 'checked':
                        getattr(self.uiUser, item).setChecked(True)
                    else:
                        getattr(self.uiUser, item).setChecked(False)
                else:
                    print(f"We got some problem: Cannot save field data: {item}")
        for side in ['left', 'right']:
            # assumption: left and right have the same attributes
            for item in list(self.parHandle.user['left']):
                # all fields are dropdown boxex
                if isinstance(getattr(self.uiUser, side+'_'+item), QtWidgets.QComboBox):
                    idx = getattr(self.uiUser, side+'_'+item).findText(self.parHandle.user[side][item])
                    getattr(self.uiUser, side+'_'+item).setCurrentIndex(idx)
                else:
                    print(f"We got some problem: Cannot save field data: {item}")
