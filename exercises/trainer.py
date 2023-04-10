'''!
The exercise Trainer allows to play a list of audio files. This is a very simple example exercise with a simple gui.
The default audio generator loads wav- and mp3 audio files.
The default player, plays back the audio.
The player 'playQtAudio' or 'playAudio' are implemented for playback

This exercise is part of the CICoachLab framework.


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
import importlib.util
from PyQt5 import QtWidgets, QtCore, QtGui

def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class trainer():
    def __init__(self, parHandle = None, settings=''):
        """!
        The constructor of the class, sets the basic default settings, sets the sub directories, sets the calibration if
        required and possible and loads the settings if provided.
        """

        print('Initializing ')
        try:
            self.parHandle = parHandle
            # this has to be initialized first because the resetting of the handle calls the destructor of the class
            # which resets and clears up everything which has been initialized nicely
            self.parHandle.curExercise['handle'] = self

            msg = 'Entering exercise: trainer'
            parHandle.statusBar().showMessage(msg)

            # making the exercise function available for the frameWork.
            self.parHandle.curExercise['functions']['prepareRun'] = self.prepareRun
            self.parHandle.curExercise['functions']['cancelRun'] = self.cancelRun
            self.parHandle.curExercise['functions']['quitRun'] = self.quitRun
            self.parHandle.curExercise['functions']['displayResults'] = None
            self.parHandle.curExercise['functions']['settingsLoading'] = self.loadSettings
            self.parHandle.curExercise['functions']['settingsDefault'] = self.setDefaultSettings
            self.parHandle.curExercise['functions']['settingsGui'] = None
            self.parHandle.curExercise['functions']['checkConditions'] = None
            self.parHandle.curExercise['functions']['destructor'] = self.__exit__
            self.parHandle.curExercise['functions']['eraseExerciseGui']  = self.eraseExerciseGui
            self.parHandle.curExercise['settings']['exerciseName'] = 'trainer'

            self.parHandle.dPrint(msg, 2)

            # loading settings or getting default settings
            if settings != 'default' and settings != '':
                # the loaded settings just may overwrite parts of the defaultSettings....
                self.loadSettings(settings)
            else:
                self.setDefaultSettings()

            # intialize player and generator if necessary
            if self.parHandle.curPlayer['settings']['playerName'] == '':
                self.parHandle.iniSubmodule('player',  'playQtAudio')
            if self.parHandle.curGenerator['settings']['generatorName'] == '':
                self.parHandle.iniSubmodule('generator',  'genWavreader')

            # initialize other variable required by the exercise
            self.presentationCounter = 0

            # initializing default calibration for time and level issues in self.parHandl.curExercise
            self.parHandle.setDefaultCalibration('curExercise', 'time')
            #self.parHandle.setDefaultCalibration('curExercise', 'level')
            # get reaction time delay from iniFile configuration
            self.parHandle.curExercise['settings']['exerciseName'] = 'trainer'
            self.parHandle.readIniFile(mode='curExerciseSettings', module='curExercise')

            self.vBLayout   = None
            self.gridLauyout= None
            self.vHLayout   = None

            # fields where controlbars of player playQtAudio are stored
            self.controlbars = dict()
            self.controlbarRefs = dict()

            self.iniAudio()

            self.itemList = list()


        except:
            self.parHandle.dPrint('Exception: Entering class failed: trainer', 1)


    def __exit__(self):
        """!
        The destructor of the class will delete the gui of the exercise with
        the function eraseExerciseGui(). The path of the exercise will be unset
        by closePath()
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': __exit__()', 2)

        self.closePath()

        self.parHandle.curExercise['settings']['exerciseName'] = ''
        self.parHandle.curExercise['functions']['destructor'] = None

        self.eraseExerciseGui()

        self.parHandle.initializeToDefaults(mode='curExercise')

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit __exit__()', 2)


    def iniAudio(self):
        """!
        This function reads the audio files and buffers the audio signal in self.audioContainer.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': iniAudio()', 2)
        self.audioContainer = dict()

        audioListLen = len(self.parHandle.curExercise['settings']['list'])
        ii = 0
        for item in self.parHandle.curExercise['settings']['list']:


            msg = f"Laden von Audiodaten: {ii/audioListLen*100:5.1f} % "
            self.parHandle.showInformation(msg)
            filename = item['wavfile']
            filenameAbs = os.path.join(self.parHandle.curExercise['path']['wavfiles'], filename)

            audio = self.parHandle.curGenerator['functions']['run'](filenameAbs)
            itemLabel = f"item{ii:02d}"
            self.audioContainer[itemLabel] = audio
            ii = ii + 1

        self.parHandle.showInformation('')

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit iniAudio()', 2)


    def iniGui(self):
        """!
        The gui elements of the exercise will be initialized.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': iniGui()', 2)

        self.vBLayout = QtWidgets.QVBoxLayout()
        self.gridLauyout = QtWidgets.QGridLayout()
        self.vHLayout = QtWidgets.QHBoxLayout()
        self.vBLayout.addLayout(self.gridLauyout)
        self.vBLayout.addLayout(self.vHLayout)
        subWidget = self.parHandle.ui.exerWidget
        subWidget.setLayout(self.vBLayout)

        self.ui = dict()

        ii = 0
        rowCounter = 0
        for item in self.parHandle.curExercise['settings']['list']:
            lineCounter = 0


            itemLabel = f"item{ii:02d}"

            if self.parHandle.curPlayer['settings']['playerName'] == 'playQtAudio':

                controlbar, controlbarRefs = self.parHandle.curPlayer['functions']['addControlbar'](
                                                                        controlbarName=itemLabel, layoutMode='inline')

                # reconnect play button
                controlbarRefs['playBtn'].clicked.disconnect()
                controlbarRefs['playBtn'].clicked.connect(self.playAudio)

                self.controlbars[itemLabel] = controlbar
                self.controlbarRefs[itemLabel] = controlbarRefs

                # duration of signal in milliseconds for handling of player position in playQtAudio.
                duration = len(self.audioContainer[itemLabel]['audio'])/self.audioContainer[itemLabel]['fs']*1000
                self.parHandle.curPlayer['functions']['durationChanged'](duration)
                # settting duration in label and range of controlbar slider
                self.parHandle.curPlayer['functions']['setControlbarLabel'](itemLabel)

                self.gridLauyout.addLayout(controlbar, rowCounter, lineCounter)
                self.itemList.append(itemLabel)
                self.ui[itemLabel] = controlbar

                self.parHandle.curExercise['gui']['exerWidgets'].append(controlbar)
            elif self.parHandle.curPlayer['settings']['playerName'] == 'playAudio':
                objectName = f"pbPlay_{ii:02d}"
                pButton = QtWidgets.QPushButton(subWidget, text='', objectName=objectName)
                pButton.clicked.connect(self.playAudio)

                file = os.path.join(self.parHandle.curExercise['path']['recources'], 'play.png')
                pButton.setIcon(QtGui.QIcon(file))
                pButton.setIconSize(QtCore.QSize(32, 32))
                # pButton.setGeometry(QtCore.QRect(32, 32, 32, 32))
                pButton.setMaximumSize(32, 32)
                pButton.setMinimumSize(32, 32)
                pButton.setStyleSheet("background-image: url('image.jpg'); border: none;")
                pButton.show()
                self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
                self.ui[objectName] = pButton
                self.gridLauyout.addWidget(pButton, rowCounter, lineCounter, 1, 1)
                lineCounter = lineCounter + 1

                if 'pause' in list(self.parHandle.curPlayer['functions']):
                    objectName = f"pbPause_{ii:02d}"
                    pButton = QtWidgets.QPushButton(subWidget, text='', objectName=objectName)
                    pButton.clicked.connect(self.pauseAudio)

                    file = os.path.join(self.parHandle.curExercise['path']['recources'], 'pause.png')
                    pButton.setIcon(QtGui.QIcon(file))
                    pButton.setIconSize(QtCore.QSize(32, 32))
                    # pButton.setGeometry(QtCore.QRect(32, 32, 32, 32))
                    pButton.setMaximumSize(32, 32)
                    pButton.setMinimumSize(32, 32)
                    pButton.setStyleSheet("border: none;")
                    pButton.setDisabled(True)
                    self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
                    self.ui[objectName] = pButton
                    self.gridLauyout.addWidget(pButton, rowCounter, lineCounter, 1, 1)
                    lineCounter = lineCounter + 1

                if 'stopp' in list(self.parHandle.curPlayer['functions']):
                    objectName = f"pbStop_{ii:02d}"
                    pButton = QtWidgets.QPushButton(subWidget, text='', objectName=objectName)
                    pButton.clicked.connect(self.stoppAudio)
                    file = os.path.join(self.parHandle.curExercise['path']['recources'], 'stop.png')
                    pButton.setIcon(QtGui.QIcon(file))
                    pButton.setIconSize(QtCore.QSize(32, 32))
                    # pButton.setGeometry(QtCore.QRect(32, 32, 32, 32))
                    pButton.setMaximumSize(32, 32)
                    pButton.setMinimumSize(32, 32)
                    pButton.setStyleSheet("border: none;")
                    pButton.setDisabled(True)
                    self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
                    self.ui[objectName] = pButton
                    self.gridLauyout.addWidget(pButton, rowCounter, lineCounter, 1, 1)
                    lineCounter = lineCounter + 1

                objectName = f"txSpacer0_{ii:02d}"
                label = QtWidgets.QLabel(subWidget, text='', objectName=objectName)
                self.parHandle.curExercise['gui']['exerWidgets'].append(label)
                self.ui[objectName] = label
                # label.show()
                self.gridLauyout.addWidget(label, rowCounter, lineCounter, 1, 1)
            else:
                raise RuntimeError("players name '{}' did not match playQtAudio or playAudio!".format(
                    self.parHandle.curPlayer['settings']['playerName']))

            lineCounter = lineCounter + 1


            if 'solution' in list(item):
                objectName = f"pbShowSolution_{ii:02d}"
                pButton = QtWidgets.QPushButton(subWidget, text=_translate("Trainer",'Show solution',None),
                                                objectName=objectName)
                pButton.clicked.connect(self.showSolution)

                self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
                self.ui[objectName] = pButton
                self.gridLauyout.addWidget(pButton, rowCounter, lineCounter, 1, 1)
                self.parHandle.setRetainSizeWhenHidden(pButton)
                lineCounter = lineCounter + 1


                objectName = f"txSpacer1_{ii:02d}"
                label = QtWidgets.QLabel(subWidget, text='', objectName=objectName)
                self.parHandle.curExercise['gui']['exerWidgets'].append(label)
                self.ui[objectName] = label
                self.gridLauyout.addWidget(label, rowCounter, lineCounter, 1, 1)
                self.parHandle.setRetainSizeWhenHidden(label)
                lineCounter = lineCounter + 1

                objectName = f"txSolution_{ii:02d}"
                label = QtWidgets.QLabel(subWidget, text='  ', objectName=objectName)
                self.parHandle.curExercise['gui']['exerWidgets'].append(label)
                self.ui[objectName] = label
                self.parHandle.setRetainSizeWhenHidden(label)
                lineCounter = lineCounter + 1

                self.gridLauyout.addWidget(label, rowCounter, lineCounter, 1, 4)

            rowCounter = rowCounter + 2
            ii = ii + 1

        objectName = 'pbFinish'
        pButton = QtWidgets.QPushButton(subWidget, text=_translate("Trainer", 'End', None), objectName=objectName)
        pButton.clicked.connect(self.finishRun)
        pButton.setMaximumSize(100, 50)
        pButton.setMinimumSize(100, 50)
        self.vHLayout.addWidget(pButton)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pButton)
        self.ui[objectName] = pButton

        self.parHandle.show()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit iniGui()', 2)


    def playAudio(self):
        """!
        Play the audio!
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': playAudio()', 2)


        if self.parHandle.curPlayer['settings']['playerName'] == 'playQtAudio':
            label = self.parHandle.curPlayer['functions']['getControlbarCaller'](self.parHandle.sender())
            itemNo = self.itemList.index(label)
            print(itemNo)
            self.parHandle.curPlayer['functions']['setControlbarLabel'](label)
            #print('')
        elif self.parHandle.curPlayer['settings']['playerName'] == 'playAudio':
            objectName = self.parHandle.sender().objectName()
            label = 'item'+objectName.split('_')[1]
            '''
            objectName = f"pbStop_{itemNo:02d}"
            if objectName in list(self.ui):
                self.ui[objectName].setDisabled(False)
            objectName = f"pbPause_{itemNo:02d}"
            if objectName in list(self.ui):
                self.ui[objectName].setDisabled(False)
            '''
        self.parHandle.curPlayer['functions']['run'](self.audioContainer[label])



        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit playAudio()', 2)


    def stoppAudio(self):
        """!
        Stopp the audio if possible!
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': stopAudio()', 2)
        self.parHandle.curPlayer['functions']['stopp']()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit stopAudio()', 2)


    def pauseAudio(self):
        """!
        Pause the audio if possible!
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': pauseAudio()', 2)
        self.parHandle.curPlayer['functions']['pause']()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit pauseAudio()', 2)


    def showSolution(self):
        """!
        Show the solution if the solution button is pressed.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': showSolution()', 2)
        objectName = self.parHandle.sender().objectName()
        # objectName is constructed as follows:

        obj, itemNoStr = objectName.split('_')
        itemNo = int(itemNoStr)
        item = self.parHandle.curExercise['settings']['list'][itemNo]
        item['solution']

        objectName = f"txSolution_{itemNo:02d}"
        self.ui[objectName].setText(item['solution'])

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit showSolution()', 2)


    def prepareRun(self):
        """!
        Prepare the run. Initialize the gui and enable buttons
        """

        if len(self.parHandle.curExercise['gui']['exerWidgets']) == 0:
            self.iniGui()
        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(False)
            except:
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)
        #self.startRun()


    def startRun(self):
        """!
        Just calling self.run()
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': startRun()', 2)

        self.run()

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving startRun()', 2)


    def runButton(self, temp, forcedInput=''):
        """!
        Calling run and measuring the reaction time.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit runButton()', 2)

        self.parHandle.measureReactionTime(self.parHandle, mode='stop')

        self.run()

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit runButton', 2)


    def run(self):
        """!

        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': run()', 2)


        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit run()', 2)


    def cancelRun(self):
        """
        This functions will finish the run. The subject is asked for
            confirmation before calling the function quitRun().
        """
        msg = _translate("Trainer", 'Would you like to cancel the run?', None)
        if self.presentationCounter > 0:
            msg = msg + '.\n.'

        response = QtWidgets.QMessageBox.question(self.parHandle.ui.exerWidget,
                                                  _translate("Trainer",'CICoachLab Information', None), msg)
        if response == QtWidgets.QMessageBox.Yes:
            self.quitRun()


    def quitRun(self):
        """!
        Just ending the run.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': quitRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit quitRun()', 2)


    def finishRun(self):
        """
        This function ends and hides the trainer part. In contrast to self.quitRun() the run will be marked as
        accomplished because CICoachLab assumes that runs ended by. self.quitRun() mark unaccomplished runs.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': finishRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit finishRun()', 2)


    def eraseExerciseGui(self):
        """!
        Erasing gui.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': eraseExerciseGui()', 2)

        print('This function might clean up the exercise gui to allocate free space for the next exercise')
        try:
            if self.vBLayout != None:
                for layOutItem in self.vBLayout.children():
                    for i in reversed(range(layOutItem.count())):
                        # This check is required since this exercise adds sublayouts to self.vBLayout
                        if layOutItem.itemAt(i).widget():
                            layOutItem.itemAt(i).widget().setParent(None)
                # the layout which is assigned to the exercise container widget cannot be deleted it just can be moved to
                # another temporary widget
                QtWidgets.QWidget().setLayout(self.parHandle.ui.exerWidget.layout())

            self.parHandle.curExercise['gui']['exerWidgets'] = list()
        except:
            self.parHandle.dPrint('Could not tidy up gui.', 2)
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit eraseExerciseGui()', 2)


    def iniPath(self):
        """!
        The dictionary self.parHandle.curExercise['path'] will be filled
        with the 'base', 'preset', 'results' and the confusionmatrix specific
        'signalFiles' path.
        The path entries of the dictionary will be added at the top of the path
        by sys.path in the frameWork.
        """

        self.parHandle.dPrint( self.parHandle.curExercise['settings']['exerciseName'] + ': iniPath()', 2)

        pwd = os.path.join(self.parHandle.frameWork['path']['exercises'], 'trainer')
        self.parHandle.curExercise['path']['base']      = pwd
        self.parHandle.curExercise['path']['presets']   = os.path.join(pwd, 'presets')
        self.parHandle.curExercise['path']['results']   = os.path.join(pwd, 'results')
        self.parHandle.curExercise['path']['analysis']  = os.path.join(pwd, 'analysis')
        self.parHandle.curExercise['path']['wavfiles']  = os.path.join(pwd, 'wavfiles')
        self.parHandle.curExercise['path']['recources'] = os.path.join(pwd, 'recources')
        self.parHandle.addingPath('curExercise')

        self.parHandle.dPrint( self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving iniPath()', 2)


    def closePath(self):
        """!
        The path of the exercise will be removed from sys.path by the frameWork.
        Reset the path dictionary in self.parHandle.curExercise by
        setting entries to empty strings.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': closePath()', 2)

        self.parHandle.closePath('curExercise')
        self.parHandle.curExercise['path']['base']      = ''
        self.parHandle.curExercise['path']['presets']   = ''
        self.parHandle.curExercise['path']['results']   = ''
        self.parHandle.curExercise['path']['analysis']  = ''

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': closePath()', 2)


    def loadSettings(self, settings='default'):
        """
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current exercise.
        """
        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': loadSettings()', 2)

        try:
            self.eraseExerciseGui()
            #self.setDefaultSettings() will be called in the central loading function
            self.parHandle.loadSettings(settings, module='curExercise')


        except:
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'

            self.parHandle.dPrint('Could not load settings ('+settingsName+') loading default settings instead', 1)
            self.setDefaultSettings()

        self.parHandle.iniSubmodule('player',  self.parHandle.curExercise['settings']['player'], \
                                 self.parHandle.curExercise['settings']['playerSettings'])
        self.parHandle.iniSubmodule('generator',  self.parHandle.curExercise['settings']['generator'], \
                                    self.parHandle.curExercise['settings']['generatorSettings'])
        self.parHandle.iniSubmodule('preprocessor',  self.parHandle.curExercise['settings']['preprocessor'], \
                                       self.parHandle.curExercise['settings']['preprocessorSettings'])

        # the assumption is, that a the setting has been changed by loading the new setting
        self.iniAudio()


        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Leaving loadSettings()', 2)


    def setDefaultSettings(self):
        """!
        The default parameters and settingLimits of the tests will be set.
        Mandatory/default fields are assigned by CICoachLab.py in
        initializeToDefaults() for each exercise, as well als generator, preprocessor and player,
        The default fields are set and extended by the
        repective items provided in this function.
        The settings can be set for single or all fields.
        """

        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': setDefaultSettings()', 2)

        exerciseName = 'trainer'
        exerciseBaseName = os.path.join(self.parHandle.frameWork['path']['exercises'], exerciseName)

        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        # setting paths to exercise subfolder like "analysis"  "presets"  "results" (and other folders if the
        # exercise requires data like sound files or other
        self.iniPath()

        self.parHandle.curExercise['settings']['exerciseName'] = exerciseName

        self.parHandle.curExercise['settings']['settingsName'] = 'default'

        self.parHandle.curExercise['settings']['player']             = 'playQtAudio'
        self.parHandle.curExercise['settings']['playerSettings']     = 'default'
        self.parHandle.curExercise['settings']['preprocessor']          = ''
        self.parHandle.curExercise['settings']['preprocessorSettings']  = 'default'
        self.parHandle.curExercise['settings']['generator']          = 'genWavreader'
        self.parHandle.curExercise['settings']['generatorSettings']  = 'default'

        self.parHandle.curExercise['settings']['list']              = []
        self.parHandle.curExercise['settings']['audioPath']         = os.path.join(exerciseBaseName, 'wavfiles')

        item = dict()
        item['wavfile'] = 'cicoachlab_noise.mp3'
        item['solution']= 'CICoachLab noise vocoded version.'
        self.parHandle.curExercise['settings']['list'].append(item)

        item = dict()
        item['wavfile'] = 'cicoachlab_sinus.mp3'
        item['solution']= 'CICoachLab sinusoid vocoded version.'
        self.parHandle.curExercise['settings']['list'].append(item)

        item = dict()
        item['wavfile'] = 'cicoachlab.wav'
        item['solution'] = 'CICoachLab unvocoded version.'
        self.parHandle.curExercise['settings']['list'].append(item)





        self.parHandle.dPrint(self.parHandle.curExercise['settings']['exerciseName'] + ': Quit setDefaultSettings()', 2)

