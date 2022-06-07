'''
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
'''

import psutil

###################################
# already part of CICoachLab
import re
import os
from PyQt5 import QtCore, QtWidgets, QtGui
import shutil
import datetime
def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)
###################################

class PatientfileBackuper(QtWidgets.QDialog):
    """!
    In the PatientfileBackuper the opened patient-file will be coppied to a defined backup place. The backup place is defined
    in CICoachLab.ini. For the filename of the backup the patient name will be extracted from the user data stored in
    the patient-file and used in the filename of the copy. If this data is corrupted, PatientfileBackuper tries to extract
    the file name from the opened excel files, which are used in our clinical routine. If both methods don't provide
    a telling patient- /filename, the  patient name can be entered manually.
    """

    def __init__(self, patientFile, user, savingPath, parHandle=None):
        """!
        input parameters:
        patientFile:
        The name of the patient file (or any other file) defined as absolut path name and as it may be defined in
        self.frameWork['settings']['patientSavingFile']
        user:
        self.user['lastname']
        self.user['forname']
        savingPath:
        Absoulte path where the coppied file will be saved. The defined path may be defined in
        self.frameWork['settings']['backupPath']
        """

        self.savingPath = savingPath
        self.patientFile = patientFile
        self.user = user
        self.parHandle = parHandle

        self.filenameBase = ''
        userFilename = self.user['lastname'] + ', ' + self.user['forname']

        super().__init__()
        self.window = QtWidgets.QWidget(self)
        self.window.show()
        self.window.resize(500, 400)

        patientFiles = []
        patientFilesAbsPath = []

        for proc in psutil.process_iter():
            try:
                for file in proc.open_files():
                    # only take a look at xls files and similar formats
                    if '.xls' in str(file) or '.xlsx' in str(file):
                        filename = re.sub('.xls', '', re.sub('.xlsx', '', file.path))
                        filenameBase = os.path.basename(filename)
                        if len(os.path.basename(filename).split()) == 2:
                            patientFiles.append(filenameBase)
                            patientFilesAbsPath.append(file.path)
            except:
                pass

        layout = QtWidgets.QVBoxLayout()
        msgQuest = _translate("MainWindow", 'Do you want to copy the patient file to the server?', None)
        msgInfo = _translate("MainWindow", 'Please select or enter the correct patient name.', None)

        sizePolicyLabel = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                QtWidgets.QSizePolicy.Maximum)
        labelQuest = QtWidgets.QLabel(msgQuest)
        labelQuest.setAlignment(QtCore.Qt.AlignHCenter)
        labelQuest.setSizePolicy(sizePolicyLabel)
        font = QtGui.QFont('', 12)
        font.setBold(True)
        labelQuest.setFont(font)

        labelInfo = QtWidgets.QLabel(msgInfo)
        labelInfo.setAlignment(QtCore.Qt.AlignHCenter)
        labelInfo.setSizePolicy(sizePolicyLabel)

        self.patientList = QtWidgets.QComboBox()
        if userFilename != ', ':
            self.patientList.addItem(userFilename)
        self.patientList.addItems(set(patientFiles))
        self.patientList.setEditable(True)

        self.okButton = QtWidgets.QPushButton(_translate("MainWindow", 'OK', None))
        self.okButton.pressed.connect(self.ok)

        self.cancelButton = QtWidgets.QPushButton(_translate("MainWindow", 'Cancel', None))
        self.cancelButton.pressed.connect(self.cancel)

        layout.addWidget(labelQuest)
        layout.addWidget(labelInfo)
        layout.addWidget(self.patientList)
        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)

        self.window.setLayout(layout)

    def __enter__(self):
        """!
        """
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """!
        Closing the dialog frame
        """
        self.close()
        return True

    def ok(self):
        """!
        """

        self.filenameBase = self.patientList.currentText()
        self.copyData()
        self.__exit__(None, None, None)

    def cancel(self):
        """!
        """
        self.__exit__(None, None, None)

    def copyData(self):
        """!
        Copying the patient file to the new file defined by self.savingPath and self.filenameBase.
        """

        ext = '.cid'
        outputname = os.path.join(self.savingPath, self.filenameBase + ext)

        if os.path.isfile(outputname):
            now = datetime.datetime.now()
            t = now.strftime("%Y-%m-%d_%H-%M-%S")
            outputname = os.path.join(self.savingPath, self.filenameBase + '_' + t + '.cid')

        if outputname != ext:
            try:
                shutil.copyfile(self.patientFile, outputname)
            except:
                msg = _translate("MainWindow", 'Could not write the output file:', None) + outputname
                if self.parHandle:
                    self.parHandle.dPrint(msg, 0, guiMode=True)
                else:
                    print(msg)

