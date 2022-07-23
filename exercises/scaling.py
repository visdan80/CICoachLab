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


import os

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
import re
import numpy as np
from exerciseBase import exerciseBase

def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class scaling(exerciseBase):
    """!
    In this exercise the user can answer a question by scaling the amount.
    """
    def __init__(self, parHandle=None, settings=''):
        """!
        The constructor of the class, sets the basic default settings, sets the sub directories, sets the calibration if
        required and possible and loads the settings if provided.
        """

        try:

            super().__init__(parHandle, settings=settings, exerciseName='scaling')

            self.parHandle.curExercise['functions']['displayResults'] = self.displayResults
            self.parHandle.curExercise['functions']['xlsxExport'] = self.xlsxExportPreparation

            self.vBLayout   = None

            self.gridLauyout= None
            #self.vHLayout   = None
            self.ui         = dict()
        except:
            self.parHandle.dPrint('Exception: Entering exercise failed: scaling', 1)


    def __exit__(self):
        """!
        The destructor of the class will delete the gui of the exercise with
        the function eraseExerciseGui(). The path of the exercise will be unset
        by closePath()
        """
        super().__exit__()

    def displayResults(self, data):
        """!
        The results of the selected run
        are displayed in an extra window.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': displayResults()', 2)

        self.loadSettings(data['settings']['exercise']['settingsName'])
        self.iniGui()
        if np.isnan(data['results']['index']):
            msg = _translate("scaling",'The user did not provide any input.', None)
            self.parHandle.showInformation(msg)
            self.parHandle.dPrint(msg, 1, guiMode=True)
            print(msg)
        else:
            if data['results']['index'] >= 0:
                item = f"pbAnswer{data['results']['index']:02d}"
            else:
                item = "pbNoAnswer"
            self.ui[item].setChecked(True)
            self.ui[item].setStyleSheet(f"font: bold; font-size: {int(self.ui[item].font().pointSizeF()*2):d}px") # font-size: 36px
            self.parHandle.enableExerciseGui()
            msg = _translate("scaling",
                             'label:' + data['results']['label'] + '  index: ' + str(data['results']['index']),None)
            self.parHandle.showInformation(msg)
            print(msg)

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving displayResults()', 2)


    def iniGui(self):
        """!
        The gui elements of the exercise will be loaded. The gui elements
        are initialized according to the loaded settings.
        A end button is always generated.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': iniGui()', 2)

        super().eraseExerciseGui()

        self.vBLayout = QtWidgets.QVBoxLayout()
        self.gridLauyout = QtWidgets.QGridLayout()

        wMaxPerc = self.parHandle.curExercise['settings']['items']['widthMax']
        wMinPerc = self.parHandle.curExercise['settings']['items']['widthMin']

        deltaWidth =(wMaxPerc - wMinPerc)/(len(self.parHandle.curExercise['settings']['items']['values']) - 1)
        subWidget = self.parHandle.ui.exerWidget
        maxWidth = int(subWidget.width() * (wMaxPerc - (0 * deltaWidth)) / 100)

        self.ui = dict()

        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.vBLayout.addItem(spacerItem)


        objectName = 'lbQuest'
        qLabelQuest = QtWidgets.QLabel(text=self.parHandle.curExercise['settings']['Question'], objectName=objectName)
        qLabelQuest.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        self.vBLayout.addWidget(qLabelQuest, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(qLabelQuest)
        self.ui[objectName] = qLabelQuest

        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.vBLayout.addItem(spacerItem)


        self.vBLayout.addLayout(self.gridLauyout)

        if self.parHandle.curExercise['settings']['noAnswer']:
            #if self.parHandle.curExercise['settings']['items']['values'][0]:
            objectName = "pbNoAnswer"
            pButton = QtWidgets.QPushButton(subWidget,
                                            text=self.parHandle.curExercise['settings']['noAnswer'],
                                            objectName=objectName)
            pButton.clicked.connect(self.runButton)
            #pButton.setMaximumWidth(maxWidth)
            self.gridLauyout.addWidget(pButton, 0, 0 ,1, 1, alignment=QtCore.Qt.AlignHCenter)#, 0, 0, 1, 1)7
            size = pButton.geometry()
            #size.setWidth(int(maxWidth))
            pButton.setFixedSize(int(maxWidth), size.height())
            self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
            self.ui[objectName] = pButton

            try:
                height = size.height()
            except:
                height = 30

            self.gridLauyout.setRowMinimumHeight(1, height)
            rowOffset = 2
        else:
            rowOffset = 0

        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.vBLayout.addItem(spacerItem)


        ii = 0
        for item in self.parHandle.curExercise['settings']['items']['values']:
            #maxWidth = int(subWidget.width() - subWidget.width() * (ii * deltaWidth) / 100)
            maxWidth = int(subWidget.width() * (wMaxPerc - (ii * deltaWidth)) / 100)
            if item:
                objectName = f"pbAnswer{ii:02d}" #TODO: Which values in Oldenburg?
                pButton = QtWidgets.QPushButton(subWidget, text=item, objectName=objectName)
                pButton.clicked.connect(self.runButton)
                #pButton.setMaximumWidth(maxWidth)
                self.gridLauyout.addWidget(pButton,ii+rowOffset,0,1,1, alignment=QtCore.Qt.AlignHCenter)
                #pButton.setMaximumWidth(maxWidth)
                size = pButton.geometry()
                pButton.setFixedSize(int(maxWidth), size.height())
                #size.s
                #pButton.setGeometry(size)
                self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
                self.ui[objectName] = pButton

            else:
                objectName = f"pbAnswer{ii:02d}"  # TODO: Which values in Oldenburg?
                qLabel = QtWidgets.QPushButton(text='', objectName=objectName)

                try:
                    height = size.height()
                except:
                    height = 30
                qLabel.setFixedSize(int(maxWidth), height)

                self.gridLauyout.setRowMinimumHeight(ii+rowOffset, height)
                self.gridLauyout.addWidget(qLabel, ii+rowOffset, 0, 1, 1, alignment=QtCore.Qt.AlignHCenter)
                self.parHandle.curExercise['gui']['exerWidgets'].append(qLabel)
                self.ui[objectName] = qLabel

                qLabel.setVisible(False)

            ii = ii + 1

        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.vBLayout.addItem(spacerItem)

        objectName = 'pbFinish'
        pButton = QtWidgets.QPushButton(subWidget, text=_translate("scaling", 'End', None), objectName=objectName)
        pButton.clicked.connect(self.finishRun)
        pButton.setMaximumSize(100, 50)
        pButton.setMinimumSize(100, 50)
        self.vBLayout.addWidget(pButton)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
        self.ui[objectName] = pButton

        subWidget.setLayout(self.vBLayout)

        self.parHandle.show()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving iniGui()', 2)


    def prepareRun(self):
        """!
        This function is called to prepare a new run. The presentation of the signals has to be started by pressing the
        Start button. This function is called by CICoachLab by self.parHandle.curExercise['functions']['prepareRun'].

        If no gui elements exist the gui initialized. If no signal signals exist the audie signal will be initialized.
        The order of the presented signals is randomized.
        The result variables are initialized.
        """

        # exercise specific result format:
        self.parHandle.curRunData['results'] = dict()
        self.parHandle.curRunData['results']['label'] = ''
        self.parHandle.curRunData['results']['index'] = np.NaN

        super().prepareRun()



    def startRun(self):
        """!
        A run of the exercise is started.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': startRun()', 2)

        self.runButton()

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving startRun()', 2)


    def runButton(self, temp, forcedInput=''):
        """!
        This function measures the reaction time and calls self.run(). It is called when the user enters the results.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': runButton()', 2)

        self.parHandle.measureReactionTime(self.parHandle, mode='stop')

        self.run()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving runButton', 2)


    def run(self):
        """!
        This function handles the user input.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': run()', 2)

        inputAnswer = self.parHandle.sender().objectName()

        if inputAnswer == 'pbNoAnswer':
            # No input was heard
            self.parHandle.curRunData['results']['label'] = self.parHandle.curExercise['settings']['noAnswer']
            self.parHandle.curRunData['results']['index'] = -1
        elif 'pbAnswer' in inputAnswer:
            # value is extracted from input
            idx = int(re.sub('pbAnswer', '', inputAnswer))
            self.parHandle.curRunData['results']['label'] = self.parHandle.curExercise['settings']['items']['values'][idx]
            self.parHandle.curRunData['results']['index'] = idx
        else:
            msg = _translate("scaling", 'This should not happen. Could not store valid anwser.', None)
            self.parHandle.dPrint(msg, 0, guiMode=True)
            self.parHandle.curRunData['results']['label'] = ''
            self.parHandle.curRunData['results']['index'] = np.NaN

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving run()', 2)

    def iniPath(self):
        """!
        iniPath will be called in exerciseBase()
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': iniPath()', 2)

        exerciseName = 'scaling'
        super().iniPath(exerciseName)

        # self.parHandle.curExercise['path']['analysis']  = os.path.join(pwd, 'analysis')
        # self.parHandle.curExercise['path']['scripts']  = os.path.join(pwd, 'scripts')

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': iniPath()', 2)

    def xlsxExportPreparation(self, data):
        """!
        This function prepares the result for the export to xlsx files and provides a datasSeries .
        The returned status can be 'Valid', 'NoAnswer', 'None', 'Failed', 'Warning'
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': xlsxExportPreparation()', 2)

        status = 'Valid'# 'Valid', 'NoAnswer', 'None', 'Failed', 'Warning'

        if data['results'] == None or np.isnan(data['results']['index']):
            msg = _translate("scaling", 'The user did not provide any input.', None)
            self.parHandle.showInformation(msg)
            self.parHandle.dPrint(msg, 1, guiMode=False)
            print(msg)
            item = 'None'
            status = 'None'
            itemList = ['None','None', item]
            question = 'No question'
        else:
            if data['results']['index'] >= 0:
                item = data['results']['label']
                status = 'Valid'
            else:
                item = "No Answer"
                status = 'NoAnswer'
            itemList = ['0 to ' + str(len(data['settings']['exercise']['items']['values'])-1), item,
                        data['results']['index']]
            question = data['settings']['exercise']['Question']
        itemTitle = ['range', question, 'index']
        dataSeries = pd.Series(itemList, index=itemTitle)

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving xlsxExportPreparation()', 2)
        return dataSeries, status


    def setDefaultSettings(self):
        """!
        The default parameters and settingLimits of the tests will be set.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': setDefaultSettings()', 2)

        exerciseName = 'scaling'
        super().setDefaultSettings(exerciseName)

        self.parHandle.curExercise['settings']['Question'] = _translate("scaling", 'How exhausting was the exercise?', None)
        self.parHandle.curExercise['settings']['noAnswer'] = _translate("scaling", 'Inaudible', None)
        self.parHandle.curExercise['settings']['items'] = dict()
        # if the first item is not empty a separat item is provided on top
        self.parHandle.curExercise['settings']['items']['values'] = [
                                                           _translate("scaling", 'Extremely exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'very exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'notedly exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'moderately exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'little exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'very little exhausting', None),
                                                           '...',
                                                           _translate("scaling", 'not exhausting', None)]
        self.parHandle.curExercise['settings']['items']['widthMax'] = 65
        self.parHandle.curExercise['settings']['items']['widthMin'] = 20

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving setDefaultSettings()', 2)
