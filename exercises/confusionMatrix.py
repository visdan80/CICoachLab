"""!
The confusion Matrix exercise is used to present phonemes, or more generally items, one after another and ask the subject
which item was presented, respectively. The subject can choose from all available items which allows to construct
to compile the confusion matrix. The items have to be provided as signal-Files.

The confusion Matrix exercise depends on the CICoachLab framework which takes care on the saving of data and graphical
integration of the exercise.

In the default setup the  generator genWavreader and player playAudio of the CICoachLab framework are used.
They are set as default generators which process the audio signal of the items in the format:
signal['audio']
signal['fs']
which is used by playAudio for the acoustical presentation. For a preprocessing of the signal a preprocessor can be
defined which can alter the signal as part of the CICoachLab framework.
Other player, preprocessors and generators can be used as long as they use a common signal format. Confusionmatrix does not process the
signal and only provides the graphical interface and logic to pass the signals from the generator to the player.


The translation of the confusion matrix module was build by:
# The source code files are confusionMatrix.py and py files in the analysis files are parsed for _translate entries.
pylupdate5 confusionMatrix.py confusionMatrix/analysis/* -ts confusionMatrix/locales/en_de.ts
# The translations can be handled with qt tool linguist.
linguist confusionMatrix/locales/en_de.ts
# the final translation en_de.qm file is generated
lrelease confusionMatrix/locales/en_de.ts

The localization will be loaded at the start of CICoachLab if it is found in the locales folder of the exercise folder.

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

import os

import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd

from matplotlib import pyplot as plt
# slow debugging because of"Backend Qt5Agg is interactive backend. Turning interactive mode on."
import matplotlib
from inspect import currentframe, getouterframes # for check which functtion called a function
import datetime
import re
try:
    matplotlib.rcParams['backend'] = 'Qt5Agg'
    matplotlib.rcParams['backend.qt5'] = 'PyQt5'
except:
    print('Debug options of matplotlib could not be set.')

def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

# TODO: Provide time estimation in settings?
# TODO: adapt system calibration
# TODO: convertLabels: make it more flexible to get rid of phoneme fixed application of confusionmatrix

class confusionMatrix():

    def __init__(self, parHandle, settings=''):
        """!
        The path are set by the member iniPath(), the defaultSettings will be
        initialized and the signal files will be read by the function iniSignal()
        """

        self.parHandle = parHandle  # handle to the parent gui of CICoachLab

        # this has to be initialized first because the resetting of the handle calls the destructor of the class
        # which resets and clears up everything which has been initialized nicely
        self.parHandle.curExercise['handle'] = self
        self.exerciseName = 'confusionMatrix'

        self.vBLayout = None
        self.controlbars = None

        # get reaction time delay from iniFile configuration and save it under
        self.parHandle.setDefaultCalibration('curExercise', 'time')
        self.parHandle.curExercise['settings']['exerciseName'] = 'confusionMatrix'
        self.parHandle.readIniFile(mode='curExerciseSettings', module='curExercise')

        self.parHandle.curExercise['functions']['prepareRun'] = self.prepareRun
        self.parHandle.curExercise['functions']['quitRun'] = self.quitRun
        self.parHandle.curExercise['functions']['displayResults'] = self.displaySingleResult
        self.parHandle.curExercise['functions']['settingsLoading'] = self.loadSettings
        self.parHandle.curExercise['functions']['settingsDefault'] = self.setDefaultSettings
        self.parHandle.curExercise['functions']['settingsGui'] = None
        self.parHandle.curExercise['functions']['checkConditions'] = None
        self.parHandle.curExercise['functions']['checkParameters'] = self.checkParameters
        self.parHandle.curExercise['functions']['destructor'] = self.__exit__
        self.parHandle.curExercise['functions']['eraseExerciseGui'] = self.eraseExerciseGui
        self.parHandle.curExercise['functions']['calibration'] = self.calibrateConfusionMatrix
        self.parHandle.curExercise['functions']['xlsxExport'] = self.xlsxExportPreparation

        self.setDefaultSettings()
        self.iniPath()
        if settings != '' and settings != 'default':
            # the loaded settings just may overwrite parts of the defaultSettings....
            try:
                self.loadSettings(settings)
            except:
                self.parHandle.dPrint(_translate("confusionMatrix",'confusionMatrix: \nThe settings "', None)
                                      + settings +
                                      _translate("confusionMatrix",'" could not be loaded. ' +
                                        '\n\nDefault values have been set.', None)
                                      , 1, guiMode = True)
        else:
            self.setDefaultSettings()

        self.iniPath()

        # intialize player and generator if necessary
        if self.parHandle.curPlayer['settings']['playerName'] == '':
            self.parHandle.iniSubmodule('player',  'playAudio')
        if self.parHandle.curGenerator['settings']['generatorName'] == '':
            self.parHandle.iniSubmodule('generator',  'genWavreader')

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': __init__()', 2)

        self.parHandle.curExercise['results']   = None

        # in the playButton Mode the user has to push the playButton below the item buttons to procede in the exercise.
        # Otherwise the next item is presented after the input for the item. The gui is generated and buttons are
        # connected to the requirerd functions accordingly (see self.iniGui)
        self.playButtonMode = True
        # handling the wrong input of the user, especially in the playButtonMode. If the user forgets to enter the
        # item answer before he presses pbPlayNextItem the self.failedInputCounter will be counted up and will be
        # reset again to zero if the user enters an item before the pressing of pbPlayNextItem.
        # The user will be informed to enter the answer first before trying to proceede in the run.
        self.failedInputCounter = 0
        # After self.failedInputMaxCounter wrong attempts the run of the exercise will be aborted.
        # The user will be informed to enter the answer first before trying to proceede in the run.
        self.failedInputMaxCounter = 5


        # will be reset in iniSignal
        self.signalContainer = {}
        # will be reset in iniGui
        self.buttonContainer= {}

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving __init__()', 2)
        # counter which indicates to current item within run, including repetitions if items are presenteted repeatedly.
        self.itemCounter = 0
        # counter which counts the number of repetitions of the item indicated by self.itemCounter.
        self.repetitionCounter = 0

        if self.parHandle.frameWork['systemCheck']:
            # setting the new handle without calling the destructor of the class because it has been called already
            # beforehand
            self.parHandle.curExercise['handle'] = self

        self.parHandle.ui.menuExer.addSeparator()
        # add function in exercise menu to measure the time delay
        actionSetup = QtWidgets.QAction(self.parHandle)
        actionSetup.setObjectName("actionMeasureTimeDelay")
        actionSetup.setText(_translate("confusionMatrix", "Measure delay time", None))
        actionSetup.triggered.connect(self.parHandle.calibrateSystem)
        self.parHandle.ui.menuExer.addAction(actionSetup)

        self.parHandle.curExercise['gui']['menu'].append(actionSetup)


    def __exit__(self):
        """!
        The destructor of the class will delete the gui of the exercise with 
        the function eraseExerciseGui(). The path of the exercise will be unset
        by closePath()
        """
        self.parHandle.dPrint(self.exerciseName + ': __exit__()', 2)

        self.eraseExerciseGui()
        self.parHandle.initializeToDefaults(mode='curExercise')
        self.closePath()
        self.parHandle.curExercise['gui']['exerWidgetsDisabled'] = []

        self.parHandle.dPrint(self.exerciseName + ': Leaving __del__()', 2)
        
    def iniPath(self):
        """!
        The dictionary self.parHandle.curExercise['path'] will be filled
        with the 'base', 'preset', 'results' and the confusionmatrix specific
        'signalFiles' path.
        The path entries of the dictionary will be added at the top of the path 
        by sys.path in the frameWork.
        """

        self.parHandle.dPrint(self.exerciseName + ': iniPath()', 2)
        pwd = os.path.join(self.parHandle.frameWork['path']['exercises'],
                           self.exerciseName)
        self.parHandle.curExercise['path']['base']      = pwd
        self.parHandle.curExercise['path']['locales']   = os.path.join(pwd,'locales')
        self.parHandle.curExercise['path']['presets']   = os.path.join(pwd,'presets')
        self.parHandle.curExercise['path']['results']   = os.path.join(pwd,'results')
        self.parHandle.curExercise['path']['analysis'] = os.path.join(pwd, 'analysis')
        self.parHandle.curExercise['path']['signalFiles']  = os.path.join(pwd,'signalFiles')

        self.parHandle.addingPath('curExercise')
        self.parHandle.dPrint(self.exerciseName + ': Leaving iniPath()', 2)

    def closePath(self):
        """!
        The path of the exercise will be removed from sys.path by the frameWork.
        Reset the path dictionary in self.parHandle.curExercise by
        setting entries to empty strings and by removing the exercise specific
        'signalFiles' entry.
        """
        self.parHandle.dPrint(self.exerciseName + ': closePath()', 2)
        
        self.parHandle.closePath('curExercise')
        self.parHandle.curExercise['path']['base']      = ''
        self.parHandle.curExercise['path']['presets']   = ''
        self.parHandle.curExercise['path']['results']   = ''
        self.parHandle.curExercise['path']['analysis'] = ''
        self.parHandle.curExercise['path']['signalFiles']  = ''

        #remove optional path from list
        self.parHandle.curExercise['path'].pop('signalFiles')

        self.parHandle.dPrint(self.exerciseName + ': closePath()', 2)
            
    def eraseExerciseGui(self):
        """!
        The exercise gui elements which are found in the layouts will be removed. self.vBLayout is the base
        layout for the other layouts.
        """

        self.parHandle.dPrint(self.exerciseName + ': eraseExerciseGui()', 2)
        # try to get children of vBlayOut
        try:
            children = self.vBLayout.children()
        except:
            children = []
        if self.vBLayout != None and children:
            for layOutItem in children:
                for ii in reversed(range(layOutItem.count())):
                    layOutItem.itemAt(ii).widget().setParent(None)
            # the layout which is assigned to the exercise container widget cannot be deleted it just can be moved to
            # another temporary widget
            QtWidgets.QWidget().setLayout(self.parHandle.ui.exerWidget.layout())

        self.parHandle.curExercise['gui']['exerWidgets'] = list()

        self.parHandle.dPrint(self.exerciseName + ': Leaving eraseExerciseGui()', 2)


    def iniSignal(self):
        """!
        All signal files of the single items which are found in the signalFiles folder  are loaded into
        the signalContainer.
        """
        self.signalContainer = {}
        
        self.parHandle.dPrint(self.exerciseName + ': iniSignal()', 2)
        
        for ii in range(len(self.parHandle.curExercise['settings']['items'])):
            signalFilename = ''
            try:
                filepath = self.parHandle.curExercise['path']['signalFiles']
                # windows does not allow utf8 filennames, linux does
                #if self.parHandle.frameWork['settings']['system']['sysname'] == 'Windows':
                signalItem = self.convertLabels(self.parHandle.curExercise['settings']['items'][ii],
                                                mode='phoneToASCII')
                #else:
                #    signalItem = self.parHandle.curExercise['settings']['items'][ii]
                signalFilename = os.path.join(filepath, signalItem)
                try:
                    signal = self.parHandle.curGenerator['functions']['run'](signalFilename)
                    self.signalContainer[signalItem] = signal
                except:
                    msg = 'Exception: Could not run generator (' + \
                          self.parHandle.curGenerator['settings']['generatorName'] + \
                          'with signal file ' + signalFilename
                    self.parHandle.dPrint(msg, 1,guiMode=True)
            except:
                self.parHandle.dPrint('Filling of signalContainer interrupted with :' + signalFilename, 2)
        
        self.parHandle.dPrint(self.exerciseName + ': Leaving iniSignal()', 2)


    def convertLabels(self, input, mode='asciiToPhone'):
        """!
        This function assumes that the defined items are phonemes. In case of windows a conversion of phoneme names
        is necessary because windows does not support utf8 file names.
        mode> 'phoneToASCII' or asciiToPhone, default: asciiToPhone
        """

        self.parHandle.dPrint(self.exerciseName + ': phoneToASCII()', 2)

        a = ['a', 'e', 'i', 'o', 'u', 'ɛ', 'y', 'ø', 'p', 'b', 'd', 't', 'k', 'g', 'm', 'n', 'ŋ',
                  'r', 'f', 'v', 's', 'z','ʃ', 'ʒ', 'ç', 'x', 'h', 'j', 'l']

        b = ['ah', 'eh', 'ih', 'oh', 'uh', 'aeh', 'ueh', 'oeh', 'p', 'b', 'd', 't', 'k', 'g', 'm', 'n', 'ng',
                    'r', 'f', 'v', 's', 'z', 'sch', 'gsch', 'ch2', 'x', 'h', 'j', 'l']

        if mode == 'asciiToPhone':
            source = b
            target = a
        elif mode == 'phoneToASCII':
            source = a
            target = b

        self.parHandle.dPrint(self.exerciseName + ': Leaving phoneToASCII()', 2)
        if input in source:
            return target[source.index(input)]
        else:
            return input


    def iniGui(self):
        """!
        The gui elements of the exercise will be initialized. The gui elements
        are initialized according to the loaded settings. The number of buttons 
        for the item identification and the activation of the repetition
        button depend on the loaded settings.
        A start and a cancel button are always generated.
        A field is provided for visual/text feedback is provided if the settings require such a feedback.
        """

        self.buttonContainer = {}
        self.parHandle.dPrint(self.exerciseName + ': iniGui()', 2)
        # Take items from settings and generate buttons for each

        subbWidget = self.parHandle.ui.exerWidget

        self.vBLayout = QtWidgets.QVBoxLayout()
        subbWidget.setLayout(self.vBLayout)
        self.gridLauyout = QtWidgets.QGridLayout()
        self.vHLayoutPreFB = QtWidgets.QHBoxLayout()
        self.vHLayoutFB = QtWidgets.QHBoxLayout()
        self.vHLayoutpostFB = QtWidgets.QHBoxLayout()
        self.vHLayoutStartQuit = QtWidgets.QHBoxLayout()

        self.vBLayout.addLayout(self.gridLauyout)
        self.vBLayout.addLayout(self.vHLayoutPreFB)
        self.vBLayout.addLayout(self.vHLayoutFB)
        self.vBLayout.addLayout(self.vHLayoutpostFB)
        self.vBLayout.addLayout(self.vHLayoutStartQuit)

        self.ui = dict()
        self.ui['itemButtons'] = dict()

        # with the playButtonMode set the items will be presented after the user has provided an answer for an item
        # and pressed the play button. otherwise the next item is presented directly after the input of the answer.
        if self.playButtonMode:
            self.ui['pbPlayNextItem'] = QtWidgets.QPushButton(subbWidget, text=
                _translate("confusionMatrix", 'Next item', None)) #
            self.ui['pbPlayNextItem'].clicked.connect(self.runNextItem)
            #self.ui['pbPlayNextItem'].setMaximumHeight(60)
            #self.ui['pbPlayNextItem'].setMaximumWidth(100)
            self.ui['pbPlayNextItem'].setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                  QtWidgets.QSizePolicy.Maximum)
            self.ui['pbPlayNextItem'].show()

            self.vHLayoutPreFB.addWidget(self.ui['pbPlayNextItem'])
            self.buttonContainer['pbPlayNextItem'] = self.ui['pbPlayNextItem']
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbPlayNextItem'])


        if self.parHandle.curExercise['settings']['feedBackCorrection']:
            self.ui['txFeedback'] = QtWidgets.QLabel(subbWidget, text='')
            self.ui['txFeedback'].setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter)
            self.ui['txFeedback'].setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
            # setting example message to determine height of fields
            msg = 'Antwort: a        Presentiert: ' + \
                 'a \n\nDie Antwort war falsch.'
            self.ui['txFeedback'].setText(msg)

            # getting minimum size of qItem which depends on the used text and font
            fm = QtGui.QFontMetrics(self.ui['txFeedback'].font())
            qSize = QtCore.QSize(fm.width(self.ui['txFeedback'].text()), self.ui['txFeedback'].width())
            self.ui['txFeedback'].setMaximumHeight(qSize.height())
            self.ui['txFeedback'].setText("")
            self.vHLayoutFB.addWidget(self.ui['txFeedback'])
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['txFeedback'])

        self.ui['pbCancelRun'] = QtWidgets.QPushButton(subbWidget, text=
        _translate("confusionMatrix", 'Cancel', None))
        self.ui['pbCancelRun'].clicked.connect(self.quitRun)
        self.ui['pbCancelRun'].setMaximumHeight(40)
        self.ui['pbCancelRun'].setDisabled(True)

        self.ui['pbStartRun'] = QtWidgets.QPushButton(subbWidget, text=
        _translate("confusionMatrix", 'Start', None))
        self.ui['pbStartRun'].clicked.connect(self.startRun)
        self.ui['pbStartRun'].setMaximumHeight(40)

        if self.parHandle.curExercise['settings']['itemRepetition'] > 0:
            self.ui['pbRepPres'] = QtWidgets.QPushButton(subbWidget, text=
            _translate("confusionMatrix", 'Repeat', None))
            self.ui['pbRepPres'].clicked.connect(self.presentCurrentItem)
            self.ui['pbRepPres'].setMaximumHeight(60)
            self.ui['pbRepPres'].setDisabled(True)

            self.vHLayoutpostFB.addWidget(self.ui['pbRepPres'])
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbRepPres'])

        self.vHLayoutStartQuit.addWidget(self.ui['pbCancelRun'])
        self.vHLayoutStartQuit.addWidget(self.ui['pbStartRun'])
        self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbCancelRun'])
        self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbStartRun'])

        self.parHandle.showInformation(_translate("confusionMatrix", 'Initializing gui: ... ', None))

        ii = 0
        jj = 0
        for item in self.parHandle.curExercise['settings']['items']:
            if 'labels' in self.parHandle.curExercise['settings'] and\
                    self.parHandle.curExercise['settings']['labels'][ii]:
                self.ui['itemButtons'][item] = QtWidgets.QPushButton(subbWidget, text='', objectName=item)

                pixmap = self.parHandle.mathTexToQPixmap(mathTex=self.parHandle.curExercise['settings']['labels'][ii],
                                               fontsize=
                                               int(np.round(int(self.parHandle.frameWork['settings']['fontSize'])*1.5)))
                self.ui['itemButtons'][item].setIcon(QtGui.QIcon(pixmap))
                self.ui['itemButtons'][item].setIconSize(pixmap.rect().size())
                self.ui['itemButtons'][item].setFocusPolicy(QtCore.Qt.NoFocus)
            else:
                self.ui['itemButtons'][item] = QtWidgets.QPushButton(subbWidget,text = item, objectName = item)

            if ii > 0 and (self.parHandle.curExercise['settings']['itemsGrouping'][ii] != self.parHandle.curExercise['settings']['itemsGrouping'][ii-1]):
                jj = 0
            self.gridLauyout.addWidget(self.ui['itemButtons'][item], self.parHandle.curExercise['settings']['itemsGrouping'][ii], jj)
            self.buttonContainer[item] = self.ui['itemButtons'][item]
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.buttonContainer[item])
            ii = ii + 1
            jj = jj + 1

        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(True)
            except:
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)
        self.ui['pbStartRun'].setDisabled(False)

        self.connectButtons()

        qSizeMaxWidth = 0
        qSizeMaxHeight = 0
        for item in self.parHandle.curExercise['settings']['items']:
            qSizeWidth = self.ui['itemButtons'][item].width()
            qSizeHeight = self.ui['itemButtons'][item].height()
            if qSizeWidth > qSizeMaxWidth:
                qSizeMaxWidth = qSizeWidth
            if qSizeHeight > qSizeMaxHeight:
                qSizeMaxHeight = qSizeHeight
        for item in self.parHandle.curExercise['settings']['items']:
            self.ui['itemButtons'][item].setFixedWidth(qSizeMaxWidth)
            self.ui['itemButtons'][item].setFixedHeight(qSizeMaxHeight)
        subbWidget.show()

        self.parHandle.showInformation('')

        self.parHandle.dPrint(self.exerciseName + ': Leaving iniGui()', 2)


    def presentCurrentItem(self):
        """!The current item will be played if the number of maximum presentation is not surpassed."""
        
        self.parHandle.dPrint('Quit presentCurrentItem()', 2)

        if self.repetitionCounter < self.parHandle.curExercise['settings']['itemRepetition']+1:
            item = self.parHandle.curExercise['settings']['items'][int(self.idxOrder[self.itemCounter])]
            self.parHandle.dPrint('Item: ' + item, 4)

            #if self.parHandle.frameWork['settings']['system']['sysname'] == 'Windows':
            signalItem = self.convertLabels(item, mode='phoneToASCII')
            #else:
            #    signalItem = item
            try:
                self.parHandle.curPlayer['functions']['run'](self.signalContainer[signalItem])
                #updating documentation of itemRepetition
                self.parHandle.curRunData['results']['repetitions'][self.itemCounter] = \
                    self.repetitionCounter
                # counting presentations only if the sound could be played back
                self.repetitionCounter = self.repetitionCounter + 1
                idxRun = int(self.runIDX[self.itemCounter])
                idxItem = int(self.idxOrder[self.itemCounter])
                self.parHandle.curRunData['results']['audioRepetitionCounter'][idxRun][idxItem] = self.repetitionCounter
            except:
                self.parHandle.dPrint('Could not open signalItem: '+signalItem, 1)

        else:
            self.parHandle.dPrint(_translate("confusionMatrix","Number of maximum presentations is exceeded.", None),
                                  0, guiMode=True)
        self.parHandle.dPrint('Quit presentCurrentItem()', 2)


    def itemSelection(self):
        """!
        This function is called when the user provides the item input after the item presentation
        """
        self.parHandle.dPrint(self.exerciseName + ': itemSelection()', 2)
        # the timer to stop the reaction time ist stopped here, it was started by the player playAtAudio automatically
        self.parHandle.measureReactionTime(self.parHandle, mode='stop')

        itemAnswer = self.parHandle.sender().objectName()
        idxRun = int(self.runIDX[self.itemCounter])
        idxItem = int(self.idxOrder[self.itemCounter])
        self.parHandle.curRunData['results']['itemInput'][idxRun][idxItem] = \
            self.parHandle.curRunData['results']['itemInput'][idxRun][idxItem] + [itemAnswer]

        # if no playButton is applied the next item will be presented, no repetition possible
        if not(self.playButtonMode):
            self.itemCounter = self.itemCounter + 1
            self.run()


        self.parHandle.dPrint(self.exerciseName + ': Leaving itemSelection()', 2)

    def connectButtons(self):
        """!
        The buttons of the items within the confusion matrix will be connected to
        self.run() which handles the entered answers and the playback of the
        next signal sample.
        """

        self.parHandle.dPrint(self.exerciseName + ': connectButtons()', 2)
        for item in self.ui['itemButtons'].keys():
            try:
                self.parHandle.dPrint(self.ui['itemButtons'][item].objectName())
                self.ui['itemButtons'][item].show()
                self.ui['itemButtons'][item].clicked.connect(self.itemSelection)
            except:
                self.parHandle.dPrint('Could not initialize Buttons')

        self.parHandle.dPrint(self.exerciseName + ': Leaving connectButtons()', 2)


    def startRun(self):
        """!
        A run of the exercise is started. The gui elements of the exercise are enabled and the Start button is disabled.
        runButton is called, which starts the measurement of the reaction time.
        """

        self.parHandle.dPrint(self.exerciseName + ': startRun()', 2)

        self.parHandle.curRunData['runAccomplished'] = False

        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(False)
            except:
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)
        self.ui['pbStartRun'].setDisabled(True)
        self.parHandle.curExercise['gui']['exerWidgetsDisabled'].append(self.ui['pbStartRun'])

        self.runButton()

        ii = 0
        # resetting size policy again to focus, otherwise button will not remain pushed after user input
        for item in self.parHandle.curExercise['settings']['items']:
            if 'labels' in self.parHandle.curExercise['settings'] and\
                    self.parHandle.curExercise['settings']['labels'][ii]:
                self.ui['itemButtons'][item].setFocusPolicy(QtCore.Qt.StrongFocus)
            ii = ii + 1

        self.parHandle.dPrint(self.exerciseName + ': Leaving startRun()', 2)


    def prepareRun(self):
        """!
        This function is called to prepare a new run. The presentation of the signals has to be started by pressing the
        Start button. This function is called by CICoachLab by self.parHandle.curExercise['functions']['prepareRun'].

        If no gui elements exist the gui initialized. If no signal signals exist the audie signal will be initialized.
        The order of the presented signals is randomized.
        The result variables are initialized. 
        """
        self.parHandle.dPrint(self.exerciseName + ': prepareRun()', 2)
        
        if len(self.parHandle.curExercise['gui']['exerWidgets']) == 0:
            self.iniGui()
        if len(self.signalContainer) == 0:
            # iniSignal is called in the loadSetting function
            self.iniSignal()

        self.itemCounter = 0
        itemLen = len(self.parHandle.curExercise['settings']['items'])
        idx = np.arange(itemLen)
        numberOfRuns = self.parHandle.curExercise['settings']['numberOfRuns']
        self.runIDX = np.ones((itemLen * numberOfRuns,1))
        self.runIDXItemCounter = 0
        idxNew = np.zeros((itemLen, numberOfRuns))
        for ii in range(self.parHandle.curExercise['settings']['numberOfRuns']):
            np.random.shuffle(idx)
            idxNew[:,ii] = idx
            self.runIDX[ii*itemLen:itemLen*(ii+1)] = ii
            
        self.idxOrder = np.reshape(idxNew.transpose(), (numberOfRuns*itemLen, 1))
        del idxNew

        
        numberOfRuns  = self.parHandle.curExercise['settings']['numberOfRuns']
        items        = self.parHandle.curExercise['settings']['items']
        self.parHandle.curRunData['results'] = dict()
        self.parHandle.curRunData['results']['confMat']     = []
        self.parHandle.curRunData['results']['reactMat']    = []
        self.parHandle.curRunData['results']['stopTime']    = [[]] * numberOfRuns
        self.parHandle.curRunData['results']['itemInput']   = [[]] * numberOfRuns

        self.parHandle.curRunData['results']['runIDX']      = [[]] * numberOfRuns
        self.parHandle.curRunData['results']['itemPresented']= [[]] * numberOfRuns
        self.parHandle.curRunData['results']['itemAnswer']  = [[]] * numberOfRuns
        self.parHandle.curRunData['results']['itemCounter'] = [[]] * numberOfRuns
        self.parHandle.curRunData['results']['audioRepetitionCounter'] = [[]] * numberOfRuns

        self.parHandle.curRunData['results']['repetitions'] = np.zeros(numberOfRuns)


        #dfReps  = pd.DataFrame(np.zeros((len(items), len(items))), index=items, columns=items)

        for runIndex in range(numberOfRuns):
            print('runIndex:'+str(runIndex), 5)
            dfConfMat = pd.DataFrame(np.zeros((len(items), len(items))), index=items, columns=items)
            dfReactMat = pd.DataFrame(np.zeros((len(items), len(items))), index=items, columns=items)

            self.parHandle.curRunData['results']['confMat'].append(dfConfMat)
            self.parHandle.curRunData['results']['reactMat'].append(dfReactMat)
            self.parHandle.curRunData['results']['itemInput'][runIndex] = [[]] * len(items)

            self.parHandle.curRunData['results']['stopTime'][runIndex] = [[]] * len(items)
            self.parHandle.curRunData['results']['runIDX'][runIndex] = [[]] * len(items)
            self.parHandle.curRunData['results']['itemPresented'][runIndex] = [[]] * len(items)
            self.parHandle.curRunData['results']['itemAnswer'][runIndex] = [[]] * len(items)
            self.parHandle.curRunData['results']['itemCounter'][runIndex] = [[]] * len(items)


            self.parHandle.curRunData['results']['audioRepetitionCounter'][runIndex] = np.zeros(len(items))




        
        self.parHandle.curRunData['numberOfItems'] = len(self.idxOrder)
        if self.parHandle.frameWork['systemCheck']:
            self.runButton()

        self.parHandle.dPrint(self.exerciseName + ': Leaving prepareRun()', 2)


    def runNextItem(self):
        """Proceeding to next item"""

        # stepping to next item after
        self.itemCounter = self.itemCounter + 1
        self.run()



    def runButton(self, event = '', forcedInput=''):
        """!This function measures the reaction time and calls self.run() """

        if self.parHandle.frameWork['systemCheck']:
            # just for testing the system, e.g. for measuring the systems reaction time
            # the first item is presented marked as virtual user input
            forcedInput = self.parHandle.curExercise['settings']['items'][0]

        self.parHandle.dPrint('runButton after reaction time measurement:', 2)
        self.run(forcedInput)
        self.parHandle.dPrint('Quit runButton:', 2)


    def run(self, forcedInput=''):
        """!
        This function handles the user input and plays back the next signal
        item after the user input if necessary.
        """
        
        # the next item will be presented for the first time at start up of this function
        self.repetitionCounter = 0

        self.runIDXItemCounter = 0

        self.parHandle.dPrint(self.exerciseName + ': run()', 2)

        self.parHandle.dPrint(self.itemCounter, 4)
        self.parHandle.dPrint(len(self.idxOrder), 4)

        
        #if its the first call of this function only sound will be played back and
        # no user input hast to be checked
        if self.itemCounter > 0:
            self.parHandle.dPrint('Pre Sender:', 4)
            try:
                if forcedInput == '':
                    inputAnswer = self.parHandle.sender().objectName()
                else:
                    inputAnswer = forcedInput
                runIdx = int(self.runIDX[self.itemCounter - 1])
                itemIdx = int(self.idxOrder[self.itemCounter-1])
                if len(self.parHandle.curRunData['results']['itemInput'][runIdx][itemIdx]) == 0:
                    # counting up the failuredInputCounter
                    self.failedInputCounter = self.failedInputCounter + 1
                    if self.failedInputCounter > self.failedInputMaxCounter:
                        msg = _translate("confusionMatrix",
                                         'Please get some help, because the process of the exercise stagnetes.\n\n'
                                         'This run will be aborted. You may try to rerun the exercise.', None)
                        # been waiting enough for the correct user input. Aborting the run of the exercise.
                        self.parHandle.dPrint(msg, 0, guiMode=True)
                    else:
                        msg = _translate("confusionMatrix",
                                         'Please enter your answer before you continue to the next item. \n\n'
                                         'Press one of the above input options', None)
                        # doing nothing but waiting for the next input.
                        self.parHandle.dPrint(msg, 0, guiMode=True)
                    return
                else:
                    self.failedInputCounter = 0

                runIDX = int(self.runIDX[self.itemCounter-1])
                itemIDX = int(self.idxOrder[self.itemCounter - 1])
                itemPresented = self.parHandle.curExercise['settings']['items'][itemIDX]
                itemAnswer = self.parHandle.curRunData['results']['itemInput'][runIDX][itemIDX][-1]

                self.parHandle.dPrint('Presented item: ' + itemPresented, 4)
                self.parHandle.dPrint('Pressed item: ' + itemAnswer, 4)

                self.parHandle.curRunData['results']['runIDX'][runIDX][itemIdx] = runIDX
                self.parHandle.curRunData['results']['itemPresented'][runIDX][itemIdx] = itemPresented
                self.parHandle.curRunData['results']['itemAnswer'][runIDX][itemIdx] = itemAnswer
                self.parHandle.curRunData['results']['itemCounter'][runIDX][itemIdx] = self.itemCounter-1


                self.parHandle.curRunData['results']['confMat'][int(runIDX)][itemPresented][itemAnswer] = \
                    self.parHandle.curRunData['results']['confMat'][int(runIDX)][itemPresented][itemAnswer]+1
                self.parHandle.curRunData['results']['reactMat'][int(runIDX)][itemPresented][itemAnswer] = \
                    self.parHandle.frameWork['temp']['reactionTimeAfterPresentation']
                self.parHandle.curRunData['results']['stopTime'][int(runIDX)][itemIDX] = \
                    pd.to_datetime(datetime.datetime.today())
                #self.parHandle.curRunData['results']['itemInput'][int(runIDX)][itemPresented][itemAnswer] = \
                #    self.parHandle.curRunData['results']['itemInput'][self.itemCounter]

                feedBackMsg = 'Default message:'
                if self.parHandle.curExercise['settings']['feedBack']:
                    stdPalette = self.parHandle.ui.exerWidget.palette()
                    if itemPresented == itemAnswer:
                        # Answer was correct
                        newPalette = QtGui.QPalette(QtGui.QColor(131, 255, 131))
                    else:
                        # change color of widget to red
                        #newPalette = QtGui.QPalette(QtCore.Qt.red)
                        newPalette = QtGui.QPalette(QtGui.QColor(255, 131, 131))
                    self.parHandle.changePalette(self.parHandle.ui.exerWidget, newPalette)
                    print(feedBackMsg)

                    timer = QtCore.QTimer(self.parHandle, timerType = QtCore.Qt.PreciseTimer)
                    timer.setSingleShot(True)
                    timer.setInterval(self.parHandle.curExercise['settings']['feedBackTime'] * 1000)
                    timer.timeout.connect(lambda: self.parHandle.changePalette(self.parHandle.ui.exerWidget, stdPalette))
                    timer.start()

                    print(feedBackMsg)
                    self.parHandle.dPrint('Visual feedback is provided', 4)
                    self.parHandle.ui.exerWidget.show()
                    self.parHandle.show()

                if self.parHandle.curExercise['settings']['feedBackCorrection']:
                    if itemPresented == itemAnswer:
                        # Show answer and presentation and Text: Answer was correct
                        feedBackMsg = _translate("confusionMatrix",'Input: ', None) + itemAnswer + \
                                      _translate("confusionMatrix",'        Presented: ', None) + \
                                      itemPresented + '\n' + \
                                      _translate("confusionMatrix",'The answer was correct.', None)
                    else:
                        # Show answer and presentation and Text: Answer was wrong
                        feedBackMsg = _translate("confusionMatrix",'Input: ', None) + itemAnswer + \
                                    _translate("confusionMatrix",'        Presented: ', None) + \
                                       itemPresented + '\n' + \
                                    _translate("confusionMatrix",'The answer was wrong.', None)

                    self.ui['txFeedback'].setText(feedBackMsg)
                    self.parHandle.dPrint('Text feedback is provided', 4)
            except:
                self.parHandle.dPrint('No valid user input', 1)

        try:
            msg = 'Running progress {:3.2f} %'.format((float(self.itemCounter)/float(self.parHandle.curRunData['numberOfItems']))*100)
            self.parHandle.showInformation(msg)
        except:
            self.parHandle.dPrint('Could not show running process', 3)

        # the next signal item is presented or the run will be finished after the last item
        if self.itemCounter == len(self.idxOrder):
            self.parHandle.closeDownRun()
        else:
            self.presentCurrentItem()



        self.parHandle.dPrint(self.exerciseName + ': Leaving run()', 2)


    def cancelRun(self):
        """!
        This functions will finish the run. The subject is asked for
            confirmation before calling the function quitRun().
        """
        if self.presentationCounter > 0:
            #'Möchten Sie die Übung abbrechen?
            msg = _translate("confusionMatrix",'Do you want to cancel the run in progress?', None)
        else:
            msg = _translate("confusionMatrix",'Do you want to cancel the run?', None)

        response = QtWidgets.QMessageBox.question(self.parHandle.ui.exerWidget,
                                                  _translate("confusionMatrix",'CICoachLab Information', None), msg)
        if response == QtWidgets.QMessageBox.Yes:
            self.quitRun()


    def quitRun(self):
        """!
        This functions finalizes the run of the exercise after the last item
        of the run or if the user cancels the run with the Quit run button.

        The results are presented if required.
        The data will be saved by calling the framework function.
        """

        self.parHandle.dPrint(self.exerciseName + ': quitRun()', 2)
        if self.parHandle.curExercise['settings']['afterRunDisplay'] and\
                not( self.parHandle.frameWork['settings']['debug']['noPLotMode']):
            self.parHandle.dPrint('Showing results:', 3)
            self.parHandle.dPrint(self.parHandle.curRunData['results']['confMat'], 4)
            self.displaySingleResult(self.parHandle.curRunData)

        self.ui['pbStartRun'].setEnabled(True)
        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
        if callingFunctionName != 'cancelRun':
            self.parHandle.curRunData['runAccomplished'] = True
            # recheck if run accomplishment is True if a runAccomplishedCondition is defined
        self.parHandle.dPrint(self.exerciseName + ': Leaving quitRun() > closeDownRun', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()

        self.parHandle.dPrint(self.exerciseName + ': Leaving quitRun()', 2)


    def calibrateConfusionMatrix(self, filename=''):
        """!
        Wrapper function which starts the run and calculates the results.


        It checks if the function is called correctly: The calling function must be called calibrateSustem() which is
        defined in CICoachLab.py

        """
        callingFunctionName = getouterframes(currentframe(), 2)[1][3]

        if callingFunctionName == 'calibrateSystem':
            try:
                self.parHandle.setDefaultCalibration('curExercise', 'time')

                self.parHandle.frameWork['settings']['muteSignal'] = True

                self.parHandle.iniRun(self.parHandle)
                # the run will be run automatically until it is finished and closeDownRun() will be run within this function

                self.parHandle.frameWork['settings']['muteSignal'] = False

                self.parHandle.curExercise['calibration']['time']['date'] = \
                    self.parHandle.curRunData['time']['startASCII']
                self.parHandle.curExercise['calibration']['time']['iterations'] = 0
                self.parHandle.curExercise['calibration']['time']['settingsName'] = \
                    self.parHandle.curExercise['settings']['settingsName']

                panel = pd.concat(self.parHandle.curRunData['results']['reactMat'])

                # getting average over first column which contains the virtual answers of the calibration
                dfMeans = panel.mean(axis=1)[0]
                dfStd = panel.std(axis=1)[0]
                msg = 'Exercise ConfusionMatrix: Calibration of reaction time:\nSystem delay: ' + str(dfMeans) +\
                    ' +/- ' + str(dfStd) +' s.'
                self.parHandle.dPrint(msg, 2)

                exerName = 'confusionMatrix'
                self.parHandle.curExercise['calibration']['time']['time']= dfMeans
                self.parHandle.curExercise['calibration']['time']['stdDev'] = dfStd

                self.parHandle.curExercise['calibration']['time']['unit'] = 's'
                self.parHandle.curExercise['calibration']['time']['iterations'] = panel.shape[0] * panel.ndim  # 0
                self.parHandle.curExercise['calibration']['time']['settingsName'] = self.parHandle.curExercise[
                    'settings']['settingsName']
                self.parHandle.curExercise['calibration']['time']['resultFile'] = filename  # ''
                self.parHandle.curExercise['calibration']['time']['info'] = []  # ''

                #self.parHandle.writeIniFile()

            except:
                self.parHandle.frameWork['settings']['muteSignal'] = False

        else:
            return


    def setDefaultSettings(self):
        """!
        The default parameters of the tests will be set. 
        """

        self.parHandle.dPrint(self.exerciseName + ': setDefaultSettings()', 2)
        self.parHandle.curExercise['settings']['version']            = '0.1'

        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        self.parHandle.curExercise['settings']['exerciseName']       = self.exerciseName
        self.parHandle.curExercise['settings']['settingsName']       = 'default'
        self.parHandle.curExercise['settings']['items']           = ['a', 'e', 'i', 'o', 'u', 'ɛ', 'ø', 'y', 's', 'z', 'b', 'g']
        self.parHandle.curExercise['settings']['itemsExample']    = ['Aal', 'Emil', 'Ida', 'Obst, langes O', 'Ärger', 'Östlich, kurzes Ö', 'Übermut, langes Ü', 'Ass', 'Sah', 'Berta', 'Gustav']
        self.parHandle.curExercise['settings']['itemsGrouping']   = [ 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2]
        self.parHandle.curExercise['settings']['itemRepetition'] = 2
        self.parHandle.curExercise['settings']['numberOfRuns']       = 1
        self.parHandle.curExercise['settings']['afterRunDisplay']    = True
        self.parHandle.curExercise['settings']['externalResultsWindow']     = True
        self.parHandle.curExercise['settings']['comment'] = ''
        
        self.parHandle.curExercise['settings']['player']             = 'playQtAudio'
        self.parHandle.curExercise['settings']['playerSettings']     = 'default'
        self.parHandle.curExercise['settings']['preprocessor']          = ''
        self.parHandle.curExercise['settings']['preprocessorSettings']  = ''
        self.parHandle.curExercise['settings']['generator']          = 'genWavreader'
        self.parHandle.curExercise['settings']['generatorSettings']  = 'default'

        self.parHandle.curExercise['settings']['feedBack']              = False
        self.parHandle.curExercise['settings']['feedBackTime']          = 0.25
        self.parHandle.curExercise['settings']['feedBackCorrection']    = False
        self.parHandle.curExercise['settings']['prerunCondition'] = ''
        self.parHandle.curExercise['settings']['postrunCondition'] = ''

        self.parHandle.curExercise['settingLimits'] = dict()
        # exerciseName and settingsName will be handled especially in SettingsDialogCall,
        # ['editable'] will not take effect
        self.parHandle.curExercise['settingLimits']['exerciseName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['exerciseName']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['exerciseName']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['exerciseName']['range'] = []
        self.parHandle.curExercise['settingLimits']['exerciseName']['editable'] = False

        # exerciseName and settingsName will be handled especially in SettingsDialogCall,
        # ['editable'] will not take effect
        self.parHandle.curExercise['settingLimits']['settingsName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['settingsName']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['settingsName']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['settingsName']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['settingsName']['range'] = []
        self.parHandle.curExercise['settingLimits']['exerciseName']['editable'] = True

        self.parHandle.curExercise['settingLimits']['items'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['items']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['items']['listStyle'] = True
        self.parHandle.curExercise['settingLimits']['items']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['items']['range'] = []
        self.parHandle.curExercise['settingLimits']['items']['editable'] = True

        self.parHandle.curExercise['settingLimits']['itemsExample'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['itemsExample']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['itemsExample']['listStyle'] = True
        self.parHandle.curExercise['settingLimits']['itemsExample']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['itemsExample']['range'] = []
        self.parHandle.curExercise['settingLimits']['itemsExample']['editable'] = True

        self.parHandle.curExercise['settingLimits']['itemsGrouping'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['itemsGrouping']['type'] = 'int'
        self.parHandle.curExercise['settingLimits']['itemsGrouping']['listStyle'] = True
        self.parHandle.curExercise['settingLimits']['itemsGrouping']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['itemsGrouping']['range'] = [0, 7]
        self.parHandle.curExercise['settingLimits']['itemsGrouping']['editable'] = True

        self.parHandle.curExercise['settingLimits']['itemRepetition'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['itemRepetition']['type'] = 'int'
        self.parHandle.curExercise['settingLimits']['itemRepetition']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['itemRepetition']['range'] = [0, 7]
        self.parHandle.curExercise['settingLimits']['itemRepetition']['unit'] = ''
        self.parHandle.curExercise['settingLimits']['itemRepetition']['editable'] = True

        self.parHandle.curExercise['settingLimits']['numberOfRuns'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['numberOfRuns']['type'] = 'int'
        self.parHandle.curExercise['settingLimits']['numberOfRuns']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['numberOfRuns']['range'] = [1, 9]
        self.parHandle.curExercise['settingLimits']['numberOfRuns']['unit'] = ''
        self.parHandle.curExercise['settingLimits']['numberOfRuns']['editable'] = True

        self.parHandle.curExercise['settingLimits']['afterRunDisplay'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['afterRunDisplay']['type'] = 'bool'
        self.parHandle.curExercise['settingLimits']['afterRunDisplay']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['afterRunDisplay']['range'] = []
        self.parHandle.curExercise['settingLimits']['afterRunDisplay']['editable'] = True

        self.parHandle.curExercise['settingLimits']['externalResultsWindow'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['externalResultsWindow']['type'] = 'bool'
        self.parHandle.curExercise['settingLimits']['externalResultsWindow']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['externalResultsWindow']['range'] = []
        self.parHandle.curExercise['settingLimits']['externalResultsWindow']['editable'] = True

        self.parHandle.curExercise['settingLimits']['comment'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['comment']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['comment']['mandatory'] = False
        self.parHandle.curExercise['settingLimits']['comment']['range'] = []
        self.parHandle.curExercise['settingLimits']['comment']['editable'] = True

        self.parHandle.curExercise['settingLimits']['player'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['player']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['player']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['player']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['player']['range'] = ['playAudioQt'] #TODO: fill preselection with availabel players
        self.parHandle.curExercise['settingLimits']['player']['editable'] = True
        self.parHandle.curExercise['settingLimits']['player']['default'] = 'playAudio'

        self.parHandle.curExercise['settingLimits']['playerSettings'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['playerSettings']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['playerSettings']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['playerSettings']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['playerSettings']['range'] = []
        self.parHandle.curExercise['settingLimits']['playerSettings']['editable'] = True
        self.parHandle.curExercise['settingLimits']['playerSettings']['default'] = 'default'

        self.parHandle.curExercise['settingLimits']['preprocessor'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['preprocessor']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['preprocessor']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['preprocessor']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['preprocessor']['range'] = []
        self.parHandle.curExercise['settingLimits']['preprocessor']['editable'] = True
        self.parHandle.curExercise['settingLimits']['preprocessor']['default'] = ''

        self.parHandle.curExercise['settingLimits']['preprocessorSettings'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['range'] = []
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['editable'] = True
        self.parHandle.curExercise['settingLimits']['preprocessorSettings']['default'] = ''

        self.parHandle.curExercise['settingLimits']['generator'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['generator']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['generator']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['generator']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['generator']['range'] = ['genWavReader']
        self.parHandle.curExercise['settingLimits']['generator']['editable'] = True
        self.parHandle.curExercise['settingLimits']['generator']['default'] = 'genWavReader'

        self.parHandle.curExercise['settingLimits']['generatorSettings'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['generatorSettings']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['generatorSettings']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['generatorSettings']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['generatorSettings']['range'] = []
        self.parHandle.curExercise['settingLimits']['generatorSettings']['editable'] = True
        self.parHandle.curExercise['settingLimits']['generatorSettings']['default'] = 'default'

        self.parHandle.curExercise['settingLimits']['prerunCondition'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['prerunCondition']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['prerunCondition']['mandatory'] = False
        self.parHandle.curExercise['settingLimits']['prerunCondition']['comboBoxStyle'] = False
        self.parHandle.curExercise['settingLimits']['prerunCondition']['range'] = []
        self.parHandle.curExercise['settingLimits']['prerunCondition']['editable'] = True
        self.parHandle.curExercise['settingLimits']['prerunCondition']['default'] = ''

        self.parHandle.curExercise['settingLimits']['postrunCondition'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['postrunCondition']['type'] = 'string'
        self.parHandle.curExercise['settingLimits']['postrunCondition']['mandatory'] = False
        self.parHandle.curExercise['settingLimits']['postrunCondition']['comboBoxStyle'] = False
        self.parHandle.curExercise['settingLimits']['postrunCondition']['range'] = []
        self.parHandle.curExercise['settingLimits']['postrunCondition']['editable'] = True
        self.parHandle.curExercise['settingLimits']['postrunCondition']['default'] = ''

        self.parHandle.frameWork['settings']['lastExerciseSetting'] = self.parHandle.curExercise['settings']['settingsName']

        self.parHandle.dPrint(self.exerciseName + ': Leaving setDefaultSettings()', 2)


    def loadSettings(self, settings):
        """!
        Loading settings ....
        The settings are searched for in as .set files in the presets path of
        the current exercise.
        """
        self.parHandle.dPrint(self.exerciseName + ': loadSettings()', 2)
        
        try:
            self.eraseExerciseGui()
            #self.setDefaultSettings() will be called in the central loading function
            self.parHandle.loadSettings(settings, module='curExercise')
        except:
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'

            msg = settingsName + _translate("confusionMatrix",
                                            ': Could not load settings.  Loading default settings instead', None)
            title = _translate("confusionMatrix", "This should not have happened.", None)
            QtWidgets.QMessageBox.critical(None, title, msg)

            self.parHandle.dPrint(msg, 0)
            self.setDefaultSettings()

        # the assumption is, that a the setting has been changed by loading the new setting and if the new signals can be
        # generated the signals will be initialized
        if self.parHandle.curGenerator['settings']['generatorName']:
            self.iniSignal()

        # check if a generator, preprocessor player can be initialized
        self.parHandle.iniSubmodule('generator',  self.parHandle.curExercise['settings']['generator'],
                                 self.parHandle.curExercise['settings']['generatorSettings'])
        self.parHandle.iniSubmodule('preprocessor',  self.parHandle.curExercise['settings']['preprocessor'],
                                 self.parHandle.curExercise['settings']['preprocessorSettings'])
        self.parHandle.iniSubmodule('player',  self.parHandle.curExercise['settings']['player'],
                                 self.parHandle.curExercise['settings']['playerSettings'])

        self.parHandle.dPrint(self.exerciseName + ': Leaving loadSettings()', 2)


    def checkParameters(self):
        """!
        This function can be used to check the settings/parameters during a run. The parameters will be checked against
        the settingLimits. This is required if the settings of the parameters can be changed by the user.
        The check of the limits prevents underruns/overruns.
        """

        self.parHandle.dPrint(self.exerciseName + ': checkParameters()', 2)

        self.parHandle.checkParameters()

        self.parHandle.dPrint(self.exerciseName + ': Leaving checkParameters()', 2)


    def displaySingleResult(self, data, fig = None):
        """!
        The results of the last confusionMatrix run or of a single selected 
        run are displayed in an extra window.
        """

        self.parHandle.dPrint(self.exerciseName + ': displaySingleResult()', 2)

        if self.parHandle.curExercise['settings']['externalResultsWindow']:

            meanConfMat = sum(data['results']['confMat']) / len(data['results']['confMat'])
            meanDelayTime = sum(data['results']['reactMat']) / len(data['results']['reactMat'])
            index = meanConfMat.columns.values

            if fig:
                axes =fig.axes
                if not (isinstance(axes, list)) or len(axes) < 2:
                    self.parHandle.dPrint('Length of axis does not equal 2 : Creating figure', 2)
                    fig, axes = plt.subplots(nrows=1, ncols=2)
            if not(fig):
                fig, axes = plt.subplots(nrows=1, ncols=2)
                self.parHandle.dPrint('No figure defined yet: Creating figure', 2)


            fig.subplots_adjust(hspace=0.5, left=0.07, right=0.93)
            ax = axes[0]

            cfm = ax.imshow(np.array(meanConfMat.T), cmap=plt.cm.autumn)
            ax.yaxis.set_ticks(range(len(index)))
            ax.xaxis.set_ticks(range(len(index)))
            ax.xaxis.set_ticklabels(index)
            ax.yaxis.set_ticklabels(index)
            ax.set_title(_translate("confusionMatrix",'Hits', None))
            ax.set_xlabel(_translate("confusionMatrix",'Input',None))
            ax.set_ylabel(_translate("confusionMatrix",'Presented', None))
            fig.colorbar(cfm, ax=ax, orientation='vertical', shrink=0.5, label='Hits', ticks=range(int(meanConfMat.max().max())+1))

            ax = axes[1]
            mdt = ax.imshow(np.array(meanDelayTime.T), cmap=plt.cm.autumn)
            ax.yaxis.set_ticks(range(len(index)))
            ax.xaxis.set_ticks(range(len(index)))
            ax.xaxis.set_ticklabels(index)
            ax.yaxis.set_ticklabels(index)
            ax.set_title(_translate("confusionMatrix",'Reaction time', None))
            ax.set_xlabel(_translate("confusionMatrix",'Input',None))
            ax.set_ylabel(_translate("confusionMatrix",'Presented', None))

            a = fig.colorbar(mdt, ax=ax, orientation='vertical',  shrink=0.5, label='Reaktionszeit [s]')
            #fig.tight_layout()
            plt.show()


        else:
            pass # Implement within window display?
        self.parHandle.dPrint(self.exerciseName + ': Leaving displaySingleResult()', 2)

        return fig

    def xlsxExportPreparation(self, data):
        """!
        This function prepares the result for the export to xlsx files and provides a datasSeries .
        The returned status can be 'Valid', 'NoAnswer', 'None', 'Failed', 'Warning'
        Excel Export forma

        Patient Messpunkt DatumUndUhr,          a_correct, b_correct, c_correct, ....., a_reactTime , a_reps, a_answers,  a_a   , aeh_oeh, ... , c_t, , 
        S01     01          01.03.22:05:47      1          1            0              ,            ,                        1
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': xlsxExportPreparation()', 2)

        status = 'Valid'# 'Valid', 'NoAnswer', 'None', 'Failed', 'Warning'
        #print(_translate("confusionMatrix", "Hello", None))

        phonemes = list(data['results']['confMat'][0].index)
        confMatArr = data['results']['confMat'][0].values


        reactMatArr = data['results']['reactMat'][0].values
        repetitions = data['results']['repetitions']

        item = []
        itemTitle = []

        phonemeIndex = list(data['results']['confMat'][0].index)

        # Averaging reaction time and input across runs/repetitions
        # a_correct = 1/3, # b_correct = 1, # c_correct = 2/3,
        confMatAv = np.zeros(data['results']['confMat'][0].shape)
        reactMatAv= np.zeros(data['results']['reactMat'][0].shape)
        for runIDX in range(len(data['results']['reactMat'])):
            confMatAv = confMatAv + data['results']['confMat'][runIDX].values
            reactMatAv = reactMatAv + data['results']['reactMat'][runIDX].values
        confMatAv = confMatAv / len(data['results']['reactMat'])
        reactMatAv = reactMatAv / len(data['results']['reactMat'])

        for phonPresented in phonemes: # phonIdx in range(len('repetitions'))
            print(phonPresented)
            ppIdx = list(data['results']['confMat'][0].index).index(phonPresented)

            #inputIdx= list(data['results']['confMat'][runIDX][phonPresented].values).index(1)
            #userInput = phonemeIndex[inputIdx]
            phonPascii = self.convertLabels(phonPresented, mode='phoneToASCII')

            itemTitle.append(phonPascii + '_correct')
            item.append(confMatAv[ppIdx][ppIdx])

            itemTitle.append(phonPascii + '_reactionTime')
            # saving average reaction time averaged across all phonem confusion with presented phoneme
            item.append(sum(reactMatAv[ppIdx])/sum(confMatAv[ppIdx]))

            itemTitle.append(phonPascii + '_itemCounter')
            ii = 0
            temp = ''
            for runIDX in range(len(data['results']['itemCounter'])):
                #print(runIDX)
                if ii == 0:
                    temp = str(data['results']['itemCounter'][runIDX][ppIdx])
                else:
                    temp = temp + ', ' + str(data['results']['itemCounter'][runIDX][ppIdx])
                ii = ii + 1
            item.append(temp)

            itemTitle.append(phonPascii + '_itemInput')
            ii = 0
            temp = ''
            for runIDX in range(len(data['results']['itemInput'])):
                if ii == 0:
                    temp = str(data['results']['itemInput'][runIDX][ppIdx])
                else:
                    temp = temp + ', ' + str(data['results']['itemInput'][runIDX][ppIdx])
                ii = ii + 1
                #temp = re.sub("\['", '', temp)
                #temp = re.sub("']", '', temp)
                #temp = re.sub("'", '', temp)
            item.append(temp)



            itemTitle.append(phonPascii + '_audioRepetitionCounter')
            ii = 0
            temp = ''
            for runIDX in range(len(data['results']['audioRepetitionCounter'])):
                if ii == 0:
                    temp = str(int(data['results']['audioRepetitionCounter'][runIDX][ppIdx]))
                else:
                    temp = temp + ', ' + str(int(data['results']['audioRepetitionCounter'][runIDX][ppIdx]))
                ii = ii + 1
            item.append(temp)



        for phonPresented in phonemes:  # phonIdx in range(len('repetitions'))
            phonPascii = self.convertLabels(phonPresented, mode='phoneToASCII')

            for phonInput in phonemes:
                inputIdx = list(data['results']['confMat'][0].index).index(phonInput)
                phonIascii = self.convertLabels(phonInput, mode='phoneToASCII')
                itemTitle.append(phonPascii + '_' + phonIascii)
                item.append(confMatAv[ppIdx][inputIdx]/sum(confMatAv[ppIdx]))




            # item.append(repetitions)

        dataSeries = pd.Series(item, index=itemTitle)

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving xlsxExportPreparation()', 2)
        return dataSeries, status
        #exerciseName = self.parHandle.curExercise['settings']['exerciseName']

