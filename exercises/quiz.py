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
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import QBrush, QPalette
import re
import numpy as np
from exerciseBase import exerciseBase
import multiprocessing as mp
from CICoachLab import Worker

# TODO: check implemenation of multithreading


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

# list of text as alternative to text to allow multiple tips
# adapt setDefaultLimits if required.
# add tippCounter to add correct item until everything was added.

class quiz(exerciseBase):
    """!
    In this exercise the user listens to a set of signals and he should choose which of the answer option is
    the correct one. In case of degraded input signals a un-degraded signal can be played back.
    """
    def __init__(self, parHandle=None, settings=''):
        """!
        The constructor of the class, sets the basic default settings, sets the sub directories, sets the calibration if
        required and possible and loads the settings if provided.
        """

        try:

            super().__init__(parHandle, settings=settings, exerciseName='quiz')

            self.exerciseName = self.parHandle.curExercise['settings']['exerciseName']
            

            #self.parHandle.curExercise['functions']['displayResults'] = self.displayResults

            self.vBLayout   = None

            #self.gridLauyout= None
            #self.vHLayout   = None
            self.ui         = dict()
            # number of item within randomized items
            self.sequenceNo = -1
            # number of previously selected item within randomized items
            self.sequenceNoPrevious = -1
            # number of question of item
            self.questNumber = -1
            self.audioSolutionFlag = False
            self.solutionTextCounter = -1
            self.itemOptions = []
            self.signalContainer = dict()
            self.signalContainer['test'] = dict()
            self.signalContainer['assistance'] = dict()

            self.enforceReplay = False
            # multithreading has not been tested yet.
            self.multiThreading = dict()
            self.multiThreading['active'] = False
            if self.multiThreading['active']:
                self.threadPool = QtCore.QThreadPool
                self.multiThreading['maxThreads'] = self.threadpool.maxThreadCount() - 1
            else:
                self.threadPool = None
                self.multiThreading['maxThreads'] = 1

            # self.parHandle.curPreprocessor['settings']['deactivate'] allows to enable and disablin of
            # preprocessor temporarily. The state at startup of quiz will be reset at closing of app.
            self.initialPreprocessorDeactivation = self.parHandle.curPreprocessor['settings']['deactivate']
        except:
            self.parHandle.dPrint('Exception: Entering exercise failed: quiz', 1)


    def __exit__(self):
        """!
        The destructor of the class will delete the gui of the exercise with
        the function eraseExerciseGui(). The path of the exercise will be unset
        by closePath()
        """

        self.parHandle.curPreprocessor['settings']['deactivate'] = self.initialPreprocessorDeactivation
        super().__exit__()



    def iniGui(self):
        """!
        The gui elements of the exercise will be initialized at the startup of the exercise.
        The gui elements are initialized according to the loaded settings.
        A end button is always generated.
        """

        self.parHandle.dPrint(self.exerciseName + ': iniGui()', 2)

        exerciseWidget = self.parHandle.ui.exerWidget

        self.vBLayout = QtWidgets.QVBoxLayout()
        #self.gridLauyout = QtWidgets.QGridLayout()

        self.ui = dict()

        objectName = 'lbQuest'
        qLabelQuest = QtWidgets.QLabel(exerciseWidget, text=_translate("quiz","Question", None), objectName=objectName)
        qLabelQuest.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        self.vBLayout.addWidget(qLabelQuest, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(qLabelQuest)
        self.ui[objectName] = qLabelQuest

        spacerWidth = 20
        spacerHeight = 40

        spacerItem = QtWidgets.QSpacerItem(spacerWidth, spacerHeight, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)



        objectName = 'teSolutionText'
        teSolution = QtWidgets.QTextEdit(exerciseWidget, objectName=objectName)
        self.document = QtGui.QTextDocument()
        self.document.setDocumentMargin(20)
        teSolution.setDocument(self.document)
        teSolution.setText(_translate("quiz", "Some Text which provides the detailed solution.", None))
        teSolution.setReadOnly(True)
        teSolution.setAlignment(QtCore.Qt.AlignHCenter)
        teSolution.append('Center alignment')
        teSolution.setAlignment(QtCore.Qt.AlignRight)

        teSolution.append('Right alignment')
        teSolution.setAlignment(QtCore.Qt.AlignLeft)
        teSolution.append('Left alignment')
        teSolution.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.vBLayout.addWidget(teSolution)
        # teSolution.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        self.parHandle.curExercise['gui']['exerWidgets'].append(teSolution)
        self.ui[objectName] = teSolution

        spacerItem = QtWidgets.QSpacerItem(spacerWidth, spacerHeight/8, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)

        objectName = 'lbSolutionText'
        qLabelSolutionText = QtWidgets.QLabel(exerciseWidget,
                                              text=_translate("quiz","Do you want to get some hints?!", None),
                                              objectName=objectName)
        qLabelSolutionText.setFont(QtGui.QFont("", 16, QtGui.QFont.Bold))
        self.vBLayout.addWidget(qLabelSolutionText, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(qLabelSolutionText)
        self.ui[objectName] = qLabelSolutionText
        self.parHandle.setRetainSizeWhenHidden(qLabelSolutionText)

        self.hSolutionLayout = QtWidgets.QHBoxLayout()
        objectName = 'pbSolutionAudio'
        pbSolutionAudio = QtWidgets.QPushButton(exerciseWidget, text='', objectName=objectName)
        #pbSolutionAudio.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        self.parHandle.setRetainSizeWhenHidden(pbSolutionAudio)

        self.hSolutionLayout.addWidget(pbSolutionAudio, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pbSolutionAudio)
        self.ui[objectName] = pbSolutionAudio

        pbSolutionAudio.setText(_translate("quiz", "Play audio hint", None))

        objectName = 'pbSolutionText'
        pbSolutionText = QtWidgets.QToolButton(exerciseWidget, text='', objectName=objectName)
        self.parHandle.setRetainSizeWhenHidden(pbSolutionAudio)
        #pbSolutionText.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        self.hSolutionLayout.addWidget(pbSolutionText, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pbSolutionText)
        self.ui[objectName] = pbSolutionText

        pbSolutionText.setText(_translate("quiz", "Show hints", None))
        self.vBLayout.addLayout(self.hSolutionLayout)

        spacerItem = QtWidgets.QSpacerItem(spacerWidth, spacerHeight, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)

        self.hOptionLayout = QtWidgets.QHBoxLayout()
        self.vBLayout.addLayout(self.hOptionLayout)

        options = [_translate("quiz",'one', None), _translate("quiz",'two', None), _translate("quiz",'three', None)]
        # randomizing order of presentated options if required
        if self.parHandle.curExercise['settings']['randomizedOptions']:
            np.random.shuffle(options)
        self.setOptions(options=options)

        spacerItem = QtWidgets.QSpacerItem(spacerWidth,spacerHeight, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)

        objectName = "loControlbar"
        controlbar, controlbarRefs = self.parHandle.curPlayer['functions']['addControlbar'](
            controlbarName=objectName, layoutMode='stacked')
        self.controlbars = dict()
        self.controlbars[objectName] = controlbar
        # redirect connected playHandler function to exercise function self.presentSignal, to be able to choose
        # between test sound and solution sound.
        self.controlbarRefs = dict()
        self.controlbarRefs[objectName] = controlbarRefs
        self.parHandle.reconnect(self.controlbarRefs[objectName]['playBtn'].clicked, self.presentSignal)
        #self.controlbarRefs[objectName]['playBtn'].clicked.connect(self.presentSignal)
        self.vBLayout.addLayout(controlbar)#, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(controlbar)
        self.ui[objectName] = controlbar

        spacerItem = QtWidgets.QSpacerItem(spacerWidth, spacerHeight*2, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)

        self.hItemLayout = QtWidgets.QHBoxLayout()
        objectName = 'pbPrevious'
        pbPrevious = QtWidgets.QPushButton(exerciseWidget, text=_translate("quiz", "Previous item", None), objectName=objectName)
        pbPrevious.setCheckable(True)
        #pbPrevious.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        pbPrevious.clicked.connect(self.previousItem)
        self.hItemLayout.addWidget(pbPrevious, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pbPrevious)
        self.ui[objectName] = pbPrevious
        self.vBLayout.addLayout(self.hItemLayout)

        objectName = 'pbNext'
        pbNext = QtWidgets.QPushButton(exerciseWidget, text=_translate("quiz", "Next item", None), objectName=objectName)
        pbNext.setCheckable(True)
        #pbNext.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
        pbNext.clicked.connect(self.nextItem)
        self.hItemLayout.addWidget(pbNext, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pbNext)
        self.ui[objectName] = pbNext

        spacerItem = QtWidgets.QSpacerItem(spacerWidth, spacerHeight/2, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.vBLayout.addItem(spacerItem)

        objectName = 'pbFinish'
        pbFinish = QtWidgets.QPushButton(exerciseWidget, text=_translate("quiz", 'Quit run', None), objectName=objectName)
        pbFinish.clicked.connect(self.quitRun)
        pbFinish.setMaximumSize(100, 50)
        pbFinish.setMinimumSize(100, 50)
        self.vBLayout.addWidget(pbFinish, alignment=QtCore.Qt.AlignRight)
        self.parHandle.curExercise['gui']['exerWidgets'].append(pbFinish)
        self.ui[objectName] = pbFinish

        exerciseWidget.setLayout(self.vBLayout)

        self.parHandle.show()
        self.parHandle.dPrint(self.exerciseName + ': Leaving iniGui()', 2)


    def centerText(self):
        """!
        Function which in future function might handle the centering a single line text in the texteditor window.
        """

        self.document.setDocumentMargin(int((self.document.size().height() - self.ui['teSolutionText'].height()) / 4))
        docHeight = self.document.size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.ui['teSolutionText'].setMinimumHeight(docHeight)


    def iniAudio(self):
        """!
        The audio signals are loaded before the start of the run. If required the preprocessing of the signals is run
        beforehand to buffer the preprocessed signal to save time during the run.
        """

        self.parHandle.dPrint(self.exerciseName + ': iniAudio()', 2)

        msg = _translate("quiz", "Initializing signal: ", None)

        # adding some comments where the multiprocessing might be enabled in future versions.
        # pool = mp.Pool(processes=mp.cpu_count() - 1)
        # looping through setting to load signals of data and signal solution if necessary
        for itemNo in range(len(self.parHandle.curExercise['settings']['list'])):

            signalfileName = self.parHandle.curExercise['settings']['list'][itemNo]['soundfile']
            assistanceFilename = self.parHandle.curExercise['settings']['list'][itemNo]['assistance']['audio'][
                'signalfile']
            self.parHandle.showInformation(msg + signalfileName)

            #pool.apply_async(generateAndPreprocess, args=(self, signalfileName, assistanceFilename,))
            if self.multiThreading['active']:
                print('multithreading')

                worker = Worker(self.generateAndPreprocess, [signalfileName, assistanceFilename])  # Any other args, kwargs are passed to the run function
                #worker.signals.result.connect(self.print_output)
                #worker.signals.finished.connect(self.thread_complete)
                #worker.signals.vocFilenameprogress.connect(self.progress_fn)

                # Execute
                self.threadpool.start(worker)
            else:
                self.generateAndPreprocess(signalfileName, assistanceFilename)
        #pool.close()
        #pool.join()

        self.parHandle.dPrint(self.exerciseName + ': Leaving iniAudio()', 2)


    # to be able to call subprocesses generateAndPreprocess() might have to be defined at module level
    def generateAndPreprocess(self, signalfileName, assistanceFilename):
        """!
        This function collects the potentially heavy-duty-processing of signal generation and signal preprocessing
        to enable multiprocessing application of this processing.
        """

        signalfile = os.path.join(self.parHandle.curExercise['path']['data'],
                                  signalfileName)
        signal = self.parHandle.curGenerator['functions']['run'](signalfile)
        self.signalContainer['test'][signalfileName] = signal
        self.parHandle.curPlayer['functions']['applyPreprocessor'](signal)

        if assistanceFilename:
            assistancefile = os.path.join(self.parHandle.curExercise['path']['dataSolution'], assistanceFilename)
            assistanceSignal = self.parHandle.curGenerator['functions']['run'](assistancefile)
            # applying preprocessor for perbuffering of signal within player buffer
            self.parHandle.curPlayer['functions']['applyPreprocessor'](assistanceSignal)
            self.signalContainer['assistance'][assistanceFilename] = assistanceSignal
        else:
            self.signalContainer['assistance'][assistanceFilename] = None


    def presentSignal(self):
        """!
        The signal is taken from the audiocontainer if a new signal is presented. If the audioPLayer is paused
        The old signal will be restarted at the given position. Whether the solution or the test signal will be checked with
        self.audioSolutionFlag, which is set in self.toggleAudioSolution()
        """

        self.parHandle.dPrint(self.exerciseName + ': presentSignal()', 2)
        # documentation of partial or total playbacks
        self.parHandle.curRunData['results']['audioPresentationCounter'] = \
            self.parHandle.curRunData['results']['audioPresentationCounter'] + 1

        # check if paused state is found or if the slider position has been changed by the user to middle of the signal
        sliderMax = self.controlbarRefs['loControlbar']['seekSlider'].maximum()
        sliderMin = self.controlbarRefs['loControlbar']['seekSlider'].minimum()
        sliderPosition = self.controlbarRefs['loControlbar']['seekSlider'].sliderPosition()
        if self.enforceReplay or ( self.parHandle.curPlayer['handle'].userAction != 2
                and (sliderPosition == sliderMax or sliderPosition == sliderMin)):
            # if the audio player is not paused the required signal will be loaded
            signalfileName = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['soundfile']
            if self.audioSolutionFlag:
                if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['audio']['signalfile']:
                    signal = self.signalContainer['assistance'][self.itemOrder[self.sequenceNo]]
                else:
                    signal = self.signalContainer['test'][signalfileName]
                if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['audio']['preprocessing']:
                    self.parHandle.curPreprocessor['settings']['deactivate'] = False
                else:
                    self.parHandle.curPreprocessor['settings']['deactivate'] = True
                # documention of usage of audio assistance
                self.parHandle.curRunData['results']['assistance']['audio'] = True
            else:
                signal = self.signalContainer['test'][signalfileName]
                # set to the initial condition of the preprocessor
                self.parHandle.curPreprocessor['settings']['deactivate'] = self.initialPreprocessorDeactivation
            self.parHandle.curPlayer['functions']['run'](signal, enforceReloadedData=True)
            self.enforceReplay = False
        else:
            # unpausing/restarting the player
            self.parHandle.curPlayer['functions']['playHandler']()
            
        self.parHandle.dPrint(self.exerciseName + ': Leaving presentSignal()', 2)


    def setOptions(self, options):
        """!
        The buttons for the answer-options are generated according to the settings.

        """

        self.parHandle.dPrint(self.exerciseName + ': setOptions()', 2)

        exerciseWidget = self.parHandle.ui.exerWidget
        for option in options:
            objectName = 'pb'+ option
            qPbOption = QtWidgets.QToolButton(exerciseWidget, text=option, objectName=objectName, )
            #qPbOption.setFont(QtGui.QFont("", 24, QtGui.QFont.Bold))
            qPbOption.setCheckable(False)
            qPbOption.clicked.connect(self.run)

            self.hOptionLayout.addWidget(qPbOption, alignment=QtCore.Qt.AlignHCenter)  # , 0, 0, 1, 1)
            self.parHandle.curExercise['gui']['exerWidgets'].append(qPbOption)
            self.ui[objectName] = qPbOption
            self.itemOptions.append(qPbOption)

        self.parHandle.dPrint(self.exerciseName + ': Leaving setOptions()', 2)


    def displayResults(self, data):
        """!
        The results of the selected run will be displayed by this function.To be finalized in future versions.
        """

        self.parHandle.dPrint(self.exerciseName + ': displayResults()', 2)

        self.loadSettings(data['settings']['exercise']['settingsName'])
        self.iniGui()
        if data['results']['itemNo'] == -1:
            msg = _translate("quiz", 'No valid data could be found. This run has been canceled, probably.', None)
            self.parHandle.dPrint(msg, 1, guiMode=True)
            return

        if data['results']['itemNo'] >= 0:
            item = f"pbAnswer{data['results']['index']:02d}"
        else:
            item = "pbNoAnswer"
        self.ui[item].setChecked(True)
        self.ui[item].setStyleSheet(f"font: bold; font-size: {int(self.ui[item].font().pointSizeF()*2):d}px") # font-size: 36px

        print('label:' + data['results']['label'] + '  index: ' + str(data['results']['itemNo']))

        self.parHandle.dPrint(self.exerciseName + ': Leaving displayResults()', 2)


    def iniItem(self):
        """!
        Change item gui according to presented item.
        If a different signal file is defined for listening to the solution the signal has to be loaded to the player.
        """

        self.solutionTextCounter = -1
        self.parHandle.dPrint(self.exerciseName + ': iniItem()', 2)
        # check if there is only one hint common to all questions of this item with self.sequenceNo or if the
        curItem = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]
        if self.sequenceNoPrevious != self.sequenceNo or \
                not(isinstance(curItem['assistance']['text']['text'], str)) or \
                not(isinstance(curItem['assistance']['text']['text'][self.questNumber], str)):
            self.ui['teSolutionText'].setText('')

        ah = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['audio']['enable']
        th = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['text']['enable']
        if ah or th:
            self.ui['lbSolutionText'].show()
        else:
            self.ui['lbSolutionText'].hide()

        if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['audio']['enable']:
            #self.ui['pbSolutionAudio'].clicked.connect(self.toggleAudioSolution)
            self.parHandle.reconnect(self.ui['pbSolutionAudio'].clicked, self.toggleAudioSolution)
            self.ui['pbSolutionAudio'].setDisabled(False)
            self.ui['pbSolutionAudio'].setCheckable(True)
            self.ui['pbSolutionAudio'].show()
            #self.ui['pbSolutionAudio'].setPalette(QPalette())
        else:
            # self.ui['pbSolutionAudio'].clicked.disconnect()
            self.parHandle.reconnect(self.ui['pbSolutionAudio'].clicked)
            self.ui['pbSolutionAudio'].setDisabled(True)
            self.ui['pbSolutionAudio'].setCheckable(False)
            self.ui['pbSolutionAudio'].hide()
            #tb = QBrush(QtCore.Qt.transparent)
            #self.ui['pbSolutionAudio'].setPalette(QPalette(tb, tb, tb, tb, tb, tb, tb, tb, tb))


        if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['text']['enable']:
            #self.ui['pbSolutionText'].clicked.connect(self.showTextSolution)
            self.parHandle.reconnect(self.ui['pbSolutionText'].clicked, self.showTextSolution)
            self.ui['pbSolutionText'].setDisabled(False)
            self.ui['pbSolutionText'].setCheckable(True)
            self.ui['pbSolutionText'].show()
            #self.ui['pbSolutionText'].setPalette(QPalette())
        else:
            #self.ui['pbSolutionText'].clicked.disconnect()
            self.parHandle.reconnect(self.ui['pbSolutionText'].clicked)
            self.ui['pbSolutionText'].setDisabled(True)
            self.ui['pbSolutionText'].setCheckable(False)
            self.ui['pbSolutionText'].hide()
            #tb = QBrush(QtCore.Qt.transparent)
            #self.ui['pbSolutionText'].setPalette(QPalette(tb, tb, tb, tb, tb, tb, tb, tb, tb))

        self.ui['pbSolutionAudio'].setChecked(False)

        quest = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['quests'][self.questNumber]
        self.ui['lbQuest'].setText(quest)

        # deleting old option, because the number of options has changed
        if not(len(self.itemOptions) ==
               len(self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['options'][self.questNumber])):
            for ii in reversed(range(self.hOptionLayout.count())):
                widgetToRemove = self.hOptionLayout.itemAt(ii).widget()
                # remove it from the layout list
                self.hOptionLayout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            self.itemOptions = []
            options = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['options'][self.questNumber]
            # randomizing order of presentated options if required
            if self.parHandle.curExercise['settings']['randomizedOptions']:
                np.random.shuffle(options)
            self.setOptions(options)
        else:
            for ii in reversed(range(self.hOptionLayout.count())):
                widgetToReset = self.hOptionLayout.itemAt(ii).widget()
                # reset the style sheet of the answer option buttons. The background/style sheet might have been set to
                # changed if the question was answered [ correctly (green) or wrong (red)] in self.run().
                widgetToReset.setStyleSheet('')

        # setting options
        for ii in range(len(self.itemOptions)):
            optionText = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['options'][self.questNumber][ii]
            self.itemOptions[ii].setText(optionText)

        '''
        pbSolutionAudio
        if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['audio']['enable']:
            pbSolutionAudio.setDisabled(False)
            pbSolutionAudio.setCheckable(True)
            #pbSolutionAudio.setPalette(QPalette())
            pbSolutionAudio.show()
            pbSolutionAudio.clicked.connect(self.toggleAudioSolution)
        else:
            pbSolutionAudio.setDisabled(True)
            pbSolutionAudio.setCheckable(False)
            pbSolutionAudio.hide()
            #tb = QBrush(QtCore.Qt.transparent)
            #pbSolutionAudio.setPalette(QPalette(tb, tb, tb, tb, tb, tb, tb, tb, tb))
        
        pbSolutionText
        if self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['assistance']['text']['enable']:
            #pbSolutionText.setPalette(QPalette())
            pbSolutionText.clicked.connect(self.showTextSolution)
            pbSolutionText.setDisabled(False)
            pbSolutionText.setCheckable(True)
            pbSolutionText.show()
        else:
            #tb = QBrush(QtCore.Qt.transparent)
            #pbSolutionText.setPalette(QPalette(tb, tb, tb, tb, tb, tb, tb, tb, tb))
            pbSolutionText.setDisabled(True)
            pbSolutionText.setCheckable(False)
            pbSolutionText.hide()
        '''
        self.parHandle.dPrint(self.exerciseName + ': Leaving iniItem()', 2)


    def nextItem(self):
        """!
        Go to next item in self.parHandle.curExercise['settings']['list'] by counting up self.sequenceNo or
        self.questNumber and calling self.iniItem()
        """

        self.audioSolutionFlag = False

        self.parHandle.dPrint(self.exerciseName + ': nextItem()', 2)
        # documenting prious sequenceNo for resetting of text hint
        self.sequenceNoPrevious = self.sequenceNo
        # asking next question of item or continue to next item
        if self.questNumber == len(self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['quests']) - 1:
            # last question of item reached: check for more items and proceed in case of more items
            if self.sequenceNo < len(self.parHandle.curExercise['settings']['list']) - 1:
                self.sequenceNo = self.sequenceNo + 1
                self.questNumber = 0
                presentSignalFlag = True
                # if the audio was paused the old item audio was played, until the audio playback was stopped.
                # stopping play back to be sure that the correct audio is played back
                if 'functions' in self.parHandle.curPlayer and \
                        'stopHandler' in self.parHandle.curPlayer['functions']:
                    self.parHandle.curPlayer['functions']['stopHandler']()
            else:
                # end of items reached
                presentSignalFlag = False
        else:
            presentSignalFlag = False
            self.questNumber = self.questNumber + 1
        self.iniItem()
        if presentSignalFlag:
            self.presentSignal()

        self.parHandle.dPrint(self.exerciseName + ': Leaving nextItem()', 2)


    def previousItem(self):
        """!
        Go to previous item in self.parHandle.curExercise['settings']['list'] by counting up self.sequenceNo or
        self.questNumber and calling self.iniItem()
        """

        self.parHandle.dPrint(self.exerciseName + ': previousItem()', 2)
        self.audioSolutionFlag = False

        self.sequenceNoPrevious = self.sequenceNo
        if self.questNumber == 0:
            if self.sequenceNo > 0:
                presentSignalFlag = True
                self.sequenceNo = self.sequenceNo - 1
                # if the audio was paused the old item audio was played, until the audio playback was stopped.
                # stopping play back to be sure that the correct audio is played back
                if 'functions' in self.parHandle.curPlayer and \
                        'stopHandler' in self.parHandle.curPlayer['functions']:
                    self.parHandle.curPlayer['functions']['stopHandler']()
            else:
                presentSignalFlag = False
        else:
            presentSignalFlag = False
            self.questNumber = self.questNumber - 1

        self.iniItem()
        # play signal if
        if presentSignalFlag:
            self.presentSignal()

        self.parHandle.dPrint(self.exerciseName + ': Leaving previousItem()', 2)


    
    def run(self):
        """!
        This function handles the user input.
        """

        self.parHandle.dPrint(self.exerciseName + ': run()', 2)


        inputAnswer = self.parHandle.sender().text()
        objectAnswer = self.parHandle.sender().objectName()

        solution = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]['solutions'][self.questNumber]

        self.parHandle.curRunData['results']['label'] = inputAnswer
        self.parHandle.curRunData['results']['sequenceNo'] = self.sequenceNo
        self.parHandle.curRunData['results']['itemNo'] = int(self.itemOrder[self.sequenceNo])
        if inputAnswer == solution:
            self.parHandle.curRunData['results']['correct'] = True

            self.ui[objectAnswer].setStyleSheet("background-color : green")
            """
            pal = QtGui.QPalette(self.ui[objectAnswer].palette())
            #origColor = pal.getcolor()
            pal.setColor(QtGui.QPalette.Background, QtCore.Qt.green)
            self.parHandle.changePalette(self.ui[objectAnswer], pal)
            """
        else:
            self.parHandle.curRunData['results']['correct'] = False
            self.ui[objectAnswer].setStyleSheet("background-color : red")
            """
            pal = QtGui.QPalette(self.ui[objectAnswer].palette())
            pal.setColor(QtGui.QPalette.Background, QtGui.QColor(QtCore.Qt.red))
            self.parHandle.changePalette(self.ui[objectAnswer], pal)
            """
        self.parHandle.dPrint(self.exerciseName + ': Leaving run()', 2)


    
    def toggleAudioSolution(self):
        """!
        Toggling self.audioSolutionFlag if the audio solution button is pressed. In self.presentSignal the presented
        signal is set accoring to self.audioSolutionFlag.
        """

        self.parHandle.dPrint(self.exerciseName + ': toggleAudioSolution()', 2)
        if self.audioSolutionFlag:
            self.audioSolutionFlag = False
        else:
            self.audioSolutionFlag = True
        # if the audio signal is changed the audio signal will be reloaded
        self.enforceReplay = True
        
        self.parHandle.dPrint(self.exerciseName + ': Leaving toggleAudioSolution()', 2)
        
    def showTextSolution(self):
        """!
        set text accordoing to settings item.
        """

        self.parHandle.dPrint(self.exerciseName + ': showTextSolution()', 2)


        curItem = self.parHandle.curExercise['settings']['list'][self.itemOrder[self.sequenceNo]]
        solution = ''
        if isinstance(curItem['assistance']['text']['text'], str):
            if self.solutionTextCounter < 0:
                solution = curItem['assistance']['text']['text']
                self.solutionTextCounter = self.solutionTextCounter + 1
        elif isinstance(curItem['assistance']['text']['text'],list):
            #solution = curItem['assistance']['text']['text']
            self.solutionTextCounter = self.solutionTextCounter + 1
            if isinstance(curItem['assistance']['text']['text'][0],str):
                if self.solutionTextCounter >= 0 and self.solutionTextCounter < len(curItem['assistance']['text']['text']):
                    solution = curItem['assistance']['text']['text'][self.solutionTextCounter]
            elif isinstance(curItem['assistance']['text']['text'][self.sequenceNo], list):
                if self.sequenceNo >= 0 and self.sequenceNo < len(curItem['assistance']['text']['text'][self.sequenceNo])\
                        and self.solutionTextCounter >= 0 and \
                        self.solutionTextCounter < len(curItem['assistance']['text']['text'][self.questNumber]):
                    solution = curItem['assistance']['text']['text'][self.questNumber][self.solutionTextCounter]
        if solution:
            if self.solutionTextCounter == 0:
                self.ui['teSolutionText'].setText('')
                self.ui['teSolutionText'].setAlignment(QtCore.Qt.AlignHCenter)

            self.ui['teSolutionText'].append(solution)
            # documention of usage of text assistance
            self.parHandle.curRunData['results']['assistance']['text'] = True

        self.parHandle.dPrint(self.exerciseName + ': Leaving showTextSolution()', 2)


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
        self.parHandle.curRunData['results']['label'] = 'noAnswer'
        self.parHandle.curRunData['results']['sequenceNo'] = -1
        self.parHandle.curRunData['results']['itemNo'] = -1
        self.parHandle.curRunData['results']['assistance'] = dict()
        # will be set to True if solution text is displayed
        self.parHandle.curRunData['results']['assistance']['text'] = False
        # will be set to True if solution audio is played back
        self.parHandle.curRunData['results']['assistance']['audio'] = False
        self.parHandle.curRunData['results']['correct'] = ''
        self.parHandle.curRunData['results']['audioPresentationCounter'] = 0

        self.sequenceNo = 0
        self.questNumber = 0

        self.itemOrder = np.arange(len(self.parHandle.curExercise['settings']['list']))
        
        # randnomized item order?
        if self.parHandle.curExercise['settings']['randomizedItems']:
            np.random.shuffle(self.itemOrder)
            
        super().prepareRun()
        self.iniAudio()
        self.iniItem()
        #self.presentSignal()




    def runButton(self, temp, forcedInput=''):
        """!
        This function measures the reaction time and calls self.run(). It is called when the user enters the results.
        """

        self.parHandle.dPrint(self.exerciseName + ': runButton()', 2)

        self.parHandle.measureReactionTime(self.parHandle, mode='stop')

        self.run()
        self.parHandle.dPrint(self.exerciseName + ': Leaving runButton', 2)


    def loadList(self):
        """!
        This function should call a gui in future to select an excel file which contains the data entrie for loading
        """

        self.parHandle.dPrint(self.exerciseName + ': loadList()', 2)

        self.parHandle.dPrint(self.exerciseName + ': Leaving loadList()', 2)


    def iniPath(self):
        """!
        iniPath will be called in exerciseBase()
        """

        self.parHandle.dPrint(self.exerciseName + ': iniPath()', 2)

        exerciseName = 'quiz'
        super().iniPath(exerciseName)

        # self.parHandle.curExercise['path']['analysis']  = os.path.join(pwd, 'analysis')
        # self.parHandle.curExercise['path']['scripts']  = os.path.join(pwd, 'scripts')
        self.parHandle.curExercise['path']['data'] = os.path.join(
            self.parHandle.curExercise['path']['base'], 'data')
        self.parHandle.curExercise['path']['dataSolution'] = os.path.join(
            self.parHandle.curExercise['path']['data'], 'solution')

        self.parHandle.dPrint(self.exerciseName + ': iniPath()', 2)


    def setDefaultSettings(self):
        """!
        The default parameters and settingLimits of the tests will be set.
        Mandatory/default fields are assigned by CICoachLab.py in
        initializeToDefaults() for each exercise, as well als generator, preprocessor and player,
        The default fields are set and extended by the
        repective items provided in this function.
        The settings can be set for single or all fields.
        """

        self.parHandle.dPrint(self.exerciseName + ': setDefaultSettings()', 2)

        exerciseName = 'quiz'
        super().setDefaultSettings(exerciseName)

        self.parHandle.curExercise['settingLimits']['randomizedItems'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['randomizedItems']['type'] = 'bool'
        self.parHandle.curExercise['settingLimits']['randomizedItems']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['randomizedItems']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['randomizedItems']['range'] = [True, False] #TODO: fill preselection with availabel players
        self.parHandle.curExercise['settingLimits']['randomizedItems']['editable'] = True
        self.parHandle.curExercise['settingLimits']['randomizedItems']['default'] = True

        self.parHandle.curExercise['settingLimits']['randomizedOptions'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['type'] = 'bool'
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['comboBoxStyle'] = True
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['range'] = [True, False] #TODO: fill preselection with availabel players
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['editable'] = True
        self.parHandle.curExercise['settingLimits']['randomizedOptions']['default'] = True

        self.parHandle.curExercise['settingLimits']['list'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curExercise['settingLimits']['list']['type'] = 'list'
        self.parHandle.curExercise['settingLimits']['list']['mandatory'] = True
        self.parHandle.curExercise['settingLimits']['list']['comboBoxStyle'] = False
        self.parHandle.curExercise['settingLimits']['list']['range'] = [True, False] #TODO: fill preselection with availabel players
        self.parHandle.curExercise['settingLimits']['list']['editable'] = False
        self.parHandle.curExercise['settingLimits']['list']['label'] = 'List of entries'
        self.parHandle.curExercise['settingLimits']['list']['toolTip'] = 'List of entries'
        self.parHandle.curExercise['settingLimits']['list']['function'] = self.loadList
        self.parHandle.curExercise['settingLimits']['list']['default'] = []

        self.parHandle.curExercise['settings']['randomizedItems']     = True
        self.parHandle.curExercise['settings']['randomizedOptions']   = True

        self.parHandle.curExercise['settings']['list']              = []


        item = dict()
        item['soundfile'] = '0011_Banjo.mp3'
        item['solutions'] = dict()
        item['quests'] = dict()
        item['options'] = dict()
        item['quests'][0] = 'What instrument do you hear?'
        item['solutions'][0] = 'Banjo'
        item['options'][0] = ['Banjo', 'Guitar', 'Cello', 'Piano']
        item['quests'][1] = 'What is the metre of the piece of music?'
        item['solutions'][1] = 'Banjo'
        item['options'][1] = ['1/4', '3/4', '4/4', '6/8', '5/4']
        item['assistance'] = dict()
        item['assistance']['text'] = dict()
        item['assistance']['text']['text'] = 'This audio sample is part of the "CIC-Hörspiel    "' + \
                                             '(https://www.cic-rheinmain.de/cic-aktiv/cic-hoerspiel/)'+\
                                             '\n\nCopyright: Sebastian Mielau'
        item['assistance']['text']['enable'] = True
        item['assistance']['audio'] = dict()
        item['assistance']['audio']['enable'] = False
        item['assistance']['audio']['preprocessing'] = False
        item['assistance']['audio']['signalfile'] = ''





        item = dict()
        item['soundfile'] = '0136_Summen.mp3'
        item['solutions'] = dict()
        item['quests'] = dict()
        item['options'] = dict()
        item['quests'][0] = 'What is the gender of the singer?'
        item['solutions'][0] = 'Female'
        item['options'][0] = ['Male', 'Female']
        item['quests'][1] = 'What is the name of the tune?'
        item['solutions'][1] = 'Happy birthday'
        item['options'][1] = ['Happy birthday', 'Twinke, twinkle little star']
        item['assistance'] = dict()
        item['assistance']['text'] = dict()
        item['assistance']['text']['text'] = [["The choosable gender is limited to 'Male' or 'Female' at this point since "
                                               "the selection of the diverse gender based on the pitch does not seem reasonable."],
                                              ['This tunes is commonly sung at birthday parties.\n',
                                              'This audio sample is part of the "CIC-Hörspiel" ' +
                                              'https://www.cic-rheinmain.de/cic-aktiv/cic-hoerspiel/'+
                                              '\n\nCopyright: Sebastian Mielau']]
        item['assistance']['text']['enable'] = True
        item['assistance']['audio'] = dict()
        item['assistance']['audio']['enable'] = False
        item['assistance']['audio']['preprocessing'] = False
        item['assistance']['audio']['signalfile'] = ''

        self.parHandle.curExercise['settings']['list'].append(item)

        item = dict()
        item['soundfile'] = "Jan Morgenstern _ Performed by Helena Fix - I Move On (Sintel's Song).mp3"
        item['solutions'] = dict()
        item['quests'] = dict()
        item['options'] = dict()
        item['quests'][0] = 'What is the duration of the song, approximately?'
        item['solutions'][0] = '4 minutes'
        item['options'][0] = ['4 minutes', '6 minutes', '15 minutes']
        item['quests'][1] = 'What is the gender of the singer?'
        item['solutions'][1] = 'Female'
        item['options'][1] = ['Male', 'Female']
        item['quests'][1] = 'When does the singing start?'
        item['solutions'][1] = '0:27'
        item['options'][1] = ['0:12', '0:27','1:45']
        item['assistance'] = dict()
        item['assistance']['text'] = dict()
        item['assistance']['text']['text'] = '''

    Title: I Move On (Sintel's Song)
    
    lyrics:
    
    Come take my journey into night
    Come be my shadow, walk at my side
    And when you see all that i have seen
    Can you tell me love from pride?
    
    I have been waiting all this time
    For one to wake me, one to call mine
    So when you´re near all that you hold dear
    Do you fear what you will find?
    
    As the dawn breaks through the night
    I move on forever longing for the home
    I found in your eyes.
    
    I will be listening for the drum
    To call me over, far away from
    My tender youth and the very truth
    Showing me what i've become.
    
    As the dawn breaks through the night
    I move on forever longing for the home
    I found in your eyes
    Your voice saw me through the night.
    
    
    Interpret: Jan Morgenstern / Performed by Helena Fix
    
    licensed under Creative Commons - CC BY-NC-ND 3.0
                                                '''
        item['assistance']['text']['enable'] = False
        item['assistance']['audio'] = dict()
        item['assistance']['audio']['enable'] = False
        item['assistance']['audio']['preprocessing'] = False
        item['assistance']['audio']['signalfile'] = ''

        self.parHandle.curExercise['settings']['list'].append(item)

        self.parHandle.dPrint(self.exerciseName + ': Quit setDefaultSettings()', 2)

