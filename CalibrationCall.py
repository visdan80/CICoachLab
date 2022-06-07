"""!
This class handles the gui to run the system calibration.

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
from Calibration import Ui_Calibration
from time import asctime


class CalibrationCall(QtWidgets.QDialog):
    def __init__(self, parHandle=None):
        """!
        Initializing the dialog window for the input of the user data.

        The gui is imported as Ui_Dialog which is defined in Calibration.py and Calibration.ui. Calibration.ui is
        converted into the pyhon file with the command line 'pyuic5 Calibration.ui -o Calibration.py'.
        """

        QtWidgets.QDialog.__init__(self, parHandle)
        self.uiCalib = Ui_Calibration()
        self.uiCalib.setupUi(self)
        # Your own init stuff

        self.parHandle = parHandle

        self.signal = self.parHandle.curGenerator['functions']['run']()

        # copying frameWork data
        self.readData()
        # filling gui with copyed values
        self.fillGui()

        self.uiCalib.pbCancel.clicked.connect(self.cancel)
        self.uiCalib.pbOK.clicked.connect(self.ok)
        self.uiCalib.pbPlay.clicked.connect(self.play)
        self.uiCalib.pbCorrectCal.clicked.connect(self.calibrate)


    def readData(self):
        """!
        Copying data from frameWork calibration levels and levels.
        """

        self.generatorLevel = self.parHandle.curGenerator['settings']['level']
        self.generatorCalLevel = self.parHandle.curGenerator['calibration']['level']['level']
        self.playerLevel = self.parHandle.curPlayer['settings']['level']
        self.playerCalLevel = self.parHandle.curPlayer['calibration']['level']['level']
        self.calLevel = self.parHandle.frameWork['calibration']['level']['level']




    def fillGui(self):
        """!
        Filling gui with copied levels and calibration levels.
        """
        self.uiCalib.lbGeneratorLevel.setText(str(self.generatorLevel))
        self.uiCalib.lbGeneratorCalLevel.setText(str(self.generatorCalLevel))
        self.uiCalib.lePlayerLevel.setText(str(self.playerLevel))
        self.uiCalib.lbPlayerCalLevel.setText(str(self.playerCalLevel))
        self.uiCalib.lbFrameWorkCalLevel.setText(str(self.calLevel))
        self.uiCalib.lbPlayerName.setText(self.parHandle.curPlayer['settings']['playerName'])
        self.uiCalib.lbGeneratorName.setText(self.parHandle.curGenerator['settings']['generatorName'])

    def play(self):
        """!
        Playing calibration signal with scale factor derived from values displayed in gui.
        """

        playerLevel = float(self.uiCalib.lePlayerLevel.text())
        calLevel = float(self.uiCalib.lbFrameWorkCalLevel.text())
        playerCalLevel = float(self.uiCalib.lbPlayerCalLevel.text())
        scalFac = 10 ** ( (playerLevel + self.generatorLevel  -  self.generatorCalLevel - playerCalLevel - calLevel)/ 20)
        signalCopy = self.signal.copy()

        signalCopy['audio'] = signalCopy['audio']*scalFac
        self.parHandle.curPlayer['functions']['run'](signalCopy)


    def ok(self):

        """!
        Leaving calibration procedure after saving new calibration to frameWork data. Other changed values like
        """

        self.parHandle.frameWork['calibration']['level']['level'] = float(self.uiCalib.lbFrameWorkCalLevel.text())
        self.parHandle.frameWork['calibration']['level']['info']  = self.uiCalib.txComment.toPlainText()

        self.parHandle.frameWork['calibration']['level']['stdDev'] = 0
        self.parHandle.frameWork['calibration']['level']['iterations'] = 0
        self.parHandle.frameWork['calibration']['level']['date'] = asctime()

        self.close()


    def cancel(self):
        """!
        Leaving calibration procedure without applying new system calibration.
        """

        self.close()


    def calibrate(self):
        """!
        Calculation of new calibration level and display update
        """

        outputLevel = float(self.uiCalib.leOutputLevel.text())
        self.calLevel = self.calLevel - (self.playerLevel - outputLevel)

        self.fillGui()
