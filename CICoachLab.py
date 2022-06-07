"""!
CICoachLab allows the start of graphical exercises which are intended for the
usage by patients.

#Player, preprocessors and generators:
The exercises can make use of generators, preprocessors and player which can be used by different exercises.
The used generators, preprocessors and players have to rely on the same signal structure of the provided data.
CICoachLab is able to handle/provide all types of signals an does not care about the signal structure.
So far CICoachLab has been tested only with generators, preprocessors, and player handling audio signals only
but other types of data should be handled as well.
Audio signals require the following signal structure:
signal['audio']
signal['fs']

For audio signals different types of player may be useful.
Different types of generators are essential, e.g. for reading audio file, or generating synthesized signal.
Preprocessor may degrade or upgrade the audio signal to simulate different kinds of hearing level or
to test the outcome of preprocessing.

CICoachLab provides the framework functions like saving, the gui framework, the settings dialog, the organization of
setlists, masterlists and other features.
The functionality of the implemented tests is organized in exercises.

Exercises:
Exercises are organized as classes which contains the algorithms/code for running the exercise.

The exercise main file defines the name of the exercise and points to exercise folder with the same name as the main
file without the .py extension. In the exercise folder the following oblgatory subdirectories have to be provided:
presets, locales, results.
Other subdirectories may be e.g.  analysis, data, signalFiles or any other subdirectories.

presets: Apart from the 'default' settings the directory contains the saved settings of the function.
locales: translations of user dialog messages will be saved here.
results: backup results will be saved in the results folder.

The main exercise file may be supported by other source code files which have to be handled by the exercise main
file.

Settings:
The settings can be saved as py-files which are a mighty approach of saving the settings because the py files have
access to the inner parts of the CICoachLab variables by the.
The settings in the set-files can be handled by the Settings dialog of.
In special cases of exercise settings, the exercise might have to provide an additional gui-Dialog to handle the
the exerise settings.

The default settings are provdided by the obligatory exercise function setDefaultSettings.
The Default settings are set at startup of the exercise, if no other specific settings are provided at the
intialization of the exercise class. The Settings can be provided as the filename of the .set- or .py file or
by passing a dictionary wich contains the setting fields as keys with their accroding values.
If not all setting fields are provided the remaining fields are set to the default values.


Exercise functions:

The function of CICoachLab and exercises are quite intermingled.

The obligatory functions have have to be linked to CICoachLab via the definition in
self.parHandle.curExercise['functions']['settingsLoading']
self.parHandle.curExercise['functions']['settingsDefault']
self.parHandle.curExercise['functions']['destructor']
self.parHandle.curExercise['functions']['eraseExerciseGui']


Other possible functions may be:
self.parHandle.curExercise['functions']['displayResults']
self.parHandle.curExercise['functions']['settingsGui']
self.parHandle.curExercise['functions']['checkConditions']
self.parHandle.curExercise['functions']['calibration']

CICoachLab functions usually called by the exercises:
self.loadSettings()
self.closeDownRun()
self.addingPath()
self.closePath()
self.dPrint()

Further use cases might require the calling of:
self.measureReactionTime()
self.checkParameters()

# calibration:
The time delay between signal presentation and the user input can be calibrated to measure reaction times.
For this case a calibration function has to be provided which is used to start a simulated run

Further information on the calibration:
To be done


setlists:
Setlist have to be defined in the setlist directory as files  with the extension *.lst




#The field entries of the setlist file are:
[exercises]
names = exercise1, exercise2, exercise3
settings = exercise1Setting, exercise2Setting, exercise3Setting

[generators]
names = None, generator, generator
settings = None, generatorSetting1, generatorSetting2

[preprocessors]
names = None, None, preprocessor
settings = None, None, None, default

[player]
names = None, player, player
settings = None, default, playerSetting

['description']
short = First item, another item, last item

To be selectable by the user the available setlists have to be defined in filter.ini
With the setlists exampleList1.lst and exampleList2.lst the entries within filter.in can be:
...
[setlists]
[[main]]
names = exampleList1, exampleList1
labels = A setlist title, Another setlist title
difficulties = 3, 1,
# use "info1","info2" to enclose infos,
# other wise '''info 1''','''info2''' can be used. this is more tricky and not recomended.
infos = "Dieses Beispiel präsentiert eine Übungsabfolge mit CI Simulation der Audio-Darbietung.",""Dieses Beispiel präsentiert eine Übungsabfolge."
visibles = True, True

...

names: defines the name(s) (without the extension ".lst") of the displayed setlist
labels: the labels define the setlist entries in the gui list, which are presented to the user for the selection
        of the setlist.
difficulties: the difficulties define which minimum level of difficulty the user has to reach to be able to see
                 and select the setlist. The difficulty of the user can be checked and defined in the user menu.
infos: a longer information text can be provided, which is displayed if the user hovers the mouse pointer above
        the entry in the setlist selection list box.
visibles: define if the entry should be be visible for the user.


An example can be found in demo.ls.
Rename the file extension and adjust the entries accordingly.

exampleList1.lst might be defined as follows:

setname: exampleList1
information = Some general information

[exercises]
names = exercise1, exercise2, sercise3
settings = exercise1Setting, exercise2Setting, sercise3Setting

[generators]
names = generator1, None, generator3
settings = generator1settings, None, generator3settings

[preprocessors]
names = None, None, None
settings = None, None, None

[player]
names = player1, None, player3
settings = player1settings, default, player3Settings

[description]
short = First description,  Second description, Third description

For all fields valid entries have to be provided.
If a submodule does not have to be defined, None should be provided as entry.
as settings the name of a valid settings preset should be provided.
Each setlist exercise must have a short description.
The short description is taken for the labeling of the entries in the setlist progress box. In the
setlist progress box the progress within the setlist is indicated by highlighting the current exercise.

setname and information won't be used within the gui and may be considerer as a description  for developers
only. The information which is displayd in the gui is defined in filter.ini.

masterlists:
Masterlists can be defined to run a set of single exercises or a set of setlists.
If the masterlist mode is set with the 'masterlistStart' field in the '[system]' section of CICoachLab.ini the
respective item is run according to masterlist field 'lastItemIDX'.

In the masterlist the fields 'name' and 'information' provide some general information as string about the masterlist.
The field 'lastItemIDX' saves the index of provides the index of the last run masterlist item. This field is updated
during the run of the masterlist.

The field entries are:
items = setlist1, singleRun1, setlist2
settings = None, singleRunSetting1, None
runmode = setlist, singleRun, setlist
preconditions = None, None, None
preconditionMessages = '''''','''''',''''''
postconditions = None, None, None
postconditionMessages = '''''','''''',''''''
description = '''One, two and three as a short description.''','''Second description''','''Third description'''


An example masterlist can be found in /masterlists with the file masterlist.ls

filter.ini:
The file filter.ini is used to define displayed exercises and setlists.
Furthermore it can be used to provide translations for the exercise names.
While the exercise names may be usefull for the programmer the gui should provide a more telling labeling of the
exercises. This labeling can be used for the translation of the exercises. For the translation of dialog entries see
the translation section


translations:
All dialog messages which are presented to the user are provided in english as default.
Other translations may be provided as well. The localization is provided in
self.frameWork['settings']['localization'] which is read from the [system] section of CICoachLab.ini.

The function self.translateAllExercises() can be used to guide the programmer through the translation process.
This function assumes that each exercise provides a 'locales' directory for the the saving and application of
translations.

These are the steps used for the translations in CICoachLab:
1) The code is parsed for the translation entries (_translate() ) with pylupdate5
2) linguist is opened with the generated file for a gui guided translation
3) The translation file is generated with lrelease and put into the locales directory of CITrainier or the
    respective modules (probably the exercise)

Setup of CICoachLab:
CICoachLab.ini provides basic framework settings and the status of the CICoachLab framework at
the last closing of CICoachLab.

CICoachLab.ini is required by CICoachLab.
The file is read at the startup of CICoachLab.
Some fields will be updated during the application of CICoachLab (e.g. lastSavingName, accumulatedRunTime, ...)
If other entries are updated during the application of CICoachLab the changed.
Changes in CICoachLab.ini which are added, when CICoachLab is oppened might be dicarded.

For the documentation of the field entries and a template of an CICoachLab.ini see CICoachLab.in.

# required files:

CICoachLab.ini:
    The file contains the system settings. The template file CICoachLab might have to be edited.
filter.ini:
    The file defines which exercises and generators, preprocessors player and its respective available settings
    can be selected by the user.
    It depends on is global visibility and the difficulty level of the user.
CICoachLabMainWindowGui2.py:
    CICoachLabMainWindowGui2.py provides the main graphical framework user interface.
    CICoachLabMainWindowGui2.py is generated with
    "pyuic5 CICoachLabMainWindowGui2.ui -o CICoachLabMainWindowGui2.py"
    CICoachLabMainWindowGui2.ui was generated with QtDesigner
UserDataDialog.py
    UserDataDialog.py provides the graphical user interface to enter personal patient data.
    UserDataDialog.py is generated with
    "pyuic5 UserDataDialog.ui -o UserDataDialog.py"
    UserDataDialog.ui was generated with QtDesigner


# locales folder:
    The german translation file en_de.qm is required up to now which can be found in the subfolder locales

# html
    The folder provides the source code documentation which may be helpfull to get an overview of the CICoachLab
    Framework.

# optional files/folder:

#system requirements:
##Hardware
Monitor Resolution:  recommended are 1920*1080, untested so far
CPU: untested so far
## Software
Linux/Windows

Python 3.8 or higher
PyQt5
Windows 7
Windows 10 if the options "fixMasterVolume" and "bitlockerMode" are set to True in CICoachLab.ini.


## python base packages
sys, os, time, bz, pickle, re, traceback, copy, PyQt5, importlib.util, webbrowser
platform, subprocess, shutil, datetime

## additional python packages:
audio2numpy (windows and linux: pip install audio2numpy, for mp3 handling required external dependencies: ffmpeg)
configObj (windows: installation with pip install conofigObj)
sounddevice (windows and linux: installation with pip install sounddevice)
soundfile (windows and linux: pip install soundfile)
psutil (windows: installation with pip install psutil)
openpyxl (windows: installation with pip install openpyxl, for pandas excel export/import)

windows:
(pip install pycaw) for managing audio volume

##recommended python packages (may be used in exercises):
numpy (recomended)
pandas (recomended)

other external dependencies:
dependencies: ffmpeg
dependencies: doxygen
dependencies: awk, only linux
dependencies: find, only linux
dependencies: amixer, only linux
dependencies: bash, only linux
dependencies: pip, only linux

If not stated otherwise the packages can be installed in windows by installing wxPython.

For the installation of python and pyqt5 in Windows the installation of winPython is recomended
(https://sourceforge.net/projects/winpython/).

linux requirements:
#ubuntu packages (ubuntu 21.04):
sudo apt install python3-numpy python3-matplotlib python3-pandas python3-pip python3-configobj awk amixer

# development
sudo apt install pyqt5-dev-tools doxygen graphviz
sudo apt install qt5-default libpcap-dev libncurses5-dev libprocps-dev libxtst-dev
sudo apt install libxcb-util0-dev qttools5-dev-tools libdtkwidget-dev libdtkwm-dev pkg-config

Other
xlrd version higher than 1.1 for excel file import with pandas

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


import sys
import os
import importlib.util # for directory specific import of py-files
import importlib.metadata
import pkg_resources
import numpy as np


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot

import bitlocker
from CICoachLabMainWindowGui2 import Ui_MainWindow
from UserDataDialogCall import UserDataDialogCall
from CalibrationCall import CalibrationCall
from PatientfileBackuper import PatientfileBackuper


from configobj import ConfigObj
from time import time, gmtime, strftime
import datetime
import bz2
import pickle
import re
import traceback
# python by default executes shallow copies of data  ( pointers in c++) instead of deep copies!
from copy import deepcopy



import webbrowser
import platform
import subprocess
from inspect import currentframe, getouterframes # for check which function called a function
from inspect import getmembers, isfunction, ismodule # for call of  dynamic functions. self.callDynmicFunctions()

# for use of latex text with self.mathTexToQPixmap()
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
from SettingsDialogCall import SettingsDialogCall

import shutil
import psutil
try:
    from PyQt5 import sip
except ImportError:
    import sip

matplotlib.rcParams['text.usetex']
matplotlib.rcParams['text.latex.preamble'] = [r'\usepackag{amsmath}]']

global globalTemp
globalTemp = dict()

# For guided translation of gui
# Returns the translation text for sourceText, by querying the installed translation files.
# The translation files are searched from the most recently installed file back to the first installed file.
def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)



class CICoachDialog(QtWidgets.QMessageBox):
    """!
    CICoachDialog uses the QMessageBox dialog as base to display messages.
    The presented Dialog is raised in the stack of frames to ensure the visibility, epecially in the windows context.
    """
    def __init__(self, parHandle, title, text, mode='question', infoText='', detailedText=''):
        """!
        parHandle:  handle to CICoachLab
        title:      window title
        text:       question or informative text
        mode:       the mode defines if a question is asked, an information is provided
                    The mode defines which buttons are displayed and which icon is provided.
        infoText:   additional text which may be provided i

        Detailed information on the different modes:
            question:
                buttons:    yes, no, cancel
                icon:       question mark
            confirmation:
                buttons:    ok, cancel
                icon:       question mark
            information
                buttons:    ok
                icon:       none
            warning:
                buttons:    ok
                icon:       warning
            error:
                buttons:    ok
                icon:       error
        """

        super().__init__()
        self.title = title
        self.text = text
        self.mode = mode
        self.infoText = infoText
        self.detailedText = detailedText
        self.parHandle = parHandle
        self.initUI()


    def initUI(self):
        '''
        self.setWindowTitle(self.title)
        self.buttonReply = QtWidgets.QMessageBox.question(self, self.title, self.question,
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        self.show()
        '''

        msg = QtWidgets.QMessageBox(self.parHandle)

        msg.setText(self.text)
        msg.setWindowTitle(self.title)
        msg.setSizeGripEnabled(True)

        if self.mode == 'question':
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            msg.setIcon(QtWidgets.QMessageBox.Question)
        if self.mode == 'confirmation':
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setIcon(QtWidgets.QMessageBox.Question)
        elif self.mode == 'information':
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif self.mode == 'warning':
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif self.mode == 'error':
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)


        if self.detailedText:
            msg.setDetailedText(self.detailedText)
        if self.infoText:
            msg.setInformativeText(self.infoText)

        msg.show()
        msg.raise_()

        self.buttonReply = msg.exec_()
        return self.buttonReply


    def returnButton(self):
        return self.buttonReply


class InformationDialog(QtWidgets.QDialog):
    """!
    Displaying messages in a non modal dialog.
    """

    def __init__(self, parent=None, msg=''):
        super().__init__(parent, modal=False)
        self.setLayout(QtWidgets.QFormLayout())
        self.textLabel = QtWidgets.QLabel(msg)
        self.layout().addRow(self.textLabel)
        self.acceptBtn = QtWidgets.QPushButton('Ok', clicked=self.accept)
        self.layout().addRow(self.acceptBtn)


class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress


    This code was published at
    https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    by Martin Fitzpatrick

    BSD-2-Clause
    """

    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function


    This code was published at
    https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    by Martin Fitzpatrick

    BSD-2-Clause
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class CICoachLab(QtWidgets.QMainWindow):
    """!
    The class CICoachLab manages the gui of the CICoachLab framework.
    """
    def __init__(self, parent=None, app=None):
        """!
        Initializing CITrainier.

        Keyword arguments:
        parent -- The handle to a parent gui is optional (default None).

        The default settings will be called. This function reads the iniFile, for the loading of the frameWork settings
        and to reload the old status of the
        last session. The frameWork gui is build. The available exercise are prepared. The gui is connected to some
        actions as far as possible.
        """

        self.app = app

        self.settingsDLGHandle = None
        super().__init__()

        ## setting up gui
        QtWidgets.QMainWindow.__init__(self, parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # initializing frameWork
        self.initializeToDefaults(mode='all')

        self.setWindowIcon(QtGui.QIcon(os.path.join(self.frameWork['path']['pwd'], 'recources', 'logo.svg')))
        screen = self.app.primaryScreen()
        screensize = screen.size()
        availableGeometry =  screen.availableGeometry()

        height = availableGeometry.height()
        width = availableGeometry.width()
        screensize.setHeight(height)
        screensize.setWidth(width)

        self.setMaximumSize(screensize)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowMinimizeButtonHint|
            QtCore.Qt.WindowMaximizeButtonHint
            )
        # Python packages which are commonly used by CICoachLab or its modules are defined.
        # In the expert mode menu the currently used packages  can be downloaded via pip as backup,
        # and installed  via pip to resolve missing dependencies.
        # The used versions of the packages can be  documented in the text file CICoachLabRequirements.txt.
        # TODO: in future versions the handling of different version and a avoiding of conflicts may be improved by
        #  using an installation tool like "pipenv"
        self.defineDependencies()

        # this will be filled if the settings dialog is used. it will contain the fields
        #   'exercise', 'generator', 'preprocessor', 'player'
        self.settings = dict()
        # getting system specific hardware settings and frameWork status at last shutdown

        success = self.readIniFile()
        if not(success):
            self.__exit__(None, None, None)
            self.deleteLater()
            return

        if self.frameWork['settings']['localization']:
            self.setLocalization(self.frameWork['settings']['localization'])
            self.ui.retranslateUi(self)

        success = self.readFilter()
        if not(success):
            self.__exit__(None, None, None)
            self.deleteLater()
            return


        if self.frameWork['settings']['expertMode']:

            self.ui.menuExpertTools = QtWidgets.QMenu(self.ui.menubar)
            self.ui.menuExpertTools.setObjectName("menuExpertTools")

            self.ui.calibrateSystemExercise = QtWidgets.QAction(self)
            self.ui.calibrateSystemExercise.setObjectName("calibrateSystemExercise")
            self.ui.calibrateSystemExercise.triggered.connect(self.calibrateSystemExercise)


            self.ui.menuCalibrateSystem = QtWidgets.QAction(self)
            self.ui.menuCalibrateSystem.setObjectName("menuCalibrateSystem")
            self.ui.menuCalibrateSystem.triggered.connect(self.calibrateSystemLevel)

            self.ui.menuSettingsDialog = QtWidgets.QAction(self)
            self.ui.menuSettingsDialog.setObjectName("menuSettingsDialog")
            self.ui.menuSettingsDialog.triggered.connect(self.openSettingsDialog)

            self.ui.menuTranslateExercise = QtWidgets.QAction(self)
            self.ui.menuTranslateExercise.setObjectName("menuTranslateExercise")
            self.ui.menuTranslateExercise.triggered.connect(self.translateAllExercises)

            self.ui.menuGettingDependencies = QtWidgets.QAction(self)
            self.ui.menuGettingDependencies.setObjectName("gettingPythonImports")
            self.ui.menuGettingDependencies.triggered.connect(self.gettingPythonImports)

            self.ui.menuDownloadDependencies = QtWidgets.QAction(self)
            self.ui.menuDownloadDependencies.setObjectName("menuDownloadDependencies")
            self.ui.menuDownloadDependencies.triggered.connect(self.downloadDependencies)

            self.ui.menuInstallMissingPackages = QtWidgets.QAction(self)
            self.ui.menuInstallMissingPackages.setObjectName("menuInstallMissingPackages")
            self.ui.menuInstallMissingPackages.triggered.connect(self.installMissingPackages)

            self.ui.menuDocumentImportedPackages = QtWidgets.QAction(self)
            self.ui.menuDocumentImportedPackages.setObjectName("menuDocumentImportedPackages")
            self.ui.menuDocumentImportedPackages.triggered.connect(self.documentPackageVersions)

            self.ui.menuExpertTools.addAction(self.ui.calibrateSystemExercise)
            self.ui.menuExpertTools.addAction(self.ui.menuCalibrateSystem)

            self.ui.menuExpertTools.addAction(self.ui.menuSettingsDialog)
            self.ui.menuExpertTools.addAction(self.ui.menuTranslateExercise)
            self.ui.menuExpertTools.addAction(self.ui.menuGettingDependencies)
            self.ui.menuExpertTools.addAction(self.ui.menuDownloadDependencies)
            self.ui.menuExpertTools.addAction(self.ui.menuInstallMissingPackages)
            self.ui.menuExpertTools.addAction(self.ui.menuDocumentImportedPackages)

            self.ui.menuExpertTools.setEnabled(True)

            menuAnalysisHandle = self.ui.menuExpertTools.addMenu('Analysis')

            ii = 0
            analysisFiles = self.getListOfFiles(os.path.join(self.frameWork['path']['masterlists'],
                                                            'analysis'), depthOfDir=1, namePart='.py')
            analysisFilesShort = []
            for item in analysisFiles:
                name = item.split('.')[0]
                analysisFilesShort.append(name)
                ii = ii + 1

            ii = 0
            for preset in analysisFilesShort:
                actionSetup = QtWidgets.QAction(self)
                actionSetup.setObjectName("actionPreset" + str(ii))
                actionSetup.setText(_translate("MainWindow", preset, None))
                actionSetup.triggered.connect(self.callDynmicFunctionsMasterlist)
                menuAnalysisHandle.addAction(actionSetup)

                self.curMasterlist['gui']['menu'].append(actionSetup)
                ii = ii + 1

            self.ui.menuExpertTools.setTitle(_translate("MainWindow", "Expert tools", None))
            self.ui.calibrateSystemExercise.setText(_translate("MainWindow", "Calibrate Exercise", None))
            self.ui.menuCalibrateSystem.setText(_translate("MainWindow", "Calibrate System", None))
            self.ui.menuSettingsDialog.setText(_translate("MainWindow", "Open settings dialog", None))
            self.ui.menuGettingDependencies.setText(_translate("MainWindow", "Finding dependencies", None))
            self.ui.menuDownloadDependencies.setText(_translate("MainWindow", "Download dependencies", None))
            self.ui.menuInstallMissingPackages.setText(_translate("MainWindow", "Install missing dependencies", None))
            self.ui.menuDocumentImportedPackages.setText(_translate("MainWindow", "Document dependencies", None))
            self.ui.menuTranslateExercise.setText(_translate("MainWindow", "Translate CICoachLab", None))

            self.ui.menubar.addAction(self.ui.menuExpertTools.menuAction())
            self.ui.menubar.show()

        self.ui.menuHelpAbout.triggered.connect(self.showAboutDialog)

        self.ui.menuSourceCodeDocu = QtWidgets.QAction(self)
        self.ui.menuSourceCodeDocu.setObjectName("menuSourceCodeDocu")
        self.ui.menuSourceCodeDocu.triggered.connect(self.openSourceCodeDocu)
        self.ui.menuSourceCodeDocu.setText(_translate("MainWindow", "Documentation", None))
        self.ui.menuHelp.addAction(self.ui.menuSourceCodeDocu)

        if len(self.frameWork['settings']['debug']['debuggingTempFile']) > 0 and self.frameWork['settings']['debug']['mode'] == True:
            self.dPrint(
                'A debug file ' + self.frameWork['settings']['debug']['debuggingTempFile'] + 'will be written.' +
                ' At the end it will be moved to: ' + self.frameWork['settings']['debug']['debuggingFile']
                ,0)

        self.frameWork['settings']['currentSessionStartTime'] = time()

        if not(strftime("%Y-%m-%d", gmtime(time())) == self.frameWork['settings']['lastRunEndTime']):
            self.frameWork['settings']['dailyCumulatedRunTime'] = 0

        if self.frameWork['settings']['dailyCumulatedRunTime'] > self.frameWork['settings']['maxDailyCumulatedRunTime']:
            msg = _translate("MainWindow", "The dayly cumulated runtime exceeded the allowed maximum time", None) + \
                    f"\n{self.frameWork['settings']['dailyCumulatedRunTime']:04.1f} > " + \
                    f"\n{self.frameWork['settings']['maxDailyCumulatedRunTime']:04.1f}"
            self.dPrint(msg, 0, guiMode=True)

        self.frameWork['gui']['buttons'].append(self.ui.pbNewRun)
        self.frameWork['gui']['buttons'].append(self.ui.pbShowResults)

        # setListMOde/tab
        self.frameWork['gui']['lists'].append(self.ui.lwSetlistNameVal)
        self.frameWork['gui']['lists'].append(self.ui.lwSetlistContentVal)
        self.frameWork['gui']['buttons'].append(self.ui.pbRunSetlist)

        # contains all gui widgets which can be disabled
        self.ui.tabTrainerMode.tabBarClicked.connect(self.selectSetlistMode)
        self.ui.pbStoppSetlist.clicked.connect(self.stoppSetlist)

        self.frameWork['gui']['lists'].append(self.ui.lwExerNameVal)
        self.frameWork['gui']['lists'].append(self.ui.lwExerSetVal)
        self.frameWork['gui']['lists'].append(self.ui.lwRuns)

        self.frameWork['gui']['menus'].append(self.ui.menuFile)
        self.frameWork['gui']['menus'].append(self.ui.menuExer)
        self.frameWork['gui']['menus'].append(self.ui.menuGenerator)
        self.frameWork['gui']['menus'].append(self.ui.menuPlayer)
        self.frameWork['gui']['menus'].append(self.ui.menuHelp)

        for item in self.frameWork['gui']['buttons']:
            try:
                item.setDisabled(True)
            except:
                self.dPrint('Exception: Could not disable exercise gui elements', 1)


        if self.frameWork['settings']['fixMasterVolume']:

            self.oldMasterVol = self.getMasterVolume()
            masterVolumeValue = int(self.frameWork['settings']['masterVolumeValue'])

            self.setMasterVolume(masterVolumeValue)
            self.fixedMasterVol = self.getMasterVolume()

        if self.frameWork['settings']['bitlockerMode']:
            # mounting a bitlocked USB Stick if the bitlock mode is set in CICoachLab.ini.
            # This may be usefull if  a USB Stick is used for saving patient data
            status = self.checkBitlockerMemory()
            if not(status):
                # if the bitlocker path  cannot be unlocked a check is run if path to directory is found.
                # this can be used to check if a obligatory memory stick for saving of the data is provided.
                msg = _translate("MainWindow",
                                 'The bitlocked path could not be unlocked.\n\n '  #
                                 'Please check if you attached the (correct) memory stick and restart CICoachLab.', None)
                self.dPrint(msg, 0, guiMode=True)
                self.__exit__(None, None, None)
                self.deleteLater()
                return


        # check for patientMode and coachMode
        # in the patientMode a predefined patient file (see CICoachLab.ini) is loaded
        # in the coachMode the same patient file is opened and
        if self.frameWork['settings']['patientMode'] or self.frameWork['settings']['coachMode']:

            msg = 'Entering patient/coachMode mode....'
            self.dPrint(msg, 3)
            if not(os.path.isfile(self.frameWork['settings']['patientSavingFile'])):
                #if patient file cannot be found a check is run if path to directory is found.
                # this can be used to check if a obligatory memory stick for saving of the data is provided.
                msg = 'Patient data file could not be found.'
                self.dPrint(msg, 3)
                if not(os.path.isdir(os.path.dirname(self.frameWork['settings']['patientSavingFile']))) and\
                        len(os.path.dirname(self.frameWork['settings']['patientSavingFile'])) > 0:
                    msg = _translate("MainWindow", 'The path for loading and saving user data could not be found.\n\n '#
                        'Please check if you attached the defined memory stick and restart CICoachLab.', None)
                    self.dPrint(msg, 0, guiMode=True)
                    self.__exit__(None,None,None)
                    self.deleteLater()
                    return
                else:
                    msg = _translate("MainWindow", 'Your data will be saved under the new file: ',
                        None) + self.frameWork['settings']['patientSavingFile'] + '(.cid)'
                    self.dPrint(msg, 1, guiMode=True)
            else:
                msg = 'Loading patient data of previous session.'
                self.dPrint(msg, 3)

                patientFile  = self.frameWork['settings']['patientSavingFile']

                self.loadRunData(filename=patientFile)
                self.updateFilter(self.user['difficulty'])
                self.updateExerciseListBox()
                self.updateExerciseSettingsListBox()

                if self.frameWork['settings']['coachMode']:
                    savingPath = self.frameWork['settings']['coachBackupPath']
                    # ask the coach if and under which name the data should be backuped at 'coachBackupPath'
                    temp = PatientfileBackuper(patientFile=patientFile, user=self.user, savingPath=savingPath)
                    temp.exec()

                # uncommenting this out would just keep a blank space where the widget was removed
                #sp = self.ui.gbSubModules.sizePolicy()
                #sp.setRetainSizeWhenHidden(True)
                #self.ui.gbSubModules.setSizePolicy(sp)
                self.ui.gbSubModules.hide()

            # deleting the options to load or save data manually by removing the respective menue entries.
            msg = 'Deleting the menus to save and load data.'
            self.dPrint(msg, 3)
            if self.frameWork['settings']['patientMode']:
                self.ui.menuFile.removeAction(self.ui.menuFileSave)
                self.ui.menuFile.removeAction(self.ui.menuFileLoad)
        else:
            self.updateFilter(self.user['difficulty'])
            self.updateExerciseListBox()
            self.updateExerciseSettingsListBox()

        if self.frameWork['settings']['studyMode']:
            if not(self.user['lastname']) or not(self.user['forname']) or not(self.user['birthday'])\
                    or self.user['birthday'] == '01.01.1900':
                msg = _translate("MainWindow", 'The personal data were not provided so far. Please provide your personal'
                      ' (name, forname and birthday) and '
                      'and confirm the input the button "Saving" .', None)
                self.dPrint(msg, verbosity=0, guiMode=True)
                self.callUserDataGui()

        # the settings will be filled by self.updateExerciseSettingsListBox() if an exercise is selected
        self.exerciseSettings = []

        for exercise in self.frameWork['settings']['access']['exercises']['main']['displayed']['names']:
            if not(exercise in self.runData.keys()):
                self.runData[exercise] = dict()

            self.prevStates['srExercises'][exercise] = dict()
            self.prevStates['srExercises'][exercise]['prevExercise'] = dict()
            self.prevStates['srExercises'][exercise]['prevGenerator'] = dict()
            self.prevStates['srExercises'][exercise]['prevPreprocessor'] = dict()
            self.prevStates['srExercises'][exercise]['prevPlayer'] = dict()
            self.prevStates['srExercises'][exercise]['prevSetlist'] = dict()

        self.updateSetlistListBox()

        for setlist in self.frameWork['settings']['access']['setlists']['main']['displayed']['names']:
            self.prevStates['setlists'][setlist] = dict()
            self.prevStates['setlists'][setlist]['prevExercise'] = dict()
            self.prevStates['setlists'][setlist]['prevGenerator'] = dict()
            self.prevStates['setlists'][setlist]['prevPreprocessor'] = dict()
            self.prevStates['setlists'][setlist]['prevPlayer'] = dict()
            self.prevStates['setlists'][setlist]['prevSetlist'] = dict()

        # filling the buttons with life
        self.ui.pbNewRun.clicked.connect(self.iniRun)
        self.ui.pbShowResults.clicked.connect(self.showRundata)
        self.ui.pbRunSetlist.clicked.connect(self.iniRun)
        # filling the gui lists with life
        self.ui.lwExerNameVal.itemSelectionChanged.connect(self.selectExer)
        self.ui.lwExerSetVal.itemSelectionChanged.connect(self.selectExerSettingFromListBox)

        self.ui.lwSetlistNameVal.itemSelectionChanged.connect(self.getSetlist)
        self.ui.lwRuns.itemSelectionChanged.connect(self.selectRundata)

        # filling static menu with life
        if not(self.frameWork['settings']['patientMode']):
            self.ui.menuFileSave.triggered.connect(self.saveRunData)
            self.ui.menuFileLoad.triggered.connect(self.loadRunData)
        self.ui.menuFileUserData.triggered.connect(self.callUserDataGui)

        self.writeIniFile()

        self.readMasterlist()
        if self.curMasterlist['settings']['masterlistStart']:
            title = _translate("MainWindow",
                             'Starting tasks?', None)
            question = _translate("MainWindow",
                             'The next task will be started. Press OK to continue', None)

            quest = CICoachDialog(self, title, question,'question')
            answer = quest.returnButton()
            if answer == QtWidgets.QMessageBox.Yes:
                status, msg = self.checkMasterList()
                if status:
                    self.curMasterlist['settings']['active'] = True

                    self.iniRun()

                    self.updateFilter(self.user['difficulty'])
                    self.updateExerciseListBox()
                    self.updateExerciseSettingsListBox()
                else:
                    msg = _translate("MainWindow",
                                          'Could not run masterlist. Check failed.', None)
                    self.dPrint(msg, 0, guiMode=True)
            else:
                self.dPrint('Aborting masterlist and closing CICoachLab.', 0)
                self.deleteLater()

        # The flag indicates if the, user input gui widgets are disabled or enabled in the functions
        # self.disableExerciseGui() or self.enableExerciseGui(). Which kinds of gui elements are disabled
        # are defined in self.checkForInputWidgets().
        self.blockUserInput = False


        # temporary storing  place to store temporary variable
        # but first of all handles to handles of widgets of matplotlib
        self.temp = dict()


    def showAboutDialog(self):
        """!
        Showing about dialog!
        """

        # TODO: update link to reprository
        QtWidgets.QMessageBox.about(self,
                                    _translate("MainWindow", "About CICoachLab", None),
                                    _translate("MainWindow",
                                               "This is CICoachLab version. 0.8<br><br>" +
                                               "It is published under the  GPL license version 3 at " +
                                               "<a href='https://github.com/'> github </a>.<br><br>" +
                                               "Loaded packages or other dependencies may be licensed differently." +
                                               "<br><br><br>" +
                                               "Author:<br>" +
                                               "Daniel Leander <visdan at web.de><br><br>", None))


    def getMasterVolume(self):
        """!
        This function returns the current master volue as integer in percent
        """

        if self.frameWork['settings']['system']['sysname'] == 'Windows':
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            #comtypes.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            vol = int(np.round((volume.GetMasterVolumeLevelScalar() * 100)))  # 0 to 1
            #comtypes.CoUninitialize()
            return int(vol)
        elif self.frameWork['settings']['system']['sysname'] == 'Linux':
            return int(re.sub('%','', subprocess.check_output(
                '''awk -F"[][]" '/dB/ { print $2 }' <(amixer sget Master) ''', shell=True,
                executable='/bin/bash', encoding='utf-8')))


    def setMasterVolume(self, vol):
        """!
        This function sets the  master value to vol.
        The volume parameter vol is provided in percent.

        The module ctypes crashes if windows 7 is used.
        """

        if self.frameWork['settings']['system']['sysname'] == 'Windows':
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(vol/100, None)
            CoUninitialize()
        elif self.frameWork['settings']['system']['sysname'] == 'Linux':
            subprocess.call("amixer sset 'Master' " + str(vol) + "%", shell=True)


    def __enter__(self):
        """!
        This function is doing nothing but to return self. It allows the initialzation of the class with "with"
        """
        return self


    def __exit__(self, exc_type, exc_value, tb):
        """!
        The destructor of the CICoachLab closes the debug file.

        The destructor __del__ is avoided, since it is called at undefined times/before or after the destruction of
        other classes. E.g. ConfigObj could not be used to handle the shutdown in the __del__ destructor.
        """

        self.dPrint('__exit__()', 2)

        if self.frameWork['settings']['patientMode']:
            self.saveRunData(filename=self.frameWork['settings']['patientSavingFile'])
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            # return False # uncomment to pass exception through

        # cleanup of exercise, generator, preprocessor, player and setlist
        self.iniExercise(exerName='')
        self.iniSubmodule('generator', submoduleName='')
        self.iniSubmodule('preprocessor',  submoduleName='')
        self.iniSubmodule('player',  submoduleName='')


        self.frameWork['settings']['dailyCumulatedRunTime'] = \
            self.frameWork['settings']['sessionCumulatedRunTime'] + self.frameWork['settings']['dailyCumulatedRunTime']

        self.writeIniFile()
        if not(self.frameWork['settings']['debug']['debuggingFileHandle'] == None):
            self.frameWork['settings']['debug']['debuggingFileHandle'].close()
            # reset closed handle to zero for correct handling in self.dPrint()
            self.frameWork['settings']['debug']['debuggingFileHandle'] = None
            # return False # uncomment to pass exception through

        source = self.frameWork['settings']['debug']['debuggingTempFile']
        destination = self.frameWork['settings']['debug']['debuggingFile']
        if destination and (destination != source) and os.path.isfile(source):
            try:
                status, temp = self.moveLogFile(source, destination)
                if status == 0:
                    debuggingTempFileBackup = self.frameWork['settings']['debug']['debuggingTempFileBackup']
                    if debuggingTempFileBackup:
                        os.remove(debuggingTempFileBackup)
                        self.frameWork['settings']['debug']['debuggingTempFileBackup'] = ''
            except:
                msg = _translate("MainWindow",
                                 'Could not move the log file from {:s} to {:s}. Please contact your admininstrator.'.format(
                                     source, destination), None)
                self.dPrint(msg, 0, guiMode=True)
                return False

        if self.frameWork['settings']['fixMasterVolume']:
            self.setMasterVolume(self.oldMasterVol)

        self.dPrint('Leaving __exit__()', 2)
        return True


    def showInformationDialog(self, msg, modal=False):
        """!
        This function generates a information dialog where the modality (modal/nonmodal) can be defined.
        """

        infoDialog = InformationDialog(msg=msg)
        infoDialog.setModal(modal)
        if modal == False:
            infoDialog.setWindowModality(QtCore.Qt.NonModal)
        infoDialog.exec()
        self.dPrint(msg, 0)
        return infoDialog


    def initializeToDefaults(self, mode='all'):
        """!
        The default settings will be set.

            keyword arguments:
            mode -- initialize all are some settings (default 'all')
                    Possible modes are
                    'all' or
                    'frameWork', 'calibration', 'debug',
                    'curExercise', 'curExerciseSettings',
                    'curPreprocessor', 'curPreprocessorSettings',
                    'curPlayer', 'curPlayerSettings',
                    'curGenerator', 'curGeneratorSettings'
                    'curRunData', 'runData', 'user', 'curSetlist',

        This function will be used to initialize mandatory fields of the generator, preprocessor, player and the
        exercise.
        """

        if hasattr(self, 'frameWork'):
            self.dPrint('initializeToDefaults()', 2)
        else:
            # do not use self.dPrint at first call in CICoachLab.__init__() because the required debug parameters have
            # not been set yet
            print('initializeToDefaults()')

        pwd = os.getcwd()
        if mode == 'frameWork' or mode == 'all':
            self.frameWork = dict()

            self.frameWork['temp'] = dict()

            self.frameWork['temp']['presentationTime'] = None
            self.frameWork['temp']['reactionTimeAfterPresentation'] = None
            self.frameWork['temp']['dPrintItemNumber'] = 0
            # if a run of an exercise is active it is set to True in self.iniRun()
            # if a single or the last run is finished it is set to False in self.closeDownRun()
            self.frameWork['temp']['activeRun'] = False

            self.frameWork['settings'] = dict()
            self.frameWork['settings']['version'] = '0.3'
            self.frameWork['settings']['iniFile'] = os.path.join(pwd, 'CICoachLab.ini')
            self.frameWork['settings']['iniFileConfig'] = []
            self.frameWork['settings']['filterFile'] = os.path.join(pwd, 'filter.ini')
            self.frameWork['settings']['filterFileConfig'] = []

            self.frameWork['settings']['debug'] = dict()
            self.frameWork['settings']['debug']['mode'] = False
            # A high verbosity is set at startup to enable debugging at startup as long as the verbosity cannot be
            # set by self.readIniFile() which is called after self.initializeToDefaults()
            self.frameWork['settings']['debug']['verbosityThreshold'] = 5
            # deactivate writing debugging information to file by default
            self.frameWork['settings']['debug']['debuggingFile'] = ''
            # if not debuggingTempFile = debuggingFile use a temporary debug file which is moved to final destination
            # later on
            self.frameWork['settings']['debug']['debuggingTempFile'] = ''
            # if debuggingTempFile of a previous session is found/was not deleted a backup file will be generated
            # before writing to new debuggingTempFile, 'debuggingTempFileBackup' will be removed in self.__exit__()
            # after the successfull moving of 'debuggingTempFile' to 'debuggingFile'
            self.frameWork['settings']['debug']['debuggingTempFileBackup'] = ''
            # the file handle will be opened in self.dPrint() once at the first call with a defined file name in
            # self.frameWork['settings']['debug']['debuggingTempFile'] which may be set in self.readIniFile() to
            # self.frameWork['settings']['debug']['debuggingFile']
            self.frameWork['settings']['debug']['debuggingFileHandle'] = None
            self.frameWork['settings']['debug']['demoMode'] = False
            self.frameWork['settings']['debug']['noPLotMode'] = False

            self.frameWork['path'] = dict()
            self.frameWork['path']['pwd'] = pwd
            self.frameWork['path']['exercises'] = os.path.join(pwd, 'exercises')
            self.frameWork['path']['player'] = os.path.join(pwd, 'player')
            self.frameWork['path']['generators'] = os.path.join(pwd, 'generators')
            self.frameWork['path']['preprocessors'] = os.path.join(pwd, 'preprocessors')
            self.frameWork['path']['setlists'] = os.path.join(pwd, 'setlists')
            self.frameWork['path']['masterlists'] = os.path.join(pwd, 'masterlists')
            self.frameWork['path']['lib'] = os.path.join(pwd, 'lib')
            self.frameWork['path']['locales'] = os.path.join(pwd, 'locales')
            # adding path to python library
            self.addingPath('frameWork')

            self.frameWork['settings']['saving'] = dict()
            self.frameWork['settings']['saving']['filename'] = 'results.cid'
            self.frameWork['settings']['saving']['format'] = 'pickle'
            self.frameWork['settings']['saving']['anonymous'] = False

            self.frameWork['settings']['exerciseFrameGeometry'] = [160, 10, 761, 711]
            self.frameWork['settings']['autoBackupResults'] = False
            self.frameWork['settings']['lastSavingPath'] = ''
            # will be set at end of run
            self.frameWork['settings']['lastExercise'] = ''
            self.frameWork['settings']['lastExerciseSettings'] = ''
            self.frameWork['settings']['lastGenerator'] = ''
            self.frameWork['settings']['lastGeneratorSettings'] = ''
            self.frameWork['settings']['lastPreprocessor'] = ''
            self.frameWork['settings']['lastPreprocessorSettings'] = ''
            self.frameWork['settings']['lastPlayer'] = ''
            self.frameWork['settings']['lastPlayerSettings'] = ''

            self.frameWork['settings']['lastSetlist'] = ''
            self.frameWork['settings']['dualScreen'] = False
            # the patient calls CICoachLab
            self.frameWork['settings']['patientMode'] = False
            # the patient coach calls CICoachLab
            self.frameWork['settings']['coachMode'] = False
            self.frameWork['settings']['coachBackupPath'] = ''
            self.frameWork['settings']['useSettingsFromLoadedData'] = False
            self.frameWork['settings']['expertSettingsMode'] = False

            self.frameWork['settings']['expertMode'] = False
            self.frameWork['settings']['patientSavingFile'] = ''
            self.frameWork['settings']['bitlockerMode'] = False
            self.frameWork['settings']['bitlockerDevice'] = ''
            self.frameWork['settings']['bitlockerPathClear'] = ''
            self.frameWork['settings']['bitlockerPathEncrypt'] = ''
            self.frameWork['settings']['studyMode'] = ''
            self.frameWork['settings']['masterlistFileConfig'] = None
            self.frameWork['settings']['exerciseFrameGeometry'] = [160, 10, 761, 711]
            self.frameWork['settings']['mainFramegeometry'] = [160, 10, 761, 711]
            self.frameWork['settings']['lastRunEndTime'] = ''
            # measured cumulated time running exercises
            self.frameWork['settings']['dailyCumulatedRunTime'] = 0
            # maximum cumulated time for running exercises
            self.frameWork['settings']['maxDailyCumulatedRunTime'] = 86400
            self.frameWork['settings']['currentSessionStartTime'] = ''
            self.frameWork['settings']['muteSignal'] = False
            self.frameWork['settings']['sessionCumulatedRunTime'] = 0

            self.frameWork['settings']['localization'] = 'en_de'  # without extension ".qm"
            self.frameWork['settings']['fixMasterVolume'] = False
            self.frameWork['settings']['masterVolumeValue'] = None
            self.frameWork['settings']['ignoreFilterFile'] = False

            self.frameWork['settings']['usePrevStates'] = False

            self.frameWork['settings']['system'] = dict()

            self.frameWork['settings']['system']['system'] = platform.uname()
            self.frameWork['settings']['system']['sysname'] = platform.system()  # Linux/Windows
            self.frameWork['settings']['system']['pythonVersion'] = sys.version
            self.frameWork['settings']['system']['qtVersion'] = QtCore.qVersion()
            self.frameWork['settings']['system']['screenResolution'] = self.app.desktop().screenGeometry()
            self.frameWork['systemCheck'] = False

            self.frameWork['functions'] = dict()
            self.frameWork['functions']['iniRun'] = self.iniRun
            self.frameWork['functions']['intraRun'] = self.intraRun
            self.frameWork['functions']['closeDownRun'] = self.closeDownRun

            self.frameWork['gui'] = dict()

            self.frameWork['gui']['menus'] = list()
            self.frameWork['gui']['buttons'] = list()
            self.frameWork['gui']['lists'] = list()

        if mode == 'calibration' or mode == 'all':
            self.setDefaultCalibration('frameWork', 'level')

        if mode == 'access' or mode == 'all':
            self.frameWork['settings']['access'] = dict()

            template = dict()
            template['names'] = list()
            template['labels'] = list()
            template['infos'] = list()
            template['difficulties'] = list()
            template['visibles'] = list()
            template['filterDefinition'] = list()

            moduleNamesFiles = ['exercises', 'generators', 'preprocessors', 'player', 'setlists']
            # looping through different modules
            for modeItem in moduleNamesFiles:
                self.frameWork['settings']['access'][modeItem] = dict()
                self.frameWork['settings']['access'][modeItem]['main'] = dict()
                self.frameWork['settings']['access'][modeItem]['settings'] = dict()

                self.frameWork['settings']['access'][modeItem]['main']['available'] = deepcopy(template)
                self.frameWork['settings']['access'][modeItem]['main']['displayed'] = deepcopy(template)

            # the list of exercises which contains the settings and its parameters is generated in self.readFilter()
            # self.frameWork['settings'] ['access'][exerciseName]
            # self.frameWork['settings'] ['access'][exerciseName]['settings']
            # self.frameWork['settings'] ['access'][exerciseName]['settings']['available']['names']
            # self.frameWork['settings'] ['access'][exerciseName]['settings']['available']['labels']
            # self.frameWork['settings'] ['access'][exerciseName]['settings']['displayed']['names']
            # self.frameWork['settings'] ['access'][exerciseName]['settings']['displayed']['labels']

            # list of exercises defining the python file name without .py extension
            # self.exercises > self.frameWork['settings']['access']['exercise']['displayed']
            # self.frameWork['settings'] ['access']['exercises']
            # self.frameWork['settings'] ['access']['exercises']['available']['names']
            # self.frameWork['settings'] ['access']['exercises']['available']['labels']
            # may differ from run to run, depending on the conditions which are met.  It maybe the same as the field ['exercises']
            # self.frameWork['settings'] ['access']['exercises']['displayed']
            # self.frameWork['settings'] ['access']['exercises']['displayed']['names']
            # self.frameWork['settings'] ['access']['exercises']['displayed']['labels']

            # self.frameWork['settings'] ['access'][playerName]
            # self.frameWork['settings'] ['access'][playerName]['settings']
            # self.frameWork['settings'] ['access'][playerName]['settings']['available']['names']
            # self.frameWork['settings'] ['access'][playerName]['settings']['available']['labels']
            # self.frameWork['settings'] ['access'][playerName]['settings']['displayed']['names']
            # self.frameWork['settings'] ['access'][playerName]['settings']['displayed']['labels']
            # the display of generators, preprocessors and player may depend on the exercise
            # self.frameWork['settings'] ['access'][playerName]['settings']['displayed']['dependency']

        if mode == 'curExercise' or mode == 'all':
            # struct which contains handles current exercise
            self.curExercise = dict()
            # setting mandatory fields / default exercis

            self.curExercise['gui'] = dict()
            self.curExercise['gui']['menu'] = []
            self.curExercise['gui']['exerWidgets'] = []
            self.curExercise['results'] = None
            self.curExercise['selectedRunData'] = None

            self.curExercise['functions'] = dict()
            self.curExercise['functions']['constructor']        = None
            self.curExercise['functions']['prepareRun']         = None
            self.curExercise['functions']['quitRun']            = None
            self.curExercise['functions']['displayResults']     = None
            self.curExercise['functions']['destructor']         = None
            self.curExercise['functions']['checkConditions']    = None
            self.curExercise['functions']['checkParameters']    = None
            self.curExercise['functions']['settingsDefault']    = None
            self.curExercise['functions']['settingsLoading']    = None
            self.curExercise['functions']['settingsGui']        = None
            self.curExercise['functions']['eraseExerciseGui']   = None
            self.curExercise['functions']['getPlayerStatus']    = None

            self.curExercise['path'] = dict()
            self.curExercise['path']['base'] = ''
            self.curExercise['path']['presets'] = ''
            self.curExercise['path']['results'] = ''
            self.curExercise['path']['analysis'] = ''

            # For debugging and system testing purposes only
            self.curExercise['handle'] = None

        if mode == 'curExercise' or mode == 'curExerciseSettings' or mode == 'all':
            # setting mandatory fields / default exercis

            self.curExercise['settings'] = dict()
            self.curExercise['settings']['version'] = None
            self.curExercise['settings']['exerciseName'] = ''
            self.curExercise['settings']['settingsName'] = ''
            self.curExercise['settings']['settingsSaved'] = False
            self.curExercise['settings']['player'] = ''
            self.curExercise['settings']['playerSettings'] = ''
            self.curExercise['settings']['preprocessor'] = ''
            self.curExercise['settings']['preprocessorSettings'] = ''
            self.curExercise['settings']['generator'] = ''
            self.curExercise['settings']['generatorSettings'] = ''
            self.curExercise['settings']['runRepetitions'] = 0
            self.curExercise['settings']['afterRunDisplay'] = True
            self.curExercise['settings']['externalWindow'] = True
            self.curExercise['settings']['comment'] = ''
            # conditions definition as checked in self.checkConditions() when called in the exercise
            self.curExercise['settings']['prerunCondition'] = ''
            self.curExercise['settings']['postrunCondition'] = ''

            self.curExercise['settingLimits'] = dict()
            self.curExercise['settingLimits']['exerciseName'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['exerciseName']['type'] = 'string'
            self.curExercise['settingLimits']['exerciseName']['mandatory'] = True
            self.curExercise['settingLimits']['exerciseName']['range'] = []
            self.curExercise['settingLimits']['exerciseName']['editable'] = False
            self.curExercise['settingLimits']['exerciseName']['unit'] = ''
            self.curExercise['settingLimits']['exerciseName']['label'] = \
                _translate("MainWindow",'Exercise name', None)
            self.curExercise['settingLimits']['exerciseName']['default'] = ''

            self.curExercise['settingLimits']['settingsName'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['settingsName']['type'] = 'string'
            self.curExercise['settingLimits']['settingsName']['mandatory'] = True
            self.curExercise['settingLimits']['settingsName']['range'] = []
            self.curExercise['settingLimits']['settingsName']['editable'] = False
            self.curExercise['settingLimits']['settingsName']['unit'] = ''
            self.curExercise['settingLimits']['settingsName']['label'] = \
                _translate("MainWindow", 'Settings name', None)
            self.curExercise['settingLimits']['settingsName']['default'] = ''

            self.curExercise['settingLimits']['player'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['player']['type'] = 'string'
            self.curExercise['settingLimits']['player']['mandatory'] = True
            self.curExercise['settingLimits']['player']['range'] = []
            self.curExercise['settingLimits']['player']['editable'] = True
            self.curExercise['settingLimits']['player']['unit'] = ''
            self.curExercise['settingLimits']['player']['label'] = \
                _translate("MainWindow", 'Players name', None)
            self.curExercise['settingLimits']['player']['default'] = ''

            self.curExercise['settingLimits']['playerSettings'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['playerSettings']['type'] = 'string'
            self.curExercise['settingLimits']['playerSettings']['mandatory'] = False
            self.curExercise['settingLimits']['playerSettings']['range'] = []
            self.curExercise['settingLimits']['playerSettings']['editable'] = True
            self.curExercise['settingLimits']['playerSettings']['unit'] = ''
            self.curExercise['settingLimits']['playerSettings']['label'] = \
                _translate("MainWindow", 'Player settings name', None)
            self.curExercise['settingLimits']['playerSettings']['default'] = 'default'

            self.curExercise['settingLimits']['generator'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['generator']['type'] = 'string'
            self.curExercise['settingLimits']['generator']['mandatory'] = True
            self.curExercise['settingLimits']['generator']['range'] = []
            self.curExercise['settingLimits']['generator']['editable'] = True
            self.curExercise['settingLimits']['generator']['unit'] = ''
            self.curExercise['settingLimits']['generator']['label'] = \
                _translate("MainWindow", 'Generator name', None)
            self.curExercise['settingLimits']['generator']['default'] = ''

            self.curExercise['settingLimits']['generatorSettings'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['generatorSettings']['type'] = 'string'
            self.curExercise['settingLimits']['generatorSettings']['mandatory'] = False
            self.curExercise['settingLimits']['generatorSettings']['range'] = []
            self.curExercise['settingLimits']['generatorSettings']['editable'] = True
            self.curExercise['settingLimits']['generatorSettings']['unit'] = ''
            self.curExercise['settingLimits']['generatorSettings']['label'] = \
                _translate("MainWindow", 'Generator settings name', None)
            self.curExercise['settingLimits']['generatorSettings']['default'] = 'default'

            self.curExercise['settingLimits']['afterRunDisplay'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['afterRunDisplay']['type'] = 'bool'
            self.curExercise['settingLimits']['afterRunDisplay']['mandatory'] = False
            self.curExercise['settingLimits']['afterRunDisplay']['range'] = [True, False]
            self.curExercise['settingLimits']['afterRunDisplay']['comboBoxStyle'] = True
            self.curExercise['settingLimits']['afterRunDisplay']['editable'] = True
            self.curExercise['settingLimits']['afterRunDisplay']['unit'] = ''
            self.curExercise['settingLimits']['afterRunDisplay']['label'] = \
                _translate("MainWindow", 'Display of results', None)
            self.curExercise['settingLimits']['afterRunDisplay']['default'] = True

            self.curExercise['settingLimits']['externalWindow'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['externalWindow']['type'] = 'bool'
            self.curExercise['settingLimits']['externalWindow']['mandatory'] = False
            self.curExercise['settingLimits']['externalWindow']['range'] = [True, False]
            self.curExercise['settingLimits']['externalWindow']['comboBoxStyle'] = True
            self.curExercise['settingLimits']['externalWindow']['editable'] = True
            self.curExercise['settingLimits']['externalWindow']['displayed'] = False
            self.curExercise['settingLimits']['externalWindow']['unit'] = ''
            self.curExercise['settingLimits']['externalWindow']['label'] = \
                _translate("MainWindow", 'External Display', None)
            self.curExercise['settingLimits']['externalWindow']['default'] = True

            self.curExercise['settingLimits']['comment'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['comment']['type'] = 'string'
            self.curExercise['settingLimits']['comment']['mandatory'] = False
            self.curExercise['settingLimits']['comment']['range'] = []
            self.curExercise['settingLimits']['comment']['editable'] = True
            self.curExercise['settingLimits']['comment']['unit'] = ''
            self.curExercise['settingLimits']['comment']['label'] = \
                _translate("MainWindow", 'Comments', None)
            self.curExercise['settingLimits']['comment']['default'] = ''

            self.curExercise['settingLimits']['prerunCondition'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['prerunCondition']['type'] = 'string'
            self.curExercise['settingLimits']['prerunCondition']['mandatory'] = False
            self.curExercise['settingLimits']['prerunCondition']['range'] = []
            self.curExercise['settingLimits']['prerunCondition']['editable'] = True
            self.curExercise['settingLimits']['prerunCondition']['unit'] = ''
            self.curExercise['settingLimits']['prerunCondition']['label'] = \
                _translate("MainWindow", 'prerunCondition', None)
            self.curExercise['settingLimits']['prerunCondition']['default'] = ''

            self.curExercise['settingLimits']['postrunCondition'] = self.setSettingLimitsTemplate()
            self.curExercise['settingLimits']['postrunCondition']['type'] = 'string'
            self.curExercise['settingLimits']['postrunCondition']['mandatory'] = False
            self.curExercise['settingLimits']['postrunCondition']['range'] = []
            self.curExercise['settingLimits']['postrunCondition']['editable'] = False
            self.curExercise['settingLimits']['postrunCondition']['unit'] = ''
            self.curExercise['settingLimits']['postrunCondition']['label'] = \
                _translate("MainWindow", 'postrunCondition', None)
            self.curExercise['settingLimits']['postrunCondition']['default'] = ''


        if mode == 'curPreprocessor' or mode == 'all':
            self.curPreprocessor = dict()

            self.curPreprocessor['gui'] = dict()
            self.curPreprocessor['gui']['menu'] = []

            self.curPreprocessor['functions'] = dict()
            self.curPreprocessor['functions']['constructor'] = None
            self.curPreprocessor['functions']['destructor'] = None
            self.curPreprocessor['functions']['run'] = None
            self.curPreprocessor['functions']['settingsLoading'] = None
            self.curPreprocessor['functions']['settingsDefault'] = None
            self.curPreprocessor['functions']['settingsGui'] = None

            # For debugging and system testing purposes only
            self.curPreprocessor['handle'] = None

            self.curPreprocessor['path'] = dict()
            self.curPreprocessor['path']['base'] = ''
            self.curPreprocessor['path']['presets'] = ''

        if mode == 'curPreprocessor' or mode == 'curPreprocessorSettings' or mode == 'all':

            self.curPreprocessor['settings'] = dict()
            self.curPreprocessor['settings']['preprocessorName'] = ''
            self.curPreprocessor['settings']['settingsName'] = ''
            self.curPreprocessor['settings']['settingsSaved'] = False
            self.curPreprocessor['settings']['comment'] = ''
            # for intermediate deactivation of the preprocessor
            # if it is set to True the preprocessing will be deactivated at playback
            self.curPreprocessor['settings']['deactivate'] = False


            self.curPreprocessor['settingLimits'] = dict()
            self.curPreprocessor['settingLimits']['preprocessorName'] = self.setSettingLimitsTemplate()
            self.curPreprocessor['settingLimits']['preprocessorName']['type'] = 'string'
            self.curPreprocessor['settingLimits']['preprocessorName']['mandatory'] = False
            self.curPreprocessor['settingLimits']['preprocessorName']['range'] = []
            self.curPreprocessor['settingLimits']['preprocessorName']['editable'] = False
            self.curPreprocessor['settingLimits']['preprocessorName']['unit'] = ''
            self.curPreprocessor['settingLimits']['preprocessorName']['label'] = ''
            self.curPreprocessor['settingLimits']['preprocessorName']['default'] = ''

            self.curPreprocessor['settingLimits']['settingsName'] = self.setSettingLimitsTemplate()
            self.curPreprocessor['settingLimits']['settingsName']['type'] = 'string'
            self.curPreprocessor['settingLimits']['settingsName']['mandatory'] = False
            self.curPreprocessor['settingLimits']['settingsName']['range'] = []
            self.curPreprocessor['settingLimits']['settingsName']['editable'] = False
            self.curPreprocessor['settingLimits']['settingsName']['unit'] = ''
            self.curPreprocessor['settingLimits']['settingsName']['label'] = ''
            self.curPreprocessor['settingLimits']['settingsName']['default'] = 'default'

            self.curPreprocessor['settingLimits']['comment'] = self.setSettingLimitsTemplate()
            self.curPreprocessor['settingLimits']['comment']['type'] = 'string'
            self.curPreprocessor['settingLimits']['comment']['mandatory'] = False
            self.curPreprocessor['settingLimits']['comment']['range'] = []
            self.curPreprocessor['settingLimits']['comment']['editable'] = True
            self.curPreprocessor['settingLimits']['comment']['unit'] = ''
            self.curPreprocessor['settingLimits']['comment']['label'] = ''
            self.curPreprocessor['settingLimits']['comment']['default'] = 'default'

            self.curPreprocessor['settingLimits']['deactivate'] = self.setSettingLimitsTemplate()
            self.curPreprocessor['settingLimits']['deactivate']['type'] = 'bool'
            self.curPreprocessor['settingLimits']['deactivate']['mandatory'] = False
            self.curPreprocessor['settingLimits']['deactivate']['range'] = []
            self.curPreprocessor['settingLimits']['deactivate']['editable'] = False
            self.curPreprocessor['settingLimits']['deactivate']['unit'] = ''
            self.curPreprocessor['settingLimits']['deactivate']['label'] = 'intermediate deacivation '
            self.curPreprocessor['settingLimits']['deactivate']['default'] = False

        if mode == 'curPlayer' or mode == 'all':
            self.curPlayer = dict()

            self.curPlayer['gui'] = dict()
            self.curPlayer['gui']['menu'] = []

            self.curPlayer['functions'] = dict()
            self.curPlayer['functions']['constructor'] = None
            self.curPlayer['functions']['destructor'] = None
            self.curPlayer['functions']['run'] = None
            self.curPlayer['functions']['settingsLoading'] = None
            self.curPlayer['functions']['settingsDefault'] = None
            self.curPlayer['functions']['settingsGui'] = None

            # For debugging and system testing purposes only
            self.curPlayer['handle'] = None

            self.curPlayer['path'] = dict()
            self.curPlayer['path']['base'] = ''
            self.curPlayer['path']['presets'] = ''

        if mode == 'curPlayer' or mode == 'curPlayerSettings' or mode == 'all':

            self.curPlayer['settings'] = dict()
            self.curPlayer['settings']['playerName'] = ''
            self.curPlayer['settings']['settingsName'] = ''
            self.curPlayer['settings']['settingsSaved'] = False
            self.curPlayer['settings']['visualPreparation'] = False
            self.curPlayer['settings']['visualPreparationTime'] = 0.0
            self.curPlayer['settings']['comment'] = ''

            self.curPlayer['settingLimits'] = dict()

            self.curPlayer['settingLimits']['playerName'] = self.setSettingLimitsTemplate()
            self.curPlayer['settingLimits']['playerName']['type'] = 'string'
            self.curPlayer['settingLimits']['playerName']['mandatory'] = True
            self.curPlayer['settingLimits']['playerName']['range'] = []
            self.curPlayer['settingLimits']['playerName']['editable'] = False
            self.curPlayer['settingLimits']['playerName']['unit'] = ''
            self.curPlayer['settingLimits']['playerName']['label'] = 'Player name'
            self.curPlayer['settingLimits']['playerName']['default'] = ''

            self.curPlayer['settingLimits']['settingsName'] = self.setSettingLimitsTemplate()
            self.curPlayer['settingLimits']['settingsName']['type'] = 'string'
            self.curPlayer['settingLimits']['settingsName']['mandatory'] = True
            self.curPlayer['settingLimits']['settingsName']['range'] = []
            self.curPlayer['settingLimits']['settingsName']['editable'] = True
            self.curPlayer['settingLimits']['settingsName']['unit'] = ''
            self.curPlayer['settingLimits']['settingsName']['label'] = 'Players settings name'
            self.curPlayer['settingLimits']['settingsName']['default'] = 'default'

            self.curPlayer['settingLimits']['comment'] = self.setSettingLimitsTemplate()
            self.curPlayer['settingLimits']['comment']['type'] = 'string'
            self.curPlayer['settingLimits']['comment']['mandatory'] = False
            self.curPlayer['settingLimits']['comment']['range'] = []
            self.curPlayer['settingLimits']['comment']['editable'] = True
            self.curPlayer['settingLimits']['comment']['unit'] = ''
            self.curPlayer['settingLimits']['comment']['label'] = 'Comments'
            self.curPlayer['settingLimits']['comment']['default'] = ''

        if mode == 'curGenerator' or mode == 'all':
            self.curGenerator = dict()

            self.curGenerator['gui'] = dict()
            self.curGenerator['gui']['menu'] = []

            self.curGenerator['path'] = dict()
            self.curGenerator['path']['base'] = ''
            self.curGenerator['path']['presets'] = ''

            self.curGenerator['functions'] = dict()
            self.curGenerator['functions']['constructor'] = None
            self.curGenerator['functions']['destructor'] = None
            self.curGenerator['functions']['run'] = None
            self.curGenerator['functions']['settingsLoading'] = None
            self.curGenerator['functions']['settingsDefault'] = None
            self.curGenerator['functions']['settingsGui'] = None

            # For debugging and system testing purposes only
            self.curGenerator['handle'] = None

        if mode == 'curGenerator' or mode == 'curGeneratorSettings' or mode == 'all':

            self.curGenerator['settings'] = dict()
            self.curGenerator['settings']['generatorName'] = ''
            self.curGenerator['settings']['settingsName'] = ''
            self.curGenerator['settings']['settingsSaved'] = False
            self.curGenerator['settings']['comment'] = ''

            self.curGenerator['settingLimits'] = dict()
            self.curGenerator['settingLimits']['generatorName'] = self.setSettingLimitsTemplate()
            self.curGenerator['settingLimits']['generatorName']['type'] = 'string'
            self.curGenerator['settingLimits']['generatorName']['mandatory'] = True
            self.curGenerator['settingLimits']['generatorName']['range'] = []
            self.curGenerator['settingLimits']['generatorName']['editable'] = False
            self.curGenerator['settingLimits']['generatorName']['unit'] = ''
            self.curGenerator['settingLimits']['generatorName']['label'] = 'Generator name'
            self.curGenerator['settingLimits']['generatorName']['default'] = ''

            self.curGenerator['settingLimits']['settingsName'] = self.setSettingLimitsTemplate()
            self.curGenerator['settingLimits']['settingsName']['type'] = 'string'
            self.curGenerator['settingLimits']['settingsName']['mandatory'] = True
            self.curGenerator['settingLimits']['settingsName']['range'] = []
            self.curGenerator['settingLimits']['settingsName']['editable'] = False
            self.curGenerator['settingLimits']['settingsName']['unit'] = ''
            self.curGenerator['settingLimits']['settingsName']['label'] = 'Generator setting name'
            self.curGenerator['settingLimits']['settingsName']['default'] = 'default'

            self.curGenerator['settingLimits']['comment'] = self.setSettingLimitsTemplate()
            self.curGenerator['settingLimits']['comment']['type'] = 'string'
            self.curGenerator['settingLimits']['comment']['mandatory'] = False
            self.curGenerator['settingLimits']['comment']['range'] = []
            self.curGenerator['settingLimits']['comment']['editable'] = True
            self.curGenerator['settingLimits']['comment']['unit'] = ''
            self.curGenerator['settingLimits']['comment']['label'] = 'Comments'
            self.curGenerator['settingLimits']['comment']['default'] = ''

        if mode == 'curRunData' or mode == 'all':
            # at the end of the current run of the
            # exercise the data will be added to runData
            self.curRunData = dict()
            self.curRunData['time'] = dict()
            self.curRunData['time']['start'] = ''  # time            self.curRunData['time']['end']      = ''  # time
            self.curRunData['time']['duration'] = ''  # time
            self.curRunData['time']['reactionTime'] = ''  # time

            self.curRunData['runIDX'] = None


            self.curRunData['user'] = dict()  # data of user which has been running this exercise
            self.curRunData['exercise'] = dict()

            self.curRunData['results'] = None
            self.curRunData['itemIdx'] = 0
            # a run of an exercise was completed
            self.curRunData['runCompleted'] = False
            # the statusMessage tracks why a run was not completed correctly if a pre-/post(run)condition was not met
            self.curRunData['statusMessage'] = ''
            # a run of an exercise was completed successfully
            # By setting the value to True exercises don't have to handle the 'runAccomplished' flag
            self.curRunData['runAccomplished'] = True
            # The conditions which have to be met can be defined by the settings
            # curExercises['settings']['postrunCondition'] can optionally be defined as string in the settings of the
            # exercise.  The string has to define a valid python expression which returns a boolean value.
            # ['settings']['postrunCondition'] can also define a python script which can run a more complex
            # check. The script has to provide a function which returns a boolean value. The script hast to be found
            # in the conditions directory which is found in the exercise base path.
            # If the postrunCondition is defined the exercise has to provide
            # a call to self.parHandle.checkConditions(self).
            # The function knows the exercise handle and the CICoachLab handle, which allows powerfull condition checks.
            # If an unvalid script or python expression is defined ['settings']['postrunCondition'] defaults
            # to ['settings']['postrunCondition'] = True

            self.curRunData['settings'] = dict()
            self.curRunData['settings']['exercise'] = None
            self.curRunData['settings']['player'] = None
            self.curRunData['settings']['generator'] = None
            self.curRunData['settings']['preprocessor'] = None
            self.curRunData['settings']['setlist'] = None
            self.curRunData['settings']['frameWork'] = None
            self.curRunData['settings']['masterlist'] = None
            self.curRunData['calibration'] = dict()
            self.curRunData['calibration']['frameWork'] = None
            self.curRunData['calibration']['generator'] = None
            self.curRunData['calibration']['preprocessor'] = None
            self.curRunData['calibration']['player'] = None



            self.curRunData['setlistName'] = ''
            self.curRunData['setlistIdx'] = -1

            self.curRunData['masterlistName'] = ''
            self.curRunData['masterlistIdx'] = -1


        if mode == 'runData' or mode == 'all':
            # at the end of each run of the exercise the data will be added to runData. For each exercise a dictionary
            # will be added4
            self.runData = dict()
            # a global runDataCounter is used for all exercises
            self.runDataCounter = 0

        if mode == 'user' or mode == 'all':
            # place to set and find user data

            self.user = dict()
            self.user['forname'] = ''
            self.user['lastname'] = ''
            self.user['birthday'] = '01.01.1900'

            self.user['gender'] = ''
            # id as provided in patient records, if used in a clinical setup
            self.user['patientID'] = ''
            self.user['comment'] = ''
            # difficulty from 5 (very easy) to 1 (very difficult), -42 shows every possible module
            self.user['difficulty'] = '3'
            # optional id, when a subject takes part in a study
            self.user['subjectID'] = ''
            self.user['studyCheck'] = ''
            self.user['vertigo'] = ''

            self.user['left'] = dict()
            self.user['left']['treatment'] = ''
            self.user['left']['deafBeforeCI'] = ''
            self.user['left']['deafReason'] = ''
            self.user['left']['deafeningProgress'] = ''
            self.user['left']['tinnitus'] = ''

            self.user['right'] = dict()
            self.user['right']['treatment'] = ''
            self.user['right']['deafBeforeCI'] = ''
            self.user['right']['deafReason'] = ''
            self.user['right']['deafeningProgress'] = ''
            self.user['right']['tinnitus'] = ''


            # be aware: its also defined in UserDataDialog.ui
            # possible handling of allowed limits of variable, might be useful for
            # alternative forced choice determination of frequency thresholds and handling checking of setting (files)
            self.userLimits = dict()

            self.userLimits['forname'] = dict()
            self.userLimits['forname']['mandatory'] = True
            self.userLimits['forname']['type'] = 'string'
            self.userLimits['forname']['editable'] = True
            self.userLimits['forname']['range'] = []
            self.userLimits['forname']['label'] = 'Forname'

            self.userLimits['lastname'] = dict()
            self.userLimits['lastname']['mandatory'] = True
            self.userLimits['lastname']['type'] = 'string'
            self.userLimits['lastname']['editable'] = True
            self.userLimits['lastname']['range'] = []
            self.userLimits['lastname']['label'] = 'Last name'

            self.userLimits['patientID'] = dict()
            self.userLimits['patientID']['mandatory'] = True
            self.userLimits['patientID']['type'] = 'int'
            self.userLimits['patientID']['editable'] = True
            self.userLimits['patientID']['range'] = [0, 9999999999999]
            self.userLimits['patientID']['label'] = 'Patienten-ID'
            self.userLimits['patientID']['information'] = 'Patienten-ID as used in the patients records in the clinical setup'

            self.userLimits['subjectID'] = dict()
            self.userLimits['subjectID']['mandatory'] = False
            self.userLimits['subjectID']['type'] = 'string'
            self.userLimits['subjectID']['editable'] = True
            self.userLimits['subjectID']['range'] = []
            self.userLimits['subjectID']['label'] = 'Subject-ID'
            self.userLimits['subjectID']['information'] = 'Subject-ID if participant takes part in a study'

            self.userLimits['studyCheck'] = dict()
            self.userLimits['studyCheck']['mandatory'] = False
            self.userLimits['studyCheck']['type'] = 'check'
            self.userLimits['studyCheck']['editable'] = True
            self.userLimits['studyCheck']['range'] = []
            self.userLimits['studyCheck']['label'] = 'General study agreement'
            self.userLimits['studyCheck']['information'] = 'Checkmark if subject allows usage of data for studies'

            self.userLimits['gender'] = dict()
            self.userLimits['gender']['mandatory'] = True
            self.userLimits['gender']['type'] = 'date'
            self.userLimits['gender']['editable'] = True
            self.userLimits['gender']['range'] = ['Female', 'Male', 'Diverse']
            self.userLimits['gender']['label'] = 'Gender'
            self.userLimits['gender']['information'] = 'Official genders are "Female", "Male" and "Divers"'

            
            self.userLimits['birthday'] = dict()
            self.userLimits['birthday']['mandatory'] = True
            self.userLimits['birthday']['type'] = 'date'
            self.userLimits['birthday']['editable'] = True
            self.userLimits['birthday']['range'] = ['01.01.1900', '01.01.2022']
            self.userLimits['birthday']['label'] = 'Birthday'
            self.userLimits['birthday']['information'] = 'Format of birthdate: [day.month.year/DD.MM.YYYY] Possible birthdates lie between 01.01.1900 and 01.01.2022'

            self.userLimits['comment'] = dict()
            self.userLimits['comment']['mandatory'] = False
            self.userLimits['comment']['string'] = 'date'
            self.userLimits['comment']['editable'] = True
            self.userLimits['comment']['range'] = []
            self.userLimits['comment']['label'] = 'Comment'

            self.userLimits['left'] = dict()

            self.userLimits['left']['treatment'] = dict()
            self.userLimits['left']['treatment']['mandatory'] = True
            self.userLimits['left']['treatment']['type'] = 'string'
            self.userLimits['left']['treatment']['editable'] = True
            self.userLimits['left']['treatment']['unit'] = ''
            # defined in UserDataDialog.ui
            # #self.userLimits['left']['treatment']['range'] = ['untreated', 'hearing aid', 'cochlear implantat',
            #                                                   'bone conduction hearing device', 'middle ear implant']
            self.userLimits['left']['treatment']['label'] = 'Treatment'

            self.userLimits['left']['deafBeforeCI'] = dict()
            self.userLimits['left']['deafBeforeCI']['mandatory'] = True
            self.userLimits['left']['deafBeforeCI']['type'] = 'string'
            self.userLimits['left']['deafBeforeCI']['unit'] = 'years'
            self.userLimits['left']['deafBeforeCI']['editable'] = True
            # defined in UserDataDialog.ui
            # self.userLimits['left']['deafBeforeCI']['range'] = [' < 1 years', '1 - 4 years',
            #                                                     '5 - 10 years', '11 - 20 years', ' 21 - 30 years',
            #                                                     '> 31 years']
            self.userLimits['left']['deafBeforeCI']['label'] = 'Duration of deafness before CI treatment'

            self.userLimits['left']['deafReason'] = dict()
            self.userLimits['left']['deafReason']['mandatory'] = True
            self.userLimits['left']['deafReason']['unit'] = ''
            self.userLimits['left']['deafReason']['type'] = 'string'
            self.userLimits['left']['deafReason']['editable'] = True
            # defined in UserDataDialog.ui
            # self.userLimits['left']['deafReason']['range'] = ['unknown', 'meningitis', 'sudden hearing loss', 'genetic',
            #                                                    'inflamation of the inner ear', 'congenital']
            self.userLimits['left']['deafReason']['label'] = 'Cause of deafness'

            self.userLimits['left']['deafeningProgress'] = dict()
            self.userLimits['left']['deafeningProgress']['mandatory'] = True
            self.userLimits['left']['deafeningProgress']['unit'] = ''
            self.userLimits['left']['deafeningProgress']['type'] = 'string'
            self.userLimits['left']['deafeningProgress']['editable'] = True
            # defined in UserDataDialog.ui
            # self.userLimits['left']['deafeningProgress']['range'] = ['progredient', 'sudden']
            self.userLimits['left']['deafeningProgress']['label'] = 'Progression of hearing loss'

            self.userLimits['right'] = dict()

            self.userLimits['right']['treatment'] = dict()
            self.userLimits['right']['treatment']['mandatory'] = True
            self.userLimits['right']['treatment']['type'] = 'string'
            self.userLimits['right']['treatment']['editable'] = True
            self.userLimits['right']['treatment']['unit'] = ''
            # defined in UserDataDialog.ui
            # self.userLimits['right']['treatment']['range'] = ['untreated', 'hearing aid', 'cochlear implantat',
            #                                                   'bone conduction hearing device', 'middle ear implant']
            self.userLimits['right']['treatment']['label'] = 'Treatment'

            self.userLimits['right']['deafBeforeCI'] = dict()
            self.userLimits['right']['deafBeforeCI']['mandatory'] = True
            self.userLimits['right']['deafBeforeCI']['type'] = 'string'
            self.userLimits['right']['deafBeforeCI']['unit'] = 'years'
            self.userLimits['right']['deafBeforeCI']['editable'] = True
            # defined in UserDataDialog.ui
            #self.userLimits['right']['deafBeforeCI']['range'] = ['< 1 years', '1 - 4 years',
            #                                                     '5 - 10 years', '11 - 20 years', '21 - 30 years',
            #                                                     '> 31 years']
            self.userLimits['right']['deafBeforeCI']['label'] = 'Duration of deafness before CI treatment'

            self.userLimits['right']['deafReason'] = dict()
            self.userLimits['right']['deafReason']['mandatory'] = True
            self.userLimits['right']['deafReason']['unit'] = ''
            self.userLimits['right']['deafReason']['type'] = 'string'
            self.userLimits['right']['deafReason']['editable'] = True
            # defined in UserDataDialog.ui
            #self.userLimits['right']['deafReason']['range'] = ['unknown', 'meningitis', 'sudden hearing loss', 'genetic',
            #                                                    'inflamation of the inner ear', 'congenital']
            self.userLimits['right']['deafReason']['label'] = 'Cause of deafness'

            self.userLimits['right']['deafeningProgress'] = dict()
            self.userLimits['right']['deafeningProgress']['mandatory'] = True
            self.userLimits['right']['deafeningProgress']['unit'] = ''
            self.userLimits['right']['deafeningProgress']['type'] = 'string'
            self.userLimits['right']['deafeningProgress']['editable'] = True
            # defined in UserDataDialog.ui
            # #self.userLimits['right']['deafeningProgress']['range'] = ['progredient', 'sudden']
            self.userLimits['right']['deafeningProgress']['label'] = 'Progression of hearing loss'


        if mode == 'curSetlist' or mode == 'all':
            self.curSetlist = dict()

            self.curSetlist['comment'] = ''

            # at startup self.curSetlist['active'] is true, which might have changed along CICoachLab usage
            self.curSetlist['active'] = True
            # is set to true if user cancels setlist run and it is reset if the start button is pressed again
            self.curSetlist['stopped'] = True
            # check if self.curSetlist['active'] has to be reset according to selected tab
            self.setSetlistActivation()
            # for the documentation which instances have been run already
            self.curSetlist['instanceCounter'] = 0

            self.curSetlist['settings'] = dict()
            self.curSetlist['settings']['setlistName'] = ''
            self.curSetlist['settings']['list'] = dict()
            self.curSetlist['settings']['list']['exercises'] = {}
            self.curSetlist['settings']['list']['exercises']['names'] = []
            self.curSetlist['settings']['list']['exercises']['settings'] = []
            self.curSetlist['settings']['list']['player'] = dict()
            self.curSetlist['settings']['list']['player']['names'] = []
            self.curSetlist['settings']['list']['player']['settings'] = []
            self.curSetlist['settings']['list']['generators'] = dict()
            self.curSetlist['settings']['list']['generators']['names'] = []
            self.curSetlist['settings']['list']['generators']['settings'] = []
            self.curSetlist['settings']['list']['preprocessors'] = dict()
            self.curSetlist['settings']['list']['preprocessors']['names'] = []
            self.curSetlist['settings']['list']['preprocessors']['settings'] = []
            self.curSetlist['settings']['list']['description'] = dict()
            self.curSetlist['settings']['list']['description']['short'] = []
            self.curSetlist['status'] = dict()

            self.curSetlist['gui'] = dict()
            self.curSetlist['gui']['menu'] = []
            self.curSetlist['gui']['actionSetlistActivate'] = None

        if mode == 'prevStates' or mode == 'all':
            # For each exercise a dictionary will be added. When initialized exercises are changed to another exercise
            # the variable curExercise
            # will be moved to self.prevStates[oldExercise]['prevExercise'] and only the old paths will be removed new ones added
            # and the same for old and new menus and the result list is updated
            self.prevStates = dict()
            self.prevStates['setlists'] = dict()
            self.prevStates['setlists']['lastSetlist'] = ''
            self.prevStates['srExercises'] = dict()
            self.prevStates['srExercises']['lastSingleRunExercise'] = ''

        if mode == 'curMasterlist' or mode == 'all':
            self.curMasterlist = dict()
            self.curMasterlist['gui'] = dict()
            self.curMasterlist['gui']['menu'] = []

            self.curMasterlist['path'] = dict()
            self.curMasterlist['path']['analysis'] = os.path.join(self.frameWork['path']['masterlists'],'analysis')

            # True if masterlist is active, user cannot select other single
            # runs other than defined in masterlist
            self.curMasterlist['settings'] = dict()
            self.curMasterlist['settings']['active'] = False
            self.curMasterlist['settings']['masterlistFile'] = ''
            self.curMasterlist['settings']['masterlistStart'] = ''

            self.curMasterlist['settings']['name'] = ''
            self.curMasterlist['settings']['information'] = ''
            self.curMasterlist['settings']['lastItemIDX'] = -1

            self.curMasterlist['settings']['items'] = []
            self.curMasterlist['settings']['runmode'] = []
            self.curMasterlist['settings']['preconditions'] = []
            self.curMasterlist['settings']['preconditionMessages'] = []
            self.curMasterlist['settings']['postconditions'] = []
            self.curMasterlist['settings']['postconditionMessages'] = []
            self.curMasterlist['settings']['description'] = []

        # at this point the level of verbosity of self.dPrint is not defined by the ini file, since the ini file can
        # called only after the initialization of the frameWork fields, which will be filled b self.readIniFile()
        # Thus, the message will be printed even if verbosity is set to 0 in the iniFile
        self.dPrint('Leaving initializeToDefaults()', 2)


    def setDefaultCalibration(self, module, mode):
        """!
        This function initializes the default calibration fields for the module and its mode

        module cam be:
            frameWork
            curGenerator
            curPreprocessor
            curPlayer
            curExercise

            All items but the frameWork calibration will be saved in the CICoachLab.ini under its specific name.

        The modes can be:
            level
            time

        module can be:
            'frameWork'
            'curGenerator'
            'curPreprocessor'
            'curPlayer'
        """

        modes = ['level', 'time']
        modules = ['frameWork', 'curGenerator', 'curPreprocessor', 'curPlayer', 'curExercise']

        if not(mode in modes):
            msg = 'Error: Could not set Calibration defaults.'
            self.dPrint(msg, 0)
            return
        if not(module in modules):
            msg = 'Error: Could not set Calibration defaults.'
            self.dPrint(msg, 0)
            return

        if not('calibration' in getattr(self, module).keys()):
            getattr(self, module)['calibration'] = dict()

        if not(mode in self.frameWork['calibration'].keys()):
            getattr(self, module)['calibration'][mode] = dict()

        # the field names of calTemplate have to match the field names in CICoachLab.ini and its template CICoachLab.in
        # if fields are defined the obligatory field 'time' or 'level' has to exist. The other optional fields are
        # written if they are not empty.
        calTemplate                   = dict()
        calTemplate[mode]             = 0.0
        calTemplate['unit']           = ''
        #optional fields
        calTemplate['stdDev']         = []  # 0.0
        calTemplate['iterations']     = []  # 0
        calTemplate['settingsName']   = []  # 'default'
        calTemplate['resultFile']     = []  # ''
        calTemplate['date']           = []  # ''
        calTemplate['info']           = []  # ''

        info = 'Calibration parameters of' + module + ' ' + mode + '.'

        getattr(self, module)['calibration'][mode] = deepcopy(calTemplate)

        if mode == 'time':
            getattr(self, module)['calibration'][mode]['unit'] = 's'
        elif mode == 'level':
            getattr(self, module)['calibration'][mode]['unit'] = 'dB'
        else:
            info = ''

        getattr(self, module)['calibration'][mode]['info'] = info


    def addingPath(self, attributeName):
        """!
        Add path entries

        key word argument:
         attributeName -- defines wich path will be added possible attributes are
                            'frameWork', 'player', 'generator', 'exercise'
        """
        self.dPrint('addingPath()', 2)
        inPut = getattr(self, attributeName)
        for ff in inPut['path'].keys():
            self.dPrint('insertionpath: ' + inPut['path'][ff], 4)
            try:
                sys.path.insert(0, inPut['path'][ff])
            except:
                self.dPrint('Exception: Could not insert ' + inPut['path'][ff] + ' in path of ' + attributeName, 1)
        self.dPrint('Leaving addingPath()', 2)


    def closePath(self, attributeName):
        """!
        Remove path entries

        key word argument:
         attributeName -- defines wich path will be added possible attributes are
                            'frameWork', 'player', 'generator', 'exercise'
        """
        self.dPrint('closePath()', 2)

        inPut = getattr(self, attributeName)
        for ff in inPut['path'].keys():
            self.dPrint('removement path: ' + inPut['path'][ff], 4)
            try:
                sys.path.remove(inPut['path'][ff])
            except:
                self.dPrint('Exception: Could not remove path ' + str(inPut['path'][ff]), 1)

        setattr(self, attributeName, inPut)
        self.dPrint('Leaving closePath()', 2)


    def showInformation(self, msg='nothing to say'):
        """!
        This function shows the text 'msg' within the toolbar
        """
        self.dPrint('showInformation()', 3)

        self.statusBar().showMessage(msg)
        self.statusBar().show()
        self.dPrint(msg, 1)
        self.show()
        # updating gui for the correct display in the statusbar
        self.app.processEvents()
        self.dPrint('Leaving showInformation()', 3)


    def iniRun(self):
        """!
        This function is called to start a single run or the runs defined in the set list.
         At the start of  the run the frameWork enables the exercise gui and disables the frameWork gui elements.
        The start time will be recorded.
        """
        self.dPrint('iniRun() starting single run', 3)

        self.initializeToDefaults(mode='curRunData')

        self.frameWork['temp']['activeRun'] = True

        self.curRunData['itemIdx'] = 0
        self.curRunData['time']['startASCII'] = datetime.datetime.today().strftime('%H:%M:%S - %d.%m.%y')
        self.curRunData['time']['start'] = time()
        self.curRunData['time']['duration'] = 0
        self.curRunData['time']['endASCII'] = ''
        self.curRunData['runCompleted'] = False
        self.curRunData['statusMessage'] = ''

        try:
            self.disableFrameWorkGui()
            if self.curSetlist['active']:
                self.ui.tabTrainerMode.setTabEnabled(0, False)
        except:
            self.dPrint('Exception: Could not disable buttons of frameWork', 1)



        if self.curMasterlist['settings']['active'] == True:
            preConditionPassed = True
            msgFail = _translate("MainWindow", "Could not run masterlist because of precondition:", None)
            #updating item number in the masterlist file
            self.readMasterlist()


            mlIdx = self.curMasterlist['settings']['lastItemIDX']+1

            precondition = self.curMasterlist['settings']['preconditions'][mlIdx]
            preconditionMessage = self.curMasterlist['settings']['preconditionMessages'][mlIdx]

            if self.curMasterlist['settings']['runmode'][mlIdx] == 'singleRun':
                self.curSetlist['active'] = False
                self.curSetlist['stopped'] = True
                exerciseName = self.curMasterlist['settings']['items'][mlIdx]
                settingsName = self.curMasterlist['settings']['settings'][mlIdx]
                self.iniExercise(exerciseName, settingsName)
                if not(precondition == 'None'):
                    self.curExercise['settings']['prerunCondition'] = precondition
                else:
                    self.curExercise['settings']['prerunCondition'] = ''
                # check will be run later
                #if not(precondition == 'None') and not(self.checkExerciseConditions(mode='prerunCondition')):
                #    preConditionPasser = False

            elif self.curMasterlist['settings']['runmode'][mlIdx] == 'setlist':
                # prepare setlist if necessary
                if not(self.curSetlist['active']) and self.curSetlist['stopped']:
                    status, feebdack = self.checkMasterListCondition(precondition)
                    if not(precondition == 'None') and not(status):
                        preConditionPassed = False
                    if not(preConditionPassed):
                        self.dPrint('Masterlist item  precondition was not met! :(mlIdx: ' + str(mlIdx) + \
                                    ', precondition: ' + precondition +
                                    ') Canceling masterlist run!',
                                    0, guiMode=False)
                        msgFail = msgFail + '\n\n' + preconditionMessage
                        self.dPrint(msgFail, 0, guiMode=True)
                        self.curRunData['statusMessage'] = self.curRunData['statusMessage'] + msgFail

                        msg = _translate("MainWindow", "CICoachLab will be closed.", None)
                        self.dPrint(msg, 0, guiMode=True)

                        self.curSetlist['active'] = False
                        self.curSetlist['stopped'] = True
                        self.frameWork['temp']['activeRun'] = False
                        self.deleteLater()
                        return
                    setlistName = self.curMasterlist['settings']['items'][mlIdx]
                    if not('.lst' in setlistName):
                        setlistName = setlistName + '.lst'

                    self.curSetlist['active'] = True
                    self.curSetlist['stopped'] = False
                    self.getSetlist(event=None, setlistName=setlistName)




        if self.curSetlist['active'] == False:
            self.dPrint('iniRun() starting single run exercise', 3)
            # check prerunCondition if they are defined
            if self.curExercise['settings']['prerunCondition']:
                # check if run can be started
                conditionsMet, feedback = self.checkExerciseConditions('prerunCondition')
                if not (conditionsMet):
                    msg = _translate("MainWindow",
                                     "Run could not be started because prerun conditions were not met. (conditions: " +
                                     self.curExercise['settings'][
                                         'prerunCondition'] + ")\n Canceling start of run.\n\n ", None)
                    msg = msg + feedback
                    self.dPrint(msg, 0, guiMode=True)
                    self.closeDownRun()
                    self.curRunData['statusMessage'] = self.curRunData['statusMessage'] + msg
                    return
            try:
                # Start single run exercise
                self.curExercise['functions']['prepareRun']()
            except:
                self.enableFrameWorkGui()
                self.frameWork['temp']['activeRun'] = False
                msg = 'Exception: Could not start single run.'
                self.dPrint(msg, 1)

        elif self.curSetlist['active']:
            self.curSetlist['stopped'] = False
            self.dPrint('iniRun() starting setlist', 3)
            instanceCounter = self.curSetlist['instanceCounter']
            self.ui.lwSetlistContentVal.setCurrentRow(instanceCounter)
            genName = None
            settings = None
            try:
                genName = self.curSetlist['settings']['list']['generators']['names'][instanceCounter]
                if not(genName == '' or genName == 'None'):
                    settings = self.curSetlist['settings']['list']['generators']['settings'][instanceCounter]
                else:
                    settings = ''
                # if no generator is defined the previous generator will be unloaded.
                self.iniSubmodule('generator', genName, settings)
            except:
                msg = _translate("MainWindow",'Exception: Loading of generator  failed: ', None)\
                      + genName + ': ' + settings
                self.dPrint(msg, 1, guiMode=True)
            preName = None
            try:
                preName = self.curSetlist['settings']['list']['preprocessors']['names'][instanceCounter]
                if not(preName == '' or preName == 'None'):
                    settings = self.curSetlist['settings']['list']['preprocessors']['settings'][instanceCounter]
                else:
                    settings = ''
                # if no preprocessor is defined the previous preprocessor will be unloaded.
                self.iniSubmodule('preprocessor',  preName, settings)
            except:
                msg = _translate("MainWindow", 'Exception: Loading of preprocessor  failed: ', None)\
                      + preName + ': ' + settings
                self.dPrint(msg, 1, guiMode=True)
            playName = None
            try:
                playName = self.curSetlist['settings']['list']['player']['names'][instanceCounter]
                if not(playName == '' or playName == 'None'):
                    settings = self.curSetlist['settings']['list']['player']['settings'][instanceCounter]
                else:
                    settings = ''
                # if no player is defined the previous player will be unloaded.
                self.iniSubmodule('player',  playName, settings)
            except:
                msg = _translate("MainWindow", 'Exception: Loading of player  failed: ', None)\
                      + playName + ': ' + settings
                self.dPrint(msg, 1, guiMode=True)
            exerName = None
            try:
                exerName = self.curSetlist['settings']['list']['exercises']['names'][instanceCounter]
                if exerName != '' or exerName != 'None':
                    settings = self.curSetlist['settings']['list']['exercises']['settings'][instanceCounter]
                    self.iniExercise(exerName, settings)
                else:
                    msg = _translate("MainWindow",
                                     'Instance of set list failed. No exercise has been defined!?\n\n', None)
                    self.dPrint(msg, 1, guiMode=True)
            except:
                msg = _translate("MainWindow",
                                 'Exception: Loading of exercise  failed: ', None) + exerName + ': ' + settings
                self.dPrint(msg, 1, guiMode=True)
            try:
                self.curExercise['functions']['prepareRun']()
            except:
                self.dPrint('Exception: Could not start run in set list.', 1)
        self.ui.exerWidget.setDisabled(False)
        self.ui.exerWidget.setVisible(True)

        self.dPrint('Leaving iniRun()', 2)


    def intraRun(self):
        """!
        This function is called after each answer to an item within a run. This is used to update the
         'estimated remaining time for achievement'
         """
        self.dPrint('intraRun()', 2)
        # calculate ETA after two presentations and the following
        self.curRunData['itemIdx'] = self.curRunData['itemIdx'] + 1
        if self.curRunData['itemIdx'] > 1:
            self.curRunData['time']['duration'] = time() - self.curRunData['time']['start']
            ETA = self.curRunData['numberOfItems'] / self.curRunData['itemIdx'] * self.curRunData['time'][
                'duration'] - self.curRunData['time']['duration']
            msg = _translate("MainWindow", "Estimated exercise duration: %5.1f min", None) % (ETA / 60)
            self.showInformation(msg=msg)

        self.curRunData['time']['endASCII'] = datetime.datetime.today().strftime('%H:%M:%S - %d.%m.%y')
        self.curRunData['time']['duration'] = time() - self.curRunData['time']['start']

        self.dPrint('Leaving intraRun()', 2)


    def closeDownRun(self):
        """!
        After the run the frameWork disables the exercise gui and re-enables the frameWork gui elements.
        The end time will be recorded the used settings of the generator, preprocessor generator and exercise will be saved
        The results will be added to the run list.
        The data will be automatically saved if defined by self.frameWork['settings']['autoBackupResults']
        """

        self.dPrint('closeDownRun()', 2)

        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
        if callingFunctionName == 'quitRun':
            self.curRunData['runAccomplished'] = False
            feedback = 'The run was canceled by the user'
        else:
            # recheck if run was successfully closed by checking 'postrunCondition'
            self.curRunData['runAccomplished'], feedback = self.checkExerciseConditions('postrunCondition')
            if not(self.curRunData['runAccomplished']):
                msg = _translate("MainWindow", 'The postrun conditions were not met!', None)
                self.dPrint(msg, 0, guiMode=True)
                feedback = feedback + '\n' +msg

        self.curRunData['time']['endASCII'] = datetime.datetime.today().strftime('%H:%M:%S - %d.%m.%y')
        self.curRunData['time']['duration'] = time() - self.curRunData['time']['start']
        self.frameWork['settings']['lastRunEndTime'] = strftime("%Y-%m-%d", gmtime(time()))

        self.frameWork['settings']['sessionCumulatedRunTime'] = \
            self.frameWork['settings']['sessionCumulatedRunTime'] + self.curRunData['time']['duration']


        # collective saving of the settings of the exercise, the player, generator and preprocessor

        self.curRunData['settings']['exercise'] = deepcopy(self.curExercise['settings'])
        self.curRunData['settings']['player'] = deepcopy(self.curPlayer['settings'])
        self.curRunData['settings']['generator'] = deepcopy(self.curGenerator['settings'])
        self.curRunData['settings']['preprocessor'] = deepcopy(self.curPreprocessor['settings'])
        self.curRunData['settings']['setlist'] = deepcopy(self.curSetlist['settings'])
        # deepcopy cannot handle file handles, ssetting it to none and resetting it with a backup handle afterwards
        handle = self.frameWork['settings']['debug']['debuggingFileHandle']
        self.frameWork['settings']['debug']['debuggingFileHandle'] = None
        self.curRunData['settings']['frameWork'] = deepcopy(self.frameWork['settings'])
        self.frameWork['settings']['debug']['debuggingFileHandle'] = handle
        self.curRunData['settings']['masterlist'] = deepcopy(self.curMasterlist['settings'])


        self.curRunData['calibration']['frameWork'] = deepcopy(self.frameWork['calibration'])
        self.curRunData['calibration']['generator'] = deepcopy(self.frameWork['calibration'])
        self.curRunData['calibration']['preprocessor'] = deepcopy(self.frameWork['calibration'])
        self.curRunData['calibration']['player'] = deepcopy(self.frameWork['calibration'])
        self.curRunData['runCompleted'] = True

        # if runData was collected wth a set list the setlist name will be saved, otherwise an empty string
        if self.curSetlist['active']:
            setListName = self.curSetlist['settings']['setlistName']
            setListIdx  = self.curSetlist['instanceCounter']
        else:
            setListName = ''
            setListIdx = - 1
        self.curRunData['setListName'] = setListName
        self.curRunData['setListIdx'] = setListIdx


        if self.curMasterlist['settings']['active']:
            fullname = self.curMasterlist['settings']['masterlistFile']
            # getting rid of fullpath to file for linux and windowscase and getting rid of extension
            masterlistName = fullname.split('\\')[-1].split('/')[-1].split('.')[0]
            masterlistIdx = 0
        else:
            masterlistName = ''
            masterlistIdx = 0
        self.curRunData['masterlistName'] = masterlistName
        self.curRunData['masterlistIdx'] = masterlistIdx

        self.runData[self.curExercise['settings']['exerciseName']][self.runDataCounter] = self.curRunData
        self.runDataCounter = self.runDataCounter + 1

        # make the run available in the gui list
        self.updateRunlist()

        self.frameWork['settings']['lastExercise'] = self.curExercise['settings']['exerciseName']
        self.frameWork['settings']['lastExerciseSettings'] = self.curExercise['settings']['settingsName']
        self.frameWork['settings']['lastGenerator'] = self.curGenerator['settings']['generatorName']
        self.frameWork['settings']['lastGeneratorSettings'] = self.curGenerator['settings']['settingsName']
        self.frameWork['settings']['lastPreprocessor'] = self.curPreprocessor['settings']['preprocessorName']
        self.frameWork['settings']['lastPreprocessorSettings'] = self.curPreprocessor['settings']['settingsName']
        self.frameWork['settings']['lastPlayer'] = self.curPlayer['settings']['playerName']
        self.frameWork['settings']['lastPlayerSettings'] = self.curPlayer['settings']['settingsName']
        self.frameWork['settings']['lastSetlist'] = self.curSetlist['settings']['setlistName']

        # updating last run settings in ini-file
        self.writeIniFile()

        if self.curSetlist['active']:

            self.ui.tabTrainerMode.setTabEnabled(0, True)
            # still not at end of setlist? go to next set list item
            if self.curSetlist['instanceCounter'] < len(self.curSetlist['settings']['list']['exercises']['names']) - 1\
                    and not(self.curSetlist['stopped']):
                self.dPrint('closeDownRun(self): calling next instance of setlist', 3)
                self.curSetlist['instanceCounter'] = self.curSetlist['instanceCounter'] + 1

                if self.curRunData['runAccomplished']:
                    msg = _translate("MainWindow", 'Starting next run of SetList ... ', None)
                    #if self.curExercise['settings']['postrunCondition']:
                    #    msg = msg + _translate("MainWindow", 'Checking Accomplishment ... ', None)
                    self.showInformation(msg)
                    self.iniRun()
                else:
                    msg = _translate("MainWindow", 'The previous run was aborted or finished without success. '
                                                                      'The setlist has been stopped', None)
                    self.showInformation(msg)
                    self.curSetlist['stopped'] = True
                    feedback = feedback + '\n' + msg
                    # if the continuation of the setlist should be allowed the next line has to be disabled
                    self.curSetlist['instanceCounter'] = 0

            else:
                self.curSetlist['instanceCounter'] = 0
                self.curSetlist['stopped'] = True

        if not(self.curSetlist['active']) or (self.curSetlist['active'] and  self.curSetlist['stopped']):
            try:
                self.ui.exerWidget.setDisabled(True)
                # for item in self.curExercise['gui']['exerWidgets']:
                #    item.setDisabled(True)
            except:
                self.dPrint('Exception: Could not enable exercise gui elements', 1)

            try:
                self.enableFrameWorkGui()
                # if a single or the last run is finished
                self.frameWork['temp']['activeRun'] = False
            except:
                self.dPrint('Exception: Could not enable buttons', 1)

        if self.curMasterlist['settings']['active'] == True:
            # check if setlist is running and continue to next masterlist item otherwise
            if not(self.curSetlist['active']) or \
                    self.curSetlist['instanceCounter'] == 0 and self.curSetlist['stopped']:
                masterItemFinished = True
                msgFail = _translate("MainWindow", "Could not continue masterlist because of postcondition:", None)

                mlIdx = self.curMasterlist['settings']['lastItemIDX'] + 1
                # end of masterlist?
                if not(len(self.curMasterlist['settings']['postconditions'])-1 > mlIdx):
                    self.dPrint("End of masterlist", 3)
                    self.curMasterlist['settings']['active'] = False
                    self.writeMasterlist()
                    # closing masterlist and closing CICoachLab
                    self.deleteLater()
                    return
                if self.curRunData['runAccomplished']:

                    postcondition = self.curMasterlist['settings']['postconditions'][mlIdx]
                    postconditionMessage = self.curMasterlist['settings']['postconditionMessages'][mlIdx]

                    if self.curMasterlist['settings']['runmode'][mlIdx] == 'singleRun':
                        if not(postcondition == 'None'):
                            self.curExercise['settings']['postrunCondition'] = postcondition
                        # exercise conditions and masterlist conditions may be allowed. Masterlist conditions should
                        # be priorized
                        status, feedbackCheck = self.checkExerciseConditions(mode='postrunCondition')
                        if not(postcondition == 'None') and not(status):
                            masterItemFinished = False

                    elif self.curMasterlist['settings']['runmode'][mlIdx] == 'setlist':
                        status, feedbackCheck = self.checkMasterListCondition(postcondition)
                        if not(postcondition == 'None') and not(status):
                            masterItemFinished = False
                    feedback = feedbackCheck + '\n' + feedbackCheck
                    if not(masterItemFinished):
                        msg = 'Masterlist item  postconditions was not met!: (' + str(mlIdx) +\
                                    ', ' + postcondition + ') Canceling masterlist run!'
                        self.dPrint(msg, 0, guiMode=False)
                        self.curRunData['statusMessage'] = self.curRunData['statusMessage'] + '\n' + feedback
                        msgFail = msgFail + '\n\n' + postconditionMessage
                        self.dPrint(msgFail, 0, guiMode=True)
                        self.curMasterlist['settings']['active'] = False
                        self.deleteLater()
                        return
                    self.curMasterlist['settings']['lastItemIDX'] = mlIdx
                    #updating item number in the masterlist file
                    self.writeMasterlist()

                    # continue to next master item
                    self.iniRun()
                else:
                    self.curRunData['statusMessage'] = self.curRunData['statusMessage'] + '\n' + feedback
                    self.dPrint(self.curRunData['statusMessage'], 0, guiMode=False)
                    self.curMasterlist['settings']['active'] = False
                    self.deleteLater()
            else:
                # doing nothing since curlist active and setlist still in progress
                msg = ''

        if self.frameWork['settings']['autoBackupResults'] or self.frameWork['settings']['patientMode']:
            if self.frameWork['settings']['autoBackupResults']:
                # saving data in temp file
                resultsFilename = os.path.join(self.curExercise['path']['results'],
                                               'backupData' + '.cid')
            elif self.frameWork['settings']['patientMode']:
                resultsFilename = self.frameWork['settings']['patientSavingFile']
            else:
                resultsFilename = ''

            self.saveRunData(filename=resultsFilename)

        msg = _translate("MainWindow", 'Run completed successfully.', None)
        self.showInformation(msg)

        self.dPrint('Leaving closeDownRun()', 2)


    def disableFrameWorkGui(self):
        """!
        This function disables the gui elements defined in self.frameWork['gui']['buttons'],
        self.frameWork['gui']['lists'], for item in self.frameWork['gui']['menus'] and
        self.ui.pbStoppSetlist and self.ui.tabTrainerMode.
        """

        for item in self.frameWork['gui']['buttons']:
            item.setDisabled(True)
        for item in self.frameWork['gui']['lists']:
            item.setDisabled(True)
        self.ui.menubar.setEnabled(False)
        for item in self.frameWork['gui']['menus']:
            item.setDisabled(True)

        self.ui.pbStoppSetlist.setDisabled(False)
        self.ui.tabTrainerMode.setDisabled(False)


    def enableFrameWorkGui(self):
        """!
        This function reenables the gui elements defined in self.frameWork['gui']['buttons'],
        self.frameWork['gui']['lists'], for item in self.frameWork['gui']['menus'] and
        self.ui.pbStoppSetlist and self.ui.tabTrainerMode.
        """

        self.dPrint('enableFrameWorkGui()', 2)

        for item in self.frameWork['gui']['buttons']:
            if item.objectName() == 'pbRunSetlist':
                if self.curSetlist['settings']['setlistName'] != '':
                    item.setDisabled(False)
            else:
                item.setDisabled(False)
        for item in self.frameWork['gui']['lists']:
            item.setDisabled(False)
        self.ui.menubar.setEnabled(True)
        for item in self.frameWork['gui']['menus']:
            item.setDisabled(False)
        self.ui.tabTrainerMode.setDisabled(False)
        self.ui.pbStoppSetlist.setDisabled(True)

        self.dPrint('Leaving enableFrameWorkGui()', 2)


    def checkForInputWidgets(self, item):
        """!
        This function returns True if a input widget is found and False otherwise.

        input widgets:
        QPushButton, QtWidgets.QSlider, QRadioButton, QToolButton, QCheckBox, QLineEdit,QTextEdit, QPlainTextEdit,
         QComboBox, QSpinBox, QFontComboBox, QSpinBox, QTimeEdit, QDateTimeEdit, QDateEdit, QDial, QKeySequenceEdit
        """

        self.dPrint('checkForInputWidgets()', 4)
        if isinstance(item, QtWidgets.QPushButton) or isinstance(item, QtWidgets.QSlider) or \
                isinstance(item, QtWidgets.QRadioButton) or isinstance(item, QtWidgets.QToolButton) or \
                isinstance(item, QtWidgets.QCheckBox) or isinstance(item, QtWidgets.QLineEdit) or \
                isinstance(item, QtWidgets.QTextEdit) or isinstance(item, QtWidgets.QPlainTextEdit) or \
                isinstance(item, QtWidgets.QComboBox) or isinstance(item, QtWidgets.QSpinBox) or \
                isinstance(item, QtWidgets.QFontComboBox) or isinstance(item, QtWidgets.QSpinBox) or \
                isinstance(item, QtWidgets.QTimeEdit) or isinstance(item, QtWidgets.QDateTimeEdit) or \
                isinstance(item, QtWidgets.QDateEdit) or isinstance(item, QtWidgets.QDial) or \
                isinstance(item, QtWidgets.QKeySequenceEdit):
            return True
        else:
            return False

        self.dPrint('Laving checkForInputWidgets()', 4)


    def disableExerciseGui(self):
        """!
        This function disables the gui elements defined in self.frameWork['gui']['buttons'].
        """

        self.dPrint('disableExerciseGui()', 2)

        self.blockUserInput = True
        for item in self.curExercise['gui']['exerWidgets']:
            try:
                if self.checkForInputWidgets(item):
                    item.blockSignals(True)
                    msg = 'Blocking signals ' + str(item)
                    self.dPrint(msg, 4)
            except:
                msg = 'Could not block signals ' + str(item)
                self.dPrint(msg, 4)

        self.dPrint('Leaving disableExerciseGui()', 2)


    def enableExerciseGui(self):
        """!
        This function disables the gui elements defined in self.frameWork['gui']['buttons'],
        self.frameWork['gui']['lists'], for item in self.frameWork['gui']['menus'] and
        self.ui.pbStoppSetlist and self.ui.tabTrainerMode.
        """

        self.dPrint('enableExerciseGui()', 2)

        self.blockUserInput = False
        for item in self.curExercise['gui']['exerWidgets']:
            try:
                if self.checkForInputWidgets(item):
                    item.blockSignals(False)
                    msg = 'Unlocking signals ' + str(item)
                    self.dPrint(msg, 4)
            except:
                msg = 'Could not unblock signals ' + str(item)
                self.dPrint(msg, 4)

        self.dPrint('Leaving enableExerciseGui()', 2)


    def checkMasterListCondition(self, condition):
        """!
        This function is called in self.iniRun() before the next run can be started.
        The Masterlist conditions are defined in the masterlist file:
        self.curMasterlist['settings']['masterlistFile']

        mode: can be 'prerunCondition' or 'postrunCondition'
        """

        self.dPrint('checkMasterListCondition()', 2)

        conditionsPath = self.frameWork['path']['masterlists']
        status, feedback = self.checkConditionsBase(condition, conditionsPath)

        self.dPrint('Leaving checkMasterListCondition()', 2)
        return status, feedback


    def checkExerciseConditions(self, mode):
        """!
        This function is called in self.iniRun() before a run can be started or in self.closeDownRun()
        after a run was finished.
        mode: can be 'prerunCondition' or 'postrunCondition'
        """

        self.dPrint('checkExerciseConditions()', 2)

        conditionsPath = os.path.join(self.curExercise['path']['base'], 'conditions')
        if mode in ['prerunCondition', 'postrunCondition']:
            # ini run points to the condition of the currently selected exercise
            condition = self.curExercise['settings'][mode]

        status, feedback = self.checkConditionsBase(condition, conditionsPath)

        self.dPrint('Leaving checkExerciseConditions()', 2)
        return status, feedback

    #def checkConditions(self, mode):
    def checkConditionsBase(self, condition, conditionPath):
        """!
        The function returns True if conditions are met or no conditions were defined or False if conditions were not
        """

        self.dPrint('checkConditionsBase()', 2)
        feedback = ''

        if condition == '':
            conditionsPassed = True
        else:
            fullFilename = os.path.join(conditionPath,
                     condition + '.py')

            if os.path.isfile(fullFilename):
                try:
                    spec = importlib.util.spec_from_file_location(
                        condition + ".py", fullFilename)
                    conditionCheck = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(conditionCheck)
                    conditionsPassed, feedback = conditionCheck.conditionCheck(self)
                except:
                    conditionsPassed = False
                    feedback = _translate("MainWindow", 'Could not run check of accomplishment: ', None)
                    self.showInformation(feedback)
            elif isinstance(condition, str):
                try:
                    conditionsPassed = eval(condition)
                except:
                    conditionsPassed = False
                    feedback = _translate("MainWindow", 'Could not run check of accomplishment (eval): %s ', None) % \
                          str(condition)
                    self.showInformation(feedback)
            else:
                conditionsPassed = False
                feedback = _translate("MainWindow", 'Could not run check of accomplishment (unsupported type): type %s', None) %\
                      str(type(condition))
                self.showInformation(feedback)

        self.dPrint('Leaving checkConditionsBase()', 2)
        return conditionsPassed, feedback


    def selectExer(self):
        """!
        This function is called when the exercise is selected in the exercise list. The exercise is
        initiliazed by calling the function self.iniExercise(exerName)
        """

        self.dPrint('selectExer()', 2)

        #exerName = self.exercises[self.ui.lwExerNameVal.currentRow()]
        exerName = self.frameWork['settings']['access']['exercises']['main']['displayed']['names'][self.ui.lwExerNameVal.currentRow()]
        try:

            msg = _translate("MainWindow", 'Selected exercise: %s', None) % exerName
            self.showInformation(msg) # Ausgewählte Übung
            self.iniExercise(exerName)
            title = _translate("MainWindow", "Exercise - %s", None) %exerName
            self.ui.exerWidget.setTitle(title)
        except:
            msg = _translate("MainWindow", 'Exception: Start of exercise not possible: %s', None) % exerName
            self.showInformation(msg)

        self.dPrint('Leaving selectExer()', 2)


    def clearSettingsInMenu(self, mode):
        """!
        Remove menu entries for the loading setting files. With the mode the removed entries can be defined.
        key word arguemnt:
        mode -- defines which settings will cleared. Possible options are:
                'curExercise', 'curGenerator', 'curPlayer', 'curPreprocessor'
        """
        self.dPrint('clearSettingsInMenu()', 2)

        if mode == 'curExercise':
            menuMode = 'menuExer'
        elif mode == 'curGenerator':
            menuMode = 'menuGenerator'
        elif mode == 'curPlayer':
            menuMode = 'menuPlayer'
        elif mode == 'curPreprocessor':
            menuMode = 'menuPreprocessor'
        else:
            self.dPrint('Leaving clearSettingsInMenu() without anything', 2)
            return
        menuEntry = None
        for index in range(len(getattr(self, mode)['gui']['menu'])):
            try:
                menuEntry = getattr(self, mode)['gui']['menu'].pop(0)
                getattr(self.ui, menuMode).removeAction(menuEntry)
            except:
                # assuming that menu entry has already been succesfully removed from list.
                try:
                    getattr(self, mode)['gui']['menu'].append(menuEntry)
                except:
                    self.dPrint('Execption: Menu entry could not be removed. Poping failed', 1)
                self.dPrint('Could not remove menu entry', 1)
        self.dPrint('Leaving clearSettingsInMenu()', 2)


    def updateExerciseListBox(self):
        """!
        filling exercise list box
        """

        self.dPrint('updateExerciseListBox()', 2)

        self.ui.lwExerNameVal.blockSignals(True)
        self.ui.lwExerNameVal.clear()
        self.ui.lwExerNameVal.blockSignals(False)
        ii = 0
        for exercise in self.frameWork['settings']['access']['exercises']['main']['displayed']['labels']:
            info = self.frameWork['settings']['access']['exercises']['main']['displayed']['infos'][ii]
            self.ui.lwExerNameVal.insertItem(ii, exercise)
            item = self.ui.lwExerNameVal.item(ii)
            item.setToolTip(info)
            ii = ii + 1

        if self.curExercise['settings']['exerciseName'] in \
                self.frameWork['settings']['access']['exercises']['main']['displayed']['names']:
            #highlight intialized exercise
            idx = self.frameWork['settings']['access']['exercises']['main']['displayed']['names'].index(
                self.curExercise['settings']['exerciseName'])

            self.ui.lwExerNameVal.blockSignals(True)

            self.ui.lwExerNameVal.setCurrentRow(idx)
            self.ui.lwExerNameVal.blockSignals(False)

        self.dPrint('Leaving updateExerciseListBox()', 2)


    def updateExerciseSettingsListBox(self):
        """!
        Filling exercise settings list box. It will be filled with the entries found in filter.ini. It does not matter
        if the defined entries are definitions of *.set or *.py setting files. Primarily CICoachLab will try to load
        *.set files. .py setting files may be shaded by a *.set file with the same name.
        If no *.set setting file is found a .py setting file will be tried.
        """

        self.ui.lwExerSetVal.blockSignals(True)
        self.ui.lwExerSetVal.clear()
        self.ui.lwExerSetVal.blockSignals(False)

        settingsName = self.curExercise['settings']['settingsName']
        exerciseName = self.curExercise['settings']['exerciseName']

        if not(exerciseName):
            return
        ii = 0
        for setting in self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['labels']:
            if self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['visibles'][ii]:
                info = self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['infos'][ii]
                self.ui.lwExerSetVal.insertItem(ii, setting)
                item = self.ui.lwExerSetVal.item(ii)
                item.setToolTip(info)

            ii = ii + 1
        # allow temporal settings set in the SettingsDialog
        if '*' in settingsName:
            idx = self.frameWork['settings']['access']['exercises']['settings'][
                exerciseName]['displayed']['names'].index(re.sub('\*', '', settingsName))
            info = self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['infos'][idx]
            settingsLabel = self.frameWork['settings']['access']['exercises']['settings'][
                exerciseName]['displayed']['labels'][idx] + '*'
            self.ui.lwExerSetVal.insertItem(ii, settingsLabel)
            item = self.ui.lwExerSetVal.item(ii)
            item.setToolTip(info)
        else:
            if settingsName == 'default':
                settingsLabel = 'default'
            else:
                if settingsName in self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed'][
                    'names']:
                    idx = self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed'][
                        'names'].index(settingsName)
                    settingsLabel = self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed'][
                        'labels'][idx]
                else:
                    settingsLabel = 'default'

        self.ui.lwExerSetVal.insertItem(ii, 'default')
        self.ui.lwExerSetVal.item(ii).setToolTip(_translate("MainWindow", 'default values', None))

        #highlight intialized exercise
        if not(settingsName == 'default'):
            match = self.ui.lwExerSetVal.findItems(settingsLabel, QtCore.Qt.MatchExactly)
            if match:
                self.ui.lwExerSetVal.blockSignals(True)
                self.ui.lwExerSetVal.setCurrentItem(match[0])
                self.ui.lwExerSetVal.blockSignals(False)
        else:
            idx = len(self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['names'])
            self.ui.lwExerSetVal.blockSignals(True)
            self.ui.lwExerSetVal.setCurrentRow(idx)
            self.ui.lwExerSetVal.blockSignals(False)
        self.dPrint('Leaving updateExerciseSettingsListBox()', 2)


    def updateSetlistListBox(self):
        """!
        This function fills the setlist box with available setlist
        (self.frameWork['settings']['access']['setlists']['main']['displayed']).
        """

        self.dPrint('updateSetlistListBox()', 2)

        self.ui.lwSetlistNameVal.blockSignals(True)
        self.ui.lwSetlistNameVal.clear()
        self.ui.lwSetlistNameVal.blockSignals(False)

        ii = 0
        for setlist in self.frameWork['settings']['access']['setlists']['main']['displayed']['labels']:
            info = self.frameWork['settings']['access']['setlists']['main']['displayed']['infos'][ii]
            self.ui.lwSetlistNameVal.insertItem(ii, setlist)
            item = self.ui.lwSetlistNameVal.item(ii)
            item.setToolTip(info)
            ii = ii + 1

        self.dPrint('Leaving updateSetlistListBox()', 2)


    def readFilter(self):
        """!
        finding all availabale modules and assigning available settings which is found in filter.ini
        finding all availabale modules and assigning available settings which is found in filter.ini
        Modules (exercises, generators, preoprocessors, player, setlists, which are undefined in filter.ini will be
        set to unvisible and to an difficulty level = 0
        """

        self.dPrint('readFilter()', 2)

        template = dict()
        # name of item, as defined by name of exercise/generator/preprocessor/player python file or setlist name
        template['names'] = list()
        # label of item which will be displayed in the gui
        template['labels'] = list()
        # additional information about the item, which will be displayed if user hovers over item in gui list.
        template['infos'] = list()
        # difficulty of item
        template['difficulties'] = list()
        # is item visible to user?
        template['visibles'] = list()
        # have been properties of available items defined in filter.ini?
        template['filterDefinition'] = list()

        moduleNamesFiles = ['exercises', 'generators', 'preprocessors', 'player', 'setlists']
        # looping through different modules
        for modeItem in moduleNamesFiles:
            self.frameWork['settings']['access'][modeItem]['main']['available'] = deepcopy(template)
            self.frameWork['settings']['access'][modeItem]['main']['displayed'] = deepcopy(template)
            modPath = os.path.join(self.frameWork['path']['pwd'], modeItem)

            if modeItem == 'setlists':
                fileFilter = '.lst'
            else:
                fileFilter = '.py'

            files = self.getListOfFiles(modPath, depthOfDir=1, namePart=fileFilter)
            files = [x.split('.')[0] for x in files ]

            tempList = deepcopy(template)
            for exerListItem in files:
                tempList['names'].append(exerListItem)
                tempList['labels'].append(exerListItem)
                tempList['infos'].append('')
                tempList['difficulties'].append('0')
                tempList['visibles'].append(False)
                tempList['filterDefinition'].append(False)

                # special handling, since setlists have no distinct settings
                if modeItem == 'setlists':
                    continue

                modSettingsPath = os.path.join(modPath,exerListItem,'presets')
                if self.frameWork['settings']['expertSettingsMode']:
                    exerSetListLongPy = self.getListOfFiles(modSettingsPath, depthOfDir=1, namePart='.py')
                    exerSetListShortPy = [x.split('.')[0] for x in exerSetListLongPy]
                else:
                    exerSetListShortPy = []
                exerSetListLongSet = self.getListOfFiles(modSettingsPath, depthOfDir=1, namePart='.set')
                exerSetListShortSet = [x.split('.')[0] for x in exerSetListLongSet]

                exerSetListShort = list(set(exerSetListShortPy + exerSetListShortSet))
                exerSetListShort.sort()
                tempSetList = deepcopy(template)
                for exerSetListItem in exerSetListShort:
                    tempSetList['names'].append(exerSetListItem)
                    tempSetList['labels'].append(exerSetListItem)
                    tempSetList['difficulties'].append('0')
                    tempSetList['infos'].append('')
                    tempSetList['visibles'].append(False)
                    tempSetList['filterDefinition'].append(False)
                self.frameWork['settings']['access'][modeItem]['settings'][exerListItem] = dict()
                self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['available'] = tempSetList
                if self.frameWork['settings']['ignoreFilterFile']:
                    self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['displayed'] = \
                        self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['available']
                    # and setting all visbibless flag to True and ...
                    noItems = len(self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['displayed']['visibles'])
                    self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['displayed']['visibles'] = [True] * noItems
                    # by setting the lowest possible difficulty
                    self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['displayed']['difficulties'] = \
                        ['1'] * noItems
                else:
                    self.frameWork['settings']['access'][modeItem]['settings'][exerListItem]['displayed'] = \
                        deepcopy(template)
            # special handling, since setlists have no distinct settings
            self.frameWork['settings']['access'][modeItem]['main']['available'] = deepcopy(tempList)
            if self.frameWork['settings']['ignoreFilterFile']:
                # making all available modules visible by copying them ...
                self.frameWork['settings']['access'][modeItem]['main']['displayed'] = \
                    self.frameWork['settings']['access'][modeItem]['main']['available']
                # and setting all visbibless flag to True and ...
                noItems = len(self.frameWork['settings']['access'][modeItem]['main']['displayed']['visibles'])
                self.frameWork['settings']['access'][modeItem]['main']['displayed']['visibles'] = [True] * noItems
                # by setting the lowest possible difficulty
                self.frameWork['settings']['access'][modeItem]['main']['displayed']['difficulties'] = ['1'] * noItems
            else:
                self.frameWork['settings']['access'][modeItem]['main']['displayed'] = deepcopy(template)

        if self.frameWork['settings']['ignoreFilterFile']:
            msg = 'Ignoring reading of "filter.ini" and making  all exercises, generators, perprocessor, player and' +\
                  ' setlists available to the user.'
            self.dPrint(msg, 0)
            return True





        if not(os.path.isfile(self.frameWork['settings']['filterFile'])):
            msg = _translate("MainWindow", "filter.ini could not be be found. You may have to copy and edit "
                                           "filter.in or retrieve the deleted file before starting CICOachLab." ,None)
            self.dPrint(msg, 0, guiMode=True)
            return False
        # encoding="utf8": Otherwise no writing will be possible in case of filter.ini
        filterConfig = ConfigObj(self.frameWork['settings']['filterFile'], encoding="utf8")

        moduleNamesFilt = list(filterConfig)
        # looping through ['exercises', 'generators', 'preprocessors', 'player', settings] if they are defined in filter.ini
        for modeItem in moduleNamesFilt:
            subItems = list(filterConfig[modeItem])
            # looping through ['main', 'settings']
            for subItem in subItems:
                subSubItems = list(filterConfig[modeItem][subItem])
                if subItem == 'main':
                    if isinstance(filterConfig[modeItem][subItem]['names'],str):
                        if len(filterConfig[modeItem][subItem]['names']):
                            itemLen = 1
                        else:
                            itemLen = 0
                    else:
                        itemLen = len(filterConfig[modeItem][subItem]['names'])

                    failedFields = []
                    failedFieldsLen = []
                    for field in ['labels', 'difficulties', 'infos', 'visibles']:
                        if itemLen != len(filterConfig[modeItem][subItem][field]):
                            failedFields.append(field)
                            failedFieldsLen.append(len(filterConfig[modeItem][subItem][field]))

                    if failedFields:
                        msg = _translate("MainWindow", ' The number of fields differs in filter.ini', None) + \
                              '\n\n' + modeItem + ' > ' + subItem + ' >>> ' + \
                              f"\n\nnames: {itemLen:0d}" + f" {str(failedFields):s}:" + f"({str(failedFieldsLen):s})"
                        self.dPrint(msg, 0, guiMode=True)
                        return False
                    for ii in range(itemLen):
                        if isinstance(filterConfig[modeItem][subItem]['names'], str):
                            modName = filterConfig[modeItem][subItem]['names']
                        else:
                            modName = filterConfig[modeItem][subItem]['names'][ii]
                        if modName in \
                                self.frameWork['settings']['access'][modeItem]['main']['available']['names']:
                            idx = self.frameWork['settings']['access'][modeItem]['main']['available']['names'].index(modName)
                            fields = ['labels', 'difficulties', 'infos', 'visibles']
                            for field in fields:
                                if field == 'infos':
                                    if isinstance(filterConfig[modeItem][subItem][field], str):
                                        temp = filterConfig[modeItem][subItem][field]
                                        temp = temp.split("''','''")
                                        temp = temp[ii]
                                    elif isinstance(filterConfig[modeItem][subItem][field], list):
                                        temp = filterConfig[modeItem][subItem][field][ii]
                                elif field == 'visibles':
                                    if isinstance(filterConfig[modeItem][subItem][field], str):
                                        temp = filterConfig[modeItem][subItem][field] == 'True'
                                    else:
                                        if not(isinstance(filterConfig[modeItem][subItem][field][ii], str)):
                                            temp = [x == 'True' for x in filterConfig[modeItem][subItem][field][ii]]
                                        else:
                                            temp = filterConfig[modeItem][subItem][field][ii] == 'True'
                                else:
                                    if isinstance(filterConfig[modeItem][subItem][field], str):
                                        temp = filterConfig[modeItem][subItem][field]
                                    else:
                                        temp = filterConfig[modeItem][subItem][field][ii]
                                self.frameWork['settings']['access'][modeItem]['main']['available'][field][idx] = temp

                            self.frameWork['settings']['access'][modeItem]['main']['available']['filterDefinition'][idx] = True
                elif subItem == 'settings':

                    for hh in subSubItems:

                        if not(hh in self.frameWork['settings']['access'][modeItem]['settings']):
                            exerNames = self.frameWork['settings']['access']['exercises']['main']['available']['names']
                            msg = _translate("MainWindow", 'The CICoachLab exercise "' + hh + '" which was defined in the file "filter.ini" ' +\
                                     'could not be found. \n\n' \
                                     'Please check and correct filter.ini!\n\n' \
                                     'Found exercises are: \n' +\
                                        str(exerNames), None)
                            self.dPrint(msg, 0, guiMode=True)
                            return False

                        if isinstance(filterConfig[modeItem][subItem][hh]['names'], str):
                            itemLen = 1
                        else:
                            itemLen = len(filterConfig[modeItem][subItem][hh]['names'])
                        failedFields = []
                        failedFieldsLen = []
                        for field in ['labels', 'difficulties', 'infos', 'visibles']:
                            if itemLen != len(filterConfig[modeItem][subItem][hh][field]):
                                failedFields.append(field)
                                failedFieldsLen.append(len(filterConfig[modeItem][subItem][hh][field]))

                        if failedFields:
                            msg = _translate("MainWindow", ' The number of fields differs in filter.ini', None) + \
                                     '\n\n' +modeItem + ' > ' + subItem + ' >> ' + hh + ' >>> ' + \
                                  f"\n\nnames: {itemLen:0d}" + f" {str(failedFields):s}:" + f"({str(failedFieldsLen):s})"
                            self.dPrint(msg, 0, guiMode=True)
                            return False

                        for ii in range(itemLen):
                            if isinstance(filterConfig[modeItem][subItem][hh]['names'], str):
                                modName = filterConfig[modeItem][subItem][hh]['names']
                            else:
                                modName = filterConfig[modeItem][subItem][hh]['names'][ii]
                            # continue if name of module as defined in filter.ini was found as *.set or .*py setting
                            if modName in \
                                    self.frameWork['settings']['access'][modeItem]['settings'][hh]['available']['names']:
                                idx = self.frameWork['settings']['access'][modeItem]['settings'][hh]['available']['names'].index(modName)
                                fields = ['labels', 'difficulties', 'infos', 'visibles']
                                for field in fields:
                                    if field == 'infos':
                                        if isinstance(filterConfig[modeItem][subItem][hh][field], str):
                                            temp = filterConfig[modeItem][subItem][hh][field]
                                            temp = temp.split("''','''")
                                            if len(temp) > ii:
                                                temp = temp[ii]
                                            else:
                                                msg = _translate("MainWindow",
                                                        'Error filter.ini: %s is shorter than other fields', None) % field
                                                self.showInformation(msg)
                                        else:
                                             temp = filterConfig[modeItem][subItem][hh][field][ii]
                                    elif field == 'visibles':
                                        if isinstance(filterConfig[modeItem][subItem][hh][field], str):
                                            temp = filterConfig[modeItem][subItem][hh][field] == 'True'
                                        else:
                                            if not (isinstance(filterConfig[modeItem][subItem][hh][field][ii], str)):
                                                temp = [x == 'True' for x in filterConfig[modeItem][subItem][hh][field][ii]]
                                            else:
                                                temp = filterConfig[modeItem][subItem][hh][field][ii] == 'True'

                                    elif field == 'difficulties':
                                        temp = filterConfig[modeItem][subItem][hh][field][ii]
                                    elif field == 'labels':
                                        if isinstance(filterConfig[modeItem][subItem][hh][field], str):
                                            temp = filterConfig[modeItem][subItem][hh][field]
                                        else:
                                            temp = filterConfig[modeItem][subItem][hh][field][ii]
                                    else:
                                        if isinstance(filterConfig[modeItem][subItem][hh][field][ii], str):
                                            temp = filterConfig[modeItem][subItem][hh][field]
                                        else:
                                            temp = filterConfig[modeItem][subItem][hh][field][ii]
                                    self.frameWork['settings']['access'][modeItem]['settings'][hh]['available'][field][idx] = \
                                        temp
                                self.frameWork['settings']['access'][modeItem]['settings'][hh]['available']['filterDefinition'][idx] = True
        self.frameWork['settings']['filterFileConfig'] = filterConfig

        self.dPrint('Leaving readFilter()', 2)
        return True


    def writeFilter(self):
        """!
        In future versions this function will write back changes in the access data which may have been introduced
        in SettingsDialog where setting may have been introduced.
        """

        self.dPrint('readFilter()', 2)

        self.frameWork['settings']['filterFileConfig'].write()

        self.dPrint('Leaving readFilter()', 2)

        """
        # TODO:
        #self.frameWork['settings']['access']['exercises']['main']['displayed']['names']
        #self.frameWork['settings']['access']['exercises']['settings'][exerName]['available']['names']
        
        # looping through modules: 'exercise', 'generators', ...
        for modeItem in access:
            subItems = access[modeItem]
            # looping through ['main', 'settings']
            for subItem in subItems:
                subSubItems = list([modeItem][subItem])
                if subItem == 'main':
                    pass
                    # filterConfig[modeItem][subItem]['names'][0]
                    # filterConfig[modeItem][subItem]['labels'][0]
                    # filterConfig[modeItem][subItem]['difficulties'][0]
                    # filterConfig[modeItem][subItem]['infos'][0]
                    # filterConfig[modeItem][subItem]['visibles'][0]


                elif subItem == 'settings':
                    # looping through implementations of an module:
                    for ii in access[modeItem][subItem]:
                        # looping through fields: 'names', 'labels', 'difficulties', 'infos', 'visibles'
                        for fieldItems in access[modeItem][subItem][ii]['available']:
                            access[modeItem][subItem][ii]['available']
                            if filterConfig[modeItem][subItem]['names'] in access[modeItem][subItem]['available']['names']:
                                msg = _translate("MainWindow", "Updating field of filter.ini: ", None) + ii
                            else:
                                msg = _translate("MainWindow", "Adding new field in filter.ini: ", None) + ii
                            self.dPrint(msg, 3)
                    pass
        """

    def updateFilter(self, difficulty):
        """!
        The displayed exercises will be updated according to the provided difficulty and the selected exercise
        """

        self.dPrint('updateFilter()', 2)

        template = dict()
        template['names'] = list()
        template['labels'] = list()
        template['infos'] = list()
        template['difficulties'] = list()
        template['visibles'] = list()
        template['filterDefinition'] = list()

        moduleNamesFiles = list(self.frameWork['settings']['access'])
        # resettings "displayed"- entries befor filling accoring to self.user['difficulty']
        for modeItem in moduleNamesFiles:
            self.frameWork['settings']['access'][modeItem]['main']['displayed'] = deepcopy(template)
            for si in list(self.frameWork['settings']['access'][modeItem]['settings']):
                self.frameWork['settings']['access'][modeItem]['settings'][si]['displayed'] = deepcopy(template)
        # looping through modules : exercises, generator,...
        for modeItem in moduleNamesFiles:
            temp = self.frameWork['settings']['access'][modeItem]['main']['available']['names']
            if isinstance(temp, str):
                itemLen = 1
            else:
                itemLen = len(temp)
            # looping through items of module
            for ii in range(itemLen):
                if (int(self.frameWork['settings']['access'][modeItem]['main']['available']['difficulties'][ii]) <= \
                        int(self.user['difficulty'])) and \
                        self.frameWork['settings']['access'][modeItem]['main']['available']['visibles'][ii]:
                    for hh in list(template):
                        self.frameWork['settings']['access'][modeItem]['main']['displayed'][hh].append(
                            self.frameWork['settings']['access'][modeItem]['main']['available'][hh][ii])
            # looping through settings
            items = list(self.frameWork['settings']['access'][modeItem]['settings'])
            for item in items:
                temp = self.frameWork['settings']['access'][modeItem]['settings'][item]['available']['names']
                if isinstance(temp, str):
                    itemSetLen = 1
                else:
                    itemSetLen = len(temp)
                for ii in range(itemSetLen):
                    if int(self.frameWork['settings']['access'][modeItem]['settings'][item]['available']['difficulties'][ii]) <= \
                            int(self.user['difficulty']) and \
                            self.frameWork['settings']['access'][modeItem]['settings'][item]['available']['visibles'][ii]:
                        for hh in list(template):
                            self.frameWork['settings']['access'][modeItem]['settings'][item]['displayed'][hh].append(
                                self.frameWork['settings']['access'][modeItem]['settings'][item]['available'][hh][ii])

        self.dPrint('Leaving updateFilter()', 2)


    def saveSettings(self, settingsModes=['all'], filename=''):
        """!
        The settings will be saved as python struct.
        settingsMode can be:
            all:
                all settings will be saved
            frameWork:
                The frameWork Settings will be saved as they are saved in the results file. The file handle of the debug
                file will be deleted, since file handles cannot be saved.
            generator
            preprocessor
            player

        """

        self.dPrint('saveSettings()', 2)

        if isinstance(settingsModes, str):
            settingsModes = [settingsModes]
        saveStruct = dict()

        for settingsMode in settingsModes:
            if settingsMode == 'frameWork' or settingsMode == 'all':
                saveStruct['frameWork'] = self.frameWork['settings'].copy()
                # file handles cannto be saved:
                saveStruct['frameWork']['debug']['debuggingFileHandle'] = None
            if settingsMode == 'generator' or settingsMode == 'all':
                saveStruct['generator'] = dict()
                saveStruct['generator']['settings'] = self.curGenerator['settings']
                saveStruct['generator']['settingLimits'] = self.curGenerator['settingLimits']
            if settingsMode == 'preprocessor' or settingsMode == 'all':
                saveStruct['preprocessor'] = dict()
                saveStruct['preprocessor']['settings'] = self.curPreprocessor['settings']
                saveStruct['preprocessor']['settingLimits'] = self.curPreprocessor['settingLimits']
            if settingsMode == 'player' or settingsMode == 'all':
                saveStruct['player'] = dict()
                saveStruct['player']['settings'] = self.curPlayer['settings']
                saveStruct['player']['settingLimits'] = self.curPlayer['settingLimits']
            if settingsMode == 'exercise' or settingsMode == 'all':
                saveStruct['exercise'] = dict()
                saveStruct['exercise']['settings'] = self.curExercise['settings']
                saveStruct['exercise']['settingLimits'] = self.curExercise['settingLimits']

            if settingsModes[0] == 'all':
                fileDialogMsg = _translate("MainWindow", 'all settings', None)
            else:
                fileDialogMsg = _translate("MainWindow",  ' the settings', None) + \
                                str(settingsModes)

        if filename:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                _translate("MainWindow", "Saving of ", None) + fileDialogMsg +
                _translate("MainWindow", "settings ...", None),
                self.frameWork['settings']['lastSavingPath'],
                _translate("MainWindow", 'Result file', None) + ' (*.set) ;;' +\
                _translate("MainWindow", 'All files', None) + ' (*)',
                _translate("MainWindow", 'Result file', None) + ' (*.set)',
                QtWidgets.QFileDialog.DontUseNativeDialog
            )

            with bz2.BZ2File(filename, 'w') as f:
                pickle.dump(saveStruct, f)

            self.frameWork['settings']['lastSavingPath'] = os.path.dirname(filename)
        self.dPrint('Leaving saveSettings()', 2)


    def selectExerSettingFromListBox(self):
        """!
        This function is called when the exercise settings is selected in the list box. The settings  will be loaded
        by  self.curExercise['functions']['settingsLoading']()
        """

        self.dPrint('selectExerSettingFromListBox()', 2)
        idx = self.ui.lwExerSetVal.currentRow()
        exerciseName = self.curExercise['settings']['exerciseName']
        if idx < len(self.frameWork['settings']['access']['exercises']['settings'][exerciseName]['displayed']['names']):
            exerciseSettingsName = self.frameWork['settings']['access']['exercises']['settings'][
                exerciseName]['displayed']['names'][idx]
        else:
            exerciseSettingsName = 'default'

        msg = _translate("MainWindow", 'Loading settings: %s  ...',
                         None) % exerciseSettingsName  # Laden von Settings
        self.showInformation(msg)


        try:
            self.iniExercise(exerciseName, exerciseSettingsName)
            #self.curExercise['functions']['settingsLoading'](exerciseSettingsName)
            msg = _translate("MainWindow", 'Loading of settings was successful: ', None) +\
                  exerciseSettingsName  # Settings erfolgreich geladen
            self.showInformation(msg)

        except:

            msg = _translate("MainWindow", 'Exception: Loading of settings %(a)s '
                                          'of exercise %(b)s was not successfull', None) % \
                  {'a':exerciseSettingsName, 'b':exerciseName}
            # Exception: Laden von Einstellungen von Übung misslungen
            self.showInformation(msg)

        self.updateInfoFields()
        self.writeIniFile()

        self.dPrint('Leaving selectExerSettingFromListBox()', 2)


    def iniSettingsInMenu(self, mode):
        """!
        Build menu entries for the loading setting files. With the mode the removed entries can be defined.
                key word arguemnt:
                mode -- defines which settings will cleared. Possible options are:
                        'curExercise', 'curGenerator', 'curPlayer', 'curPreprocessor', curSetlist
        """

        # self.ui.actionSettingsExp.triggered.connect(self.showInformation)
        self.dPrint('iniSettingsInMenu()', 2)

        if mode == 'curExercise':
            menuMode = 'menuExer'
            modeAvailable = 'exercises'
            modName = getattr(self, mode)['settings']['exerciseName']
        elif mode == 'curGenerator':
            menuMode = 'menuGenerator'
            modeAvailable = 'generators'
            modName = getattr(self, mode)['settings']['generatorName']
        elif mode == 'curPreprocessor':
            menuMode = 'menuPreprocessor'
            modeAvailable = 'preprocessors'
            modName = getattr(self, mode)['settings']['preprocessorName']
        elif mode == 'curPlayer':
            menuMode = 'menuPlayer'
            modeAvailable = 'player'
            modName = getattr(self, mode)['settings']['playerName']
        elif mode == 'curSetlist':
            menuMode = 'menuSetlists'
            modeAvailable = 'setlists'
        else:
            menuMode = ''
            modeAvailable = ''

        if mode in ['curExercise', 'curGenerator', 'curPreprocessor', 'curPlayer']:
            if self.frameWork['settings']['expertSettingsMode']:
                presetlistPy = self.getListOfFiles(getattr(self, mode)['path']['presets'], depthOfDir=1,
                                                namePart='.py')
            else:
                presetlistPy = []

            presetlistSet = self.getListOfFiles(getattr(self, mode)['path']['presets'], depthOfDir=1,
                                               namePart='.set')
            presetlist = list(set(presetlistPy + presetlistSet))
            ii = 0
            presetlistShort = []
            for item in presetlist:
                name = item.split('.')[0]
                presetlistShort.append(name)
                ii = ii + 1
            ii = 0
            for preset in presetlistShort:

                available = self.frameWork['settings']['access'][modeAvailable]['settings'][modName]['available']
                if preset in available['names']:
                    idx = available['names'].index(preset)
                    if available['visibles'][idx] and \
                            int(available['difficulties'][idx]) <= int(self.user['difficulty']):
                        actionSetup = QtWidgets.QAction(self)
                        actionSetup.setObjectName("actionPreset" + str(ii))
                        actionSetup.setText(_translate("MainWindow", preset, None))
                        actionSetup.triggered.connect(lambda: self.selectSettingsFromMenu(mode))
                        # mode is passed as argument to the connected function to distinguish between the different menus
                        getattr(self.ui, menuMode).addAction(actionSetup)

                        getattr(self, mode)['gui']['menu'].append(actionSetup)
                ii = ii + 1

            for pathItem in ['analysis', 'scripts']:
                if pathItem in getattr(self, mode)['path']:
                    # the current exercise requires additionaly entries for  the analysis of the data

                    getattr(self.ui, menuMode).addSeparator()

                    analysisList = self.getListOfFiles(getattr(self, mode)['path'][pathItem], depthOfDir=1, \
                                                      namePart='.py')
                    ii = 0
                    analysisListShort = []
                    for item in analysisList:
                        name = item.split('.')[0]
                        analysisListShort.append(name)
                        ii = ii + 1

                    ii = 0
                    for item in analysisListShort:
                        actionSetup = QtWidgets.QAction(self)
                        actionSetup.setObjectName("actionPreset" + str(ii))
                        actionSetup.setText(_translate("MainWindow", item, None))
                        if mode == 'curExercise':
                            actionSetup.triggered.connect(self.callDynmicFunctionsExercise)
                        if mode == 'curGenerator':
                            actionSetup.triggered.connect(self.callDynmicFunctionsGenerator)
                        if mode == 'curPreprocessor':
                            actionSetup.triggered.connect(self.callDynmicFunctionsPreprocessor)
                        if mode == 'curPlayer':
                            actionSetup.triggered.connect(self.callDynmicFunctionsPlayer)
                        getattr(self.ui, menuMode).addAction(actionSetup)
                        getattr(self, mode)['gui']['menu'].append(actionSetup)
                        ii = ii + 1
        elif mode == 'curSetlist':
            ii = 0

            for item in self.frameWork['settings']['access']['setlists']['main']['displayed']['names']:
                actionSetup = QtWidgets.QAction(self)
                actionSetup.setObjectName("actionsetlist" + str(ii))
                actionSetup.setText(_translate("MainWindow", item, None))
                actionSetup.triggered.connect(self.getSetlist)  #
                getattr(self.ui, menuMode).addAction(actionSetup)
                getattr(self, mode)['gui']['menu'].append(actionSetup)
                ii = ii + 1

            actionSetup = QtWidgets.QAction(self)
            actionSetup.setObjectName("actionSetlistActivate")
            actionSetup.setText(_translate("MainWindow", 'Setlist activated', None))
            actionSetup.setCheckable(True)
            actionSetup.setChecked(True)
            actionSetup.setEnabled(False)
            actionSetup.triggered.connect(self.setSetlistActivation)
            self.curSetlist['gui']['actionSetlistActivate'] = actionSetup
            getattr(self.ui, menuMode).addAction(actionSetup)

        self.dPrint('Leaving iniSettingsInMenu()', 2)


    def selectSetlistMode(self):
        """!
        This function is called when the TrainerMode tab is used to switch between single run and
        set list mode.
        Be aware: Debugging of this function might not return correct tab index. Whyever!
        """

        self.dPrint('selectSetlistMode()', 2)

        # if a setlist run is activte nothing should happen: no tab change, no button clicks
        # (see disabled buttons)
        mPos = QtGui.QCursor.pos()
        mPosInTabBar = self.ui.tabTrainerMode.tabBar().mapFromGlobal(mPos)

        ch = self.ui.tabTrainerMode.children()
        tabIndex = -1
        for ii in range(self.ui.tabTrainerMode.tabBar().count()):
            if self.ui.tabTrainerMode.tabBar().tabRect(ii).contains(mPosInTabBar):
                tabIndex = ii

        self.setSetlistActivation(tabIndex)

        # for setting index to correct setting and exercise after running an setlist
        if tabIndex == 0:
            self.updateExerciseSettingsListBox()
            self.updateInfoFields()

        # connect( self.getSetlist)
        self.dPrint('Leaving selectSetlistMode()', 2)


    def setSetlistActivation(self, tabIndex=-1):
        """!
        Toggle the activation of the setlist. If a setlist is selected it can be activated/deactivatet.
        A setlist can only be started if it is activatetd.
        Be aware: Debugging of this function might not return correct tab index. Whyever!
        """

        self.dPrint('selectSetlistMode()', 2)

        # setChecked
        if tabIndex < 0:
            tabIndex = self.ui.tabTrainerMode.currentIndex()

        if tabIndex == 0:
            self.curSetlist['active'] = False
        elif tabIndex == 1:
            self.curSetlist['active'] = True
        else:
            msg = _translate("MainWindow", 'Trainer Selection Mode: No Hit?!?', None)
            self.dPrint(msg, 1, guiMode=True)
        self.dPrint(' Quit selectSetlistMode()', 2)


    def selectSettingsFromMenu(self, mode='curPlayer'):
        """!
         This function is called if a setting is selected in the menue of the
        exercise, generator, preprocess, player.
        """

        self.dPrint('selectSettingsFromMenu()', 2)
        try:
            settingsName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            settingsName = re.sub('&', '', settingsName)

            if mode == 'curExercise':
                #self.iniExercise()
                self.curExercise['functions']['settingsLoading'](settings=settingsName)
            elif mode == 'curGenerator':
                self.iniSubmodule('generator', self.curGenerator['settings']['generatorName'],
                                  settingsName, enforceInit=True)
                self.curGenerator['functions']['settingsLoading'](settings=settingsName)
            elif mode == 'curPlayer':
                # TOOO: vorteil von iniSubmodule: nicht nur felder werden gesetzt sondern
                self.iniSubmodule('player', self.curPlayer['settings']['playerName'],
                                  settingsName, enforceInit=True)
                self.curPlayer['functions']['settingsLoading'](settings=settingsName)
            elif mode == 'curPreprocessor':
                self.iniSubmodule('preprocessor', self.curPreprocessor['settings']['processorName'],
                                  settingsName, enforceInit=True)
                self.curPreprocessor['functions']['settingsLoading'](settings=settingsName)
        except:
            self.dPrint('Exception: Could not load setting for ' + mode, 1)

        self.updateInfoFields()
        self.dPrint('Leaving selectSettingsFromMenu()', 2)


    def iniSubmodule(self, mode, submoduleName, settings='', enforceInit=False):
        """!
        Initializing the submodule as defined in submoduleName if it wasn't initialized already. The destructor of the
        previous submodule is called if necessary. If submoduleName = '' only the previous submodule will be closed down.

        key word argument:
        mode - defines which submodule has to be initialized. It can be 'generator', 'preprocesspr' or 'player'
        submoduleName - defines the generator, preprocessr, player which will be initialized
        settings - settings defined as string defining a setting file by its base name or a dictionary of settings as
                    used in and getattr(self, module)['settings']
        enforceInit - defines if a the submodule has to be reinitilized again
        """
        self.dPrint(' iniSubmodule()', 2)

        if mode == 'generator':
            module = 'curGenerator'
        elif mode == 'preprocessor':
            module = 'curPreprocessor'
        elif mode == 'player':
            module = 'curPlayer'
        Mode = mode[0].upper() + mode[1:]

        if getattr(self, module)['settings'][mode + 'Name'] == submoduleName and not (enforceInit):
            return
        # if settings are loaded submoduleName and getattr(self,'cur' + Mode(['settings'][mode  + 'Name'] are the same
        if not(getattr(self, module)['settings'][mode + 'Name'] == '') \
                and getattr(self, module)['settings'][mode + 'Name'] != mode + 'Name':
            self.dPrint('Calling destructor of previous ' + submoduleName + '.', 3)
            self.clearSettingsInMenu(mode=module)
            try:
                getattr(self, module)['functions']['destructor']()
            except:

                self.dPrint('Exception: Could not call destructor of ' + mode + ': ' +
                            getattr(self, module)['settings'][mode + 'Name'], 1)

        if not (settings):
            if mode in self.settings and submoduleName != '' and submoduleName in self.settings[mode]:
                lastSettingsName = self.settings[mode][submoduleName]['lastSettingsName']
                settings = self.settings[mode][submoduleName][lastSettingsName]
                msg = "ini" + Mode + "(): using settings defined in self.settings['" + mode + "'] "
            else:
                if self.frameWork['settings']['last' + Mode + 'Settings'] and \
                        self.frameWork['settings']['last' + Mode] == submoduleName:
                    settings = self.frameWork['settings']['last' + Mode + 'Settings']
                    msg = "ini" + Mode + "(): using settings defined in " + \
                          "self.frameWork['settings']['last" + Mode + "Setting']"
                else:
                    msg = "ini" + Mode + "(): no previous settings found"
            self.dPrint(msg, 3)
        if mode == 'player':
            tempMode = mode
        else:
            tempMode = mode + 's'
        if not (submoduleName == 'None' or submoduleName == ''):
            modulePath = os.path.join(self.frameWork['path'][tempMode],
                                      submoduleName + '.py')
            spec = importlib.util.spec_from_file_location(submoduleName, modulePath)
            specModule = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(specModule)
            getattr(specModule, submoduleName)(self, settings)
            self.iniSettingsInMenu(module)

            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = settings['settingsName']

            self.curExercise['settings'][mode] = submoduleName
            self.curExercise['settings'][mode+'Settings'] = settingsName

            if not (mode in self.settings):
                self.settings[mode] = dict()
                self.settings[mode]['last' + Mode + 'Name'] = ''

            if not (submoduleName in self.settings[mode]):
                self.settings[mode][submoduleName] = dict()
                self.settings[mode][submoduleName]['lastSettingsName'] = ''
            self.settings[mode][submoduleName][settingsName] = getattr(self, module)['settings']

            self.settings[mode]['last' + Mode + 'Name'] = submoduleName
            self.settings[mode][submoduleName]['lastSettingsName'] = settingsName

        self.dPrint('Leaving iniSubmodule()', 2)


    def readIniFile(self, mode='frameWorkSettings', module='frameWork'):
        """!
        Loading configuration and status of the frameWork.
        The option 'mode' allows to read all fields or just specified fields of the iniFile.
        mode can be:
            'frameWorkSettings' or anything else otherwise

        module can be:
            'frameWork', 'curExercise', 'curGenerator', 'curPreprocessor', 'curPlayer'

        In case of 'frameWork' all settings defined in the ini-file of the frameWork
        [last exercise and its settings, last generator and its settings,...]
        will be read and the system calibration will be set.
        In the other cases the calibration of the modules will be read.
        """

        self.dPrint(' readIniFile()', 2)
        if not(os.path.isfile(self.frameWork['settings']['iniFile'])):
            msg = _translate("MainWindow", "CICoachLab.ini could not be be found. You may have to copy and edit "
                                           "CICoachLab.in or retrieve the deleted file before starting CICOachLab." ,None)
            self.dPrint(msg, 0, guiMode=True)
            return False
        iniFileConfig = ConfigObj(self.frameWork['settings']['iniFile'], encoding="utf8")
        try:
            if mode == 'frameWorkSettings':
                self.frameWork['settings']['lastSavingPath'] = iniFileConfig['DynamicSettings']['lastSavingPath']
                self.frameWork['settings']['lastExercise'] = iniFileConfig['DynamicSettings']['lastExercise']
                self.frameWork['settings']['lastExerciseSettings'] = iniFileConfig['DynamicSettings']['lastExerciseSettings']
                self.frameWork['settings']['lastGenerator'] = iniFileConfig['DynamicSettings']['lastGenerator']
                self.frameWork['settings']['lastGeneratorSettings'] = iniFileConfig['DynamicSettings']['lastGeneratorSettings']
                self.frameWork['settings']['lastPreprocessor'] = iniFileConfig['DynamicSettings']['lastPreprocessor']
                self.frameWork['settings']['lastPreprocessorSettings'] = iniFileConfig['DynamicSettings']['lastPreprocessorSettings']
                self.frameWork['settings']['lastPlayer'] = iniFileConfig['DynamicSettings']['lastPlayer']
                self.frameWork['settings']['lastPlayerSettings'] = iniFileConfig['DynamicSettings']['lastPlayerSettings']
                self.frameWork['settings']['lastSetlist'] = iniFileConfig['DynamicSettings']['lastSetlist']

                self.frameWork['settings']['lastRunEndTime'] = iniFileConfig['DynamicSettings']['lastRunEndTime']
                self.frameWork['settings']['dailyCumulatedRunTime'] = iniFileConfig['DynamicSettings'].as_float(
                    'dailyCumulatedRunTime')
                self.frameWork['settings']['maxDailyCumulatedRunTime'] = iniFileConfig['DynamicSettings'].as_float(
                    'maxDailyCumulatedRunTime')
                self.frameWork['settings']['currentSessionStartTime'] = iniFileConfig['DynamicSettings'].as_float(
                    'currentSessionStartTime')

                self.frameWork['settings']['autoBackupResults'] = iniFileConfig['system'].as_bool('autoBackupResults')
                self.frameWork['settings']['dualScreen'] = iniFileConfig['system']['dualScreen']
                self.frameWork['settings']['patientMode'] = iniFileConfig['system'].as_bool('patientMode')
                self.frameWork['settings']['coachMode'] = iniFileConfig['system'].as_bool('coachMode')
                self.frameWork['settings']['coachBackupPath'] = iniFileConfig['system']['coachBackupPath']
                self.frameWork['settings']['useSettingsFromLoadedData'] = iniFileConfig['system'].as_bool(
                    'useSettingsFromLoadedData')
                self.frameWork['settings']['expertSettingsMode'] = iniFileConfig['system'].as_bool(
                    'expertSettingsMode')
                self.frameWork['settings']['expertMode'] = iniFileConfig['system'].as_bool('expertMode')
                self.frameWork['settings']['patientSavingFile'] = iniFileConfig['system']['patientSavingFile']
                self.frameWork['settings']['bitlockerMode'] = iniFileConfig['system'].as_bool('bitlockerMode')
                self.frameWork['settings']['bitlockerDevice'] = iniFileConfig['system']['bitlockerDevice']
                self.frameWork['settings']['bitlockerPathClear'] = iniFileConfig['system']['bitlockerPathClear']
                self.frameWork['settings']['bitlockerPathEncrypt'] = iniFileConfig['system']['bitlockerPathEncrypt']
                self.frameWork['settings']['studyMode'] = iniFileConfig['system'].as_bool('studyMode')
                self.curMasterlist['settings']['masterlistFile'] = iniFileConfig['system']['masterlistFile']
                self.curMasterlist['settings']['masterlistStart'] = iniFileConfig['system'].as_bool('masterlistStart')
                self.frameWork['settings']['exerciseFrameGeometry'] = iniFileConfig['system']['exerciseFrameGeometry']
                self.frameWork['settings']['mainFramegeometry'] = iniFileConfig['system']['mainFramegeometry']
                self.frameWork['settings']['localization'] = iniFileConfig['system']['localization']
                self.frameWork['settings']['fixMasterVolume'] = iniFileConfig['system'].as_bool('fixMasterVolume')
                self.frameWork['settings']['masterVolumeValue'] = iniFileConfig['system']['masterVolumeValue']
                self.frameWork['settings']['ignoreFilterFile'] = iniFileConfig['system'].as_bool('ignoreFilterFile')

                self.frameWork['settings']['debug']['mode'] = iniFileConfig['debug'].as_bool('mode')
                self.frameWork['settings']['debug']['verbosityThreshold'] = iniFileConfig['debug'].as_int('verbosityThreshold')
                self.frameWork['settings']['debug']['debuggingFile'] = iniFileConfig['debug']['debuggingFile']
                self.frameWork['settings']['debug']['debuggingTempFile'] = iniFileConfig['debug']['debuggingTempFile']
                self.frameWork['settings']['debug']['demoMode'] = iniFileConfig['debug'].as_bool('demoMode')
                # self.frameWork['settings']['debug']['debuggingFile'] is an empty string no debug file will be written
                # if no temporary debug file is defined self.frameWork['settings']['debug']['debuggingTempFile'] is set
                # to self.frameWork['settings']['debug']['debuggingFile']
                if self.frameWork['settings']['debug']['debuggingFile'] and \
                    not(self.frameWork['settings']['debug']['debuggingTempFile']):
                    self.frameWork['settings']['debug']['debuggingTempFile'] = self.frameWork['settings']['debug']['debuggingFile']

                # move debugging file of previous session to temporary debug file to append new debugging information
                destination = self.frameWork['settings']['debug']['debuggingTempFile']
                source = self.frameWork['settings']['debug']['debuggingFile']
                if destination and (destination != source):
                    try:
                        status, self.frameWork['settings']['debug']['debuggingTempFileBackup'] = \
                            self.copyLogFile(source, destination, backupDestination=True, logMode=False)
                    except:
                        msg = _translate("MainWindow",
                                         'Could not copy the log file from {:s} to {:s}. Please contact your admininstrator.'.format(
                                             source, destination), None)
                        self.dPrint(msg, 0, guiMode=True)
                        self.__exit__(None, None, None)


            # module = 'frameWork'  or  'curGenerator', 'curPreprocessor', 'curPlayer', 'curExercise'
            for moduleItem in getattr(self, module)['calibration']:  # 'level', 'time'
                # 'level/'time','unit', optionally 'stdDev', 'iterations', ...  for more see self.setDefaulCalibration

                if module == 'frameWork':
                    iniFileModule = 'frameWork'
                    moduleShort = 'frameWork'
                elif module == 'curExercise':
                    iniFileModule = self.curExercise['settings']['exerciseName']
                    moduleShort = 'exercises'
                elif module == 'curGenerator':
                    iniFileModule = self.curGenerator['settings']['generatorName']
                    moduleShort = 'generators'
                elif module == 'curPreprocessor':
                    iniFileModule = self.curPreprocessor['settings']['preprocessorName']
                    moduleShort = 'preprocessor'
                elif module == 'curPlayer':
                    iniFileModule = self.curPlayer['settings']['playerName']
                    moduleShort = 'player'

                if iniFileModule in iniFileConfig['calibration']:
                    if moduleItem in iniFileConfig['calibration'][iniFileModule]:
                        for item in getattr(self, module)['calibration'][moduleItem]:
                            try:
                                # check if (optional) calibration infos have been written to iniFile
                                if item in iniFileConfig['calibration'][iniFileModule]:
                                    if item == moduleItem:
                                        getattr(self, module)['calibration'][moduleItem][item] = \
                                        float(iniFileConfig['calibration'][iniFileModule][moduleItem][item])
                                    else:
                                        getattr(self, module)['calibration'][moduleItem][item] = \
                                            iniFileConfig['calibration'][iniFileModule][moduleItem][item]
                                    msg = 'Reading calibration from iniFile: '+module+'/'+iniFileModule+', '+mode+', '+item
                                    self.dPrint(msg, 2)
                            except:
                                msg = 'Exception: Could not read calibration item from iniFile.'
                                self.dPrint(msg, 0)

                # creating default fields of dynamically created fields (player,exercises,etc....)if no entries are found
                if not(moduleShort == 'frameWork'):
                    if not(iniFileModule in iniFileConfig['calibration']):
                        iniFileConfig['calibration'][iniFileModule] = {}
                    if not(moduleItem in iniFileConfig['calibration'][iniFileModule]):
                        iniFileConfig['calibration'][iniFileModule][moduleItem] = ''

            self.frameWork['settings']['iniFileConfig'] = iniFileConfig
            status = True
        except Exception as e:
            msg = _translate("MainWindow", 'IniFile could not be read successfully. '
                                           'Please check content of iniFile and/or call administrator'
                                           f"\nError: \'{e}\'"
                             , None)
            self.dPrint(msg, 0, guiMode=True)
            status = False
        self.dPrint('Leaving readIniFile()', 2)
        return status

    def iniExercise(self, exerName, settings='', enforceInit=False):
        """!
        Initializing the exercise as defined in exerName if it wasn't initialized already. The destructor of the
        previous exercise is called and the gui items in the menu are removed if necessary.
        The new menu entries will be added.

        key word argument:
        exerName -- defines the exercise which will be initialized
        """

        self.dPrint('iniExercise()', 2)

        if self.curSetlist['active']:
            runMode = 'setlists'
            statesName = self.curSetlist['settings']['setlistName']
        else:
            runMode = 'srExercises'
            statesName = exerName
        iniSuccess = False

        # just initialize exercise if it was not selected before
        if exerName != self.curExercise['settings']['exerciseName'] or enforceInit:
            # save previous exercise if an old exercise exists and no setlist is active
            oldExerName = self.curExercise['settings']['exerciseName']
            if (oldExerName != '' and \
                    oldExerName != exerName) or enforceInit:    # and not(self.curSetlist['active']):
                try:
                    self.clearSettingsInMenu(mode='curExercise')
                    if self.curExercise['functions']['eraseExerciseGui'] != None:
                        self.curExercise['functions']['eraseExerciseGui']()
                    else:
                        self.dPrint('eraseExerciseGui is undefined: This may be the case if data and  settings are set from saved data', 2)
                except:
                    self.dPrint('Exception: Could not eraseGui for  ' + self.curExercise['settings']['exerciseName'], 1)

                if self.frameWork['settings']['usePrevStates']:
                    try:
                        if self.curSetlist['active']:
                            self.savePrevState(setOrExerMode=runMode, setOrExername=self.curSetlist['settings']['setlistName'])
                        else:
                            self.savePrevState(setOrExerMode=runMode, setOrExername=oldExerName)
                    except:
                        self.dPrint('Exception: Could not save previous '+ runMode +' states for ' +
                            self.curExercise['settings']['exerciseName'], 1)

            if not(exerName == '' or exerName == 'None'):
                if self.frameWork['settings']['usePrevStates'] and\
                    not(exerName == '') and not(self.prevStates[runMode][statesName]['prevExercise'] == dict())\
                        and self.prevStates[runMode][statesName]['prevExercise']['settings']['exerciseName'] == exerName:
                    # exerName is found in the prevStates it has been initialized before and should be callable from
                    # prevStates
                    self.loadPrevState(setOrExerMode=runMode, setOrExername=exerName)
                    iniSuccess = True
                else:
                    if not(settings):
                        if 'exercise' in self.settings and exerName in self.settings['exercise']:
                            if ('lastSettingsName' in self.settings['exercise'][exerName]) and \
                                    bool(self.settings['exercise'][exerName]['lastSettingsName']):
                                lastSettingsName = self.settings['exercise'][exerName]['lastSettingsName']
                                settings = self.settings['exercise'][exerName][lastSettingsName]
                                msg = "iniExercise(): using settings defined in self.settings['exercise'] "
                            else:
                                settings = 'default'
                                msg = "iniExercise(): no previous settings found"
                        else:
                            if self.frameWork['settings']['lastExerciseSettings'] and \
                                    self.frameWork['settings']['lastExercise'] == exerName and\
                                    self.frameWork['settings']['lastExerciseSettings'] != 'settings (dict)':
                                settings = self.frameWork['settings']['lastExerciseSettings']
                                msg = "iniExercise(): using settings defined in " + \
                                    "self.frameWork['settings']['lastExerciseSettings']:" + settings
                            else:
                                settings = 'default'
                                msg = "iniExercise(): no previous settings found"
                        self.dPrint(msg, 3)

                    module = ''
                    try:
                        modulePath = os.path.join(self.frameWork['path']['exercises'],
                                                  exerName + '.py')
                        spec = importlib.util.spec_from_file_location(exerName, modulePath)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        self.curExercise['settings']['name'] = exerName
                        # call __ini__ of exercise in loaded module with self and settings
                        try:
                            getattr(module, exerName)(self, settings)
                            # setting up menu entries of exercise, if generator, etc are initialized as well the
                            # respective menu entries will be generated during initialization
                            self.iniSettingsInMenu('curExercise')
                            iniSuccess = True
                        except:
                            msg = _translate("MainWindow", 'Exception: Could not initialize exercise settings %(a)s from module '
                                             '%(b)s! ', None) %{'a': exerName, 'b': module}
                            self.dPrint(msg, 1, guiMode=True)
                        self.updateRunlist()
                    except:
                        msg = _translate("MainWindow", 'Exception: Could not import exercise %(a)s'
                                                      ' from module %(b)s!', None) %\
                                    {'a':exerName, 'b': module}
                        self.dPrint(msg, 1, guiMode=True)

                self.prevStates[runMode]['lastSingleRunExercise'] = exerName
            else:
                self.dPrint('No exercise is defined for initialization!', 1)
            try:
                for item in self.frameWork['gui']['buttons']:
                    if item.objectName() == 'pbRunSetlist':
                        if self.curSetlist['settings']['setlistName'] != '':
                            item.setDisabled(False)
                    else:
                        item.setDisabled(False)
            except:
                self.dPrint('Exception: Could not disable exercise gui elements', 1)
        else:
            if settings and self.curExercise['functions']['settingsLoading']:
                self.curExercise['functions']['settingsLoading'](settings)
            elif not(self.curExercise['functions']['settingsLoading']):
                msg = _translate("MainWindow",
                    'A loading function for the settings should to be defined which calls the loading of CICochLab ' +\
                    'to handle the loading of settings of the submodules. Alternatively the loading of the submodules ' +\
                    'has to be handled by exercise. Which is not recommended.  Please contact your admin.'
                                 , None)
                self.dPrint(msg, 0, guiMode=True)
                """
                # after the exercise settings have been updated the defined generator, preprocessor and player are loaded
                playerSettings = self.curPlayer['settings']
                generatorSettings = self.curGenerator['settings']
                preprocessorSettings = self.curPreprocessor['settings']
                self.iniSubmodule('player', playerSettings['playerName'],
                                  playerSettings, enforceInit=True)
                self.iniSubmodule('generator', generatorSettings['generatorName'],
                                  generatorSettings, enforceInit=True)
                self.iniSubmodule('preprocessor', preprocessorSettings['preprocessorName'],
                                  preprocessorSettings, enforceInit=True)
                """
            self.dPrint('Exercise is already selected but settings have changed. Just calling loadSetting-function', 3)
            iniSuccess = True

        if iniSuccess:
            if not('exercise' in self.settings):
                self.settings['exercise'] = dict()
                self.settings['exercise']['lastExerciseName'] = ''
            if not(exerName in self.settings['exercise']):
                self.settings['exercise'][exerName] = dict()
                self.settings['exercise'][exerName]['lastSettingsName'] = ''

            if isinstance(settings, str):
                settingsName = settings
            elif isinstance(settings, dict) and \
                    'settingsName' in settings:
                settingsName = settings['settingsName']

            self.settings['exercise']['lastExerciseName'] = exerName
            self.settings['exercise'][exerName]['lastSettingsName'] = settingsName
            #
            if settingsName:
                self.settings['exercise'][exerName][settingsName] = deepcopy(self.curExercise['settings'])

            # quit function if no gui exists for an update
            if not(sip.isdeleted(self.ui.centralwidget)):
                self.updateExerciseListBox()
                self.updateExerciseSettingsListBox()
                self.updateInfoFields()

        self.dPrint('Leaving iniExercise()', 2)


    def writeIniFile(self, mode='frameWork', module='frameWork'):
        """!
        Writing back changes of the configuration and status of the frameWork
        """

        self.dPrint('writeIniFile()', 2)
        if len(self.frameWork['settings']['iniFileConfig']) == 0:
            msg = _translate("MainWindow", 'Writing of ini File failed. Inifile configuration could not bee read before. '
                             'Check content of iniFile', None)
            self.dPrint(msg, 0, guiMode = True)
        else:
            try:
                if mode == 'frameWork':
                    iniFileConfig = self.frameWork['settings']['iniFileConfig']

                    iniFileConfig['DynamicSettings']['lastSavingPath'] = self.frameWork['settings']['lastSavingPath']
                    iniFileConfig['DynamicSettings']['lastExercise'] = self.frameWork['settings']['lastExercise']
                    iniFileConfig['DynamicSettings']['lastExerciseSettings'] = self.frameWork['settings']['lastExerciseSettings']
                    iniFileConfig['DynamicSettings']['lastGenerator'] = self.frameWork['settings']['lastGenerator']
                    iniFileConfig['DynamicSettings']['lastGeneratorSettings'] = self.frameWork['settings']['lastGeneratorSettings']
                    iniFileConfig['DynamicSettings']['lastPreprocessor'] = self.frameWork['settings']['lastPreprocessor']
                    iniFileConfig['DynamicSettings']['lastPreprocessorSettings'] = self.frameWork['settings']['lastPreprocessorSettings']
                    iniFileConfig['DynamicSettings']['lastPlayer'] = self.frameWork['settings']['lastPlayer']
                    iniFileConfig['DynamicSettings']['lastPlayerSettings'] = self.frameWork['settings']['lastPlayerSettings']
                    iniFileConfig['DynamicSettings']['lastSetlist'] = self.frameWork['settings']['lastSetlist']

                    iniFileConfig['DynamicSettings']['lastRunEndTime'] = self.frameWork['settings']['lastRunEndTime']
                    iniFileConfig['DynamicSettings']['dailyCumulatedRunTime'] = self.frameWork['settings']['dailyCumulatedRunTime']
                    iniFileConfig['DynamicSettings']['maxDailyCumulatedRunTime'] = self.frameWork['settings']['maxDailyCumulatedRunTime']
                    iniFileConfig['DynamicSettings']['currentSessionStartTime'] = self.frameWork['settings'][
                        'currentSessionStartTime']

                    iniFileConfig['system']['autoBackupResults'] = self.frameWork['settings']['autoBackupResults']
                    iniFileConfig['system']['dualScreen'] = self.frameWork['settings']['dualScreen']
                    iniFileConfig['system']['patientMode'] = self.frameWork['settings']['patientMode']
                    iniFileConfig['system']['coachMode'] = self.frameWork['settings']['coachMode']
                    iniFileConfig['system']['coachBackupPath'] = self.frameWork['settings']['coachBackupPath']
                    iniFileConfig['system']['useSettingsFromLoadedData'] = self.frameWork['settings'][
                        'useSettingsFromLoadedData']
                    iniFileConfig['system']['expertSettingsMode'] = self.frameWork['settings'][
                        'expertSettingsMode']
                    iniFileConfig['system']['expertMode'] = self.frameWork['settings']['expertMode']
                    iniFileConfig['system']['patientSavingFile'] = self.frameWork['settings']['patientSavingFile']
                    iniFileConfig['system']['bitlockerMode'] = self.frameWork['settings']['bitlockerMode']
                    iniFileConfig['system']['bitlockerDevice'] = self.frameWork['settings']['bitlockerDevice']
                    iniFileConfig['system']['bitlockerPathClear'] = self.frameWork['settings']['bitlockerPathClear']
                    iniFileConfig['system']['bitlockerPathEncrypt'] = self.frameWork['settings']['bitlockerPathEncrypt']
                    iniFileConfig['system']['studyMode'] = self.frameWork['settings']['studyMode']
                    iniFileConfig['system']['masterlistFile'] = self.curMasterlist['settings']['masterlistFile']
                    iniFileConfig['system']['masterlistStart'] = self.curMasterlist['settings']['masterlistStart']
                    iniFileConfig['system']['exerciseFrameGeometry'] = self.frameWork['settings']['exerciseFrameGeometry']
                    iniFileConfig['system']['mainFramegeometry'] = self.frameWork['settings']['mainFramegeometry']
                    iniFileConfig['system']['localization'] = self.frameWork['settings']['localization']
                    iniFileConfig['system']['fixMasterVolume'] = self.frameWork['settings']['fixMasterVolume']
                    iniFileConfig['system']['masterVolumeValue'] = self.frameWork['settings']['masterVolumeValue']
                    iniFileConfig['system']['ignoreFilterFile'] = self.frameWork['settings']['ignoreFilterFile']

                    iniFileConfig['debug']['mode'] = self.frameWork['settings']['debug']['mode']
                    iniFileConfig['debug']['verbosityThreshold'] = self.frameWork['settings']['debug']['verbosityThreshold']
                    iniFileConfig['debug']['debuggingFile'] = self.frameWork['settings']['debug']['debuggingFile']
                    iniFileConfig['debug']['debuggingTempFile'] = self.frameWork['settings']['debug']['debuggingTempFile']
                    iniFileConfig['debug']['demoMode'] = self.frameWork['settings']['debug']['demoMode']

                # module = 'frameWork'  or  'curGenerator', 'curPreprocessor', 'curPlayer', 'curExercise'
                for moduleItem in getattr(self, module)['calibration']:  # 'level', 'time'
                    # 'level/'time','unit', optionally 'stdDev', 'iterations', ...  for more see self.setDefaulCalibration

                    if module == 'frameWork':
                        iniFileModule = 'frameWork'
                    elif module == 'curExercise':
                        iniFileModule = self.curExercise['settings']['exerciseName']
                    elif module == 'curGenerator':
                        iniFileModule = self.curGenerator['settings']['generatorName']
                    elif module == 'curPreprocessor':
                        iniFileModule = self.curPreprocessor['settings']['preprocessorName']
                    elif module == 'curPlayer':
                        iniFileModule = self.curPlayer['settings']['playerName']

                    if moduleItem in iniFileConfig['calibration'][iniFileModule]:
                        for item in getattr(self, module)['calibration'][moduleItem]:
                            # write optional fields only if they contain entries.
                            if not(isinstance(getattr(self, module)['calibration'][moduleItem][item], list) and\
                                len(getattr(self, module)['calibration'][moduleItem][item]) > 0):
                                try:
                                    iniFileConfig['calibration'][iniFileModule][moduleItem][item] = \
                                        getattr(self, module)['calibration'][moduleItem][item]
                                    msg = 'Writing calibration to iniFile: ' + module + '/' + iniFileModule + ', ' + mode + ', ' + item
                                    self.dPrint(msg, 2)
                                except:
                                    msg = 'Exception: Could not write calibration to iniConfig.'
                                    self.dPrint(msg, 0)

                #iniFileConfig['calibration']['frameWork']['level'] = \
                #    self.frameWork['calibration']['level']['level']

                iniFileConfig.filename = self.frameWork['settings']['iniFile']
                iniFileConfig.write_empty_values = True
                iniFileConfig.write()
            except:
                msg = _translate("MainWindow", 'Writing of inifile failed. Check file permissions.', None)
                self.dPrint(msg, 0, guiMode=True)

        self.dPrint('Leaving writeIniFile()', 2)


    def dPrint(self, msg, verbosity=2, guiMode=False):
        """!
        This functions handles the feedback to the calling python console and the debug/log file as defined in
        config['debug']['debuggingTempFile'] which can be set via the ini file. The verbosity level defines how much information

        key word argument:
        verbosity -- The higher the option the less likely it is that it will be displayd.

        is provided. The debug verbosity can be defined in the ini file:
        0: no output.
        1: print-message in case of unexpected behavour or basic information
        2: print-message tracking call of functions
        3: print-message tracking logic within functions
        4: print message in other cases

        guiMode: provide additional gui feedback for the user.
        with verbosity set to 0 or 1 the gui will be provided as warning and as information otherwise
        """

        try:
            if self.frameWork['settings']['debug']['verbosityThreshold'] >= verbosity:

                if guiMode:
                    if verbosity == 0:
                        title = _translate("MainWindow", 'CICoachLab - Critical error', None)
                        text = msg + f"\n({self.frameWork['temp']['dPrintItemNumber']:03d}) "
                        CICoachDialog(self, title, text, 'error')
                    elif verbosity < 2:
                        title = _translate("MainWindow", 'CICoachLab - Warning', None)
                        text = msg + f"\n({self.frameWork['temp']['dPrintItemNumber']:03d}) "
                        CICoachDialog(self, title, text, 'warning')
                    else:
                        title =  _translate("MainWindow", 'CICoachLab - Information', None)
                        text = msg + f"\n({self.frameWork['temp']['dPrintItemNumber']:03d}) "
                        CICoachDialog(self, title, text, 'information')
                msg = f"\n{self.frameWork['temp']['dPrintItemNumber']:03d}: "+msg
                print(msg)

                if self.frameWork['settings']['debug']['verbosityThreshold'] >= verbosity and \
                        self.frameWork['settings']['debug']['mode']:
                    try:
                        if not(self.frameWork['settings']['debug']['debuggingTempFile'] == None or
                               self.frameWork['settings']['debug']['debuggingTempFile'] == ''):
                            try:
                                if self.frameWork['settings']['debug']['debuggingFileHandle'] == None:
                                    # open debug file for writing/appending if it wasn't before
                                    print('Open debug file for writing')
                                    self.frameWork['settings']['debug']['debuggingFileHandle'] = open(
                                        self.frameWork['settings']['debug']['debuggingTempFile'], 'a')
                            except:
                                print('Exception: Could not open debug file for writing', 1)
                            else:
                                # writing to debug file
                                self.frameWork['settings']['debug']['debuggingFileHandle'].write(msg + '\n')
                    except:
                        print('Exception: Could not write into debug file', 1)
        except:
            print(msg, 1)
        self.frameWork['temp']['dPrintItemNumber'] = self.frameWork['temp']['dPrintItemNumber'] + 1


    def updateRunlist(self):
        """!
        List all runs of the currently selected exercise
        """

        # removing all items
        self.ui.lwRuns.clear()
        if not(self.curExercise['settings']['exerciseName'] == '') and \
            self.curExercise['settings']['exerciseName'] in self.runData.keys():

            exerName = self.curExercise['settings']['exerciseName']

            items = [self.runData[exerName][ii]['time']['endASCII'] for ii in
                     list(self.runData[exerName])]
            #items = self.runData[self.curExercise['settings']['exerciseName']].keys()
            ii = 1
            for item in items:
                self.ui.lwRuns.insertItem(ii, item)
                ii = ii + 1


    def selectRundata(self):
        """!
        Select a single or multiple runs as selected in the run list.
        """

        self.dPrint('selectRundata()', 2)

        rows = [x.row() for x in self.ui.lwRuns.selectedIndexes()]
        self.curExercise['selectedRunData'] = rows

        self.updateInfoFields()

        self.dPrint('Leaving selectRundata()', 2)


    def showRundata(self):
        """!
        Showing the mean results of a single or multiple runs as selected in the run list.
        """

        self.dPrint('showRundata()', 2)

        exerciseName = self.curExercise['settings']['exerciseName']
        if self.curExercise['functions']['displayResults'] == None:
            msg = _translate("MainWindow",'No display function is defined for ', None) + exerciseName
            self.dPrint(msg, 0, guiMode=True)
            return
        try:
            items = list(self.runData[exerciseName])

            for row in self.curExercise['selectedRunData']:
                self.curExercise['functions']['displayResults'](
                    self.runData[self.curExercise['settings']['exerciseName']][items[row]])

        except:
            self.dPrint(_translate("MainWindow",'Exception: Could not show results', None), 1, guiMode=True)
        self.dPrint('Leaving showRundata()', 2)


    def loadRunData(self, event='', filename=''):
        """!
        Loading run data and the last settings of the exercise, player, preprocessor, generator and the frameWork
        as used in the last run. The data will be loaded from the filename provided as argument. If no filename is
        provided the user can select a file via gui.
        The last used player, generator, preprocessor and exercise are initialized.
        The loaded settings can be set to the player, generator, preprocessor and exercise if the flag
        self.frameWork['settings']['useSettingsFromLoadedData'] is set to 'True'.
        """

        self.dPrint('loadRunData()', 2)
        if filename == '':
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                _translate("MainWindow", 'Opening of CICoachLab results...', None),
                self.frameWork['settings']['lastSavingPath'],
                _translate("MainWindow", 'Result-files', None) + ' (*.cid);;' +\
                _translate("MainWindow", 'All files', None) + ' (*)',
                _translate("MainWindow", 'Result-files', None) + ' (*.cid)',
                QtWidgets.QFileDialog.DontUseNativeDialog
            )

        if filename != '':
            try:
                usingBitlocker = self.requiresBitlocker(filename)
                if usingBitlocker:
                    self.unlockBitlocker()
                with bz2.open(filename, 'rb') as f:
                    loadStruct = pickle.load(f)
                if usingBitlocker:
                    self.lockBitlocker()


                if not(loadStruct['frameWork'] == self.frameWork['settings']):
                    self.dPrint(
                        'The frameWork settings differ between the current system and the system used in the loaded data',
                        0)

                if self.frameWork['settings']['useSettingsFromLoadedData']:
                    self.dPrint(
                        'Setting settings to settings of loaded data. (except: self.frameWork[\'settings\']) ', 0)
                    generatorSettings =  loadStruct['generator']['settings']
                    preprocessorSettings  = loadStruct['preprocessor']['settings']
                    playerSettings  = loadStruct['player']['settings']
                    exerciseSettings  = loadStruct['exercise']['settings']

                else:
                    playerSettings = loadStruct['player']['settings']['settingsName']
                    generatorSettings = loadStruct['generator']['settings']['settingsName']
                    preprocessorSettings = loadStruct['preprocessor']['settings']['settingsName']
                    exerciseSettings = loadStruct['exercise']['settings']['settingsName']




                self.user = loadStruct['user']
                self.iniSubmodule('player',  loadStruct['player']['settings']['playerName'],
                                playerSettings, enforceInit=True)
                self.iniSubmodule('generator', loadStruct['generator']['settings']['generatorName'],
                                  generatorSettings, enforceInit=True)
                self.iniSubmodule('preprocessor',  loadStruct['preprocessor']['settings']['preprocessorName'],
                                     preprocessorSettings, enforceInit=True)
                self.iniExercise(loadStruct['exercise']['settings']['exerciseName'],
                                 exerciseSettings, enforceInit=True)

                self.runData = loadStruct['runData']

                maxRunDataCounter = -1
                for item in list(self.runData):
                    # if entries are found get the highest counter number, which may be 0 in case of one item
                    if len(self.runData[item]):
                        maxRunDataCounter = max(maxRunDataCounter, max(self.runData[item]))


                self.runDataCounter = maxRunDataCounter + 1
                # check if system settings have been the same and

                self.updateRunlist()
                self.updateInfoFields()
                self.frameWork['settings']['saving']['filename'] = filename
                self.frameWork['settings']['lastSavingPath'] = os.path.dirname(filename)

                # uodate last saving path
                self.writeIniFile()

            except:
                self.dPrint('Exception: Loading of data was not succesfull.', 1)
        else:
            self.dPrint('Loading of data was canceled by the user', 1)
        self.dPrint('Leaving loadRunData()', 2)


    def saveRunData(self, event='', filename=''):
        """!
        Saving run data and the last settings of the exercise, player, preprocessor, generator and the frameWork
        as used in the last run. The data will be saved in the filename provided as argument. If no filename is
        provided the user can select a file via gui.
        For an easier gui access the last saving path is read from the iniFile and will be reset after saving. if the backup
        data is saved the self.frameWork['settings']['lastSavingPath'] will not be set.

        key word argument>
        filename -- a filename can be provided.  (default '')
                    If no filename is provided the default filename self.frameWork['settings']['saving']['filename']
                    will be tried. As last resort 'backupData.cid' will be written in the current working directory.
        """

        self.dPrint('saveRunData()', 2)

        # update last saving path, it might have changed since start of MainWindow because the data might have saved
        # elsewhere


        if self.frameWork['settings']['coachMode']:
            title = _translate("MainWindow", 'Saving data as "coach"?', None)
            question = _translate("MainWindow",
                                  'You are currently logged in as "coach". Do you really want to save the data?\n\n' +
                                  'Please confirm the filename or even better select a new filename.'
                                  , None)
            quest = CICoachDialog(self, title, question)
            answer = quest.returnButton()
            if not(answer == QtWidgets.QMessageBox.Yes):
                msg = "The user 'coach' aborted the saving process."
                self.dPrint(msg, 0)
                return
            if filename:
                lastPath = filename
            else:
                lastPath = self.frameWork['settings']['lastSavingPath']

        else:
            lastPath = self.frameWork['settings']['lastSavingPath']

        backUpfile = ''

        if filename == '':
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                _translate("MainWindow", "Saving of CICoachLab results",None),
                lastPath,
                _translate("MainWindow", "Result files", None)+'(*.cid) ;;' + \
                _translate("MainWindow", "All files", None) + '(*)',
                _translate("MainWindow", "Result files", None)+'(*.cid)',
                QtWidgets.QFileDialog.DontUseNativeDialog
            )

        
        if filename != '':
            try:
                if not('.cid' in filename):
                    filename = filename+'.cid'

                saveStruct = dict()
                saveStruct['runData'] = self.runData

                saveStruct['frameWork'] = self.frameWork['settings'].copy()

                saveStruct['generator'] = dict()
                saveStruct['generator']['settings'] = self.curGenerator['settings']
                saveStruct['generator']['settingLimits'] = self.curGenerator['settingLimits']

                saveStruct['preprocessor'] = dict()
                saveStruct['preprocessor']['settings'] = self.curPreprocessor['settings']
                saveStruct['preprocessor']['settingLimits'] = self.curPreprocessor['settingLimits']

                saveStruct['player'] = dict()
                saveStruct['player']['settings'] = self.curPlayer['settings']
                saveStruct['player']['settingLimits'] = self.curPlayer['settingLimits']

                saveStruct['exercise'] = dict()
                saveStruct['exercise']['settings'] = self.curExercise['settings']
                saveStruct['exercise']['settingLimits'] = self.curExercise['settingLimits']

                saveStruct['user'] = self.user
                saveStruct['userLimits'] = self.userLimits
                # saveStruct['exercise']['settings']['exerciseName']




                usingBitlocker = self.requiresBitlocker(filename)
                if usingBitlocker:
                    self.unlockBitlocker()

                # backup file with unique filename if file already exists
                if os.path.isfile(filename):
                    backUpfile = self.backupFile(filename,'.cid')


                # creates files diretory if it does not exist, if the app forgot to create the directory
                dirname = os.path.dirname(filename)
                if not(os.path.isdir(dirname)) and dirname:
                    os.mkdir(dirname)

                # search for and replace function handles because function handles cannot be saved.
                saveStruct = self.replaceFunctionHandlesByName(saveStruct, 'function')
                # file handles cannot be saved:
                saveStruct['frameWork']['debug']['debuggingFileHandle'] = None
                with bz2.BZ2File(filename, 'w') as f:
                    pickle.dump(saveStruct, f)

                if filename != 'backupData.cid' and not(self.frameWork['systemCheck']):
                    self.frameWork['settings']['lastSavingPath'] = dirname
                    self.writeIniFile()
                else:
                    self.dPrint('Saving path of backup file was not written to' + self.frameWork['settings']['iniFile']
                                + '.', 4)
                self.frameWork['settings']['saving']['filename'] = filename
                if backUpfile:
                    self.dPrint('Removing backup file ' + backUpfile, 3)
                    os.remove(backUpfile)
                if usingBitlocker:
                    self.lockBitlocker()
            except:
                if backUpfile:
                    self.dPrint('Exception: Saving of data was not successful. Backup data was saved to ' + backUpfile, 1)
                else:
                    self.dPrint('Exception: Saving of data was not successful.', 1)

        else:
            self.dPrint('Saving of data was canceled by user.', 1)

        self.dPrint('Leaving saveRunData()', 2)


    def backupFile(self, filename, ext):
        """!
        The function creates a unique backupfile name based on the time
        with the format "%Y-%m-%d_%H-%M-%S".

        The new backup file name is returned.
        """
        #self.dPrint('Leaving saveRunData()', 2)

        now = datetime.datetime.now()
        t = now.strftime("%Y-%m-%d_%H-%M-%S")
        backupfilename = re.sub(ext, '_' + t + '_bu' + ext, filename)
        shutil.copyfile(filename, backupfilename)

        self.dPrint('backup filename: "' + backupfilename + '"', 4)

        #self.dPrint('Leaving saveRunData()', 2)
        return backupfilename


    def replaceFunctionHandlesByName(self, struct, key):
        """!
        Recursively loop through levels of dictionary and check for functions defined in the dictionary items.
        If the item 'function' is found the item will be set to the function name.
        """

        if key in struct:
            try:
                if struct[key] != None and not(isinstance(struct[key],str)):
                    struct[key] = struct[key].__qualname__
                else:
                    struct[key] = ''
            except:
                struct[key] = str(struct[key])
            return struct
        for k, v in struct.items():
            if isinstance(v, dict):
                 struct[k] = self.replaceFunctionHandlesByName(v, key)  # added return statement

        return struct


    def measureReactionTime(self, parHandle, mode=''):
        """!
        This function should be called right after the presentation of the item in the player function to start the
        measurements and right at the beginning of the feedback function. The function is called by the exxercise class,
        which is the reason why self does not point to the CICoachLab Class.

        The saving and display of the measurement has to be handled by the exercise function for a consistent format of the data.
        """
        try:
            reactionTimeDelay = self.curExercise['calibration']['time']['time']
        except:
            reactionTimeDelay = 0

        parHandle.dPrint('measureReactionTime()', 2)
        if mode == 'start':
            parHandle.frameWork['temp']['presentationTime'] = time()
        elif mode == 'stop' and not(parHandle.frameWork['temp']['presentationTime'] == None):
            parHandle.frameWork['temp']['reactionTimeAfterPresentation'] = \
                time() - parHandle.frameWork['temp']['presentationTime'] - reactionTimeDelay
        parHandle.dPrint('Leaving measureReactionTime()', 2)


    def calibrateSystemExercise(self, temp=None, parHandle=None):

        self.calibrateSystem(mode='exercise')


    def calibrateSystemLevel(self, temp=None, parHandle=None):
        self.calibrateSystem(mode='level')


    def calibrateSystem(self, temp=None, parHandle=None, mode='reactionTime'):
        """!
        This function measures the system reaction time between the presentation of an item and the automatic calling
        of the user input function of the currently selected input function. The data will be saved in the ini file
        in an the exercise specific entry.

        The function should be called from within the exercise specific menu where it might be called with dofferent modes.
        reaction time, level, screenSize calibration or whatever.
        # This function measures the time after closing of the playback function and the time when the user button is
        called automatically. The time in seconds is saved
        """

        # making run of calibration independant from chosen tab
        tempSetListMode = self.curSetlist['active']
        self.dPrint('calibrateReactionTime()', 2)

        # Entering system calibration mode
        self.frameWork['systemCheck'] = False
        if mode == 'exercise':
            if not('calibration' in self.curExercise['functions']) or not(self.curExercise['functions']['calibration']):
                msg = _translate("MainWindow", 'No Calibration function is defined in current exercise.', None)
                self.dPrint(msg, 2, guiMode=True)
                return
            # check if exercise, player and generator are initializyed, disregarding the optional preprocessing
            if not(self.curExercise['settings']['exerciseName'] == '' or self.curGenerator['settings'][
                'generatorName'] == '' or
                    self.curPlayer['settings']['playerName'] == ''):

                if self.curSetlist['active']:
                    #switch to single run tab and deactivate
                    self.curSetlist['active'] = False

                exerciseName = self.curExercise['settings']['exerciseName']
                filename = os.path.join(self.curExercise['path']['results'],
                    'calibration_reactionTime_' + exerciseName + '.cid')
                # call exercise specific calibration function, because exercises know what has to be calibrated
                self.curExercise['functions']['calibration'](filename=filename)

                self.saveRunData(filename=filename)

                # saving data  into base path of exercies
                filename = os.path.join(self.curExercise['path']['base'] + 'calibrationTimeDelay.cid')
                self.saveRunData(event='', filename=filename)

                # create exercise specific reactionTime entry
                self.writeIniFile(mode='frameWork', module='curExercise')
            else:
                msg = 'Could not start calibration of reaction time: Check if the player or the generator are set.'
                self.dPrint(msg, 0)
        elif mode == 'level': # level or system level calibration
            # saving status of generator and player for
            oldGeneratorName = self.curGenerator['settings']['generatorName']
            oldGeneratorSettingsName = self.curGenerator['settings']['settingsName']
            oldGeneratorSettings = self.curGenerator['settings']

            oldPlayerName = self.curPlayer['settings']['playerName']
            oldPlayerSettingsName = self.curPlayer['settings']['settingsName']
            oldPlayerSettings  = self.curPlayer['settings']
            self.iniSubmodule('generator', 'genSin')
            self.iniSubmodule('player',  'playAudio')

            oldCalDB = self.frameWork['calibration']['level']['level']

            genPath = os.path.join(self.frameWork['path']['generators'],'genHarmXdBperOct',
                                      'harmXdBperOct.py')
            genSpec = importlib.util.spec_from_file_location('harmXdBperOct.py', genPath)
            genHarm = importlib.util.module_from_spec(genSpec)
            genSpec.loader.exec_module(genHarm)

            # generate 15 seconds of 1000Hz sinusoid
            dur = 20
            parameter = dict()
            parameter['f0'] = 1000
            parameter['fs'] = 44100
            parameter['dur'] = dur  + 2/parameter['fs']
            parameter['rampTime'] = 0.0
            parameter['maxF'] = 1000
            # loading the default calibartion
            self.curGenerator['functions']['settingsLoading'](settings=parameter)

            temp = CalibrationCall(self)
            temp.exec_()

            self.writeIniFile(mode='frameWork', module='frameWork')

            self.iniSubmodule('player',  oldPlayerName, '')
            self.iniSubmodule('generator', oldGeneratorName, '')

            self.curGenerator['functions']['settingsLoading'](oldGeneratorSettings)
            self.curPlayer['functions']['settingsLoading'](oldPlayerSettings)

        # Leaving the system calibration mode
        self.frameWork['systemCheck'] = False
        self.curSetlist['active'] = tempSetListMode

        msg = _translate("MainWindow", 'Finished calibration successfully', None)
        self.dPrint(msg, 0, guiMode=True)
        self.dPrint('Leaving calibrateReactionTime()', 2)


    def stoppSetlist(self):
        """!
        This function sets self.curSetlist['stopped'] to True and calls the function quitRun() of the
        current exercise.
        """

        self.dPrint('stoppSetlist()', 2)
        # check if setlist really was running when stoppSetList is called
        if self.curSetlist['stopped']:
            isJustRunning = False
        else:
            isJustRunning = True

        # just call stopp function if set list was running (should not happen)
        if isJustRunning:
            # set list is now officialy stopped, when the quitRun function of the exercise calls the self.closeDownRun()
            # thr progress of the setlist is paused.
            self.curSetlist['stopped'] = True
            self.ui.pbStoppSetlist.setDisabled(False)
            self.curExercise['functions']['cancelRun']()
        self.dPrint('Leaving stoppSetlist()', 2)


    def loadSettings(self, settings, module):
        """!
        The framework function loadSettings, reads setting files if the settings string defines filename or copies the
        settings item from the dictionary settings to self.
        self.loadSettings is called by the loadSettings functions of the modules or by the the SettingsDialog.
        If self.loadSettings is called by the SettingsDialog the modules will be (re) initialized with the new settings.
        If the function is called by the loading functions
        of the modules module specific action can be run before or after self.loadSettings().
        E.g., the loading of a setting in an exercise may require some more actions after loading new settings like
        loading new audio, updating the exercise gui, or initialization of generators, preprocessor, player.
        The handling of a failed loading of the settings may differ.

        The setting files can be a python struct which contains the settings of the a single or more modules or it can
        be a python file which sets the settings. The usage of a python struct format should be the default.
        The python struct can be generated with the settings Dialog.
        The settings in the python struct are equal to the settings saved

        in self.settings[module][settingsName]

        The python script setting format can be used as well. It is more versatile, powerfull and dangerous, since it
        it potentially can damage the CICoachLab instance by misuse of the CICoachLab handle
        instance and it might affect the system as well if system calls are defined and applied in the python script.
        The usage of the python script format requires profound knownledge of the CICoachLab format.

        If both types of setting files are present the *.set format is used.

        The modules can be:
        curGenerator
        curPreprocessor
        curPlayer
        curExercise

        The frameWork settings may be saved as well but will not be loaded.
        The loaded settings of the modules will be passed to the repective loading function of the modules.
        The settingLimits of the modules are saved as well but will not be loaded to respect changes/updates of settingLimits.
        """

        self.dPrint('loadSettings()', 2)

        if module == 'curExercise':
            mode = 'exercise'
        elif module == 'curGenerator':
            mode = 'generator'
        elif module == 'curPreprocessor':
            mode = 'preprocessor'
        elif module == 'curPlayer':
            mode = 'player'
        if self.curExercise['functions']['eraseExerciseGui']:
            self.curExercise['functions']['eraseExerciseGui']()
        if self.curExercise['functions']['settingsDefault']:
            self.curExercise['functions']['settingsDefault']()

        if isinstance(settings, str):
            self.dPrint(settings, 4)

            # check which kind of setting file has to be loaded: *.set or *.py. If two types of
            tempSettingsPath = os.path.join(getattr(self, module)['path']['presets'],
                                      settings + '.set')
            if os.path.isfile(tempSettingsPath):
                with bz2.open(tempSettingsPath, 'rb') as f:
                    loadStruct = pickle.load(f)

                for settingsMode in list(loadStruct):
                    if settingsMode == module or module == 'all':
                        #if called by loading function of module the settings will be set otherwise the module will be
                        # (re)initialized with the new passed settings
                        callingFunctionName = getouterframes(currentframe(), 2)[1][3]
                        if callingFunctionName == 'loadSettings':
                            getattr(self, module)['settings'] = loadStruct[settingsMode]
                        else:
                            if not(mode == 'exercise'):
                                self.iniSubmodule(mode, loadStruct[settingsMode][mode + 'Name'],
                                                  loadStruct[settingsMode])
                            else:
                                self.iniExercise(loadStruct[settingsMode][mode + 'Name'],
                                                      loadStruct[settingsMode])
                        getattr(self, module)['settings']['settingsName'] = settings

            else:
                modulePath = os.path.join(getattr(self, module)['path']['presets'],
                                          settings + '.py')
                if os.path.isfile(modulePath):
                    if self.frameWork['settings']['expertSettingsMode']:
                        spec = importlib.util.spec_from_file_location(settings + ".py", modulePath)
                        set = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(set)  # required for in exercise loading
                        set.defineSettings(self)

                        getattr(self, module)['settings']['settingsName'] = settings
                    else:
                        self.dPrint(_translate("MainWindow",'This should not happen: loadSettings failed. '
                                    'A python setting has been found but is disabled according to .'
                                    '"expertSettingsMode" in CICoachLab.ini', None), 0, guiMode=True)

                else:
                    self.dPrint('This should not happen: loadSettings failed. '
                                'String does not define a valid file name.', 0)
        elif isinstance(settings, dict):
            self.dPrint('Update settings ' + settings[mode + 'Name'] + '.', 0)
            for item in settings:
                #if item in settings: #getattr(self, module)['settings']:
                #if item in settings: #getattr(self, module)['settings']:
                getattr(self, module)['settings'][item] = settings[item]
                self.dPrint('Update settings.' + item, 0)
        else:
            self.dPrint('This should not happen: loadSettings failed', 0)

        getattr(self, module)['settings']['settingsSaved'] = True

        self.dPrint('Leaving loadSettings()', 2)


    def getSetlist(self, event=None, setlistName=''):
        """!
        Loading setlist: The set list is defined by the selected gui menu or by the passing of the argument.
        """

        self.dPrint('getSetlist()', 2)

        try:
            # do not initialize/read a setlist if the setlist mode is not active
            if self.curSetlist['active']:
                if setlistName == '':
                    if self.sender().objectName() == 'lwSetlistNameVal':
                        setlistNames = self.frameWork['settings']['access']['setlists']['main']['displayed']['names']
                        setlistName = setlistNames[self.ui.lwSetlistNameVal.currentRow()]+'.lst'
                    else:
                        # selected from menu bar
                        setlistName = self.sender().text()
                        # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
                        setlistName = re.sub('&', '', setlistName)
                # save single run state if a single run exercise has noted its initialization in inExercise() before
                if self.prevStates['srExercises']['lastSingleRunExercise'] != '':
                    oldExerciseName = self.prevStates['srExercises']['lastSingleRunExercise']
                    if self.frameWork['settings']['usePrevStates']:
                        self.savePrevState(setOrExerMode='srExercises', setOrExername=oldExerciseName)

                # if data of the new setlist is found in a previous states the previous state is reloaded
                if self.frameWork['settings']['usePrevStates'] and\
                        not(self.prevStates['setlists'][setlistName]['prevExercise'] == dict()):
                    self.loadPrevState(setOrExerMode='setlists', setOrExername=setlistName)
                else:
                    # the new set list will be read from file after checking for saving of previous setlist
                    try:
                        if self.frameWork['settings']['usePrevStates']:
                            if self.curSetlist['settings']['setlistName'] != '' and \
                                    self.curSetlist['settings']['setlistName'] != setlistName:
                                # a setlist with a different name has been loaded initialized before > save it in prevState
                                oldSetlist = self.curSetlist['settings']['setlistName']
                                mode = 'setlists'
                                self.savePrevState(setOrExerMode=mode, setOrExername=oldSetlist)
                            else:
                                oldSetlist = ''
                        # finally, reading new set list!!!
                        setlistConfig = ConfigObj(
                            os.path.join(self.frameWork['path']['setlists'], setlistName), encoding="utf8")

                        validsetlistConfig = True
                        settingSections = ['exercises', 'generators', 'preprocessors', 'player']
                        section = ''
                        for section in self.curSetlist['settings']['list'].keys():
                            if section in settingSections:
                                # check entries for consistency within sections
                                # type(setlistConfig['exercises']['names']) != 1: not valid since a single string entry is imported as string
                                # not list as in a multi string case
                                if not(type(setlistConfig[section]['names']) == str) and \
                                        len(setlistConfig[section]['names']) != len(setlistConfig[section]['settings']):
                                    msg = _translate("MainWindow", 'Could not read setlist ', None)\
                                          + setlistName + \
                                          _translate("MainWindow", '\nSection ', None) + section + \
                                                _translate("MainWindow", ': The number of items in names(', None)+ str(
                                        len(setlistConfig['exercises']['names'])) + \
                                                _translate("MainWindow", ')  and settings (', None) + \
                                                str(len(setlistConfig[section]['settings'])) +\
                                        _translate("MainWindow", ') does not match', None)
                                    self.dPrint(msg , 0,
                                                guiMode=True)
                                    validsetlistConfig = False
                                    break

                        # consistency check across sections
                        if not((len(setlistConfig['exercises']['settings']) == len(
                                setlistConfig['player']['settings']) ==
                                len(setlistConfig['generators']['settings']) ==
                                len(setlistConfig['description']['short'])
                                ) and
                                (len(setlistConfig['generators']['settings']) == len(
                                    setlistConfig['preprocessors']['settings'])
                                 or len(setlistConfig['preprocessors']['settings']) == 0)):
                            self.dPrint('Could not read setlist ' + setlistName +
                                        ': The number of items in names(' + str(
                                len(setlistConfig['exercises']['names'])) + \
                                        ')  and settings (' +
                                        str(len(setlistConfig[section]['settings'])) +
                                        ') does not match across exercises, generators, preprocessors and player', 0)

                        # for an easier later access make the single name entry as long as the settings entries
                        if validsetlistConfig:
                            for section in self.curSetlist['settings']['list'].keys():
                                if section in settingSections:
                                    self.curSetlist['settings']['list'][section]['settings'] = setlistConfig[section][
                                        'settings']
                                    if type(setlistConfig[section]['names']) != type(setlistConfig[section]['settings']) \
                                            and len(setlistConfig[section]['names']) != len(
                                        setlistConfig[section]['settings']):
                                        self.curSetlist['settings']['list'][section]['names'] \
                                            = [setlistConfig[section]['names']] * len(setlistConfig[section]['settings'])  #
                                    else:
                                        self.curSetlist['settings']['list'][section]['names'] = setlistConfig[section][
                                            'names']
                                elif section == 'description' and 'description' in setlistConfig and \
                                        'short' in setlistConfig['description']:
                                    # extract optional description from setlist file
                                    self.curSetlist['settings']['list'][section]['short'] = setlistConfig[section]['short']

                        self.curSetlist['settings']['setlistName'] = setlistName
                        self.ui.pbRunSetlist.setDisabled(False)
                        self.ui.pbNewRun.setEnabled(False)
                        # noting down setlistName, for saving of state if the state will be changed to single run mode or
                        # another setlist
                        self.prevStates['setlists']['lastSetlist'] = setlistName
                        self.prevStates['srExercises']['lastSingleRunExercise'] = ''
                    except:
                        self.dPrint('Exception: Could not read setlist ' + setlistName, 1)
            else:
                self.dPrint('Could not read setlist because setlistMode is False: setlistName: ' + setlistName, 1)
        except:
            self.dPrint('Exception: Could not read setlist ' + setlistName, 1)

        self.ui.lwSetlistContentVal.clear()
        ii = 0
        if len(self.curSetlist['settings']['list']['description']['short']) > 1:
            for item in self.curSetlist['settings']['list']['description']['short']:
                self.ui.lwSetlistContentVal.addItem(item)
        else:
            for item in self.curSetlist['settings']['list']['exercises']['names']:
                self.ui.lwSetlistContentVal.addItem(item)

        self.updateInfoFields()
        self.dPrint('Leaving getSetlist()', 2)


    def savePrevState(self, setOrExerMode, setOrExername):
        """!
        this function saves the previously used states of the exercise, generator, preprocessor, player, setlist
        """

        self.prevStates[setOrExerMode][setOrExername]['prevExercise'] = self.curExercise.copy()
        self.prevStates[setOrExerMode][setOrExername]['prevGenerator'] = self.curGenerator.copy()
        self.prevStates[setOrExerMode][setOrExername]['prevPreprocessor'] = self.curPreprocessor.copy()
        self.prevStates[setOrExerMode][setOrExername]['prevPlayer'] = self.curPlayer.copy()
        self.prevStates[setOrExerMode][setOrExername]['prevSetlist'] = self.curSetlist.copy()

        self.closePath('curExercise')
        self.closePath('curGenerator')
        self.closePath('curPreprocessor')
        self.closePath('curPlayer')

        self.clearSettingsInMenu('curExercise')
        self.clearSettingsInMenu('curGenerator')
        self.clearSettingsInMenu('curPreprocessor')
        self.clearSettingsInMenu('curPlayer')

        self.initializeToDefaults('curExercise')
        self.initializeToDefaults('curGenerator')
        self.initializeToDefaults('curPreprocessor')
        self.initializeToDefaults('curPlayer')
        if self.curSetlist['active'] == False:
            self.initializeToDefaults('curSetlist')


    def loadPrevState(self, setOrExerMode, setOrExername):
        """!
        this function loads the previously used states of the exercise, generator, preprocessor, player, setlist
        """

        self.curExercise = self.prevStates[setOrExerMode][setOrExername]['prevExercise'].copy()
        self.curGenerator = self.prevStates[setOrExerMode][setOrExername]['prevGenerator'].copy()
        self.curPreprocessor = self.prevStates[setOrExerMode][setOrExername]['prevPreprocessor'].copy()
        self.curPlayer = self.prevStates[setOrExerMode][setOrExername]['prevPlayer'].copy()
        self.curSetlist = self.prevStates[setOrExerMode][setOrExername]['prevSetlist'].copy()

        self.addingPath('curExercise')
        self.addingPath('curGenerator')
        self.addingPath('curPreprocessor')
        self.addingPath('curPlayer')

        self.updateRunlist()
        self.iniSettingsInMenu('curExercise')
        self.iniSettingsInMenu('curGenerator')
        self.iniSettingsInMenu('curPreprocessor')
        self.iniSettingsInMenu('curPlayer')


    def updateInfoFields(self):
        """!
        his function updates the information label about the selected generator, preprocessor, player
        and the respective settings. The menus will be filled by the ini functions.
        """

        self.dPrint('updateInfoFields()', 2)

        try:
            self.ui.labelGeneratorNameVal.setText(self.curGenerator['settings']['generatorName'])
            self.ui.labelGeneratorSetVal.setText(self.curGenerator['settings']['settingsName'])
            self.ui.labelPreProcNameVal.setText(self.curPreprocessor['settings']['preprocessorName'])
            self.ui.labelPreProcSetVal.setText(self.curPreprocessor['settings']['settingsName'])
            self.ui.labelPlayerNameVal.setText(self.curPlayer['settings']['playerName'])
            self.ui.labelPlayerSetVal.setText(self.curPlayer['settings']['settingsName'])

            if self.curExercise['settings']['exerciseName'] != '':
                # after a setlist the selected exercise in the exercise listbox has to be reset
                if self.curExercise['settings']['exerciseName'] in \
                        self.frameWork['settings']['access']['exercises']['main']['displayed']['names']:
                    idx = self.frameWork['settings']['access']['exercises']['main']['displayed']['names'].index(
                        self.curExercise['settings']['exerciseName'])

                    # blocking changeEvent-signal is required since the change of the selected item would call this
                    # function again resetting the exercise otherwise.
                    self.ui.lwExerNameVal.blockSignals(True)
                    self.ui.lwExerNameVal.setCurrentRow(idx)
                    self.ui.lwExerNameVal.blockSignals(False)
                else:
                    self.dPrint('The selection could not be set because the exercise ' +
                                self.curExercise['settings']['exerciseName'] + ' is not displayed.', 2)

                exerName = self.curExercise['settings']['exerciseName']
                settings = self.frameWork['settings']['access']['exercises']['settings'][exerName]['displayed']['names']
                # same for the exercise settings listbox
                if self.curExercise['settings']['settingsName'] == 'default' or self.curExercise['settings']['settingsName'] == '':
                    idxSetting = -1
                else:
                    if self.curExercise['settings']['settingsName'] in settings:
                        idxSetting = settings.index(self.curExercise['settings']['settingsName'])
                        self.ui.lwExerSetVal.blockSignals(True)
                        self.ui.lwExerSetVal.setCurrentRow(idxSetting)
                        self.ui.lwExerSetVal.blockSignals(False)
                    else:
                        self.dPrint('The selection could not be set because the setting ' +
                                    self.curExercise['settings']['settingsName'] + ' is not displayed.', 2)
        except:
            self.dPrint('Exception: updateInfoFields(): Could not update info fields', 1)
        self.dPrint('Leaving updateInfoFields()', 2)


    def changePalette(self, guiHandle, qPalette):
        """!
        This function changes the color palette of the provided guiHandle.
        qPalette has to be provided as defined by QtGui.QPalette
        """
        self.dPrint(self.curExercise['settings']['exerciseName'] + ': changePalette()', 2)
        guiHandle.setPalette(qPalette)
        guiHandle.show()

        self.dPrint(self.curExercise['settings']['exerciseName'] + ': Leaving changePalette()', 2)


    def callUserDataGui(self):
        """!
        This function calls the gui for the input of the user data.
        """
        self.dPrint('callUserDataGui()', 2)

        tempDifficulty = self.user['difficulty']
        form = UserDataDialogCall(self)
        form.exec_()

        if tempDifficulty != self.user['difficulty']:
            self.updateFilter(self.user['difficulty'])
            self.updateExerciseListBox()
            self.updateExerciseSettingsListBox()
            self.updateSetlistListBox()
        self.dPrint('Leaving callUserDataGui()', 2)


    def openSourceCodeDocu(self):
        """!
        This function opens the source code documentation.
        It is callable from the expertMode menu.
        """
        self.dPrint('openSourceCodeDocu()', 2)

        filename = os.path.join(self.frameWork['path']['pwd'],
                                'html', 'index.html')
        if not(os.path.isfile(filename)):
            msgDoxyStart = _translate("MainWindow", 'Please wait the source code documentation will be generated.', None)
            windowHandle = self.showInformationDialog(msgDoxyStart)
            subprocess.call('doxygen')
            try:
                windowHandle.close()
                msg = 'End of doxygen documentation. closing User dialog.'
            except:
                msg = 'End of doxygen documentation.'
            self.dPrint(msg, 2)
        try:
            webbrowser.open_new(filename)
        except:
            msg = _translate("MainWindow", 'Exception: Could not open the source code documentation', None)
            self.dPrint(msg, 0, guiMode=True)
        self.dPrint('Leaving openSourceCodeDocu()', 2)


    def closeEvent(self, event):
        """!
        This function overrides the closeEventFunction of Qwidgets which is called if self.close() is called
        or if the X of the frame is pressed.
        It allows to prevent the closing of the frame if a run is still active
        """
        self.dPrint('closeEvent()', 2)

        # check if a run has to be finished first
        if self.frameWork['temp']['activeRun']:
            msg = _translate("MainWindow", 'You have to finish, close, or cancel your active run before you can finish CICoachLab', None)
            self.dPrint(msg, 0, guiMode=True)

            event.ignore()
        else:
            event.accept()  # let the window close
        self.dPrint('Leaving closeEvent()', 2)


    def callDynmicFunctionsGenerator(self, event=None, funcName=''):
        """!
        This function calls the function which has been chosen in the exercise menu. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        """
        self.dPrint('callDynmicFunctionsGenerator()', 2)

        if funcName == '':
            # selected from menu bar
            funcName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            funcName = re.sub('&', '', funcName)

        dynamicScriptPath = self.getModulesDynamicSciptPath('curGenerator')

        self.callDynmicFunctionsBase(event=None, funcName=funcName, dynamicScriptPath=dynamicScriptPath)

        self.dPrint('Leaving callDynmicFunctionsGenerator()', 2)


    def callDynmicFunctionsPreprocessor(self, event=None, funcName=''):
        """!
        This function calls the function which has been chosen in the exercise menu. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        """
        self.dPrint('callDynmicFunctionsPreprocessor()', 2)

        if funcName == '':
            # selected from menu bar
            funcName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            funcName = re.sub('&', '', funcName)

        dynamicScriptPath = self.getModulesDynamicSciptPath('curPreprocessor')

        self.callDynmicFunctionsBase(event=None, funcName=funcName, dynamicScriptPath=dynamicScriptPath)

        self.dPrint('Leaving callDynmicFunctionsPreprocessor()', 2)


    def callDynmicFunctionsPlayer(self, event=None, funcName=''):
        """!
        This function calls the function which has been chosen in the exercise menu. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        """
        self.dPrint('callDynmicFunctionsPlayer()', 2)

        if funcName == '':
            # selected from menu bar
            funcName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            funcName = re.sub('&', '', funcName)

        dynamicScriptPath = self.getModulesDynamicSciptPath('curPlayer')

        self.callDynmicFunctionsBase(event=None, funcName=funcName, dynamicScriptPath=dynamicScriptPath)

        self.dPrint('Leaving callDynmicFunctionsPlayer()', 2)


    def callDynmicFunctionsExercise(self, event=None, funcName=''):
        """!
        This function calls the function which has been chosen in the exercise menu. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        """
        self.dPrint('callDynmicFunctionsExercise()', 2)

        if funcName == '':
            # selected from menu bar
            funcName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            funcName = re.sub('&', '', funcName)

        dynamicScriptPath = self.getModulesDynamicSciptPath('curExercise')

        self.callDynmicFunctionsBase(event=None, funcName=funcName, dynamicScriptPath=dynamicScriptPath)

        self.dPrint('Leaving callDynmicFunctionsExercise()', 2)


    def getModulesDynamicSciptPath(self, module):
        """!
        This function returns a list of the available path name, which can contain dynamic scripts.
        Possible paths relative to the modules are:
        analysis
        scripts

        modules can be:
        curGenerator
        curPreprocessor
        curPlayer
        curExercise
        """
        self.dPrint('getModulesPath()', 2)
        dynamicPath = []

        for pathItem in ['analysis','scripts']:
            if pathItem in getattr(self, module)['path']:
                dynamicScriptPath = getattr(self, module)['path'][pathItem]
                dynamicPath.append(dynamicScriptPath)

        self.dPrint('Leaving getModulesPath()', 2)
        return dynamicPath


    def callDynmicFunctionsMasterlist(self, event=None, funcName=''):
        """!
        This function calls the function which has been chosen in the exercise menu. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        """
        self.dPrint('callDynmicFunctionsMasterlist()', 2)

        if funcName == '':
            # selected from menu bar
            funcName = self.sender().text()
            # qt- adds '&' to some menu entries which handles the calling of menu entries via  shortcuts
            funcName = re.sub('&', '', funcName)

        dynamicScriptPath = self.curMasterlist['path']['analysis']

        self.callDynmicFunctionsBase(event=None, funcName=funcName, dynamicScriptPath=dynamicScriptPath)

        self.dPrint('Leaving callDynmicFunctionsMasterlist()', 2)


    def callDynmicFunctionsBase(self, event=None, funcName='', dynamicScriptPath=''):
        """!
        This function calls the  dynamic function. The function is defined by the name
        of the menu which is the name of the python script without the py-extension.
        dynamicScriptPath defines the path or the optional paths for the called funcName.
        If several paths are defined the first path which contains the script is used.

        """
        self.dPrint('callDynmicFunctions()', 2)

        if isinstance(dynamicScriptPath, str):
            dynamicScriptPath = [dynamicScriptPath]

        try:
            for pathItem in dynamicScriptPath:
                analysisFullPath = os.path.join(pathItem, funcName + '.py')
                if os.path.isfile(analysisFullPath):
                    spec = importlib.util.spec_from_file_location(funcName + '.py', analysisFullPath)
                    func = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(func)
                    # calling the function analyse

                    allFunctions = getmembers(func, isfunction)
                    # assumption, just a single function is defined in the loaded function
                    getattr(func, allFunctions[0][0])(self)
                    # if script has been found, the next path item won't be checked. The first hit counts >
                    # breaking out of for loop
                    break
        except:
            msg = _translate("MainWindow", 'Could not call the Dynamic Function ', None) + funcName + '.'
            self.dPrint(msg, 0, guiMode=True)

        self.dPrint('Leaving callDynmicFunctions()', 2)


    def setSettingLimitsTemplate(self):
        """!
        This function returns a a template of settingLimits.
        The settingLimits are used to check the variables in the settingsDialogCall.py.
        SettingLimits can be used in exercises as well in exercises to chech the input of the user or the output of
        algorithms whch reacts to the input of the user (e.g. The calculation of SNR in the OLSA algorithm or the
        calculation of th stepsize in alternative forced choice (AFC) algorithms).

        settingLimitsTemplate = dict()
        #type: float, int, string, bool or a list of types.
        #In this case a list of ranges has to be defined
        settingLimitsTemplate['type'] = ''
        # listStyle:
        # defines if a list of types is expected, this is implemented for
        # string, ints, floats, bools
        settingLimitsTemplate['listStyle'] = False
        # comboBoxStyle: defines if a binary range should be interpreted as range or as choice of values
        # True, False
        # if a range with more than two values is provided, it should be obvious that instead of a minimum and
        # maximum, the selectable values are provided. But in case of two entries comboBoxStyle helps
        # SettingsDialogCall to distinguish between normal entries and combobox entries.
        # settingLimitsTemplate['comboBoxStyle'] = True allows only the value provided in range.
        settingLimitsTemplate['comboBoxStyle'] = False
        # mandatory [or optional input]: True, False
        settingLimitsTemplate['mandatory'] = True
        # range: two values defining inklusive minimum and maximum, or list of possible value, list item type
        # depends on type
        settingLimitsTemplate['range'] = []
        # editable [by user?]: True or False
        settingLimitsTemplate['editable'] = False
        # unit: some string for the labeling
        settingLimitsTemplate['unit'] = ''
        # label: some string defining the unit
        settingLimitsTemplate['label'] = ''
        # default:
        settingLimitsTemplate['default'] = None
        # comment: some longer informative string
        settingLimitsTemplate['comment'] = ''


        """
        # deactivated since function is called before reading verbosityThreshold definition from iniFile
        #self.dPrint('setSettingLimitsTemplate()', 4)

        settingLimitsTemplate = dict()
        """ type: float, int, string, bool or a list of types.
        If a list of types is provided the range, the comboBOxStyle and the listStyle have to be defined 
        as lists as well"""
        settingLimitsTemplate['type'] = ''
        # listStyle:
        # defines if a list of types is expected, this is implemented for
        # string, ints, floats, bools
        settingLimitsTemplate['listStyle'] = False
        # comboBoxStyle: defines if a binary range should be interpreted as range or as choice of values
        # True, False
        # if a range with more than two values is provided, it should be obvious that instead of a minimum and
        # maximum, the selectable values are provided. But in this case comboBoxStyle help SettingsDialogCall to
        # distinguish between normal entries and combobox entries.
        settingLimitsTemplate['comboBoxStyle'] = False
        # mandatory [or optional input]: True, False
        settingLimitsTemplate['mandatory'] = True
        # range: two values defining inklusive minimum and maximum, or list of possible value, list item type
        # depends on type
        settingLimitsTemplate['range'] = []
        # editable [by user?]: True or False
        settingLimitsTemplate['editable'] = False
        # displayed [to user?]: True or False
        settingLimitsTemplate['displayed'] = True
        # unit: some string for the labeling
        settingLimitsTemplate['unit'] = ''
        # label: some string defining the unit
        settingLimitsTemplate['label'] = ''
        # default:
        settingLimitsTemplate['default'] = None
        # comment: some longer informative string
        settingLimitsTemplate['comment'] = ''
        # 'function' may contain function handles, which can be called by clickking on the settings gui.
        # If a function is defined it will be provided as handle. Just for saving the data the handle will be
        # reset to the string containing the function name, because function handles (like file handles)
        # cannot be saved by "pickled" for saving.
        settingLimitsTemplate['function'] = ''
        settingLimitsTemplate['toolTip'] = ''
        #self.dPrint('Leaving setSettingLimitsTemplate()', 4)

        return settingLimitsTemplate


    def checkParameters(self, mode, parameters):
        """!
        This function runs the basic entry checks of the parameters of modules. The function can be run to check the
        parameters of a statis setting or the dynimic parameters used for a single presentation within a run of an
        exercise.

        This functions returns the status True if all settingItem entries passed the test successfully
        If no settingLimits are defined for this setting item or this module the check returns True as well.

        More information about the check is returned with the status.
        For a template of settingLimits see self.setSettingLimits().

        input:
            mode defines the checked module:
                'exercise'
                'generator'
                'preprocessor'
                'player'

        output:
            status      True if all checks passed succesfully
            report      Detailed information about the ckecks which contain:
                        typeOfError:
                        items:      name parameter items
                        checked:    True if found in settingLimits, otherwise False
                        typeOfError: None if check of item passed succesfully, otherwise the errors can be
                                     'type', 'underrun', 'exceed' and 'undefined'.
                                     type: The expected type was not found.
                                     underrun: The value falls below the minimum of the range
                                     exceed: The value exceeds the maximum of the range.
        """

        self.dPrint('checkParameters()', 4)

        Mode = mode[0].upper() + mode[1:]

        checkpassed = True
        report = dict()
        report['typeOfError'] = []
        report['items'] = []
        report['checked'] = []

        if 'settingLimits' in getattr(self, 'cur' + Mode):
            settingLimits = getattr(self, 'cur' + Mode)['settingLimits']
        else:
            self.dPrint('checkParameters(): no check possible because "settingLimits" not defined  ', 4)
            return True, report

        for item in list(parameters):
            report['items'].append(item)
            if item in settingLimits:
                entry = parameters[item]
                if isinstance(settingLimits[item]['type'], list):
                    print('Some special handling')
                else:
                    value = 0
                    if settingLimits[item]['type'] == 'int':
                        # checking type
                        try:
                            test = int(entry)
                            report['typeOfError'].append(None)
                        except ValueError:
                            report['items'].append(item)
                            checkpassed = False
                            report['typeOfError'].append('type')
                            msg = f"Exception: Wrong input type. '{settingLimits['type']:s}' expected. '" \
                                  f" Conversion not possible."

                    elif settingLimits[item]['type'] == 'float':
                        # checking type
                        try:
                            value = float(entry)
                            report['typeOfError'].append(None)
                        except ValueError:
                            msg = f"Exception: Wrong input type. '{settingLimits['type']:s}' expected. '" \
                                  f"Conversion not possible."
                            report['typeOfError'].append('type')
                            checkpassed = False
                    elif settingLimits[item]['type'] == 'bool':
                        # checking type
                        if not('True' in entry or 'False' in entry):
                            msg = f"Exception: Wrong input. '{settingLimits['type']:s}' expected. '" \
                                  f"But did not find True or False in " + entry + ". Conversion not possible."
                            checkpassed = False
                            report['typeOfError'].append('type')
                        else:
                           report['typeOfError'].append(None)

                    if settingLimits[item]['type'] in ['float', 'int']:
                        # checking range
                        value = 1
                        if len(settingLimits[item]['range']) > 2 or \
                                (len(settingLimits[item]['range']) == 2 and settingLimits[item]['comboBoxStyle']):
                            if not(value in settingLimits[item]['range']):
                                checkpassed = False
                                report['typeOfError'].append('undefined')
                                msg = f"value out of range: Found {float(value):02.6f} and expected range within " + \
                                      str(settingLimits['range'])
                            else:
                                report['typeOfError'].append(None)
                        elif len(settingLimits[item]['range']) == 2 and \
                                not(settingLimits[item]['comboBoxStyle']):
                            if settingLimits[item]['range'][0] > value:
                                checkpassed = False
                                report['typeOfError'].append('underrun')
                                msg = f"value underun range: Found {float(value):02.6f} and expected range within " + \
                                    f"{settingLimits['range'][0]:02.6f} to {float(settingLimits['range'][1]):02.6f}"

                            elif settingLimits[item]['range'][1] < value:
                                msg = f"value exceeded range: Found {float(value):02.6f} and expected range within " + \
                                      f"{settingLimits['range'][0]:02.6f} to {float(settingLimits['range'][1]):02.6f}"

                                checkpassed = False
                                report['typeOfError'].append('exceeded')
                            else:
                                report['typeOfError'].append(None)
                        elif len(settingLimits[item]['range']) == 0:
                            report['typeOfError'].append(None)

                report['checked'].append(True)
            else:
                report['typeOfError'].append(None)
                report['checked'].append(False)

            self.dPrint(msg, 4)


        self.dPrint('Leaving checkParameters()', 4)

        return checkpassed, report
 

    def checkBitlockerMemory(self):
        """!
        This function just unlocks and relocks the bitlocked device and determines the time needed for the process.
        The required time will be written to the log file.
        """

        self.dPrint('checkBitlockerMemory()', 2)
        if self.frameWork['settings']['system']['sysname'] == 'Linux':
            status = False
            if not(os.path.isdir(self.frameWork['settings']['bitlockerPathClear'])):
                msg = _translate("MainWindow",
                     'Could not find bitlocker path: {}. \nPlease contact your administrator. Check CICoachLab.ini'.format(
                     self.frameWork['settings']['bitlockerPathClear']), None)
                self.dPrint(msg, 0, guiMode=True)
                return status

            status = False
            if not(os.path.isdir(self.frameWork['settings']['bitlockerPathEncrypt'])):
                msg = _translate("MainWindow",
                     'Could not find bitlocker path: {}. \nPlease contact your administrator. Check CICoachLab.ini'.format(
                     self.frameWork['settings']['bitlockerPathClear']), None)
                self.dPrint(msg, 0, guiMode=True)
                return status


        startTime = time()
        statusUnlock = self.unlockBitlocker()
        statusLock = False
        if statusUnlock:
            statusLock = self.lockBitlocker()
            endTime = time()
            if statusLock:
                msg = 'Time required to to succesfully lock and unlock device: {:.2f} s'.format(endTime - startTime)
            else:
                msg = 'Could not lock and unlock bitlocker device:'
        else:
            msg = 'Could not lock bitlocker device:'

        self.dPrint(msg, 0)

        status = statusLock and statusUnlock
        self.dPrint('Leaving checkBitlockerMemory()', 2)
        return status



    def unlockBitlocker(self):
        """!
        This function unlocks the defined bitlocked device.
        """
        import bitlocker
        #self.dPrint('unlockBitlocker()', 2)

        systemName = self.frameWork['settings']['system']['sysname']  # Linux/Windows
        # path to the encrypted memory stick or directory
        device = self.frameWork['settings']['bitlockerDevice']
        # for linux use required only: mounting points of clear (decrypted) and encrypted data
        bitlockerPathClear = self.frameWork['settings']['bitlockerPathClear']
        bitlockerPathEncrypt = self.frameWork['settings']['bitlockerPathEncrypt']

        status = bitlocker.unlockBitlocker(systemName, device, bitlockerPathClear, bitlockerPathEncrypt)

        return status


    def lockBitlocker(self):
        """!
        This function locks the defined bitlocked device.
        """

        #self.dPrint('lockBitlocker()', 2)

        systemName = self.frameWork['settings']['system']['sysname']  # Linux/Windows
        # path to the encrypted memory stick or directory
        device = self.frameWork['settings']['bitlockerDevice']
        # for linux use required only: mounting points of clear (decrypted) and encrypted data
        bitlockerPathClear = self.frameWork['settings']['bitlockerPathClear']
        bitlockerPathEncrypt = self.frameWork['settings']['bitlockerPathEncrypt']

        status = bitlocker.lockBitlocker(systemName, device, bitlockerPathClear, bitlockerPathEncrypt)

        self.dPrint('Leaving lockBitlocker()', 2)
        return status

        #self.dPrint('Leaving lockBitlocker()', 2)



    def moveLogFile(self, source, destination, backupDestination=False, logMode=True):
        """!
        This function moves the file from 'source' to 'destination'.
        For more information see self.moveCopyFile().
        """

        return self.moveCopyFile(source, destination, mode='move', backupDestination=backupDestination, logMode=logMode)


    def copyLogFile(self, source, destination, backupDestination=False, logMode=True):
        """!
        This function moves the file from 'source' to 'destination'.
        For more information see self.moveCopyFile().
        """

        return self.moveCopyFile(source, destination, mode='copy', backupDestination=backupDestination, logMode=logMode)


    def moveCopyFile(self, source, destination, mode, backupDestination, logMode):
        """!
        This function moves or copies the file from 'source' to 'destination'.

        Mode destinguishes between move and copy.
        If 'backupDestination' is True an existing file destination will be backuped to a file where the extension of
        the file will be replaced by the extension and a leading time stamp.

        If 'logMode' is True messages are logged wtih self.dPrint() or print otherwise.

        If the bitlocker mode is activated and the bitlocked  directory is part of the source or destination
        the bitlocker path will be unlocked.
        This function return the status of the operation and the destinationbackupfile

        status:
            0: everything went fine
            5: something went wrong at unlocking the bitlocker, if the bitlocker mode is required.
        """

        destinationbackupfile = ''

        if logMode:
            self.dPrint('moveCopyFile()', 2)

        usingBitlocker = self.requiresBitlocker(source) or self.requiresBitlocker(destination)

        if usingBitlocker:
            status = self.unlockBitlocker()
        if not(status):
            msg = _translate("MainWindow", 'Could not ' + mode + ' ' + source + ' to ' + destination, None)
            if logMode:
                # not using dPrint since log file might not have been moved allready
                print(msg)
            else:
                self.dPrint(msg, 0, guiMode=True)
            return 5, destinationbackupfile

        if backupDestination and os.path.isfile(destination):
            ext = os.path.splitext(destination)[1]
            destinationbackupfile = self.backupFile(destination, ext)

        if os.path.isfile(source):
            if mode == 'move':
                shutil.move(source, destination)
            elif mode == 'copy':
                shutil.copy(source, destination)

        msg = _translate("MainWindow", 'Successfully we could  ' + mode + ' ' + source + ' to ' + destination, None)
        if logMode:
            self.dPrint(msg, 0)
        else:
            print(msg)

        if usingBitlocker:
            status = self.lockBitlocker()

        if logMode:
            self.dPrint('Leaving moveCopyLogFile()', 2)
        return 0, destinationbackupfile


    def requiresBitlocker(self, filename):
        """!
        This function checks if self.frameWork['settings']['bitlockerPathClear']
        is part of filename and if the bitlocked partition has to be locked and unlocked after accessing the filenam.
        The function return True or False.
        """

        if self.frameWork['settings']['bitlockerMode']:
            systemName = self.frameWork['settings']['system']['sysname']
            if systemName == 'Linux':
                bitlockerPathClear = self.frameWork['settings']['bitlockerPathClear']
                if bitlockerPathClear in filename:
                    status = True
                else:
                    status = False
            elif systemName == 'Windows':
                bitlockerDevice  = self.frameWork['settings']['bitlockerDevice']
                if bitlockerDevice in filename:
                    status = True
                else:
                    status = False

        else:
            status = False

        return status

    def defineDependencies(self):
        """!
        This function defines the imported pyhon packages/modules used in CICoachLab or in import submodules.
        """

        self.dPrint('defineDependencies()', 2)

        dependencies = dict()
        dependencies['Windows'] = dict()
        dependencies['Linux'] = dict()
        dependencies['Windows']['pip'] = dict()
        dependencies['Windows']['pip']['packages'] = \
            ['configobj', 'soundfile', 'audio2numpy', 'sounddevice', 'pycaw']
        dependencies['Windows']['pip']['requiredBy'] = \
            ['CICoachLab', 'genWavReader', 'genWavReader', 'playAudio', 'CICoachLab']
        dependencies['Linux']['other'] = dict()
        dependencies['Linux']['other']['packages'] = ['ffmpeg']
        dependencies['Linux']['other']['requiredBy'] = ['genWavReader']
        dependencies['Linux']['distro'] = dict()
        dependencies['Linux']['distro']['packages'] = ['PyQt5',
                                                       'datetime', 'inspect', 'bz2', 'copy', 'functools', 'importlib',
                                                       'io', 'matplotlib',
                                                       'multiprocessing', 'numpy', 'os', 'pandas', 'pickle', 'platform',
                                                       'psutil', 'py_compile', 're', 'scipy',
                                                       'shutil',
                                                       'sounddevice', 'subprocess', 'sys', 'time', 'traceback',
                                                       'webbrowser', 'windows_tools.bitlocker',
                                                       'pkg_resources']
        dependencies['Linux']['distro']['requiredBy'] = ['CICoachLab',
                                                         'CICoachLab', 'CICoachLab', 'CICoachLab', 'CICoachLab',
                                                         'soundcheck', 'CICoachLab', 'playQtAudio',
                                                         'ConfusionMatrix', 'CICoachLab', 'quiz', 'confusionMatrix',
                                                         'CICoachLab', 'ConfusionMatrix',
                                                         'CICoachLab', 'CICoachLab', 'CICoachLab', 'CICoachLab',
                                                         'CICoachLab', 'genHarmXdBPerOct',
                                                         'CICoachLab', 'genHarmXdBPerOct', 'CICoachLab', 'CICoachLab',
                                                         'CICoachLab', 'CICoachLab',
                                                         'CICoachLab', 'CICoachLab', 'CICoachLab']
        dependencies['Linux']['pip'] = dict()
        dependencies['Linux']['pip']['packages'] = ['soundfile', 'audio2numpy', 'sounddevice']
        dependencies['Linux']['pip']['requiredBy'] = ['genWavReader', 'genWavReader', 'playAudio']

        self.dependencies = dependencies

        self.dPrint('Leaving defineDependencies()', 2)


    def installMissingPackages(self):
        """!
        This function checks if all required and recomended dependencies are installed. If not the user is asked if the
        missing dependencies should be installed. the recommended and required dependencies are defined in
        self.defineDependencies()

        Remove in future version to replace it by pidenv?
        """

        self.dPrint('installMissingPackages()', 2)

        systemName = self.frameWork['settings']['system']['sysname']  # Linux/Windows

        # checking pip installations
        ii = 0
        for pipItem in self.dependencies[systemName]['pip']['packages']:
            pipItemCheckFail = list()
            # checking for dependencies
            if importlib.util.find_spec(pipItem):
                msg = 'Check Pip-installation passed: ' + pipItem + ' required by: ' + \
                      str(self.dependencies[systemName]['pip']['requiredBy'][ii])
                self.dPsmartrint(msg, 0)
            else:
                pipItemCheckFail.append(pipItem)

            ii = ii + 1
        # any dependency missing?
        if pipItemCheckFail:
            # asking for installation
            title = _translate("MainWindow", 'Installing missing dependencies.', None)
            question = _translate("MainWindow",
                                  'Some dependencies are missing. Do you want to install the following packages?: ',
                                  None) + str(pipItemCheckFail)
            quest = CICoachDialog(self, title, question)
            answer = quest.returnButton()
            if answer == QtWidgets.QMessageBox.Yes:
                for package in pipItemCheckFail:
                    msg = 'pip install ' + package
                    self.dPrint(msg, 3)
                    subprocess.check_call("pip" + " install " + package, shell=True)

        self.dPrint('Leaving installMissingPackages()', 2)



    def documentPackageVersions(self):
        """!
        This functions documents the version of the imported modules of CICoachLab, as they are installed and defined in
        self.defineDependencies(). The versions are printed to the console and 'CICoachLabRequirements.txt'.
        """

        self.dPrint('documentPackageVersions()', 2)

        packages = self.dependencies['Linux']['pip']['packages'] + self.dependencies['Linux']['other']['packages'] + \
                   self.dependencies['Linux']['distro']['packages']
        requiredBy = self.dependencies['Linux']['pip']['requiredBy'] + self.dependencies['Linux']['other'][
            'requiredBy'] + \
                     self.dependencies['Linux']['distro']['requiredBy']

        versions = []
        for item in packages:
            vers = 'NaN'
            # trying to get version of packages imported in CICoachLab or in submodules / missing in CICoachLab.
            try:
                vers = importlib.metadata.version(item)
            except:
                try:
                    obj = eval(item)
                except:
                    obj = importlib.import_module('numpy')
                if hasattr(obj, 'version'):
                    if isinstance(obj.version, str):
                        vers = obj.version
                    elif ismodule(obj.version):
                        vers = obj.version.full_version
                    elif isfunction(obj.version):
                        vers = obj.version()
                elif hasattr(obj, '__version__'):
                    vers = obj.__version__
                else:
                    failed = False
                    try:
                        vers = importlib.metadata.version(item)
                    except:
                        failed = True
                    try:
                        vers = pkg_resources.get_distribution(item).version
                    except:
                        failed = True
                    if not (failed):
                        print("Could not find version")
                        vers = re.sub('\n', '', sys.version)
            versions.append(vers)


        ii = 0
        txt = 'Package, version: required by module\n\npython: ' + re.sub('\n', '', sys.version) + ': CICoachLab\n\n'
        for item in packages:
            txt = txt + item + ', ' + versions[ii] + ': ' + requiredBy[ii] + '\n'
            ii = ii + 1

        print('Installed packages:')
        print(txt)
        systemName = self.frameWork['settings']['system']['sysname']  # Linux/Windows
        f = open(os.path.join(self.frameWork['path']['lib'], systemName, 'CICoachLabRequirements.txt'), 'w')
        f.write(txt)
        f.close()

        self.dPrint('Leaving documentPackageVersions()', 2)


    def downloadDependencies(self):
        """!
        The required packages of the python will be downlaoded to the path.
        """

        self.dPrint('downloadDependencies()', 2)
        systemName = self.frameWork['settings']['system']['sysname']  # Linux/Windows

        downloadPath = os.path.join(self.frameWork['path']['pwd'], 'lib', 'archive', systemName)
        packages = self.dependencies['Linux']['pip']['packages'] + self.dependencies['Linux']['distro']['packages']
        for package in packages:
            try:
                subprocess.check_call("pip" + " download --destination-directory " + downloadPath + " " + package,
                                      shell=True)
            except:
                msg = _translate("MainWindow", "Could not download package '" + package + "' ", None)
                self.dPrint(msg, 0, guiMode=True)

        self.dPrint('Leaving downloadDependencies()', 2)


    
    def gettingPythonImports(self):
        """!
        This function scans the for all py-files in self.frameWork['path']['pwd'], ignoring the path defined in
        'ignoreDir'. The function counts the number of lines found and prints out the line
        containing 'import ' and 'pip install' to the console. The search for 'pip install' assumes that the
        installation with pip is documented somewhere in the source code.
        """

        self.dPrint('gettingPythonImports()', 2)
        basePath = os.path.join(self.frameWork['path']['pwd'], '') #self.frameWork['path']['pwd']
        output = subprocess.check_output(
            """find """ + basePath + """ -name '*.py'""", shell=True).decode("utf-8")

        output = output.split()
        # ciTrainer was renamed to CICoachLab
        ignoreDir = ['__pycache__', '.git', '.idea', 'venvp', 'tools', 'ciTrainer', 'archive']

        num_lines = []
        filtered = []
        for file in output:
            file = re.sub(basePath, '', file)
            state = True
            for check in ignoreDir:
                if check in file:
                    state = False
            if state:
                filtered.append(file)
                num_lines.append(sum(1 for line in open(os.path.join(basePath, file))))
        noLines = np.sum(num_lines)
        textNumOfLine = 'Number of lines found in CICoachLab py-scripts: ' + str(noLines)
        print(textNumOfLine)

        # %%
        extractImport = []
        pipImport = []
        externalImports = []
        for file in filtered:
            fullFile = os.path.join(basePath, file)
            lineCounter = 0
            for line in open(fullFile):
                lineCounter = lineCounter + 1
                lineOrig = line

                if 'import ' in line:
                    print(fullFile + ': ' + line)
                    if line.index('import ') == 0 or ('from ' in line and line.index('from ') == 0):
                        if 'from' in line:
                            line = re.split('from|import', line)[1]
                        line = re.sub('import ','', line)
                        line = re.sub('\n','', line)
                        line = re.split('as', line)[0]
                        line = line.replace(' ','')
                        if ',' in line:
                            line = line.split(',')
                        if isinstance(line,str):
                            extractImport.append(line)
                        elif isinstance(line,list):
                            [extractImport.append(i) for i in line]
                line = lineOrig
                if 'pip install ' in line:
                    if not('XYZ' in line):
                        if line.find('pip install ') == 0:
                            line = line[line.find('pip install ') + len('pip install '):]
                            line = line.split()
                            if isinstance(line, str):
                                pipImport.append(line)
                            elif isinstance(line, list):
                                [pipImport.append(i) for i in line]
                        else:
                            # pip install XYZ # some comments
                            line = line[line.find('pip install ') + len('pip install '):].split()[0].replace(')','')
                            if len(line) > 1:
                                pipImport.append(line)
                line = lineOrig
                if 'dependencies:' in line:
                    line = line[line.find('dependencies:') + len('dependencies:'):].split()[0].replace(')','').replace('\\n\\n','')
                    if len(line)>1:
                        externalImports.append(line)


        extractImportText = '\n\nPython imports: \n\n' + '\n'.join(str(item) for item in set(extractImport))
        pipImportText = '\n\nPip install imports: \n\n' + '\n'.join(str(item) for item in set(pipImport))
        externalImportsText = '\n\nExternal dependencies: \n\n' + '\n'.join(str(item) for item in set(externalImports))
        print(extractImportText)
        print(pipImportText)
        print(externalImportsText)

        try:
            textNumOfLine = _translate("MainWindow", f"Python and Pip-install-Imports and dependencies were found in {noLines:d} lines: ", None)
            text = _translate("MainWindow",
                                       f"Dependencies have been found.\n Details are provided in 'Show Details' and dependencies.txt", None)
            title = _translate("MainWindow", "Python and Pip-install-Imports and dependencies", None)
            detailedText=textNumOfLine + '\n' + extractImportText + pipImportText + externalImportsText
            CICoachDialog(self, title, text, 'information', detailedText=detailedText)

            filename = os.path.join(self.frameWork['path']['pwd'], 'dependencies.txt')
            with open(filename,'w') as f:
                f.write(detailedText)
        except:
            self.dPrint("Could not print out results of python imports and pip-installation.", 0)



        self.dPrint('Leaving gettingPythonImports()', 2)




    def openSettingsDialog(self):
        """!
        The settings dialog will be opened.
        After the settings might have changed the exercise and its settings box and the infoFields are updated.
        """

        self.dPrint('openSettingsDialog()', 2)

        temp = SettingsDialogCall(self)
        temp.exec_()

        # the display will be updated in self.iniExercise() which is called in SettingsDialogCall()
        #self.updateExerciseListBox()
        #self.updateExerciseSettingsListBox()
        #self.updateInfoFields()

        self.writeFilter()
        self.updateInfoFields()
        self.dPrint('Leaving openSettingsDialog()', 2)


    def setLocalization(self, localization):
        """!
        The localization is set to the for CICoachLab and its exercises.

        The permanent settings of the localization
        """

        self.dPrint('Leaving setLocalization()', 2)

        # providing the translation of CICoachLab
        translationPath = self.frameWork['path']['locales']
        translator = QtCore.QTranslator(self.app)
        translator.load(localization, translationPath)
        self.app.installTranslator(translator)

        # providing the translation of all exercises (defined by .py files in exercise foldert)
        #   which provide a 'locales'-directory
        exercisePath  = self.frameWork['path']['exercises']

        exercises = self.frameWork['settings']['access']['exercises']['main']['available']['names']

        for exercise in exercises:
            exercise = re.sub('.py', '', exercise)
            exerciseLocales = os.path.join(exercisePath, exercise, 'locales')
            if os.path.isdir(exerciseLocales):
                # loading localization
                translator = QtCore.QTranslator(self.app)
                translator.load(localization, os.path.join(exercisePath, exercise, 'locales'))
                self.app.installTranslator(translator)

        self.dPrint('Leaving setLocalization()', 2)

    def translateExercise(self):
        """!
        This function guides through the translation process of the currently selected exercise.
        """

        self.dPrint('translateExercise()', 2)

        curExercise = self.curExercise['settings']['exerciseName']
        self.translateBase(exercise=curExercise)

        self.dPrint('Leaving translateExercise()', 2)


    def translateAllExercises(self):
        """!
        This function guides through the translation process of the currently available exercise and the
        generators, preprocessors, player.
        """

        self.dPrint('translateExercise()', 2)

        localization = self.frameWork['settings']['localization']
        for exercise in self.frameWork['settings']['access']['exercises']['main']['available']['names']:
            self.translateBase(modulesPath=self.frameWork['path']['exercises'],
                               module=exercise, localization=localization)

        for generator in self.frameWork['settings']['access']['generators']['main']['available']['names']:
            self.translateBase(modulesPath=self.frameWork['path']['generators'],
                               module=generator, localization=localization)

        for preprocessor in self.frameWork['settings']['access']['preprocessors']['main']['available']['names']:
            self.translateBase(modulesPath=self.frameWork['path']['preprocessors'],
                               module=preprocessor, localization=localization)

        for player in self.frameWork['settings']['access']['player']['main']['available']['names']:
            self.translateBase(modulesPath=self.frameWork['path']['player'],
                               module=player, localization=localization)

        cmd = '/usr/bin/pylupdate5 ' + \
                os.path.join(self.frameWork['path']['pwd'], '') + 'CICoachLab.py ' +\
                os.path.join(self.frameWork['path']['pwd'], '') + 'CICoachLabMainWindowGui2.py ' +\
                os.path.join(self.frameWork['path']['pwd'], '') + 'UserDataDialog.py ' + \
                os.path.join(self.frameWork['path']['pwd'], '') + 'SettingsDialogCall.py ' + \
                os.path.join(self.frameWork['path']['pwd'], '') + 'SettingsDialog.py ' + \
               '-ts locales/' + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        cmd = 'linguist ' + os.path.join(self.frameWork['path']['pwd'], 'locales', '') + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        cmd = 'lrelease ' + os.path.join(self.frameWork['path']['pwd'], 'locales', '') + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        self.dPrint('Leaving translateExercise()', 2)


    def translateBase(self, modulesPath, module, localization=''):
        """!
        This function guides through the translation process of the provided module.
        The provided localization is used or self.frameWork['settings']['localization'] is used otherwise.

        1) The code is parsed for the translation entries (_translate() ) with pylupdate5
        2) linguist is opened with the generated file for a gui guided translation
        3) The translation file is generated with lrelease and put into the locales directory of CITrainier or the
            respective modules (exercise) or submodule like generator, preprocessor or player. 
        """

        self.dPrint('translateBase()', 2)

        if not(localization):
            localization = self.frameWork['settings']['localization']

        modulesSubDir = os.path.join(modulesPath, module)
        # check if locales directory exists
        if not(os.path.isdir(os.path.join(modulesSubDir, 'locales', ''))):
            msg = _translate("MainWindow", "No locales directory could be found for " + modulesSubDir +".\n\n"
                                           "Translation process will be canceled for this element.", None)
            self.dPrint(msg, 0, guiMode=True)
            return

        subFiles = self.getListOfFiles(modulesSubDir, depthOfDir=3, namePart='.py', nameIgnore='.pyc', fullPath=True)

        if subFiles:
            cmd = '/usr/bin/pylupdate5 ' + os.path.join(modulesPath,
                                                        '') + module + '.py '
            for file in subFiles:
                cmd = cmd +  file + ' '
            cmd = cmd + ' -ts ' + os.path.join(modulesSubDir, 'locales', '') + localization + '.ts'
        else:
            # just processing the module main file
            cmd = '/usr/bin/pylupdate5 ' + os.path.join(modulesPath,
                                                        '') + module + '.py ' + \
                  '  -ts ' + os.path.join(modulesSubDir, 'locales', '') + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        cmd = 'linguist ' + os.path.join(modulesSubDir, 'locales', '') + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        cmd = 'lrelease ' + os.path.join(modulesSubDir, 'locales', '') + localization + '.ts'
        subprocess.Popen(cmd, shell=True).wait()

        self.dPrint('Leaving translateBase()', 2)


    def readMasterlist(self):
        """!
        This function reads the mastlist file which is defined in
        """

        self.dPrint('readMasterlist()', 2)

        if self.curMasterlist['settings']['masterlistFile'] and \
                os.path.isfile(self.curMasterlist['settings']['masterlistFile']):
            try:
                masterlistFileConfig = ConfigObj(self.curMasterlist['settings']['masterlistFile'], encoding="utf8")
            except:
                self.dPrint("Could not open masterListfile: " + self.curMasterlist['settings']['masterlistFile'], 2)
            else:
                self.curMasterlist['settings']['name'] = masterlistFileConfig['name']
                self.curMasterlist['settings']['information'] = masterlistFileConfig['information']
                self.curMasterlist['settings']['lastItemIDX'] = masterlistFileConfig.as_int('lastItemIDX')

                self.curMasterlist['settings']['items'] = masterlistFileConfig['items']
                self.curMasterlist['settings']['settings'] = masterlistFileConfig['settings']
                self.curMasterlist['settings']['runmode'] = masterlistFileConfig['runmode']

                self.curMasterlist['settings']['preconditions'] = masterlistFileConfig['preconditions']
                self.curMasterlist['settings']['preconditionMessages'] = \
                                        masterlistFileConfig['preconditionMessages']
                self.curMasterlist['settings']['postconditions'] = masterlistFileConfig['postconditions']
                self.curMasterlist['settings']['postconditionMessages'] = \
                    masterlistFileConfig['postconditionMessages']
                self.curMasterlist['settings']['description'] = masterlistFileConfig['description']

                self.frameWork['settings']['masterlistFileConfig'] = masterlistFileConfig
        else:
            msg = _translate("MainWindow", "Could not read masterlist: ", None)
            self.dPrint(msg + self.curMasterlist['settings']['masterlistFile'], 2)

        self.dPrint('Leaving readMasterlist()', 2)


    def writeMasterlist(self):
        """!
        This function writes back the masterlist file which is defined in
        """

        self.dPrint('writeMasterlist()', 2)

        if self.curMasterlist['settings']['masterlistFile']:
            masterlistFileConfig = self.frameWork['settings']['masterlistFileConfig']

            masterlistFileConfig['name'] = self.curMasterlist['settings']['name']
            masterlistFileConfig['information'] = self.curMasterlist['settings']['information']
            masterlistFileConfig['lastItemIDX'] = self.curMasterlist['settings']['lastItemIDX']

            masterlistFileConfig['items'] = self.curMasterlist['settings']['items']
            masterlistFileConfig['settings'] = self.curMasterlist['settings']['settings']
            masterlistFileConfig['runmode'] = self.curMasterlist['settings']['runmode']
            masterlistFileConfig['preconditions'] = self.curMasterlist['settings']['preconditions']
            masterlistFileConfig['preconditionMessages'] = \
                self.curMasterlist['settings']['preconditionMessages']
            masterlistFileConfig['postconditions'] = self.curMasterlist['settings']['postconditions']
            masterlistFileConfig['postconditionMessages'] = \
                self.curMasterlist['settings']['postconditionMessages']
            masterlistFileConfig['description'] = self.curMasterlist['settings']['description']

            masterlistFileConfig.filename = self.curMasterlist['settings']['masterlistFile']
            masterlistFileConfig.write_empty_values = True
            masterlistFileConfig.write()
        else:
            pass
        self.dPrint('Leaving writeMasterlist()', 2)


    def checkMasterList(self):
        """!
        This function runs the masterlist
        """

        msgOut = 'Checking masterlist:\n'
        status = True
        self.dPrint('checkMasterList()', 2)

        self.dPrint('masterlist check:', 0)
        for mlCounter in range(len(self.curMasterlist['settings']['items'])):
            # runmode
            setDif = set(self.curMasterlist['settings']['runmode']) - set(['setlist','singleRun'])
            if setDif:
                msg = 'setlist ' + str(setDif) + ' could not be found!'
                msgOut = msgOut + msg + '\n'
                self.dPrint(msg, 0)
                status = False
            # checking items
            name = self.curMasterlist['settings']['items'][mlCounter]
            if self.curMasterlist['settings']['runmode'][mlCounter] == 'setlist':
                if not(name in self.frameWork['settings']['access']['setlists']['main']['available']['names']):
                    msg = 'setlist ('+ name + ') could not be found!'
                    msgOut = msgOut + msg + '\n'
                    self.dPrint(msg, 0)
                    status = False
            elif self.curMasterlist['settings']['runmode'][mlCounter] == 'singleRun':
                if not(name in self.frameWork['settings']['access']['exercises']['main']['available']['names']):
                    msg = 'exercise ('+ name + ') could not be found!'
                    msgOut = msgOut + msg + '\n'
                    self.dPrint(msg, 0)
                    status = False
                # checking settings
                settingsName = self.curMasterlist['settings']['settings'][mlCounter]
                if settingsName != 'None':
                    path = os.path.join(self.frameWork['path']['exercises'], name, 'presets')
                    if not( os.path.isfile(path+os.path.sep+settingsName+'.set')):
                        # did not find a set-preset?: Try py-preset!
                        if not((os.path.isfile(path + os.path.sep + settingsName + '.py') and
                            self.frameWork['settings']['expertSettingsMode'])):
                            #did not find a set-preset and not a py-preset or was not allowed to use it?
                            if self.frameWork['settings']['expertSettingsMode']:
                                appendMsg = ''
                            else:
                                appendMsg = 'py-presets are not allowed according to "expertSettingsMode" in CICoachLab.'
                            msg = 'exercise settings (' + settingsName + ') of exercise (' + name + ')' +\
                                'could not be found!\n' + appendMsg
                            self.dPrint(msg, 0)
                            status = False
        if status:
            msgOut = 'Checking masterlist:\nCheck passed.'

        self.dPrint(msgOut, 3)
        self.dPrint('Leaving checkMasterList()', 2)
        return status, msgOut


    def mathTexToQPixmap(self, mathTex, fontsize):
        """!
        This function is used to add formated text on buttons.

        This code was published at
        https://stackoverflow.com/questions/32035251/displaying-latex-in-pyqt-pyside-qtablewidget
        on 23.05.2017 by 'Jean-Sébastien'

        CC-BY-SA-3.0
        """

        fig = Figure()
        fig.patch.set_facecolor('none')
        fig.set_canvas(FigureCanvasAgg(fig))
        renderer = fig.canvas.get_renderer()

        # ---- plot the mathTex expression ----
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.patch.set_facecolor('none')
        t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize=fontsize)

        # ---- fit figure size to text artist ----
        fwidth, fheight = fig.get_size_inches()
        figBbox = fig.get_window_extent(renderer)

        textBbox = t.get_window_extent(renderer)

        tightFwidth = textBbox.width * fwidth / figBbox.width
        tightFheight = textBbox.height * fheight / figBbox.height

        fig.set_size_inches(tightFwidth, tightFheight)

        # ---- convert mpl figure to QPixmap ----
        buf, size = fig.canvas.print_to_buffer()
        qimage = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, size[0], size[1],
                                                      QtGui.QImage.Format_ARGB32))
        qpixmap = QtGui.QPixmap(qimage)

        return qpixmap


    def reconnect(self, signal, newHandler=None, oldHandler=None):
        """!
        Connect a new function to a signal slot of pushbuttons or other input signal. If a function has been
        connected before this function will be disconnected.

        This code was published at
        https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect
        by 'ekhumoro'  on 17.08.2017

        CC-BY-SA-3.0
        """

        try:
            if oldHandler is not None:
                while True:
                    signal.disconnect(oldHandler)
            else:
                signal.disconnect()
        except TypeError:
            pass
        if newHandler is not None:
            signal.connect(newHandler)


    def getListOfFiles(self, searchPath, depthOfDir=2, namePart=[], nameIgnore=[], fullPath=False):
        """!
        This function returns the list of files that are found in 'search_path' and
        subdirectories of 'search_path'. To find all subdirectories the function
        GetListOfDirectories(searchPath, depthOfDir) is used.

        input  :
            searchPath      string that gives the path of files whose list will
                                be compiled
            depthOfDir      number of subdirectories, 1 means no
                                subdirectories
            namePart         list of strings that shall be part of the filename

        output :
            files      list of matching files in path.
        """

        # import at top of file not possible since the library path is set in self.initializeToDefaults(mode='all')
        # loading module to get list of files with specified conditions
        modulePath = os.path.join(self.frameWork['path']['lib'], 'fhe.py')
        spec = importlib.util.spec_from_file_location('fhe.py', modulePath)
        fhe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fhe)

        files = fhe.getListOfFiles(searchPath, depthOfDir=depthOfDir, namePart=namePart,
                                   nameIgnore=nameIgnore, fullPath=fullPath)

        return files


    def clickable(self, widget):
        """!
        This function can be used to make any widget clickable.

        e.g.: exercises can use "clickable" to define functions for the setting entries which can be called in
        SettingsDialogCall

        functionHandle = settingLimits[dynItem]['function']
        self.parHandle.clickable(self.uiSettingsDyn[mode][dynItem + 'Entry']).connect(functionHandle)
        self.parHandle.clickable(self.uiSettingsDyn[mode][dynItem + 'Entry']).connect(someFunction)

        label = QLabel(self.tr("Hello world!"))
        clickable(label).connect(self.someFunction)


        This code was licensed under Python Software Foundation License at 2014-06-04 22:13:48 by DavidBoddie
        https://wiki.python.org/moin/PyQt/Making%20non-clickable%20widgets%20clickable

        PSF-2.2
        """

        class Filter(QtCore.QObject):

            clicked = QtCore.pyqtSignal()

            def eventFilter(self, obj, event):

                if obj == widget:
                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            # The developer can opt for .emit(obj) to get the object within the slot.
                            return True
                return False

        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked

    def setRetainSizeWhenHidden(self, widgetObj):
        """!
        When you call this function with a widget object, this object can be hidden (.hide()) without changing
        the format/size of the layout. Normally, the size of a hidden layout is zero, which changes the relation
        of the other widegts within the parent layout.
        """

        sp = widgetObj.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        widgetObj.setSizePolicy(sp)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    with CICoachLab(app=app) as ciTraining:
        ciTraining.show()
        # app.exec is sufficient in PyQt5 in PyQt4 sys exit is required.
        sys.exit(app.exec())  # In interactive environments (debugging) sys.exit leads to an error, which is ok.



