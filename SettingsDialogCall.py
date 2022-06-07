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


from PyQt5 import QtWidgets, QtCore, QtGui
from SettingsDialog import Ui_SettingsWindow
import Validators

import os
import bz2
import pickle
import re
# Todo: Check result of OK and cancel. Cancel does not work probably
from copy import deepcopy


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)




class SettingsDialogCall(QtWidgets.QDialog):
    def __init__(self, parHandle=None):
        """!
        Initializing the dialog window within the CICoachLab framework for the management of the settings data.

        The gui is imported as Ui_Dialog which is defined in Calibration.py and Calibration.ui. Calibration.ui is
        converted into the python file with the command line 'pyuic5 SettingsDialog.ui -o SettingsDialog.py'.

        The modes define which settings are handled across all function of the SettingsDialogCall class.

        mode can be given modules
            exercise
            generator
            preprocessor
            player


        In the settings dialog the settings of the modules can be changed. For each module a tab is exists which
        is dynamically filled with the gui fields for the settings which can be changed by the user. If a setting
        is editable is defined by the exercise in the settingLimits. The common template of the setting limits is
        defined by the CICoachLab function self.setSettingLimitsTemplate() which defines descriptions and defaults for
        the different options.

        In each module tab the common buttons are found as follows:
        "New":
             A new settings entry is generated with the current settings. These setting are not saved at the generation and
             will be lost, when CICoachLab is close
        "Save as":
            The current setting will be saved as preset with a new name which has to be defined
        "Save"
            The current setting will be saved as preset.
        "Save all":
            The current settings of all modules will be saved.
        "Reset":
            The settings will be reset to the default values
        "Reload":
            Reload the current preset to undo current changes.
        "Ok":
            The current settings will be confirmed.
            If unsaved data exists in any module a dialog will ask if the presets should be saved.
        "Cancel":
            The settings will be reset to the old settings. Nothing will be saved at close down.
        """

        self.parHandle = parHandle
        # providing CICoachLab the handle to the setting window for some handling of field entries
        self.parHandle.settingsDLGHandle = self

        self.parHandle.dPrint('Leaving __init__()', 2)

        # TODO: Otherwise introduce and check prevStates again.
        self.oldGeneratorName = self.parHandle.curGenerator['settings']['generatorName']
        self.oldGeneratorSettings = self.parHandle.curGenerator['settings']
        self.oldPreprocessorName = self.parHandle.curPreprocessor['settings']['preprocessorName']
        self.oldPreprocessorSettings = self.parHandle.curPreprocessor['settings']
        self.oldPlayerName = self.parHandle.curPlayer['settings']['playerName']
        self.oldPlayerSettings =  self.parHandle.curPlayer['settings']
        self.oldExerciseName = self.parHandle.curExercise['settings']['exerciseName']
        self.oldExerciseSettings =  self.parHandle.curExercise['settings']

        self.prevGeneratorName = self.parHandle.curGenerator['settings']['generatorName']
        self.prevGeneratorSettings = self.parHandle.curGenerator['settings']
        self.prevPreprocessorName = self.parHandle.curPreprocessor['settings']['preprocessorName']
        self.prevPreprocessorSettings = self.parHandle.curPreprocessor['settings']
        self.prevPlayerName = self.parHandle.curPlayer['settings']['playerName']
        self.prevPlayerSettings =  self.parHandle.curPlayer['settings']
        self.prevExerciseName = self.parHandle.curExercise['settings']['exerciseName']
        self.prevExerciseSettings =  self.parHandle.curExercise['settings']

        self.generatorSettings = dict()
        self.generatorSettings[self.parHandle.curGenerator['settings']['settingsName']] = \
            self.parHandle.curGenerator['settings'].copy()
        self.preprocessorSettings = dict()
        self.preprocessorSettings[self.parHandle.curPreprocessor['settings']['settingsName']] = \
            self.parHandle.curPreprocessor['settings'].copy()
        self.playerSettings = dict()
        self.playerSettings[self.parHandle.curPlayer['settings']['settingsName']] = \
            self.parHandle.curPlayer['settings'].copy()

        self.settings = self.parHandle.settings
        self.newEntries = dict()

        modules = ['exercise', 'generator', 'preprocessor', 'player']
        # initialize modules
        for module in modules:
            Module = module[0].upper() + module[1:]
            curModuleName = 'cur' + Module
            if not(module in self.settings):
                self.settings[module] = dict()
            # TODO: Settings
            moduleName = getattr(self.parHandle, curModuleName)['settings'][module + 'Name']
            if not(moduleName in self.settings[module]):
                self.settings[module][moduleName] = dict()
            # TODO: Settings
            moduleSettingsName = getattr(self.parHandle, curModuleName)['settings']['settingsName']
            if not(moduleName in self.settings[module][moduleName]):
                # TODO: Settings
                self.settings[module][moduleName][moduleSettingsName] = \
                    deepcopy(getattr(self.parHandle, curModuleName)['settings'])

        QtWidgets.QDialog.__init__(self, parHandle)
        self.uiSettings = Ui_SettingsWindow()
        self.uiSettings.setupUi(self)

        self.uiSettingsDyn = dict()
        self.uiSettingsDyn['exercise'] = dict()
        self.uiSettingsDyn['generator'] = dict()
        self.uiSettingsDyn['preprocessor'] = dict()
        self.uiSettingsDyn['player'] = dict()

        # connect functions to static fields (as defined in SettingsDialog.ui/SettingsDialog.py)
        modes = ['exercise', 'generator', 'preprocessor', 'player']
        for mode in modes:
            Mode = mode[0].upper() + mode[1:]
            curModule = 'cur' + Mode
            setattr(self.uiSettings, 'gridLayout'+Mode,
                QtWidgets.QGridLayout(getattr(self.uiSettings,'gb' + Mode + 'Settings')))
            getattr(self.uiSettings, 'gridLayout'+Mode).setObjectName("dynamicGrid")

            self.iniGui(mode=mode)
            curModuleName = getattr(self.parHandle, curModule)['settings'][mode + 'Name']
            curModuleSettingsName = getattr(self.parHandle, curModule)['settings']['settingsName']
            self.readlCurrentSettings(mode, curModuleName, curModuleSettingsName)

            self.updateGui(mode=mode, curModName=curModuleName, curModSettings=curModuleSettingsName)

            getattr(self.uiSettings, 'pb' + Mode + 'OK').clicked.connect(self.ok)
            getattr(self.uiSettings, 'pb' + Mode + 'Cancel').clicked.connect(self.cancel)

            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentIndexChanged.connect(self.openSettings)

            getattr(self.uiSettings, 'pb' + Mode + 'New').clicked.connect(self.new)
            getattr(self.uiSettings, 'pb' + Mode + 'SaveAs').clicked.connect(self.saveAs)
            getattr(self.uiSettings, 'pb' + Mode + 'SaveAll').clicked.connect(self.saveAll)
            getattr(self.uiSettings, 'pb' + Mode + 'Save').clicked.connect(self.save)

            getattr(self.uiSettings, 'pb' + Mode + 'Reset').clicked.connect(self.reset)
            getattr(self.uiSettings, 'pb' + Mode + 'Reload').clicked.connect(self.reload)

            getattr(self.uiSettings, 'pb' + Mode + 'SyncToExer').clicked.connect(self.syncToExer)
            getattr(self.uiSettings, 'pb' + Mode + 'SyncFromExer').clicked.connect(self.syncFromExer)

            getattr(self.uiSettings, 'cb' + Mode + 'Name').currentIndexChanged.connect(self.moduleSelection)

        self.uiSettings.twSettings.tabBarClicked.connect(self.tabChange)


        currentIndex = self.uiSettings.twSettings.currentIndex()
        self.lastModuleTab = self.uiSettings.twSettings.widget(currentIndex).objectName()
        # will be used to reset the standard palette after highlighting wrong entries in self.validateEntries
        #self.stdPalette = QtGui.QPalette()

        self.currentWidget = None

        self.parHandle.dPrint('Leaving __init__()', 2)


    def __enter__(self):
        """!
        This function is doing nothing but to return self. It allows the initialzation of the class with "with" a
        content manager in python.
        """

        return self


    def __exit__(self):
        """!
        The destructor __del__ is avoided, since it is called at undefined times/before or after the destruction of
        other classes.
        """

        self.parHandle.dPrint('__exit__()', 2)
        self.parHandle.dPrint('Leaving __exit__()', 2)
        self.close()

        self.parHandle.settingsDLGHandle = None


        return True


    def moduleSelection(self, event, mode=''):
        """!
        This function initializes the module with default settings, the new gui is generated
        with self.iniGui() and the fields are filled with self.updateGui()

        The function is connected to cbExerciseName, cbGeneratorName, cbPreprocessorName, cbPlayerName.
        """

        self.parHandle.dPrint('moduleSelection()', 2)

        sendersName = self.parHandle.sender().objectName()
        if mode == '':
            if sendersName == 'cbExerciseName':
                mode = 'exercise'
            elif sendersName == 'cbGeneratorName':
                mode = 'generator'
            elif sendersName == 'cbPreprocessorName':
                mode = 'preprocessor'
            elif sendersName == 'cbPlayerName':
                mode = 'player'

        Mode = mode[0].upper() + mode[1:]
        curMode = 'cur' + Mode
        curModuleLabel = getattr(self.uiSettings, sendersName).currentText()

        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'

        listLabels = self.parHandle.frameWork['settings']['access'][tempMode]['main']['available']['labels']
        listNames = self.parHandle.frameWork['settings']['access'][tempMode]['main']['available']['names']

        if curModuleLabel in listLabels:
            curModuleName = listNames[listLabels.index(curModuleLabel)]
        else:
            curModuleName = ''

        if mode == 'exercise':
            #initialize submodule with default settings
            self.parHandle.iniExercise(curModuleName)
        else:
            self.parHandle.iniSubmodule(mode, curModuleName)

        curModuleSettingsName = getattr(self.parHandle, curMode)['settings']['settingsName']
        self.iniGui(mode)
        self.readlCurrentSettings(mode, curModuleName, curModuleSettingsName)
        self.updateGui(mode, curModuleName, curModuleSettingsName)

        setattr(self, 'prev' + Mode + 'Name', curModuleName)
        setattr(self, 'prev' + Mode + 'Settings', curModuleSettingsName)

        self.parHandle.dPrint('leaving moduleSelection()', 2)


    def settingsChanged(self, mode = '', label = '', changeByOpening = False):
        """!
        This function handles the reinitialization of the module if the settings have been changed.
        It is called if the module settings are changed in self.reload(), self.openSettings(),
        self.subModuleSelection() and self.reset() or if a parameter is changed withhin a field of the dynamically
        produced setting fields.

        mode    default '':   defines which settings have to be loaded.
        label   default '':   the label of the settings can be passed to define a setting. Otherwise it is extracted from
                                the modules settings combo box.

        The settings is loaded by calling the CICoachLab ini function with the setting as parameter if possible.
        """

        self.parHandle.dPrint('settingsChanged(): ' + mode, 2)
        self.currentWidget= self.parHandle.sender().objectName()
        if mode == '':
            if mode == '':
                sendersName = self.parHandle.sender().parent().objectName()
                if sendersName == 'gbExerciseSettings':
                    mode = 'exercise'
                elif sendersName == 'gbGeneratorSettings':
                    mode = 'generator'
                elif sendersName == 'gbPreprocessorSettings':
                    mode = 'preprocessor'
                elif sendersName == 'gbPlayerSettings':
                    mode = 'player'

        if not(changeByOpening):
            self.checkSettingsChanged(mode=mode)

        Mode = mode[0].upper()+mode[1:]

        self.setSettings(None, mode=mode)

        curSettingsName = self.getCurrentSettingsName(mode)

        getattr(self.uiSettings,'lb' + Mode + 'SettingsName').setText(curSettingsName)

        moduleName = getattr(self.parHandle, 'cur' + Mode)['settings'][mode + 'Name']
        if label:
            self.settings[mode][moduleName][curSettingsName]['settingsSaved'] = False


        self.update()
        self.currentWidget = None
        self.parHandle.dPrint('Leaving settingsChanged(): ' + mode, 2)


    def readlCurrentSettings(self, mode, curModuleName, settingsName):
        """!
        This functions loads the settings of the module into self.settings.

        mode: exercise, generator, preprocessor, player
        """

        self.parHandle.dPrint('readlCurrentSettings(): ' + mode, 2)

        Mode = mode[0].upper() + mode[1:]
        curMode = 'cur' + Mode

        if not mode in self.settings:
            self.settings[mode] = dict()
        if not (curModuleName in self.settings[mode]):
            self.settings[mode][curModuleName] = dict()
        # without deepcopy funny things happened
        self.settings[mode][curModuleName][settingsName] = deepcopy(getattr(self.parHandle, curMode)['settings'])

        self.parHandle.dPrint('Leaving readlCurrentSettings(): ' + mode, 2)


    def iniGui(self, mode):
        """!
        This function generates the dynamic setting fields depending on the chosen module and instance.
        The fields are generated according to the settingLimits of the module.
        """


        self.parHandle.dPrint('iniGui(): ' + mode, 2)

        Mode = mode[0].upper()+mode[1:]
        curMode = 'cur' + Mode

        # TODO: Settings
        modName = getattr(self.parHandle, curMode)['settings'][mode+'Name']

        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'

        modulesListLabels = [''] + self.parHandle.frameWork['settings']['access'][tempMode]['main'][
            'displayed']['labels']

        getattr(self.uiSettings, 'cb' + Mode + 'Name').blockSignals(True)
        getattr(self.uiSettings, 'cb' + Mode + 'Name').clear()

        getattr(self.uiSettings, 'cb' + Mode + 'Name').setEditable(True)
        getattr(self.uiSettings, 'cb' + Mode + 'Name').lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        # getattr(self.uiSettings, 'cb' + Mode + 'Name').setEditable(False)
        getattr(self.uiSettings, 'cb' + Mode + 'Name').addItems(modulesListLabels)
        getattr(self.uiSettings, 'cb' + Mode + 'Name').blockSignals(False)

        # deleting old dynamic fields of this mode
        for item in self.uiSettingsDyn[mode]:
            self.uiSettingsDyn[mode][item].deleteLater()
        self.uiSettingsDyn[mode].clear()

        # check if a submodule/module is undefined
        if not(modName):
            self.parHandle.dPrint('Leaving iniGui(): ' + mode + 'submodule/module is undefined', 0)
            return

        settingsListLabels = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
            modName]['displayed']['labels']

        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(True)
        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').clear()

        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').addItem('')
        for item in settingsListLabels:
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').addItem(item)
        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').addItem('default')
        #getattr(self.uiSettings,'cb' + Mode + 'SettingsName').addItem(_translate("SettingsDialog", "New entry ...", 'None'))
        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(False)

        settingLimits = getattr(self.parHandle, curMode)['settingLimits']

        # generating (new) dynamic fields
        for dynItem in settingLimits:
            if not( dynItem in [mode+'Name', 'settingsName'] ):
                if not('displayed' in settingLimits[dynItem]) or settingLimits[dynItem]['displayed']:
                    #getattr(self.parHandle, curMode)['settingLimits']['phonemes']['']
                    label = QtWidgets.QLabel(getattr(self.uiSettings,'gb' + Mode + 'Settings'))
                    self.uiSettingsDyn[mode][dynItem+'Label'] =  label
                    if settingLimits[dynItem]['label']:
                        label.setText(settingLimits[dynItem]['label'])
                    else:
                        label.setText(dynItem)
                    if settingLimits[dynItem]['toolTip']:
                        label.setToolTip(settingLimits[dynItem]['toolTip'])
                    if dynItem in ['generator', 'generatorSettings', 'preprocessor',
                                 'preprocessorSettings', 'player', 'playerSettings']:

                        self.uiSettingsDyn[mode][dynItem + 'Entry'] = QtWidgets.QComboBox(
                            getattr(self.uiSettings,'gb' + Mode + 'Settings'))
                        self.uiSettingsDyn[mode][dynItem + 'Entry'].setObjectName(dynItem + 'Entry')
                        self.uiSettingsDyn[mode][dynItem + 'Entry'].currentIndexChanged.connect(
                            lambda: self.subModuleSelection(mode, dynItem))
                    else:
                        try:
                            if settingLimits[dynItem]['displayed']:
                                # handling special case if different type options are possible
                                if (isinstance(settingLimits[dynItem]['comboBoxStyle'], bool)  and \
                                    settingLimits[dynItem]['comboBoxStyle'] and not(settingLimits[dynItem]['function']))or \
                                        (isinstance(settingLimits[dynItem]['comboBoxStyle'], list) and
                                            any(settingLimits[dynItem]['comboBoxStyle']) ):
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'] = QtWidgets.QComboBox(
                                        getattr(self.uiSettings,'gb' + Mode + 'Settings'))
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setObjectName(dynItem + 'Entry')
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].currentIndexChanged.connect(
                                        self.checkSettingsChanged)
                                    self.currentWidget = self.uiSettingsDyn[mode][dynItem + 'Entry']
                                elif settingLimits[dynItem]['function']:
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'] = QtWidgets.QLabel()
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setObjectName(dynItem + 'Entry')
                                    #self.uiSettingsDyn[mode][dynItem + 'Entry'].setStyleSheet(
                                    #    QtWidgets.QFrame.Panel |  QtWidgets.QFrame.Sunken|
                                    #    'background-color: rgb(0, 0, 0);\nborder-color: rgb(255, 255, 255);'
                                    #)
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setStyleSheet(
                                        'background-color: rgb(0, 0, 0);\nborder-color: rgb(255, 255, 255);'
                                    )
                                    functionHandle = settingLimits[dynItem]['function']
                                    self.parHandle.clickable(self.uiSettingsDyn[mode][dynItem + 'Entry']).connect(
                                        functionHandle)
                                else:
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'] = QtWidgets.QLineEdit()
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setObjectName(dynItem + 'Entry')
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].editingFinished.connect(self.settingsChanged)
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].installEventFilter(self)

                                    self.currentWidget = self.uiSettingsDyn[mode][dynItem + 'Entry']

                                    # define input checks
                                    if settingLimits[dynItem]['type'] in ['int', 'float']:
                                        # first guess for convertFunc
                                        convertFunc = float
                                        if settingLimits[dynItem]['type'] == 'int':
                                            convertFunc = int

                                        if settingLimits[dynItem]['listStyle']:
                                            validator = Validators.NumberListValidator(inputRange=settingLimits[dynItem]['range'],
                                                                        convertFunc=convertFunc, comboStyle=False)
                                        else:
                                            #
                                            validator = Validators.NumberValidator(inputRange=settingLimits[dynItem]['range'],
                                                                        convertFunc=convertFunc, comboStyle=False)

                                            # validator.setRange(range)
                                            #self.lineEdit1.setValidator(validator)
                                            #validator.setRange(settingLimits[dynItem]['range'])
                                    elif settingLimits[dynItem]['type'] == 'bool':
                                        if settingLimits[dynItem]['listStyle']:
                                            validator = Validators.BoolListValidator()
                                        else:
                                            validator = Validators.BoolValidator()
                                    elif settingLimits[dynItem]['type'] == 'string':
                                        if settingLimits[dynItem]['listStyle']:
                                            validator = Validators.StringListValidator(inputRange=settingLimits[dynItem]['range'])
                                        else:
                                            validator = Validators.StringValidator(inputRange=settingLimits[dynItem]['range'])

                                    elif isinstance(settingLimits[dynItem]['type'], list):

                                        #(type, listStyle = None, inputRange=None, convertFunc=None, comboStyle=None)
                                        validator = Validators.AnyValidator(type=settingLimits[dynItem]['type'],
                                                                listStyle=settingLimits[dynItem]['listStyle'],
                                                                inputRange=settingLimits[dynItem]['range'],
                                                                convertFunc=None,
                                                                comboStyle=settingLimits[dynItem]['comboBoxStyle'])

                                    validator.validationChanged.connect(self.markGuiFieldState)
                                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setValidator(validator)
                        except:
                            # this exception might occur if the settingLimits are not not generated with
                            #   self.(parHandle.).setSettingLimitsTemplate(). Required field entries might not exist.
                            msg = _translate("SettingsDialog",
                                    'Error during check of input. Please contact you administatrator.', None)
                            self.parHandle.dPrint(msg, 0, guiMode=True)
        self.currentWidget = None

        self.parHandle.dPrint('Leaving iniGui(): ' + mode, 2)


    def eventFilter(self, source, event):
        """!
        The eventfilter is defined for the events of the SettingsDialog widget which allows to determine and store the
        currently selected widget.
        """

        self.currentWidget = source

        return super(SettingsDialogCall, self).eventFilter(source, event)


    def updateGui(self, mode, curModName='', curModSettings=''):
        """!
        This function fills the settings fields and combo boxes. For the


        A 'default' entry will be added to the combo box of the modules fields of the
        generator, preprocessor and player even though a setting file
        probably does not exist. This should define an obvious way to set the default settings.

        The presented modules and settings are extracted from access filter, as it is defined in filter.ini.

        Added settings are added to the acces filter definition. The writeback to filter.ini will be handled by the
        CICoachLab. (TODO: Yet to be done)
        """

        self.parHandle.dPrint('updateGui(): ' + mode, 2)

        Mode = mode[0].upper()+mode[1:]
        curMode = 'cur' + Mode


        #TODO: settings
        if not(curModName):
            curModName = getattr(self.parHandle, curMode)['settings'][mode+'Name']
        # check if a submodule/module is undefined
        if not(curModName):
            self.parHandle.dPrint('Leaving updateGui(): ' + mode + 'submodule/module is undefined', 0)
            return
        if curModSettings:
            curModSettings = getattr(self.parHandle, curMode)['settings']['settingsName']

        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'

        getattr(self.uiSettings,'lb' + Mode + 'Name').setText(curModName)
        getattr(self.uiSettings, 'lb' + Mode + 'SettingsName').setText(curModSettings)

        modulesListLabels = self.parHandle.frameWork['settings']['access'][tempMode]['main'][
            'displayed']['labels']
        modulesListNames = self.parHandle.frameWork['settings']['access'][tempMode]['main'][
            'displayed']['names']
        settingsListLabels = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
            curModName]['displayed']['labels']
        settingsListNames = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
            curModName]['displayed']['names']

        if curModName in modulesListNames:
            index = modulesListNames.index(curModName)
            curModLabel = modulesListLabels[index]
        else:
            curModLabel = ''

        index = getattr(self.uiSettings, 'cb' + Mode + 'Name').findText(curModLabel)
        if index > -1:
            getattr(self.uiSettings, 'cb' + Mode + 'Name').blockSignals(True)
            getattr(self.uiSettings, 'cb' + Mode + 'Name').setCurrentIndex(index)
            getattr(self.uiSettings, 'cb' + Mode + 'Name').blockSignals(False)
        if curModSettings in settingsListNames or curModSettings == 'default':
            if curModSettings == 'default':
                index = getattr(self.uiSettings,'cb' + Mode + 'SettingsName').findText('default')
            else:
                indexLabel = settingsListNames.index(curModSettings)
                index = getattr(self.uiSettings,'cb' + Mode + 'SettingsName').findText(settingsListLabels[indexLabel])
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').blockSignals(True)
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').setCurrentIndex(index)
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').blockSignals(False)

        generatorList = \
            self.parHandle.frameWork['settings']['access']['generators']['main']['available']['labels']
        # TODO: settings
        curGeneratorName = self.parHandle.curGenerator['settings']['generatorName']
        if curGeneratorName and curGeneratorName in self.parHandle.frameWork['settings']['access']['generators'] \
                ['settings']:
            generatorSettingsList = self.parHandle.frameWork['settings']['access']['generators'] \
                ['settings'][curGeneratorName]['available']['labels']
        else:
            generatorSettingsList = []

        preprocessorList = \
            self.parHandle.frameWork['settings']['access']['preprocessors']['main']['available'][
                'labels']

        curPreprocessorName = self.parHandle.curPreprocessor['settings']['preprocessorName']
        if curPreprocessorName:
            curPreprocessorSettingsList = \
                self.parHandle.frameWork['settings']['access']['preprocessors'] \
                    ['settings'][curPreprocessorName]['available']['labels']
        else:
            curPreprocessorSettingsList = []


        playerList = self.parHandle.frameWork['settings']['access']['player']['main']['available'][
            'labels']
        # TODO: settings
        curPlayerName = self.parHandle.curPlayer['settings']['playerName']
        if curPlayerName:
            curPlayerSettingsList = self.parHandle.frameWork['settings']['access']['player'] \
                ['settings'][curPlayerName]['available']['labels']
        else:
            curPlayerSettingsList = []

        lineCounter = 0
        rowCounter = 0

        for dynItem in getattr(self.parHandle, curMode)['settingLimits']:
            if not( dynItem in [mode+'Name', 'settingsName'] )\
                    and getattr(self.parHandle, curMode)['settingLimits'][dynItem]['displayed']:
                line = self.uiSettingsDyn[mode][dynItem + 'Entry']
                if dynItem in ['generator', 'generatorSettings',
                               'preprocessor', 'preprocessorSettings',
                               'player', 'playerSettings']:
                    if dynItem == 'generator':
                        moduleList = generatorList
                        curItem = curGeneratorName
                        accessName = dynItem+'s'
                    elif dynItem == 'preprocessor':
                        moduleList = preprocessorList
                        curItem = curPreprocessorName
                        accessName = dynItem+'s'
                    elif dynItem == 'player':
                        moduleList = playerList
                        curItem = curPlayerName
                        accessName = dynItem
                    elif dynItem == 'generatorSettings':
                        moduleList = generatorSettingsList

                        # TODO: settings
                        curItem = self.parHandle.curGenerator['settings']['settingsName']
                        accessName = '' #hsa to be defined dynammically later on
                    elif dynItem == 'preprocessorSettings':
                        moduleList = curPreprocessorSettingsList

                        # TODO: settings
                        curItem = self.parHandle.curPreprocessor['settings']['settingsName']
                        accessName = ''  # hsa to be defined dynammically later on
                    else: #elif dynItem == 'playerSettings':
                        moduleList = curPlayerSettingsList

                        # TODO: settings
                        curItem = self.parHandle.curPlayer['settings']['settingsName']
                        accessName = ''  # hsa to be defined dynammically later on

                    self.updateSubModuleSettings(mode, dynItem, moduleList)

                    curLabel = curItem
                    if dynItem in ['generator', 'preprocessor', 'player']:
                        if curItem in self.parHandle.frameWork['settings']['access'][accessName]['main']['displayed']['names']:
                            idx = self.parHandle.frameWork['settings']['access'][accessName][
                                'main']['displayed']['names'].index(curItem)
                            curLabel = self.parHandle.frameWork['settings']['access'][accessName][
                                'main']['displayed']['labels'][idx]
                    else:
                        # name of module settings:
                        # eg: field 'generatorSettings' or 'playerSettings'
                        name = self.uiSettingsDyn[mode][dynItem + 'Entry'].currentText()
                        # e.g.: generators, player
                        accessName = re.sub('Settings', '', dynItem)
                        if not(accessName == 'player'):
                            accessName = accessName+'s'

                        if name and not(name == 'default'):
                            if curItem in self.parHandle.frameWork['settings']['access'][accessName]['settings'][name][
                                'displayed']['names']:
                                idx = self.parHandle.frameWork['settings']['access'][accessName][
                                    'settings'][name]['displayed']['names'].index(curItem)
                                curLabel = self.parHandle.frameWork['settings']['access'][accessName][
                                    'settings'][name]['displayed']['labels'][idx]
                        elif name == 'default':
                            curLabel = name
                    self.currentWidget = self.uiSettingsDyn[mode][dynItem + 'Entry']
                    index = self.uiSettingsDyn[mode][dynItem + 'Entry'].findText(curLabel)
                    self.uiSettingsDyn[mode][dynItem + 'Entry'].blockSignals(True)
                    self.uiSettingsDyn[mode][dynItem + 'Entry'].setCurrentIndex(index)
                    self.uiSettingsDyn[mode][dynItem + 'Entry'].blockSignals(False)

                else:
                    if isinstance(getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'],str):
                        typeLen = 1
                    else:
                        typeLen = len(getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'])

                    for ii in range(typeLen):
                        if ii == 0 and ii == typeLen - 1:
                            tempType = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type']
                            tempListStyle = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle']
                        else:
                            tempType = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'][ii]
                            tempListStyle = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle'][ii]

                        if tempType == 'string' and\
                                tempListStyle:
                            text = ', '.join(getattr(self.parHandle, curMode)['settings'][dynItem])
                        elif tempType == 'string':
                            text = self.settings[mode][curModName][curModSettings][dynItem]
                        #elif tempType == 'string' and \
                        #        isinstance(self.settings[mode][curModName][curModSettings][dynItem], str):
                        #    text = self.settings[mode][curModName][curModSettings][dynItem]
                        elif tempType == 'int' and \
                            tempListStyle:
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])[1:-1]
                        elif tempType == 'int':
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])
                        elif tempType == 'float' and\
                                tempListStyle:
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])[1:-1]
                        elif tempType == 'float':
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])
                        elif tempType == 'bool' and \
                                tempListStyle:
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])
                        elif tempType == 'bool':
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])
                        else:
                            text = str(self.settings[mode][curModName][curModSettings][dynItem])
                        self.currentWidget = self.uiSettingsDyn[mode][dynItem + 'Entry']
                        line.blockSignals(True)
                        if isinstance(line, QtWidgets.QComboBox):
                            try:
                                setRange = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['range']
                                if setRange:
                                    allItems  = []
                                    for ii in setRange:
                                        if isinstance(ii, str):
                                            entry = ii
                                        else:
                                            entry = str(ii)
                                        line.addItem(entry)
                                        allItems.append(entry)
                                    if not (text in allItems):
                                        msg = _translate("SettingsDialog", 'This should not happen. '
                                                                           'Could not set settings entry: ',
                                                         None) \
                                              + '\ndynItem:' + dynItem + '\nentry: ' + text + '\nsetRange:' + str(setRange)
                                        self.parHandle.dPrint(msg, 0, guiMode=True)
                                line.setCurrentText(text)
                            except:
                                self.parHandle.dPrint('Could not set combobox entry. value: '
                                                      + text + ' for ' + dynItem + ' entries: ' +  str(setRange),
                                                      0,  guiMode=True)
                        else:
                            line.setText(text)
                        line.blockSignals(False)

                getattr(self.uiSettings, 'gridLayout' + Mode).addWidget(self.uiSettingsDyn[mode][dynItem+'Label'],
                                                                      lineCounter, rowCounter, 1, 1)
                getattr(self.uiSettings, 'gridLayout' + Mode).addWidget(self.uiSettingsDyn[mode][dynItem+'Entry'],
                                                                      lineCounter, rowCounter + 1, 1, 1)

                lineCounter = lineCounter + 1
                if lineCounter > 6:
                    lineCounter = 0
                    rowCounter = rowCounter + 2

        self.currentWidget = None

        self.parHandle.dPrint('Leaving updateGui(): ' + mode, 2)

    def updateSubModuleSettings(self, mode, dynItem, moduleList):

        self.uiSettingsDyn[mode][dynItem + 'Entry'].blockSignals(True)
        if self.uiSettingsDyn[mode][dynItem + 'Entry'].count() > 0:
            for item in range(self.uiSettingsDyn[mode][dynItem + 'Entry'].count()):
                self.uiSettingsDyn[mode][dynItem + 'Entry'].removeItem(0)

        #if self.uiSettingsDyn[mode][dynItem + 'Entry'].count() == 0:
        # self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem('')
        if -1 == self.uiSettingsDyn[mode][dynItem + 'Entry'].findText('default'):
            self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem('')
            if dynItem in ['generatorSettings',
                           'preprocessorSettings',
                           'playerSettings']:
                self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem('default')

        if isinstance(moduleList, str):
            self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem(moduleList)
        else:
            for item in moduleList:
                self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem(item)
        # self.uiSettingsDyn[mode][dynItem + 'Entry'].addItem(_translate("SettingsDialog", "New entry ...", 'None'))

        self.uiSettingsDyn[mode][dynItem + 'Entry'].blockSignals(False)


    def tabChange(self):
        """!
        This function is called if the tab is changed.
        """

        self.parHandle.dPrint('tabChange()', 2)

        mPos = QtGui.QCursor.pos()
        mPosInTabBar = self.uiSettings.twSettings.tabBar().mapFromGlobal(mPos)

        ch = self.uiSettings.twSettings.children()
        tabIndex = -1
        for ii in range(self.uiSettings.twSettings.tabBar().count()):
            if self.uiSettings.twSettings.tabBar().tabRect(ii).contains(mPosInTabBar):
                tabIndex = ii

        if tabIndex >= 0:
            #print(self.uiSettings.twSettings.widget(tabIndex).objectName())
            #print(self.uiSettings.twSettings.tabBar().tabText(tabIndex))
            objectName = self.uiSettings.twSettings.widget(tabIndex).objectName()

            if objectName == 'twExercise':
                mode = 'exercise'
            elif objectName == 'twGenerator':
                mode = 'generator'
            elif objectName == 'twPreprocessor':
                mode = 'preprocessor'
            elif objectName == 'twPlayer':
                mode = 'player'
            else:
                self.parHandle.dPrint('No tab selected.', 3)
                return

            if self.lastModuleTab == 'twExercise':
                prevMode = 'exercise'
                lastModuleTabIdx = 0
            elif self.lastModuleTab == 'twGenerator':
                prevMode = 'generator'
                lastModuleTabIdx = 1
            elif self.lastModuleTab == 'twPreprocessor':
                prevMode = 'preprocessor'
                lastModuleTabIdx = 2
            elif self.lastModuleTab == 'twPlayer':
                prevMode = 'player'
                lastModuleTabIdx = 3

        if QtGui.QValidator.Invalid == self.validateEntries(prevMode):
            # ask to ignore invalid data in previous modules tab or go back to previous modules tab.


            msgTitle = _translate("SettingsDialog", 'Do you want to continue to next tab?', None)
            msgQuest = _translate("SettingsDialog",
                                  'Invalid data entries have been found.\nDo you want to continue to next tab?', None)
            msgInfo = _translate("SettingsDialog", 'In the previous tab invalid entries have been marked as red\n '
                                 + 'Intermediate entries has been marked orange', None)

            questScreen = QtWidgets.QMessageBox()
            questScreen.setWindowTitle(msgTitle)
            questScreen.setText(msgQuest)
            questScreen.setDetailedText(msgInfo)
            questScreen.addButton(QtWidgets.QMessageBox.Yes)
            questScreen.addButton(QtWidgets.QMessageBox.No)
            answer = questScreen.exec()


            if answer == QtWidgets.QMessageBox.No:
                # going back to previous tab because of invalid data entries
                self.uiSettings.twSettings.setCurrentIndex(lastModuleTabIdx)
                self.parHandle.dPrint('Invalid data entries. Going back to previous modules tab', 0)
            else:
                # change tab despite invalid data entries in previous modules tab.
                self.lastModuleTab = objectName
        else:
            self.lastModuleTab = objectName

        self.parHandle.dPrint('Leaving tabChange()', 2)


    def validateEntries(self, mode=''):
        """!
        This function checks all entries during the saving of settings or closing of the SettingsDialog or changing the
        modules tab.
        It should be called in self.ok, self.save, self.tabChange

        The function returns the state.
        The states are provided as a dictionary where the fieldNames define the field names and the status can be
        QtGui.QValidator.Acceptable, QtGui.QValidator.Intermediate or QtGui.QValidator.Invalid


        """

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseSaveAs':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorSaveAs':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorSaveAs':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerSaveAs':
                mode = 'player'
        Mode = mode[0].upper()+mode[1:]
        curMode = 'cur' + Mode
        settingLimits = getattr(self.parHandle, curMode)['settingLimits']

        stateOutDict = dict()
        stateOutList = []
        stateOut = None
        if not(self.uiSettingsDyn[mode]):
            return stateOut

        if self.uiSettingsDyn:
            for dynItem in settingLimits:
                fieldName = dynItem + 'Entry'
                if fieldName in self.uiSettingsDyn[mode]:
                    # handle different gui widgets
                    if isinstance(self.uiSettingsDyn[mode][fieldName], QtWidgets.QLineEdit):
                        entry = self.uiSettingsDyn[mode][fieldName].text()

                        # check if Validator is set
                        if self.uiSettingsDyn[mode][fieldName].validator():
                            state, entry, index = self.uiSettingsDyn[mode][fieldName].validator().validate(entry, 0)
                            """
                            if not(QtGui.QValidator.Acceptable == state):
                                if QtGui.QValidator.Invalid == state:
                                    color = QtGui.QColor(QtCore.Qt.red)
                                    setBoldFlag = True
                                else:
                                    #orange color
                                    color = QtGui.QColor(255, 130, 0)
                                    setBoldFlag = True
                                pal = QtGui.QPalette()
                                pal.setColor(QtGui.QPalette.Text, color)
                            else:
                                color = QtGui.QColor(QtCore.Qt.black)
                                setBoldFlag = False
                                pal = self.stdPalette


                            myFont = QtGui.QFont()
                            myFont.setBold(setBoldFlag)
                            self.uiSettingsDyn[mode][fieldName].setFont(myFont)
                            self.uiSettingsDyn[mode][fieldName].setPalette(pal)
                            """
                            stateOutDict[fieldName] = state
                            stateOutList.append(state)
                        else:
                            stateOutDict[fieldName] = QtGui.QValidator.Acceptable
                        #QtGui.QValidator.Acceptable, QtGui.QValidator.Intermediate or QtGui.QValidator.Invalid

        if stateOutList:
            stateOut = list(set(stateOutList))[0]

        return stateOut, stateOutDict


    def isTrue(self, x):
        """!
        This function translates a string x, which may contain 'True' or 'False', into its corresponding boolean values.
        """

        if x == 'True':
            y = True
        else:
            y = False
        return  y


    def subModuleSelection(self, mode, module):
        """!
        If a module is selected the module has to be initialized to define available settings.
        During the initialization ta check of the setting might occur which requires the initilization of the
        modules.
        """

        self.parHandle.dPrint('subModuleSelection(): ' + mode, 2)

        objectName = self.parHandle.sender().objectName()
        if objectName == 'generatorEntry' or objectName == 'generatorSettingsEntry':
            mode = 'generator'
        if objectName == 'preprocessorEntry' or objectName == 'preprocessorSettingsEntry':
            mode = 'preprocessor'
        if objectName == 'playerEntry' or objectName == 'playerSettingsEntry':
            mode = 'player'

        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'

        label = self.uiSettingsDyn['exercise'][mode + 'Entry'].currentText()
        settingsLabel = self.uiSettingsDyn['exercise'][mode + 'SettingsEntry'].currentText()
        if label:
            labels = self.parHandle.frameWork['settings']['access'][tempMode]['main']['displayed']['labels']
            if label in labels:
                idx = labels.index(label)
                name = self.parHandle.frameWork['settings']['access'][tempMode]['main']['displayed']['names'][idx]
            else:
                name = self.parHandle.curExercise['settingLimits'][mode]['default']
            if settingsLabel:
                settingLabels = self.parHandle.frameWork['settings']['access'][tempMode][
                    'settings'][name]['displayed']['labels']
                if settingsLabel in settingLabels:
                    idx = settingLabels.index(settingsLabel)
                    settings = self.parHandle.frameWork['settings']['access'][tempMode]['settings'
                    ][name]['displayed']['names'][idx]
                else:
                    if settingsLabel == 'default':
                        settings = 'default'
                    else:
                        if mode in self.parHandle.curExercise['settingLimits']\
                            and 'default' in self.parHandle.curExercise['settingLimits'][mode + 'Settings']:
                            settings = self.parHandle.curExercise['settingLimits'][mode + 'Settings']['default']
                        else:
                            settings = 'default'

                self.parHandle.iniSubmodule(mode,  name, settings)
                self.iniGui(mode=mode)
                self.readlCurrentSettings(mode, name, settings)
                # updating subModule gui
                settings = self.getCurrentSettingsName(mode=mode)
                self.updateGui(mode=mode, curModName=name, curModSettings=settings)
                self.settingsChanged(mode=mode)
                if mode != 'exercise':
                    settingsExercise = self.getCurrentSettingsName(mode='exercise')
                    self.updateGui(mode='exercise', curModName=self.parHandle.curExercise['settings']['exerciseName'], curModSettings=settingsExercise)
                    self.settingsChanged(mode='exercise')
                # updating exerise gui
                curExerciseName = self.parHandle.curExercise['settings']['exerciseName']
                settingsExercise = self.settings['exercise'][curExerciseName]
                self.updateGui(mode='exercise', curModName=curExerciseName, curModSettings=settingsExercise)

        self.parHandle.dPrint('Leaving subModuleSelection(): ' + mode, 2)


    def setSettings(self, event, mode, curSettingsName=''):
        """!
        just a tempory setting, which will be fed to the initilization function of the module, which
        applies the setttings if possible. Checks may be run by the

        If the settings are applied, depends if Ok or cancel or reload buttons are pressed. The settings don't have to be
        saved in a file to be applied for an employment in the ongoing CICoachLab session.
        Reload reloads the selected settings without closing the Dialog.
        To end the Settings dialog Ok applies the settings and Candel reloads the settings from the beginning of the
        Settings dialog.
        New creates a new setting which can be saved under the new setting name.
        For a persistent saving of settings, an application after a restart, the data has to be saved within a file
        with "Save" or "Save as".

        """

        self.parHandle.dPrint('setSettings(): ' + mode, 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseOK':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorOK':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorOK':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerOK':
                mode = 'player'

        Mode = mode[0].upper() + mode[1:]
        curMode = 'cur' + Mode

        # TODO: settings
        moduleName = getattr(self.parHandle, curMode)['settings'][mode + 'Name']
        if not(curSettingsName):
            curSettingsName = self.getCurrentSettingsName(mode)


        # if settings have been changed a new item has to be added in self.settings[mode][moduleName] which is based on
        # on the old settings.
        if '*' in curSettingsName:
            if not(curSettingsName in self.settings[mode][moduleName]):
                self.settings[mode][moduleName][curSettingsName] = \
                    self.settings[mode][moduleName][re.sub('\*','',curSettingsName)]
                self.settings[mode][moduleName][curSettingsName]['settingsName'] = curSettingsName


        for dynItem in getattr(self.parHandle, curMode)['settingLimits']:
            if not( dynItem in [mode + 'Name', 'settingsName'] ) and\
                    getattr(self.parHandle, curMode)['settingLimits'][dynItem]['displayed']:
                line = self.uiSettingsDyn[mode][dynItem + 'Entry']
                if dynItem in ['generator', 'generatorSettings', 'preprocessor',
                               'preprocessorSettings', 'player', 'playerSettings']:
                    entry = line.currentText()
                else:
                    if isinstance(line, QtWidgets.QComboBox):
                        entry = line.currentText()
                    else:
                        entry = line.text()
                try:

                    if getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'string' and \
                            getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle']:
                        # remove white spaces arround coma, concatene
                        self.settings[mode][moduleName][curSettingsName][dynItem] = \
                            "".join(entry.split()).split(',')
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'string':
                        if dynItem in ['generator', 'preprocessor', 'player']:
                            if dynItem == 'generator':
                                accessName = dynItem + 's'
                            elif dynItem == 'preprocessor':
                                accessName = dynItem + 's'
                            else: # dynItem == 'player':
                                accessName = dynItem

                            if entry in self.parHandle.frameWork['settings']['access'][
                                accessName]['main']['displayed']['labels']:
                                idx = self.parHandle.frameWork['settings']['access'][accessName][
                                    'main']['displayed']['labels'].index(entry)
                                entry = self.parHandle.frameWork['settings']['access'][accessName][
                                    'main']['displayed']['names'][idx]
                            elif entry in self.parHandle.frameWork['settings']['access'][accessName][
                                    'main']['displayed']['names']:
                                msg = dynItem + ' was provided as direct name and not as label. Probably causeed by user input. '
                                self.parHandle.dPrint(msg, 0)
                            else:
                                # check for empty fields
                                if entry:
                                    msg = _translate("SettingsDialog",
                                          "Could not find accessible module entry. Please check entry: ", None) + dynItem
                                    self.parHandle.dPrint(msg, 0, guiMode=True)
                        self.settings[mode][moduleName][curSettingsName][dynItem] = entry

                    #elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'string' and \
                    #        isinstance(self.settings[mode][moduleName][curSettingsName][dynItem], str):
                    #    self.settings[mode][moduleName][curSettingsName][dynItem] = entry
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'int' and \
                            getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle']:
                        self.settings[mode][moduleName][curSettingsName][dynItem] =  list(map(int, entry.split(', ')))
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'int':
                        self.settings[mode][moduleName][curSettingsName][dynItem] = int(entry)
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'float' and \
                            getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle']:
                        self.settings[mode][moduleName][curSettingsName][dynItem] = list(map(float, entry.split(', ')))
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'float':
                        self.settings[mode][moduleName][curSettingsName][dynItem] = float(entry)
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'bool' and \
                             getattr(self.parHandle, curMode)['settingLimits'][dynItem]['listStyle']:
                        self.settings[mode][moduleName][curSettingsName][dynItem] = list(
                            map(self.isTrue, entry.split(', ')))
                    elif getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type'] == 'bool':
                        self.settings[mode][moduleName][curSettingsName][dynItem] = 'True' in entry
                    else:
                        self.settings[mode][moduleName][curSettingsName][dynItem] = entry
                except ValueError:
                    tempType = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type']
                    msg = _translate("SettingsDialog",
                            f"Could not convert gui entry into {tempType:s}: {mode:s}>{moduleName:s}>{curSettingsName:s}>{dynItem:s}",
                                     None)
                except:
                    tempType = getattr(self.parHandle, curMode)['settingLimits'][dynItem]['type']
                    msg = _translate("SettingsDialog",
                            f"Unexpected Error: Could not convert gui entry into {tempType:s}: "
                            f"{mode:s}>{moduleName:s}>{curSettingsName:s}>{dynItem:s}",
                                     None)
                    self.parHandle.dPrint(msg, 0, guiMode=True)
        self.settings[mode][moduleName][curSettingsName][mode + 'Name'] = getattr(self.uiSettings, 'lb' + Mode + 'Name').text()


        self.parHandle.dPrint('Leaving setSettings(): ' + mode, 2)


    def checkSettingsChanged(self, event = '', mode=''):
        """!
        The function marks the settings as changed by adding a star to the settings name in the setting list box.

        self.settings[mode][curModuleName][entryName]['settingsSaved'] will be set to False to label the settings.
        self.settings[mode][curModuleName][entryName]['settingsSaved'] will be set to saved if the preset is saved as
        a setting file with self.save()
        """

        self.parHandle.dPrint('checkSettingsChanged run(): ' + mode, 2)

        # get mode if check is initialized by call of user input via widget
        if not(mode):
            if self.parHandle.sender().parent().parent().objectName() == 'twPlayer':
                mode = 'player'
            elif self.parHandle.sender().parent().parent().objectName() == 'twPreprocessor':
                    mode = 'preprocessor'
            elif self.parHandle.sender().parent().parent().objectName() == 'twGenerator':
                    mode = 'generator'
            elif self.parHandle.sender().parent().parent().objectName() == 'twExercise':
                    mode = 'exercise'

        Mode = mode[0].upper() + mode[1:]
        #if not(getattr(self.uiSettings,'lb' + Mode + 'Name').text()[-1] == '*'):
        #    getattr(self.uiSettings,'lb' + Mode + 'Name').setText(getattr(self.uiSettings,'lb' + Mode + 'Name').text()+'*')
        if getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText() and \
                not(getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText()[-1] == '*'):
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').setItemText(
                getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentIndex(),
                getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText()+'*')

        curModuleName = getattr(self.uiSettings, 'lb' + Mode + 'Name').text()
        entryName = self.getCurrentSettingsName(mode)
        entryName = re.sub('\*', '', entryName)
        self.settings[mode][curModuleName][entryName]['settingsSaved'] = False

        self.parHandle.dPrint('Leaving checkSettingsChanged(): ' + mode, 2)


    def ok(self, event, mode=''):
        """!
        This function quits the settingsDialog and it initializes the selected exercise with the defined settings.
        The settings may or may not be saved as a preset file. If unsaved setting have been found, as marked by an
        asterisk, the user will be asked if a preset file should be saved. The submodules will be checked for unsaved
        settings as well and inconsistent selection between exercises and its submodules.
        """

        self.parHandle.dPrint('ok(): ' + mode, 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseOK':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorOK':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorOK':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerOK':
                mode = 'player'

        confirmationFlag = True

        Mode = mode[0].upper() + mode[1:]

        curMode  = 'cur' + Mode

        # check if the settings of the  module are saved
        curModuleName = getattr(self.uiSettings, 'lb' + Mode + 'Name').text()
        #settingsName = getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText()
        settingsName = self.getCurrentSettingsName(mode=mode)
        #if curModuleName[-1] == '*':
        if settingsName[-1] == '*':
            msg = _translate("SettingsDialog",
                 'Unsaved settings were found. Do you want to save the settings as preset?',
                             None)
            msgInfo = _translate("SettingsDialog",
                'If you press "yes" all settings will be saved and applied.\n'
                'If you press "No" the settings will be applied in the next runs but not saved as presets\n'
                'If you press "Cancel" the closing of the Settings dialog will be aborted.', None)

            questScreen = QtWidgets.QMessageBox()
            questScreen.setWindowTitle(_translate("SettingsDialog", 'Save unsaved data?', None))
            questScreen.setText(msg)
            #questScreen.setInformativeText(msgInfo)
            questScreen.setDetailedText(msgInfo)
            #questScreen.setWindowModality(qtc.Qt.WindowModal)
            questScreen.addButton(QtWidgets.QMessageBox.Yes)
            questScreen.addButton(QtWidgets.QMessageBox.No)
            questScreen.addButton(QtWidgets.QMessageBox.Abort)
            answer = questScreen.exec()



            if answer == QtWidgets.QMessageBox.Yes:
                self.save(mode)
                self.parHandle.dPrint("Saving of settings: " + mode, 0)
            if answer == QtWidgets.QMessageBox.Abort:
                self.parHandle.dPrint("Staying in Settings Dialog: " + mode, 0)
                confirmationFlag = False
            if answer == QtWidgets.QMessageBox.No:
                self.parHandle.dPrint("Applying settings without saving: " + mode, 0)
            # check if the data has been saved successfully, indicatey by a missing asterix
            curModuleName = getattr(self.uiSettings, 'lb' + Mode + 'Name').text()

        # check if the settings of the  submodule are saved and synchronized
        if mode == 'exercise' and confirmationFlag:
            subModes = ['generator', 'preprocesor', 'player']
            unSavedModules = []
            unSynchedModules = []

            for subMode in subModes:
                bigSubMode = subMode[0].upper() + subMode[1:]
                #if hasattr(self.uiSettings, 'lb' + bigSubMode + 'Name'):
                #    if getattr(self.uiSettings, 'lb' + bigSubMode + 'Name').text()[-1] == '*':
                if hasattr(self.uiSettings, 'cb' + bigSubMode + 'SettingsName'):
                    if getattr(self.uiSettings, 'cb' + bigSubMode + 'SettingsName').currentText() and \
                        getattr(self.uiSettings, 'cb' + bigSubMode + 'SettingsName').currentText()[-1] == '*':
                        unSavedModules.append(subMode)

            if unSavedModules:
                msg = _translate("SettingsDialog",
                                 'Unsaved sub settings have been found. Do you want to save the settings as presets?',
                                 None)
                msgInfo = _translate("SettingsDialog",
                                     'If you press "yes" all settings will be saved and applied.\n'
                                     'If you press "No" the old settings will be applied.\n'
                                     'If you press "Cancel" the closing of the Settings dialog will be aborted.',
                                     None)

                questScreen = QtWidgets.QMessageBox()
                questScreen.setWindowTitle(_translate("SettingsDialog",'Save unsaved data?', None))
                questScreen.setText(msg)
                # questScreen.setInformativeText(msgInfo)
                questScreen.setDetailedText(msgInfo)
                # questScreen.setWindowModality(qtc.Qt.WindowModal)
                questScreen.addButton(QtWidgets.QMessageBox.Yes)
                questScreen.addButton(QtWidgets.QMessageBox.No)
                questScreen.addButton(QtWidgets.QMessageBox.Abort)
                answer = questScreen.exec()

                if answer == QtWidgets.QMessageBox.Yes:
                    self.parHandle.dPrint("Saving of settings: " + mode, 0)
                    for subMode in unSavedModules:
                        self.save(subMode)
                if answer == QtWidgets.QMessageBox.Abort:
                    self.parHandle.dPrint("Staying in settings dialog: ", 0)
                    confirmationFlag = False
                if answer == QtWidgets.QMessageBox.No:
                    self.parHandle.dPrint("Leaving Settings dialog without saving settings: ", 0)
                    confirmationFlag = False
                    self.cancel(None, mode=mode)

            if confirmationFlag:
                for subMode in subModes:
                    bigSubMode = subMode[0].upper() + subMode[1:]
                    if hasattr(self.uiSettingsDyn, subMode):
                        if not(getattr(self.uiSettingsDyn, subMode).currentText() ==
                                getattr(self.uiSettings, 'cb' + bigSubMode + 'Name').currentText()):
                            unSynchedModules.append(subMode)
                if unSynchedModules:
                    msg = _translate("SettingsDialog",
                                     'Unsynched sub settings have been found. Do you want to sync the sub settings?',
                                     None)
                    msgInfo = _translate("SettingsDialog",
                                         'If you press "yes" all settings will be synced and applied.\n'
                                         'If you press "No" the settings cannot be applied and old settings will be reloaded.\n'
                                         'If you press "Cancel" the closing of the Settings dialog will be aborted.',
                                         None)
                    questScreen = QtWidgets.QMessageBox()
                    questScreen.setWindowTitle(_translate("SettingsDialog",'Sync modules?', None))
                    questScreen.setText(msg)
                    # questScreen.setInformativeText(msgInfo)
                    questScreen.setDetailedText(msgInfo)
                    # questScreen.setWindowModality(qtc.Qt.WindowModal)
                    questScreen.addButton(QtWidgets.QMessageBox.Yes)
                    questScreen.addButton(QtWidgets.QMessageBox.No)
                    questScreen.addButton(QtWidgets.QMessageBox.Abort)
                    answer = questScreen.exec()

                    if answer == QtWidgets.QMessageBox.Yes:
                        self.parHandle.dPrint("Saving of settings: " + mode, 0)
                        for subMode in unSavedModules:
                            self.save(subMode)
                    if answer == QtWidgets.QMessageBox.Abort:
                        self.parHandle.dPrint("Staying in settings dialog: ", 0)
                        confirmationFlag = False
                    if answer == QtWidgets.QMessageBox.No:
                        self.parHandle.dPrint("Leaving Settings dialog without saving settings: ", 0)
                        confirmationFlag = False
                        self.cancel(None, mode=mode)
                        self.setSettings(None, mode=mode, curSettingsName=settingsName)

        # every check has been passed and confirmed
        if confirmationFlag:
            curModuleSettingsLabel = getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText()
            if curModuleSettingsLabel:
                if mode == 'player':
                    tempMode = mode
                else:
                    tempMode = mode + 's'
                if curModuleSettingsLabel == 'default':
                    curModuleSettingsName = curModuleSettingsLabel
                else:
                    curModuleSettingsName = self.getCurrentSettingsName(mode)
                    #curModuleSettingsName =names[labels.index(curModuleSettingsLabel)]
                curModuleSettings = self.settings[mode][curModuleName][curModuleSettingsName]

                #TODO: get right settings
                if mode == 'exercise':
                    getattr(self.parHandle, 'iniExercise')(curModuleName, curModuleSettings)
                else:
                    getattr(self.parHandle, 'iniSubmodule')(mode, curModuleName, curModuleSettings)

                currentDifficulty = self.parHandle.user['difficulty']
                # self.newEntries[mode][curModuleName].append(entryName)
                for mode in self.newEntries:
                    for module in self.newEntries[mode]:
                        for entry in self.newEntries[mode][module]:
                            # add entry to filterConfig for writing new filter.ini if the presets have been saved.
                            # only saved presets will be added to filter.ini, because ist is the source for the generatiion for
                            # the preset selection .
                            # unsaved preset.
                            if self.settings[mode][module][entry]['settingsSaved']:
                                msg = _translate("SettingsDialog",'Adding entry to filter.ini:', None)
                                self.parHandle.dPrint(msg, 0)
                                self.parHandle.frameWork['settings']['filterFileConfig']
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module]
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'names'].append(entry)
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'labels'].append(entry)
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'difficulties'].append(currentDifficulty)
                                infos = self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'infos']
                                infos = infos + "\'\'\',\'\'\'User defined setting"
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'infos'] = infos
                                self.parHandle.frameWork['settings']['filterFileConfig'][tempMode]['settings'][module][
                                    'visibles'].append('True')
                                """
                                # filterConfig[exercises][settings]['confusionMatrix']['names']
                                names = All - Phonemes, ShortCM, All - Copy
                                labels = Großes Set, Demo Set, Demo Set All
                                difficulties = 5, 3, 1
                                infos = '''Lang und schwierig''', '''Kurz und einfach''', '''Kalibrierung'''
                                visibles = True, True, True
                                """
            else:
                self.parHandle.dPrint(_translate("SettingsDialog",'Leaving without saving and application of setting: ',
                                                 None) + mode, 0, guiMode=True)

            #    getattr(self.parHandle, 'ini' + Mode)(curModuleSettingsName)
            self.parHandle.dPrint('Leaving ok() before exit call: ' + mode, 2)

            self.__exit__()

        self.parHandle.dPrint('Leaving ok(): ' + mode, 2)


    def cancel(self, event, mode=''):
        """!
        This function quits the settingsDialog and it reloads the exercise and its settings at the startup of the
        Settings Dialog.

        The mode is not required and only serves for the documentation of the calling gui object
        """
        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseCancel':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorCancel':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorCancel':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerCancel':
                mode = 'player'

        self.parHandle.dPrint('cancel(): ' + mode, 2)

        self.parHandle.iniSubmodule('generator',  self.oldGeneratorName, self.oldGeneratorSettings)
        self.parHandle.iniSubmodule('preprocessor',  self.oldPreprocessorName, self.oldPreprocessorSettings)
        self.parHandle.iniSubmodule('player',  self.oldPlayerName, self.oldPlayerSettings)

        self.parHandle.iniExercise(self.oldExerciseName, self.oldExerciseSettings)

        self.parHandle.dPrint('Leaving cancel(): ' + mode, 2)

        self.__exit__()


    def saveAs(self, event, mode = ''):
        """!
        The current setting is saved under a new preset name. The name will be asked for.
        """

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseSaveAs':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorSaveAs':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorSaveAs':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerSaveAs':
                mode = 'player'

        Mode = mode[0].upper() + mode[1:]


        # TODO: add new setting file to filter.ini if it does not exist already?
        self.parHandle.dPrint('saveAs()', 2)

        Mode = mode[0].upper() + mode[1:]
        ii = 0
        maxTrials = 5
        filename = 'default'
        while 'default' in  filename or 'Default' in filename:
            if ii > 0:
                self.parHandle.dPrint(_translate("SettingsDialog",
                    "'default' is not a valid preset/filename. Please enter a valid filename.", None
                    ), 0, guiMode=True)
            if ii < maxTrials:
                filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                    self,
                    _translate("SettingsDialog", "Saving of ", None) + mode + ' ' +
                        _translate("SettingsDialog", "settings ...", None),
                    getattr(self.parHandle, 'cur' + Mode)['path']['presets'],
                    _translate("SettingsDialog", 'Settings file', None) + ' (*.set) ;;'+
                    _translate("SettingsDialog", 'All files', None)+ ' (*)',
                    _translate("SettingsDialog", 'Settings file', None) + ' (*.set)',
                    QtWidgets.QFileDialog.DontUseNativeDialog
                )
            else:
                self.parHandle.dPrint(_translate("SettingsDialog",
                     "The maximum number of trials was reached and the filename selection is canceled.", None
                     ), 0, guiMode=True)
                filename = ''
                return
            ii = ii + 1
        if filename:
            # check if extension should be added
            if not('.set' in filename):
                filename = filename + '.set'
            filenamebase = os.path.basename(filename).split('.')[0]

            #curSettingsName = self.getCurrentSettingsName(mode)


            # TODO: settings
            moduleName = getattr(self.parHandle, 'cur' + Mode)['settings'][mode + 'Name']

            """
            if not mode in self.settings:
                self.settings[mode] = dict()
            if not(curModuleName in self.settings[mode]):
                self.settings[mode][moduleName] = dict()
            if not(filenamebase in self.settings[mode][curModuleName]):
                self.settings[mode][moduleName][filenamebase] = dict()
                
            self.settings[mode][moduleName][filenamebase]['settingsName'] = filenamebase
            """
            self.addNewItem(mode, entryName=filenamebase)
            self.save(None, mode, filename)



        self.parHandle.dPrint('Leaving addNewItem()', 2)


    def addNewItem(self, mode, entryName):
        """!
        This function adds a new entry to the settings box if it is a unique entry.

        The new item is added to the access filter as defined in filter.ini.
        As base for the new filter entry the previous displayed (or the last in rare cases) item is taken.
        For finetuning filter.ini has to be edited.

        A new settings entry is created based on the last setting.
        """

        self.parHandle.dPrint('addNewItem()', 2)

        Mode = mode[0].upper() + mode[1:]

        # add new name to combo box
        if getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').findText(entryName) == -1:
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(True)
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').addItem(entryName)
            index = getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').findText(entryName)
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').setCurrentIndex(index)
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(False)

        #add new name to access filter
        # move to other place, where item is added to combo box
        curModuleName = getattr(self.parHandle, 'cur' + Mode)['settings'][mode + 'Name']
        curModuleSettings = getattr(self.parHandle, 'cur' + Mode)['settings']
        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'

        prevModName = getattr(self,'prev' + Mode + 'Name')
        prevModSettingsName = getattr(self, 'prev' + Mode + 'Settings')
        if prevModSettingsName == 'default' or not(prevModSettingsName in
                self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']['names']):
            idx = -1
        else:
            idx = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']['names'].index(prevModSettingsName)

        if idx < 0:
            for item in self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']:
                if item  == 'visibles':
                    entry = True
                else:
                    entry, okPressed = QtWidgets.QInputDialog.getText(self,
                                            _translate("SettingsDialog", "Enter new field entries", None),
                                            _translate("SettingsDialog", "New entry ", None) + '[' + item + ']:'
                                            , QtWidgets.QLineEdit.Normal, "")
                    if not(okPressed) or not(entry):
                        entry = entryName
                if item == 'filterDefinition':
                    if entry == 'False':
                        entry = False
                    else:
                        entry = True
                self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                    curModuleName]['displayed'][item].append(entry)
                self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                    curModuleName]['available'][item].append(entry)
        else:
            for item in self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']:
                entry  = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                    curModuleName]['displayed'][item][idx]
                if item == 'names' or item == 'labels':
                    entry = entryName
                self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                    curModuleName]['displayed'][item].append(entry)
                self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                    curModuleName]['available'][item].append(entry)
        if isinstance(prevModSettingsName, str):
            self.settings[mode][curModuleName][entryName] = self.settings[mode][curModuleName][prevModSettingsName]
        else:
            self.settings[mode][curModuleName][entryName] = prevModSettingsName
        self.settings[mode][curModuleName][entryName]['settingsName'] = entryName
        self.settings[mode][curModuleName][entryName]['settingsSaved'] = False

        setattr(self, 'prev' + Mode + 'Name', curModuleName)
        setattr(self, 'prev' + Mode + 'Settings', self.settings[mode][curModuleName][entryName]['settingsName'])

        if not(mode in self.newEntries):
            self.newEntries[mode] = dict()
        if not (curModuleName in self.newEntries[mode]):
            self.newEntries[mode][curModuleName] = list()

        self.newEntries[mode][curModuleName].append(entryName)

        self.parHandle.dPrint('Leaving addNewItem()', 2)


    def save(self, event, mode='', filename=''):
        """!
        mode defines a single module. It can be:

        exercise
        generator
        preprocessor
        player
        """

        self.parHandle.dPrint('save(): ' + mode, 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName in ['pbExerciseSave', 'pbExerciseOK']:
                mode = 'exercise'
            elif sendersName in ['pbGeneratorSave', 'pbGeneratorOK']:
                mode = 'generator'
            elif sendersName in ['pbPreprocessorSave', 'pbPreprocessorOK']:
                mode = 'preprocessor'
            elif sendersName in ['pbPlayerSave', 'pbPlayerOK']:
                mode = 'player'

        Mode = mode[0].upper() + mode[1:]
        curMode = 'cur' + Mode
        if filename == '':
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(True)
            #settingsLabel = getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText()
            settingsName = self.getCurrentSettingsName(mode)
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(False)

            filename = os.path.join(getattr(self.parHandle, curMode)['path']['presets'],
                                   settingsName + '.set')

        """
        while self.checkFilename(filename, mode):
            msg = filename + _translate("SettingsDialog",' is not valid preset name. Please enter another filename', None)
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                _translate("SettingsDialog", "Saving of ", None) + fileDialogMsg +
                _translate("SettingsDialog", "settings ...", None),
                self.parHandle.frameWork['settings']['lastSavingPath'],
                _translate("SettingsDialog", 'Result file', None) + ' (*.set) ;;' +
                _translate("SettingsDialog", 'All files', None) + ' (*)',
                _translate("SettingsDialog", 'Result file', None) + ' (*.set)',
                QtWidgets.QFileDialog.DontUseNativeDialog
            )
        """

        #if getattr(self.uiSettings,'lb' + Mode + 'Name').text()[-1] == '*':
        #    getattr(self.uiSettings,'lb' + Mode + 'Name').setText(getattr(self.uiSettings,'lb' + Mode + 'Name').text()[0:-1])
        if getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText()[-1] == '*':
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').setItemText(
                getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentIndex(),
            getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText()[0:-1])

        self.setSettings(None,mode=mode)

        # TODO: settings
        moduleName = getattr(self.parHandle, curMode)['settings'][mode + 'Name']
        curSettingsName = self.getCurrentSettingsName(mode)
        self.settings[mode][moduleName][curSettingsName]['settingsSaved'] = True

        saveStruct = dict()
        saveStruct[curMode] = deepcopy(self.settings[mode][moduleName][curSettingsName])

        with bz2.BZ2File(filename, 'w') as f:
            pickle.dump(saveStruct, f)

        self.parHandle.dPrint('Leaving save(): ' + mode, 2)


    def checkFilename(self, mode):
            """!
            """

            self.parHandle.dPrint('checkFilename(): ' + mode, 2)

            self.parHandle.dPrint('Leaving checkFilename(): ' + mode, 2)


    def saveAll(self, event, modeIn = ''):
        """!
        All settings of the modules will be saved.

        Mode is passed just for dccumentation of calling modules tab.
        """

        self.parHandle.dPrint('Leaving save(): ' + modeIn, 2)

        modes = ['generator', 'preprocessor', 'player', 'exercise']
        for mode in modes:
            self.save(event, mode)

        self.parHandle.dPrint('Leaving save(): ' + modeIn, 2)


    def new(self, event, mode = ''):
        """!
        Adds a new Item to the settingsList without saving it to a file.
        The user has to provide an item name in opening gui. To the provided name an asterisk is added because the
        settings have not been saved yet.
        To add entry and save file choose "Save as" [self.saveAs()].
        """

        self.parHandle.dPrint('new(): ' + mode, 2)

        sendersName = self.parHandle.sender().objectName()

        if mode == '':
            sendersName = sendersName
            if sendersName == 'pbExerciseNew':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorNew':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorNew':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerNew':
                mode = 'player'

        #Mode = mode[0].upper() + mode[1:]
        name = 'default'
        ii = 0
        maxTrials = 5
        while name == 'default':
            if ii > 0:
                self.parHandle.dPrint(_translate("SettingsDialog",
                    "'default' is not a valid preset/filename. Please enter a valid filename.", None
                    ), 0, guiMode=True)
            if ii < maxTrials:
                name, okPressed = QtWidgets.QInputDialog.getText(self,
                                        _translate("SettingsDialog", "Enter name of new item", None),
                                        _translate("SettingsDialog", "New item:", None)
                                        , QtWidgets.QLineEdit.Normal, "")
                if not(okPressed):
                    name = ''
            else:
                self.parHandle.dPrint(_translate("SettingsDialog",
                     "The maximum number of trials was reached and the filename selection is canceled.", None
                     ), 0, guiMode=True)
                name = ''
                return
            ii = ii + 1

        if okPressed and name != '':
            # '*' is added to the name since the settings have not been saved yet
            self.addNewItem(mode, entryName=name+'*')
            #self.settings[mode][name]['settingsName'] = name

        self.parHandle.dPrint('Leaving new(): ' + mode, 2)


    def openSettings(self, event, mode=''):
        """!
        The selected module can be defined by mode. If the function is called with the combo box, the
        object name of the calling widget defines the module

        mode can be:
            generator
            preprocessor
            player

        """

        self.parHandle.dPrint('open(): ' + str(mode), 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if  sendersName == 'cbExerciseSettingsName' or \
                    sendersName == 'pbExerciseReload' or\
                    mode == 'exercise':
                mode = 'exercise'
                module = 'curExercise'
            elif sendersName == 'cbGeneratorSettingsName' or\
                    sendersName == 'pbGeneratorReload' or \
                    mode == 'generator':
                mode = 'generator'
                module = 'curGenerator'
            elif sendersName == 'cbPreprocessorSettingsName' or \
                    sendersName == 'pbPreprocessorReload' or \
                    mode == 'preprocessor':
                mode = 'preprocessor'
                module = 'curPreprocessor'
            elif sendersName == 'cbPlayerSettingsName' or\
                    sendersName == 'pbPlayerReload' or\
                    mode == 'player':
                mode = 'player'
                module = 'curPlayer'

        Mode = mode[0].upper() + mode[1:]
        curSettingsName = self.getCurrentSettingsName(mode)


        # TODO: settings
        moduleName = getattr(self.parHandle, 'cur' + Mode)['settings'][mode + 'Name']

        # loading Settings from file or loading unsaved settings from temporary settingsStruct
        if not(moduleName in self.settings[mode]) or not(curSettingsName in self.settings[mode][moduleName]):# and\
                #self.settings[mode][moduleName][curSettingsName]['settingsSaved']:
            if curSettingsName:
                try:
                    getattr(self.parHandle, 'cur' + Mode)['functions']['settingsLoading'](
                        curSettingsName)  # TODO: all-Copy wird überschrieben
                    # load data from module int self.settings
                    self.readlCurrentSettings(mode, moduleName, curSettingsName)
                    self.settingsChanged(mode, curSettingsName, changeByOpening = True)
                except:
                    msg = _translate("SettingsDialog",
                                     'This should not have happened. Could not load setting . Please check settings ' +
                                     ' with name ', None) + curSettingsName
                    self.parHandle.dPrint(msg, 0, guiMode=True)
            else:
                self.parHandle.dPrint('Could not open settings file with name ' + curSettingsName, 0, guiMode=True)
        else:
            self.parHandle.dPrint('Using setttings found in self.setting  ' + curSettingsName, 1)
            try:
                getattr(self.parHandle, 'cur' + Mode)['functions']['settingsLoading'](
                    self.settings[mode][moduleName][curSettingsName])
                self.settingsChanged(mode, curSettingsName, changeByOpening = True)
            except:
                msg = _translate("SettingsDialog",
                                 'This should not have happened. Could not load setting . Please check settings ' +
                                 'which have been saved in self.settings ', None) + curSettingsName
                self.parHandle.dPrint(msg, 0, guiMode=True)


        self.parHandle.dPrint('Leaving open(): ' + str(mode), 2)


    def getCurrentSettingsName(self, mode):
        """!
        Returns the settings name of the current mode as defined in the settings combo box.
        """

        self.parHandle.dPrint('Leaving open(): ' + str(mode), 2)

        Mode = mode[0].upper() + mode[1:]
        getattr(self.uiSettings,'cb' + Mode + 'SettingsName').blockSignals(True)
        settingsLabel = getattr(self.uiSettings,'cb' + Mode + 'SettingsName').currentText()
        getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').blockSignals(False)
        if 'default' in settingsLabel:
            curSettingsName = re.sub('\*', '', settingsLabel)
        else:
            if not('*' in settingsLabel):
                curSettingsName = self.settingsLabelToName(settingsLabel, mode)
            else:
                curSettingsName = self.settingsLabelToName(re.sub('\*', '', settingsLabel), mode) + '*'

        if not(curSettingsName):
            curSettingsName = 'default'

        curModuleName = getattr(self.uiSettings, 'lb' + Mode + 'Name').text()
        if not(curSettingsName in self.settings[mode][curModuleName]):
            curSettingsName = self.settings[mode][curModuleName]['lastSettingsName']
            msg = 'Warning: Resetting settings name to lastSettings name: ' + curSettingsName
            self.parHandle.dPrint(msg, 2)

        self.parHandle.dPrint('Leaving open(): ' + str(mode), 2)
        return curSettingsName


    def settingsLabelToName(self, label, mode):
        """!
        This function converts the label of a setting to its name. The label is displayed to the user whereas the name
        is the name of the referenced setting file without its file extension (.set or .py).
        If the labels are not defined in filter.ini  label and name are the same.

        mode can be:
            generator
            preprocessor
            player

        The label is usually determined by:
        label = getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText()
        """

        Mode = mode[0].upper() + mode[1:]
        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'



        # TODO: settings
        curModuleName  = getattr(self.parHandle,'cur' + Mode)['settings'][mode+'Name']

        #if mode == 'exercise':
        #    settingsListLabels = self.parHandle.frameWork['settings']['access'][tempMode]['main']['displayed']['labels']
        #    settingsListNames = self.parHandle.frameWork['settings']['access'][tempMode]['main']['displayed']['names']
        #else:
        settingsListLabels = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']['labels']
        settingsListNames = self.parHandle.frameWork['settings']['access'][tempMode]['settings'][
                curModuleName]['displayed']['names']


        if label in settingsListLabels:
            idx = settingsListLabels.index(label)
            name = settingsListNames[idx]
        else:
            name = ''

        return name


    def reset(self, event, mode=''):
        """!
        Reset settings to default values.
        """

        self.parHandle.dPrint('reset(): ' + mode, 2)
        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseReset':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorReset':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorReset':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerReset':
                mode = 'player'

        Mode = mode[0].upper() + mode[1:]
        curMode = 'cur' + Mode

        # check if unsaved settings exist
        #if getattr(self.uiSettings, 'lb' + Mode + 'Name').text()[-1] == '*':
        if getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText() and \
            getattr(self.uiSettings, 'cb' + Mode + 'SettingsName').currentText()[-1] == '*':
            msg = 'The settings have been changed. Do you want to save the changes in the preset'
            answer = QtWidgets.QMessageBox.question(
                self, _translate("SettingsDialog",'Save unsaved data?', None), msg,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Abort
            )
            if answer == QtWidgets.QMessageBox.Abort:
                self.parHandle.dPrint('reset(): Aborting resetting of settings', 2)
                return
            if answer == QtWidgets.QMessageBox.Yes:
                self.parHandle.dPrint('reset(): saving unsaved changes', 2)
                self.save(None, mode=mode)

        # setting default settings
        if getattr(self.parHandle, curMode)['functions']['settingsDefault']:
            getattr(self.parHandle, curMode)['functions']['settingsDefault']()
            moduleName = getattr(self.parHandle, curMode)['settings'][mode + 'Name']
            self.readlCurrentSettings(mode, moduleName, 'default')
            # reading new settings

            self.updateGui(mode=mode, curModName=moduleName, curModSettings='default')
            self.settingsChanged(mode=mode, changeByOpening = True)
            self.parHandle.dPrint('reset(): Settings have been reset to defaults', 0)

        self.parHandle.dPrint('Leaving reset(): ' + mode, 2)


    def reload(self, event, mode = ''):
        """!
        This is just another way to load the setting, currently selected in the settings combo box.
        """

        self.parHandle.dPrint('reload(): ' + mode, 2)

        if not(mode):
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseReload':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorReload':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorReload':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerReload':
                mode = 'player'

        curMode = 'cur' + mode[0].upper() + mode[1:]

        # TODO: settings
        if getattr(self.parHandle, curMode)['settings']['settingsName'] in ['', 'default']:
            getattr(self.parHandle, curMode)['functions']['settingsDefault']()
            self.updateGui(mode=mode)
            self.settingsChanged(mode=mode, changeByOpening = True)
        else:
            self.openSettings(mode)

        self.parHandle.dPrint('Leaving reload(): ' + mode, 2)


    def syncToExer(self, event, mode = ''):
        """!
        This function syncs all submodules from the submodule tabs to the exercise module tab if the exercise tab is
        selected. If a submodule tab is selected the selected item of the submodule and its settings are synced to
        the exercise tab.
        """

        self.parHandle.dPrint('syncToExer(): ' + mode, 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseSyncToExer':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorSyncToExer':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorSyncToExer':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerSyncToExer':
                mode = 'player'

        if mode == 'exercise':
            modeItems = ['generator', 'player', 'preprocessor']
        else:
            modeItems = [mode]

        for ii in range(len(modeItems)):
            modeItem = modeItems[ii]
            ModeItem = modeItem[0].upper() + modeItem[1:]

            subModulName = getattr(self.uiSettings, 'cb' + ModeItem + 'Name').currentText()
            subModulsettingsName = getattr(self.uiSettings, 'cb' + ModeItem + 'SettingsName').currentText()

            idx = self.uiSettingsDyn['exercise'][modeItem + 'Entry'].findText(subModulName)
            if idx >= 0:
                self.uiSettingsDyn['exercise'][modeItem + 'Entry'].setCurrentIndex(idx)
            idx = self.uiSettingsDyn['exercise'][modeItem + 'SettingsEntry'].findText(subModulsettingsName)
            if idx >= 0:
                self.uiSettingsDyn['exercise'][modeItem + 'SettingsEntry'].setCurrentIndex(idx)
        self.updateGui(mode)
        self.parHandle.dPrint('Leaving syncToExer(): ' + mode, 2)


    def syncFromExer(self, event, mode = ''):
        """!
        This function syncs all submodules from the exercise tab to the submodule tabs if the exercise tab is selected.
        If a submodule tab
        is selected the selected item of the submodule and its settings are synced to the exercise tab.
        """

        self.parHandle.dPrint('syncFromExer(): ' + mode, 2)

        if mode == '':
            sendersName = self.parHandle.sender().objectName()
            if sendersName == 'pbExerciseSyncFromExer':
                mode = 'exercise'
            elif sendersName == 'pbGeneratorSyncFromExer':
                mode = 'generator'
            elif sendersName == 'pbPreprocessorSyncFromExer':
                mode = 'preprocessor'
            elif sendersName == 'pbPlayerSyncFromExer':
                mode = 'player'

        if mode == 'exercise':
            modeItems = ['generator', 'player', 'preprocessor']
        else:
            modeItems = [mode]

        for ii in range(len(modeItems)):
            modeItem = modeItems[ii]
            ModeItem = modeItem[0].upper() + modeItem[1:]

            subModulName = self.uiSettingsDyn['exercise'][modeItem + 'Entry'].currentText()
            subModulsettingsName = self.uiSettingsDyn['exercise'][modeItem + 'SettingsEntry'].currentText()

            idx = getattr(self.uiSettings, 'cb' + ModeItem + 'Name').findText(subModulName)
            if idx >= 0:
                idx = getattr(self.uiSettings, 'cb' + ModeItem + 'Name').setCurrentIndex(idx)

            idx = getattr(self.uiSettings, 'cb' + ModeItem + 'SettingsName').findText(subModulsettingsName)
            if idx >= 0:
                getattr(self.uiSettings, 'cb' + ModeItem + 'SettingsName').setCurrentIndex(idx)

        self.parHandle.dPrint('Leaving syncFromExer(): ' + mode, 2)


    def closeEvent(self, event=None):
        """!
        This function overrides the closeEventFunction of Qwidgets which is called if self.close() is called in self.ok
        or self.cancel or if the X of the frame is pressed.
        It allows to prevent the closing of the frame if a run is still active
        """
        self.parHandle.dPrint('closeEvent()', 2)

        sendersName = self.parHandle.sender().objectName()
        if not(sendersName in ['pbExerciseOK', 'pbExerciseCancel',
                               'pbGeneratorOK', 'pbGeneratorCancel',
                               'pbPreprocessorOK', 'pbPreprocessorCancel',
                               'pbPlayerOK', 'pbPlayerCancel']):
            self.cancel(event, mode='SettingsWindow')
            self.parHandle.dPrint(_translate(
                "SettingsDialog", 'Closing Settings dialog without saving or applying setting.', None), 0,
                guiMode = True)

        self.parHandle.settings = self.settings

        self.parHandle.dPrint('Leaving closeEvent()', 2)

        event.accept()  # let the window close


    def markGuiFieldState(self, state):
        """!
        This function takes the input state, which was changed for the widget defined in  self.currentWidget.
        The function changes the entry color according to the validation state of the entry.
        """

        widgetHandle = self.currentWidget

        if isinstance(widgetHandle, QtWidgets.QLineEdit):
            if not (QtGui.QValidator.Acceptable == state):
                if QtGui.QValidator.Invalid == state:
                    color = QtGui.QColor(QtCore.Qt.red)
                    setBoldFlag = True
                else:
                    # orange color
                    color = QtGui.QColor(255, 130, 0)
                    setBoldFlag = True
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Text, color)
            else:
                pal = QtGui.QPalette()
                #color = QtGui.QColor(QtCore.Qt.black)
                setBoldFlag = False


            myFont = QtGui.QFont()
            myFont.setBold(setBoldFlag)

            widgetHandle.setFont(myFont)
            widgetHandle.setPalette(pal)
