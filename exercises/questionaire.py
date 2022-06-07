"""!
The questionaire can provide a questionaire within the CICoachLab framework.

Overall Information can be displayed before above the  questions.

The questionaire checks if all obligatory questions have been answered before finishing the questionaire and hints to unanswered questions.
If not all obligatory questions are answered the questionaire cannot be stopped with the "Finish" button. An unfinished
questionaire can only be stopped with the "Cancel" button. An informational question will be asked after pressing
the Cancel button which has to be confirmed by the subject.

The possible options and fields are provided in the questionare which is defined in the  default settings.

In this implementation no audio or other output, other than the questions is provided.
Regarding the CICoachLab framework: no player and generator is required.


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
GPL-3.0-or-later
"""

from PyQt5 import QtCore, uic
import os
import importlib.util
from PyQt5 import QtWidgets, QtGui
from numpy import zeros
import pandas as pd
from numpy import array
from inspect import currentframe, getouterframes
import Validators

# TODO: implement missing features:
# TODO: 'multipleChoice', 'ranking'; 'noAnswer', 'allowNoAnswer', allowOther, 'orientation', 'displayTick',
# TODO: 'addSingleComment', 'displayTicks', 'default', 'range', ,'conditions'
# TODO: implement randomized order of responses
# TODO: Fragegruppen nur mit gleichen antwortypen, introduce check
# TODO: make more flexible: qtItem.setFixedWidth(qSizeMax.width())
# TODO: wrong label above standard settings dropdown


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)


class questionaire():
    def __init__(self, parHandle = None, settings = ''):
        """!
        The default parameters are set or the parameters of a provided settings file are loaded.
        """
        self.vBLayout = None
        self.controlbars = None

        try:
            msg = _translate("questionaire", 'Entering exercise: questionaire', None)
            parHandle.statusBar().showMessage(msg)
            self.parHandle = parHandle

            # this has to be initialized first because the resetting of the handle calls the destructor of the class
            # which resets and clears up everything which has been initialized nicely
            self.parHandle.curExercise['handle'] = self

            # loading default settings as basic settings
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.setDefaultSettings()
            # setting paths to exercise subfolder like "analysis"  "presets"  "results" (and other folders if the
            # exercise requires data like sound files or other
            self.iniPath()

            if settings != 'default' and settings != '':
                # the loaded settings just may overwrite parts of the defaultSettings....
                self.loadSettings(settings)

            # get reaction time delay which compensates the system/hardware realted delay between presentation of
            # stimuli and the fastest possible registrationa of the user input.
            self.parHandle.frameWork['calibration']['questionaire'] = {}
            # get reactionTimeDelay from iniFile configuration and save it under
            
            # check mark if answeres have been checked (by self.checkFinishedRun)
            self.finishRunCheck = False
            # place to save standard colors/palette of Qlabel
            virtualButton = QtWidgets.QPushButton()
            self.stdPalQLabels = virtualButton.palette()
            # keeping track of the pressed objects for an easier resetting of the gui
            self.answerObjectNames = []
            self.numberOfQuestions = 0
            self.previousQuestionaireGroup = 0
            try:
                self.parHandle.frameWork['calibration'][self.parHandle.curExercise['settings']['exerciseName']]['value'] = \
                    float(self.parHandle.frameWork['settings']['iniFileConfig']['exercises']['questionaire']['reactionTimeDelay'])
            except:
                msg = 'questionaire: Could not read reactionTimeDelay from ini File'
                self.parHandle.dPrint(msg, 2)
                self.parHandle.frameWork['calibration'][self.parHandle.curExercise['settings']['exerciseName']]['value'] = 0
        except:
            print('Entering exercise failed: questionaire')
        self.parHandle.dPrint('questionaire: __init__()', 2)


    def __exit__(self):
        """!
        This function is run at the closing of the class object.
        """

        self.parHandle.dPrint('questionaire: __exit__()', 2)

        self.closePath()

        self.parHandle.curExercise['settings']['exerciseName'] = ''
        self.parHandle.curExercise['functions']['destructor'] = None

        #self.eraseExerciseGui()

        self.parHandle.curExercise['settings']['exerciseName']              = ''
        self.parHandle.curExercise['functions']['prepareRun']          = None
        self.parHandle.curExercise['functions']['quitRun']           = None
        self.parHandle.curExercise['functions']['displayResults']    = None
        self.parHandle.curExercise['functions']['settingsLoading']   = None
        self.parHandle.curExercise['functions']['settingsDefault']   = None
        self.parHandle.curExercise['functions']['destructor']        = None

        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        self.parHandle.dPrint('questionaire: __exit__()', 2)


    def iniGui(self, settings=dict()):
        """!
        The gui is initialized or cleaned up if a gui of a previous questionaire exists and the same
        questionaire has to be started again.

        The "Cancel" button and "Finish" buttons are created.
        If no gui elements exist the gui will be initialized according to the loaded settings.

        If gui elements exist the selection of the previous runs will be removed.

        The generated items are saved in the dictionary self.ui. The items can be accessed by the corresponding unique
        objectname. The object name is generated as follows>

        e.g. objectName: sc_01_02_002_val01:
            sc:     singleChoice        type of input item
            01:     item number         internal numbering of formating items (spacer, information, question,  )
            01:     group number,       items can be grouped together with the same group number
            002:    question number,    the number of the question presented to the user
            val01:  value number,       in most case val01 but in case of single choice it indicates the input option

         The following types are implemented up to no
         items:             objectname label:
         'singleChoice':    sc
         'slider':          sl
         'text':            tt
         'textlong':        tl
         'dropdown':        dd
         'float':           tf
         'int':             ti
        """

        self.parHandle.dPrint('questionaire: iniGui()', 2)
        if len(settings) == 0:
            settings = self.parHandle.curExercise['settings']

        if len(self.parHandle.curExercise['gui']['exerWidgets']) == 0:
            # question specific information
            self.question = dict()
            self.question['answered']            = [] # False initially and True after user input (item spe
            self.question['questionNo']         = [] # number of a question as seen by the subject
            self.question['questObjectName']    = []
            self.question['answObjectName']     = []  # handle to selected object
            self.question['inputObjectName']    = []  # handle to text object
            self.question['itemNo']             = [] # no of item in settings
            self.question['requested']          = [] # input of user is requested

            subWidget = self.parHandle.ui.exerWidget

            self.vBLayout = QtWidgets.QVBoxLayout()

            subWidget.setLayout(self.vBLayout)

            maxAnswerPoints = 0
            for item in settings['items']:
                if 'noOfPoints' in item.keys() and item['noOfPoints'] > maxAnswerPoints:
                    maxAnswerPoints = item['noOfPoints']

            self.gridLauyout = QtWidgets.QGridLayout()
            self.vHLayout = QtWidgets.QHBoxLayout()

            self.vBLayout.addLayout(self.gridLauyout)

            self.vHLayoutStartQuit = QtWidgets.QHBoxLayout()
            self.vBLayout.addLayout(self.vHLayoutStartQuit)

            self.ui = dict()

            self.ui['pbCancelRun'] = QtWidgets.QPushButton(subWidget, text=_translate("questionaire", 'Cancel', None))
            self.ui['pbCancelRun'].setToolTip(
                _translate("questionaire", 'The questionaire is canceled without the check of the data.'
            'The data might be incomplete and not be usefull for the desired purpose.',
                           None))
            self.ui['pbCancelRun'].clicked.connect(self.cancelRun)

            self.ui['pbFinishedRun'] = QtWidgets.QPushButton(subWidget, text=_translate("questionaire",'Finished',None))
            self.ui['pbFinishedRun'].clicked.connect(self.checkFinishedRun)

            self.ui['pbFinishedRun'].setToolTip(
                _translate("questionaire", 'The input of the data is confirmed and the data validity will be '
                                           'checked. If data is missing or the input is wrong the regarding '
                                           'questions will be marked in red. You can correct the missing or wrong input. '
                                           'If all marked questions have been answered you can finish this questioniare. '
                                           '\n\nIf you want and are allowed to quit this questionaire without the data '
                           'check choose the Cancel button.'
                           , None))
            self.vHLayoutStartQuit.addWidget(self.ui['pbCancelRun'])
            self.vHLayoutStartQuit.addWidget(self.ui['pbFinishedRun'])
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbCancelRun'])
            self.parHandle.curExercise['gui']['exerWidgets'].append(self.ui['pbFinishedRun'])

            self.firstInGroup = True
            self.groupRowCounter = 0
            subWidget.setLayout(self.vBLayout)

            groupInputWidth = 1
            for item in settings['items']:
                if 'noOfPoints' in item.keys():
                    groupInputWidth = max([groupInputWidth, item['noOfPoints']])

            self.questionNo  = 0
            rowCounter = 0
            itemCounter = 0
            for item in settings['items']:
                try:
                    if item['group'] != self.previousQuestionaireGroup:
                        rowCounter = rowCounter + 1                # add an extra line as space between groups
                        print('rowcounter')
                        self.firstInGroup = True
                    else:
                        self.firstInGroup = False
                    if item['information'] != '':
                        objectName = f"info_{itemCounter:02d}_{item['group']:02d}{self.questionNo:03d}"
                        qtItem = QtWidgets.QLabel(parent = subWidget, text = item['information'], objectName=objectName,
                                                  alignment=QtCore.Qt.AlignCenter, )
                        qtItem.setWordWrap(True)
                        # fields:
                        # Question no., question, answer fields (depends on maximal number of answering points), comment (if necessary)
                        self.gridLauyout.addWidget(qtItem, rowCounter, 1, 1, 4 +maxAnswerPoints-1)
                        self.parHandle.curExercise['gui']['exerWidgets'].append(qtItem)
                        self.ui[objectName] = qtItem
                        #self.question['inputObjectName'].append([])
                        rowCounter = rowCounter + 1

                    if item['question'] != '':
                        self.questionNo = self.questionNo + 1

                        inputFieldOffset = 1

                        if self.firstInGroup:
                            # labeling the answers of the group
                            if len(item['labels']) == 2:

                                # two labels for minimum and maximum
                                idx = 1 + inputFieldOffset
                                objectName = f"lb_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{idx:02d}"
                                qtItem0 = QtWidgets.QLabel(parent=subWidget, text=item['labels'][0], objectName=objectName)
                                qtItem0.setAlignment(QtCore.Qt.AlignLeft)
                                self.gridLauyout.addWidget(qtItem0, rowCounter, idx, \
                                                           alignment=QtCore.Qt.AlignTrailing)
                                self.parHandle.curExercise['gui']['exerWidgets'].append(qtItem0)
                                self.ui[objectName] = qtItem0

                                idx = groupInputWidth + inputFieldOffset + 2
                                objectName = f"lb_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{idx:02d}"
                                qtItem1 = QtWidgets.QLabel(parent=subWidget, text=item['labels'][1], objectName=objectName)
                                qtItem1.setAlignment(QtCore.Qt.AlignRight)
                                self.gridLauyout.addWidget(qtItem1, rowCounter, idx, alignment=QtCore.Qt.AlignLeading)
                                self.parHandle.curExercise['gui']['exerWidgets'].append(qtItem1)
                                self.ui[objectName] = qtItem1

                                rowCounter = rowCounter + 1

                            elif len(item['labels']) == item['noOfPoints']:

                                qSizeMax = QtCore.QSize(0, 0)
                                # each answer gets a label
                                labelCounter = 0
                                for label in item['labels']:
                                    idx = 2+inputFieldOffset+labelCounter
                                    objectName = f"lb_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{idx:02d}"
                                    qtItem = QtWidgets.QLabel(parent=subWidget, text=item['labels'][labelCounter], objectName=objectName,
                                                              alignment=QtCore.Qt.AlignCenter)

                                    # getting minimum size of qItem which depends on the used text and font
                                    fm = QtGui.QFontMetrics(qtItem.font())
                                    qSize = QtCore.QSize(fm.width(qtItem.text()), qtItem.width())

                                    if qSize.width() > qSizeMax.width():
                                        qSizeMax.setWidth(qSize.width())
                                    if qSize.height() > qSizeMax.height():
                                        qSizeMax.setHeight(qSize.height())

                                    self.gridLauyout.addWidget(qtItem, rowCounter, idx)
                                    qtItem.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
                                    labelCounter = labelCounter + 1
                                    self.ui[objectName] = qtItem

                                # after all labels have been created resizing all labels to the same size qSizeMax
                                for labelCounter in range(len(item['labels'])):
                                    idx = 2 + inputFieldOffset + labelCounter
                                    objectName = f"lb_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{idx:02d}"

                                    qtItem = self.ui[objectName]
                                    #item.setFixedWidth(fm.width(item.text()))
                                    qtItem.setFixedWidth(qSizeMax.width())


                                rowCounter = rowCounter + 1

                        if item['type'] == 'singleChoice':
                            if item['allowOther']:
                                item['orientation'] = 'Vertical'

                            self.question['inputObjectName'].append([])

                            bGroup = QtWidgets.QButtonGroup(subWidget)
                            bGroup.setExclusive(True)
                            pointCounter = 0
                            for point in range(item['noOfPoints']):
                                objectName = f"sc_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{pointCounter:02d}"
                                button = QtWidgets.QRadioButton(parent = subWidget, objectName = objectName)
                                button.clicked.connect(self.runButton)
                                bGroup.addButton(button)
                                self.question['inputObjectName'][-1].append(objectName)
                                self.parHandle.curExercise['gui']['exerWidgets'].append(button)

                                self.ui[objectName] = button

                                self.gridLauyout.addWidget(button, rowCounter, 2 + pointCounter + inputFieldOffset, alignment=QtCore.Qt.AlignCenter)
                                button.show()
                                pointCounter = pointCounter + 1
                            self.parHandle.show()
                        objectName = f"questNo_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}"
                        qtItem = QtWidgets.QLabel(parent = subWidget, text = str(self.questionNo), objectName=objectName)
                        self.gridLauyout.addWidget(qtItem, rowCounter, 0)
                        self.parHandle.curExercise['gui']['exerWidgets'].append(qtItem)
                        self.ui[objectName] = qtItem

                        questObjectName = f"quest_{itemCounter:02d}_{item['group']:02d}{self.questionNo:03d}"
                        qtItemQ = QtWidgets.QLabel(parent = subWidget, text = item['question'], objectName=questObjectName)
                        qtItemQ.setWordWrap(True)
                        if 'toolTip' in item and item['toolTip']:
                            qtItemQ.setToolTip(item['toolTip'])

                        self.gridLauyout.addWidget(qtItemQ, rowCounter, 1, alignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter)
                        qtItemQ.setAlignment(QtCore.Qt.AlignHCenter)
                        self.parHandle.curExercise['gui']['exerWidgets'].append(qtItemQ)
                        self.ui[questObjectName] = qtItemQ

                        if item['type'] == 'slider':
                            if item['orientation'] == 'Horizontal':
                                orientation = QtCore.Qt.Horizontal
                            elif item['orientation'] == 'Vertical':
                                orientation = QtCore.Qt.Vertical
                            else:
                                orientation = QtCore.Qt.Horizontal

                            objectName = f"sl_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            slider = QtWidgets.QSlider(parent = subWidget, objectName= objectName,
                                    orientation = orientation)

                            slider.setMinimum(0)
                            slider.setMaximum(100)
                            if 'default' in list(item):
                                slider.setValue(item['default'])
                            else:
                                slider.setValue(50)
                            #if item['displayTicks']:
                            # if 'stepsize' in list(item) and item['stepsize'] > 0:
                            #    slider.setTickPosition(QSlider.TicksBelow)
                            #    slider.setTickInterval(5)
                            slider.setFixedHeight(60)
                            slider.setMinimumHeight(60)
                            slider.setMaximumHeight(60)
                            #if 'stepsize' in list(item) and item['stepsize'] > 0:
                            slider.setSingleStep(1)
                            slider.sliderReleased.connect(self.runButton)
                            slider.sliderMoved.connect(self.runButton)

                            self.parHandle.curExercise['gui']['exerWidgets'].append(slider)
                            self.ui[objectName] = slider

                            self.gridLauyout.addWidget(slider, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            slider.show()


                        if item['type'] == 'dropdown':
                            objectName = f"dd_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            dropdown = QtWidgets.QComboBox(parent = subWidget, objectName= objectName)
                            for entry in item['range']:
                                dropdown.addItem(entry, entry)

                            dropdown.currentIndexChanged.connect(self.runButton)

                            self.parHandle.curExercise['gui']['exerWidgets'].append(dropdown)
                            self.ui[objectName] = dropdown
                            self.gridLauyout.addWidget(dropdown, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            dropdown.show()

                        if item['type'] == 'text':
                            objectName = f"tt_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            txt = QtWidgets.QLineEdit(parent = subWidget, objectName= objectName)

                            txt.editingFinished.connect(self.runButton)

                            self.parHandle.curExercise['gui']['exerWidgets'].append(txt)
                            self.ui[objectName] = txt
                            self.gridLauyout.addWidget(txt, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            txt.show()
                        if item['type'] == 'textlong':
                            objectName = f"tl_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            txt = QtWidgets.QPlainTextEdit(parent = subWidget, objectName= objectName)
                            txt.textChanged.connect(self.run)
                            """
                            txt = QtWidgets.QLineEdit(parent = subWidget, objectName= objectName)
                            txt.setMinimumHeight(txt.height() * 3)
                            txt.editingFinished.connect(self.runButton)
                            
                            """
                            self.parHandle.curExercise['gui']['exerWidgets'].append(txt)
                            self.ui[objectName] = txt
                            self.gridLauyout.addWidget(txt, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            txt.show()

                        if item['type'] == 'int':
                            objectName = f"ti_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            ti = QtWidgets.QLineEdit(parent = subWidget, objectName= objectName)
                            convertFunc = int
                            validator = Validators.NumberValidator(inputRange=item['range'],
                                                                   convertFunc=convertFunc, comboStyle=False)
                            ti.setValidator(validator)

                            ti.editingFinished.connect(self.runButton)

                            self.parHandle.curExercise['gui']['exerWidgets'].append(ti)
                            self.ui[objectName] = ti
                            self.gridLauyout.addWidget(ti, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            ti.show()

                        if item['type'] == 'float':
                            objectName = f"tf_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val01"
                            self.question['inputObjectName'].append([])
                            self.question['inputObjectName'][-1].append(objectName)

                            tf = QtWidgets.QLineEdit(parent = subWidget, objectName= objectName)
                            convertFunc = float
                            validator = Validators.NumberValidator(inputRange=item['range'],
                                                                   convertFunc=convertFunc, comboStyle=False)
                            tf.setValidator(validator)

                            tf.editingFinished.connect(self.runButton)

                            self.parHandle.curExercise['gui']['exerWidgets'].append(tf)
                            self.ui[objectName] = tf
                            self.gridLauyout.addWidget(tf, rowCounter, 2 + inputFieldOffset, 1, groupInputWidth)
                            tf.show()

                        self.question['answered'].append(False)
                        self.question['questionNo'].append(self.questionNo)
                        self.question['questObjectName'].append(questObjectName)
                        self.question['itemNo'].append(itemCounter)
                        if 'requested' in item.keys():
                            self.question['requested'].append(item['requested'])
                        else:
                            self.question['requested'].append(True)
                except:
                    self.parHandle.showInformation('Item of questionaire could not be set.')
                self.question['answObjectName'] = [''] * len(self.question['requested'])

                rowCounter = rowCounter + 1

                objectName = 'spacer01'
                qtItem = QtWidgets.QLabel(parent = subWidget, text = '', objectName=objectName)
                self.gridLauyout.addWidget(qtItem, rowCounter, 0)

                self.previousQuestionaireGroup = settings['items'][itemCounter]['group']
                itemCounter = itemCounter + 1
        else:
            # cleaning up previous run if required.
            self.question['answered'] = [False] * len(self.question['requested'])

            #  add default value handling and type handling
            # iniGui should be called to handle reinitialization of self.question
            #if len(self.question['answObjectName']) > 0:

            for questCounter in range(len(self.question['itemNo'])):
                #item = self.question['inputObjectName'][self.question['itemNo'][questCounter]][0]
                item = self.question['inputObjectName'][questCounter]
                try:
                    settingItem = settings['items'][self.question['itemNo'][questCounter]]
                    if settingItem['type'] == 'singleChoice':
                        #self.ui[self.question['inputObjectName'][self.question['itemNo'][0]][0]].group().setExclusive(False)
                        #for rbItem in self.question['inputObjectName'][self.question['itemNo'][questCounter]]:
                        for rbItem in item:
                            self.ui[rbItem].group().setExclusive(False)
                            self.ui[rbItem].setChecked(False)
                            self.ui[rbItem].group().setExclusive(True)

                    elif settingItem['type'] == 'slider':
                        if 'default' in list(settingItem):

                            self.ui[item[0]].setValue(settingItem['default'])
                        else:
                            self.ui[item[0]].setValue(50)
                    elif settingItem['type'] == 'text':
                        self.ui[item[0]].setText('')
                    elif settingItem['type'] == 'textlong':
                        'active'
                        self.ui[item[0]].setPlainText('')

                    elif settingItem['type'] == 'dropdown':
                        idx = self.ui[item[0]].findText('')
                        self.ui[item[0]].setCurrentIndex(idx)
                    elif settingItem['type'] == 'float':
                        self.ui[item[0]].setText('')
                    elif settingItem['type'] == 'int':
                        self.ui[item[0]].setText('')
                except:
                    msg = _translate("questionaire",'Result could not be displayed.', None)
                    self.parHandle.dPrint(msg, 0, guiMode = True)


            self.question['answObjectName'] = [''] * len(self.question['requested'])

            self.parHandle.ui.exerWidget.setVisible(True)

        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(False)
            except:
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)

        self.parHandle.ui.exerWidget.show()
        self.parHandle.dPrint('questionaire: iniGui()', 2)


    def eraseExerciseGui(self):
        """!
        The exercise gui elements which are found in the layouts will be removed. self.vBLayout is the base
        layout for the other layouts. This function will be called if the exercises is changed or another questionaire
        is loaded.
        """

        self.parHandle.dPrint('questionaire: eraseExerciseGui()', 2)
        try:
            if self.vBLayout != None:
                for layOutItem in self.vBLayout.children():
                    for ii in reversed(range(layOutItem.count())):
                        layOutItem.itemAt(ii).widget().setParent(None)
                # the layout which is assigned to the exercise container widget cannot be deleted it just can be moved to
                # another temporary widget
                QtWidgets.QWidget().setLayout(self.parHandle.ui.exerWidget.layout())
        except:
            self.parHandle.dPrint('questionaire: Could not delete gui', 2)
        self.parHandle.curExercise['gui']['exerWidgets'] = list()

        self.parHandle.dPrint('questionaire: Leaving eraseExerciseGui()',
                              2)


    def startRun(self):
        """!
        This function is called to start a questionaire.
        The gui is initialized by enabling the questionaire elements and by calling iniGui().
        """

        self.runIdx = 0
        self.parHandle.dPrint('questionaire: startRun()', 2)
        
        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(False)
            except:
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)
        #self.ui['pbFinishedRun'].setDisabled(True)

        # initialize other variable required by the exercise
        self.presentationCounter = 0
        self.previousQuestionaireGroup = 0
        self.questionNo = 0
        self.runIdx = 0
        self.finishRunCheck = False
        self.parHandle.curRunData['results'] = []

        self.iniGui()

        labels = ['Question', 'Group', 'InputType', 'Value', 'Other', 'NoAnswer', 'Comment']

        self.determineNumberOfQuestions()

        valType = zeros(self.numberOfQuestions)
        entries = { "Questions": [""] * self.numberOfQuestions,
                    "Group": zeros(self.numberOfQuestions),
                    "InputType": [""] * self.numberOfQuestions,
                    "Value": valType,
                    "Other": [""] * self.numberOfQuestions,
                    "NoAnswer": [False] * self.numberOfQuestions,
                    "Comment": [""] * self.numberOfQuestions,
                    "ObjectName": [""] * self.numberOfQuestions}
        questMat = pd.DataFrame(entries, columns = labels)

        self.parHandle.curRunData['results'].append(questMat)
        self.parHandle.curRunData['runAccomplished'] = False


    def determineNumberOfQuestions(self, settings = dict()):
        """!
        This function extracts the number of questions from self.parHandle.curExercise['settings']['items']
        and sets self.numberOfQuestions.
        """

        self.parHandle.dPrint('questionaire: determineNumberOfQuestions()', 2)

        if len(settings) == 0:
            settings = self.parHandle.curExercise['settings']

        self.numberOfQuestions = 0
        for ii in range(len(settings['items'])):
            if len(settings['items'][ii]['question']) != 0:
                self.numberOfQuestions = self.numberOfQuestions + 1
        self.parHandle.dPrint('questionaire: Leaving determineNumberOfQuestions()', 2)


    def runButton(self, event='', forcedInput=''):
        """!
        This functions is called if any question of the questionaire is answered.
        """

        self.parHandle.dPrint('questionaire: runButton()', 2)

        # measuring reaction time does inionly make sense if questions are presented line by line after answering
        # the previous question, add later as option in special cases?
        #self.parHandle.measureReactionTime(self.parHandle, mode='stop')
        callingFunctionName = getouterframes(currentframe(), 2)[1][3]

        if callingFunctionName != 'displaySingleResults' and callingFunctionName != 'iniGui':
            self.run()


    def displaySingleResults(self, data):
        """!
        This function displays the result as a filled questionaire form.
        The gui will be initialized with the settings set by the user, or while loading old data
        """

        self.parHandle.dPrint('questionaire: displaySingleResults()', 2)
        self.loadSettings(data['settings']['exercise']['settingsName'])
        self.iniGui()
        if not(hasattr(data['results'][0], 'ObjectName')):
            msg = _translate("questionaire", 'No valid data could be found. This run has been canceled, probably.', None)
            self.parHandle.dPrint(msg, 1 , guiMode=True)
            return

        objectNames = data['results'][0]['ObjectName']
        inputTypes = data['results'][0]['InputType']
        values = data['results'][0]['Value']
        ic = 0
        for item in objectNames:
            token = item.split('_')[0]
            if token == 'sc':
                # single choise
                self.ui[item].setChecked(True)
            elif token == 'tt':
                # free text
                self.ui[item].setText(values[ic])
            elif token == 'tl':
                #long text
                self.ui[item].setPlainText(values[ic])
            elif token == 'dd':
                # text from drop down
                idx = self.ui[item].findText(values[ic])
                self.ui[item].setCurrentIndex(idx)
                pass
            elif token == 'ti':
                # text: integer
                self.ui[item].setText(str(values[ic]))
            elif token == 'tf':
                # text float
                self.ui[item].setText(str(values[ic]))
            elif token == 'sl':
                # slider
                self.ui[item].setValue(values[ic])
                #self.ui[item].
            elif token == 'mc':
                #multiple choice
                print('TODO')
            ic = ic + 1
        pass
        self.parHandle.dPrint('questionaire: Leaving displaySingleResults()', 2)


    def run(self):
        """!
        This function provides the logic to handle the input of the user.

        The data is saved. If any questions are highlighted because the user tried to finish the run with  missing data at
        the highlighting is removed.
        """

        self.parHandle.dPrint('questionaire: run()', 2)

        # if gui is reinitialized the resetting is interpreted as user input which is ignored here
        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
        if callingFunctionName == 'iniGui':
            self.parHandle.dPrint('self.run(): ignoring call by iniGui.', 3)
            return

        objectName = self.parHandle.sender().objectName()
        # objectName is constructed as follows:
        # f"answer_{itemCounter:02d}_{item['group']:02d}_{self.questionNo:03d}_val{pointCounter}"

        labels = ['Question', 'Group', 'InputType', 'Value', 'Other', 'NoAnswer', 'Comment']
        obj, itemNoStr, groupNoStr, questNoStr, valStr = objectName.split('_')

        itemNo = int(itemNoStr)
        groupNo = int(groupNoStr)
        questNo = int(questNoStr)

        # tracking answered objects
        self.question['answObjectName'][questNo-1] = objectName

        question = self.parHandle.curExercise['settings']['items'][itemNo]['question']
        inputType =self.parHandle.curExercise['settings']['items'][itemNo]['type']
        #self.parHandle.curExercise['settings']['items'][itemNo]

        if inputType == 'singleChoice':
            val = int(valStr[3:])
        elif inputType == 'slider':
            val = self.ui[objectName].value()
        elif inputType == 'dropdown':
            val = self.ui[objectName].currentText()
        elif inputType == 'text':
            val = self.ui[objectName].text()
        elif  inputType == 'textlong':
            val = self.ui[objectName].toPlainText()
        elif inputType == 'int':
            val = int(self.ui[objectName].text())
        elif inputType == 'float':
            val = float(self.ui[objectName].text())

        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'Question'] = question
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'Group'] = groupNo
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'InputType'] = inputType
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'Value'] = val
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'ObjectName'] = objectName

        if 'allowOther' in self.parHandle.curExercise['settings']['items'][itemNo].keys()\
                and self.parHandle.curExercise['settings']['items'][itemNo]['allowOther'] == True:
            self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'Other'] = ""
                #self.parHandle.curExercise['settings']['items'][itemNo]['other']
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'NoAnswer'] = False
        self.parHandle.curRunData['results'][self.runIdx].loc[questNo - 1, 'Comment'] = ''

        self.presentationCounter = self.presentationCounter + 1
        # reset marked Questions to standard colors/palette
        if self.finishRunCheck == True:# and self.question['answered'][questNo-1] == False:
            self.ui[self.question['questObjectName'][questNo - 1]].setPalette(self.stdPalQLabels)
            myFont = QtGui.QFont()
            myFont.setBold(False)
            self.ui[self.question['questObjectName'][questNo - 1]].setFont(myFont)

        self.question['answered'][questNo - 1] = True
        self.parHandle.dPrint('questionaire: run()', 2)


    def checkFinishedRun(self):
        """!
        The function is called if the button "finish" is pressed. Before finishing the run, this functions checks if all
        obligatory data has been answered. If not the regarding question will be highligthed and a popup window will
        inform the the subject, that the highlighted questions have to be answered befor successfully finishing the
        run.
        """

        self.parHandle.dPrint('questionaire: checkFinishedRun()', 2)

        #check if all requested questions have been answered
        requested = array(self.question['requested'])
        answered = array(self.question['answered'])
        # check all runs which have to be answered
        idx = (requested == True)
        if all(requested[idx] == answered[idx]):
            self.finishRun()
        else:
            #find and mark unanswered runs
            checkItems = (requested[idx] == answered[idx]) == False
            questNo = 1
            for item in idx:
                if item == True and not(answered[questNo-1]):
                    pal = QtGui.QPalette(self.ui[self.question['questObjectName'][questNo-1]].palette())
                    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(QtCore.Qt.red))
                    self.ui[self.question['questObjectName'][questNo-1]].setPalette(pal)

                    myFont = QtGui.QFont()
                    myFont.setBold(True)
                    self.ui[self.question['questObjectName'][questNo-1]].setFont(myFont)
                else:
                    self.ui[self.question['questObjectName'][questNo-1]].setPalette(self.stdPalQLabels)
                    myFont = QtGui.QFont()
                    myFont.setBold(False)
                    self.ui[self.question['questObjectName'][questNo-1]].setFont(myFont)
                questNo = questNo + 1

            msg = _translate("questionaire", 'Some questions still have to be answered yet.\n\n' + \
                             'Please enter the questiones which have been marked in red.', None)
            title = _translate("questionaire", 'CICoachLab information', None)
            QtWidgets.QMessageBox.information(self.parHandle.ui.exerWidget, title , msg)
        self.finishRunCheck = True
        
        self.parHandle.dPrint('questionaire: quit checkFinishedRun()', 2)


    def cancelRun(self):
        """!
        This functions will finish the run, even if some questions have not been answered yet. The subject is asked for
            confirmation before calling the function quitRun().
        """

        if self.presentationCounter > 0:
            #msg = _translate("questionaire", 'Möchten Sie die Befragung abbrechen?.\nIhre bisherigen Angaben des ' +\
            #                 'Fragebogens können damit nicht für weitere Auswertungen verwendet werden.', None)
            msg = _translate("questionaire", 'Would you like to cancel the questionaire?.\n ' +\
                             'Your entered input could not be used.',
                             None)
        else:
            #msg = _translate("questionaire", 'Möchten Sie die Befragung abbrechen?', None)
            msg = _translate("questionaire", 'Would you like to cancel the questionaire?', None)

        title = _translate("questionaire", 'CICoachLab Information', None)
        response = QtWidgets.QMessageBox.question(self.parHandle.ui.exerWidget, title, msg)
        if response == QtWidgets.QMessageBox.Yes:
            self.quitRun()


    def quitRun(self):
        """!
        This function ends and hides the questionaire part.
        """

        self.parHandle.dPrint('questionaire: quitRun()', 2)

        self.parHandle.ui.exerWidget.setVisible(False)

        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
        if callingFunctionName != 'cancelRun':
            self.parHandle.curRunData['runAccomplished'] = True
            # central recheck if run accomplishment is True in
            #   self.parHandle.frameWork['functions']['closeDownRun']() > self.parHandle.checkConditions
            #self.parHandle.checkConditions(self)

        self.parHandle.dPrint('questionaire: Quit quitRun() > closeDownRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()


    def finishRun(self):
        """!
        This function ends and hides the questionaire part. In contrast to self.quitRun() the run will be marked as
        accomplished because CICoachLab assumes that runs ended by. self.quitRun() mark unaccomplished runs.
        """
        self.parHandle.dPrint('finishRun: finishRun()', 2)

        self.parHandle.ui.exerWidget.setVisible(False)

        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
        if callingFunctionName != 'cancelRun':
            self.parHandle.curRunData['runAccomplished'] = True
            # central recheck if run accomplishment is True in
            #   self.parHandle.frameWork['functions']['closeDownRun']() > self.parHandle.checkConditions
            #self.parHandle.checkConditions(self)

        self.parHandle.dPrint('questionaire: Quit finishRun() > closeDownRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()


    def iniPath(self):
        """!
        The dictionary self.parHandle.curExercise['path'] will be filled
        with the 'analysis', 'preset', 'results' path.
        The path entries of the dictionary will be added at the top of the path
        by sys.path in the frameWork.
        """

        self.parHandle.dPrint( 'questionaire: iniPath()', 2)

        pwd = os.path.join(self.parHandle.frameWork['path']['exercises'], 'questionaire')
        self.parHandle.curExercise['path']['base']      = pwd
        self.parHandle.curExercise['path']['presets']   = os.path.join(pwd, 'presets')
        self.parHandle.curExercise['path']['results']   = os.path.join(pwd, 'results')
        self.parHandle.curExercise['path']['analysis']  = os.path.join(pwd, 'analysis')
        self.parHandle.curExercise['path']['conditions']  = os.path.join(pwd, 'conditions')

        self.parHandle.addingPath('curExercise')

        self.parHandle.dPrint( 'questionaire: Leaving iniPath()', 2)


    def closePath(self):
        """!
        The path of the exercise will be removed from sys.path by the frameWork.
        Reset the path dictionary in self.parHandle.curExercise by
        setting entries to empty strings.
        """

        self.parHandle.dPrint('questionaire: closePath()', 2)

        self.parHandle.closePath('curExercise')

        self.parHandle.curExercise['path']['base']      = ''
        self.parHandle.curExercise['path']['presets']   = ''
        self.parHandle.curExercise['path']['results']   = ''
        self.parHandle.curExercise['path']['analysis']  = ''

        self.parHandle.dPrint('questionaire: closePath()', 2)


    def loadSettings(self, settings):
        """!
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current exercise.
        """

        self.parHandle.dPrint('questionaire: loadSettings()', 2)

        try:
            self.eraseExerciseGui()

            self.parHandle.loadSettings(settings, module='curExercise')
        except:
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'

            self.parHandle.dPrint('Could not load settings ('+settingsName+') loading default settings instead', 1)

            self.parHandle.dPrint('Could not load settings (' + settingsName + ') loading default settings instead', 1)
            self.setDefaultSettings()

        # check if a generator, preprocessor player can be initialized, not required so far in this implemtation
        #if not(self.parHandle.curExercise['settings']['generator'] == ''):
        self.parHandle.iniSubmodule('generator',  self.parHandle.curExercise['settings']['generator'],\
                                 self.parHandle.curExercise['settings']['generatorSettings'])
        #if not(self.parHandle.curExercise['settings']['preprocessor'] == ''):
        self.parHandle.iniSubmodule('preprocessor',  self.parHandle.curExercise['settings']['preprocessor'],\
                                 self.parHandle.curExercise['settings']['preprocessorSettings'])
        #if not(self.parHandle.curExercise['settings']['player'] == ''):
        self.parHandle.iniSubmodule('player',  self.parHandle.curExercise['settings']['player'],\
                                 self.parHandle.curExercise['settings']['playerSettings'])

        self.parHandle.dPrint('questionaire: Leaving loadSettings()', 2)


    def setDefaultSettings(self):
        """!
        The default parameters of the tests will be set.
        """

        self.parHandle.dPrint('questionaire: Leaving setDefaultSettings()', 2)

        exerciseBaseName = self.parHandle.frameWork['path']['exercises']
        exerciseName = 'questionaire'

        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        self.parHandle.curExercise['settings']['exerciseName'] = exerciseName
        self.parHandle.curExercise['path'] = dict()
        self.parHandle.curExercise['path']['base'] = os.path.join(exerciseBaseName, exerciseName)
        self.parHandle.curExercise['path']['presets'] = os.path.join(exerciseBaseName, 'presets')

        self.parHandle.curExercise['settings']['settingsName'] = 'default'

        # Check format
        # exercise specific settings
        questionaireItems = []

        item = dict()
        item['information']     = \
            _translate("questionaire","With this questionaire the possibilities of the questionaire exercise "
                                      "should be demonstrated. The questions and answers won't make sense.\n\n"
                                    "In some cases it might be interesting to check the tooltips "
                                    " of the individuell questions. Hover of over the question to see the tooltips.",
                       None)
        item['question']        = ''
        item['group']           = 1
        item['requested']       = False
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'How often does the sun shine on you?', None)
        item['type']            = 'singleChoice'
        item['allowNoAnswer']   = True
        item['allowOther']      = True
        item['addSingleComment']= True
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 7
        item['labels']          = [_translate("questionaire",'never', None), _translate("questionaire",'always', None)]
        item['displayTicks']      = False
        item['group']           = 2
        item['requested']       = True
        item['toolTip']            = ''
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'Are you shure?', None)
        item['type']            = 'singleChoice'
        item['allowNoAnswer']   = True
        item['allowOther']      = True
        item['addSingleComment']= True
        item['orientation']     = 'Horizontal' # for scaling only
        item['noOfPoints']      = 7
        item['labels']          = [_translate("questionaire",'never', None), _translate("questionaire",'always', None)]
        item['displayTicks']      = False
        item['group']           = 2
        item['toolTip']            = 'No input is required.'
        item['requested']       = False
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'How often does the sun shine on you, exactly?', None)
        item['type']            = 'slider'
        item['allowNoAnswer']   = True
        item['allowOther']      = True
        item['addSingleComment']= True
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = [_translate("questionaire",'never', None), _translate("questionaire",'always', None)]
        item['displayTicks']      = True
        item['group']           = 3
        item['range']           = []
        item['toolTip']            = _translate("questionaire", 'Move the handle to any position of the slider.', None)
        item['requested']       = True
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'How long have you been deaf?', None)
        item['type']            = 'dropdown'
        item['allowNoAnswer']   = True
        item['allowOther']      = True
        item['addSingleComment']= True
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = True
        item['group']           = 4
        item['requested']       = True
        item['toolTip']            = ''
        item['range']           = ['', 'very long', 'not at all', 'sometimes', 'maybe']
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'Free text input', None)
        item['type']            = 'text'
        item['allowNoAnswer']   = False
        item['allowOther']      = False
        item['addSingleComment']= False
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = False
        item['group']           = 5
        item['requested']       = True
        item['toolTip']            = _translate("questionaire",
                                                'A short line of free text without linebreaks can be entered.',
                                                None)
        item['range']           = []
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'Free long text input', None)
        item['type']            = 'textlong'
        item['allowNoAnswer']   = False
        item['allowOther']      = False
        item['addSingleComment']= False
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = False
        item['group']           = 5
        item['requested']       = True
        item['toolTip'] = _translate("questionaire",
                                     'A longer free text with linebreaks can be entered.',
                                     None)
        item['range']           = []
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'Please provide an integer number.', None)
        item['type']            = 'int'
        item['allowNoAnswer']   = False
        item['allowOther']      = False
        item['addSingleComment']= False
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = False
        item['group']           = 5
        item['requested']       = True
        item['toolTip']            = 'You can only put in numbers without "." or ","'
        item['range']           = []
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'Please provide an integer number.', None)
        item['type']            = 'int'
        item['allowNoAnswer']   = False
        item['allowOther']      = False
        item['addSingleComment']= False
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = False
        item['group']           = 5
        item['requested']       = True
        item['toolTip']            = 'You can only put in numbers without "." or "," in the range of -10 to 99'
        item['range']           = [-10, 99]
        questionaireItems.append(item)

        item = dict()
        item['information']     = ''
        item['question']        = _translate("questionaire",'You can provide a floating point number.', None)
        item['type']            = 'float'
        item['allowNoAnswer']   = False
        item['allowOther']      = False
        item['addSingleComment']= False
        item['orientation']     = 'Horizontal'
        item['noOfPoints']      = 0
        item['labels']          = []
        item['displayTicks']      = False
        item['group']           = 5
        item['requested']       = True
        item['toolTip']            = 'Use a "." to enter a floating point number.'
        item['range']           = []
        questionaireItems.append(item)

        # settingLimits just defines the range for each entry
        # Default values are useless in most cases but the slider
        itemLimits = dict()
        itemLimits['Information']       = ['']  # some string/information without any possible/required input.
        itemLimits['question']          = ['']
        itemLimits['type']              = ['singleChoice', 'dropdown', 'multipleChoice', 'ranking',\
                                            'slider', 'text', 'textlong', 'int', 'float']
        itemLimits['allowNoAnswer']     = [True, False] # for all but text (== ''), and int and float (empty)
        itemLimits['allowOther']        = [True, False] # for all but free text (), and int and float
        itemLimits['addSingleComment']  = [True, False] # for all types but text
        itemLimits['orientation']       = ['Horizontal', 'Vertical'] # orientation of slider
        itemLimits['noOfPoints']        = 7 # number of possible answers or ticks at a slider
        itemLimits['labels']            = ['', ''] # two values show the limits or the labels in the binary case
        itemLimits['displayTicks']      = [True, False]
        itemLimits['default']           = 0.5   # in most cases useless but may be required for the slider
                                                # depending on type of item other types of values might be feasible
        # item in the same group have the same type and share the same labels/limits, if possible they should be
        # displayed at the same page. Between two groups additional space is added.
        itemLimits['group']             = [0 - 999999]
        itemLimits['requested']         = [True, False] #Input of subject ist requested, default: True
        # some text which may be displayed if the user hovers over the respective label
        itemLimits['tooltip']              = ''
        itemLimits['range']             = [] # combobox/dropdown: list of strings, which can be selected.
                                             # int/float: minimum and maximum
        self.parHandle.curExercise['settings']['items'] = questionaireItems

        # making the exercise function available for the frameWork.
        self.parHandle.curExercise['functions']['prepareRun'] = self.startRun
        self.parHandle.curExercise['functions']['cancelRun'] = self.cancelRun
        self.parHandle.curExercise['functions']['quitRun'] = self.quitRun
        self.parHandle.curExercise['functions']['displayResults'] = self.displaySingleResults
        self.parHandle.curExercise['functions']['settingsLoading'] = self.loadSettings
        self.parHandle.curExercise['functions']['settingsDefault'] = self.setDefaultSettings
        self.parHandle.curExercise['functions']['settingsGui'] = None
        self.parHandle.curExercise['functions']['checkConditions'] = None
        self.parHandle.curExercise['functions']['destructor'] = self.__exit__
        self.parHandle.curExercise['functions']['eraseExerciseGui'] = self.eraseExerciseGui
        self.parHandle.curExercise['settings']['exerciseName'] = 'questionaire'

        # setting paths to exercise subfolder like "analysis"  "presets"  "results" (and other folders if the
        # exercise requires data like sound files or other
        self.iniPath()

        self.parHandle.dPrint('playAudio: Leaving setDefaultSettings()', 2)


