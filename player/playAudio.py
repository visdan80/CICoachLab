"""!
Created on Tue Jan 21 22:19:47 2020

@author: Daniel Leander
"""

import importlib.util
import os
from PyQt5 import QtCore, QtGui
import sounddevice as sd

#import numpy as np
def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class playAudio():
    def __init__(self, parHandle=None, settings = 'default'):
        """!
        Initializing the CICoachLab player playAudio. This function provides the funcition to play back audio signals.
        with the signal format:
        signa['audio']
        signal['fs']
        is expected.
        If a preprocessor is defined the preprocessor will be called.
        The module vocoder.py will be used and initialized here and passed in
        self.vocoder to the calculating function run().
        The default settings will be set or the provided settings will be loaded.
        """

        if parHandle == None:
            print('cannot initilize without framework.')
        self.parHandle   = parHandle

        self.setDefaultSettings()
        self.parHandle.addingPath('curPlayer')
        if settings != 'default' and settings != '':
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.loadSettings(settings)


        self.sysname     = self.parHandle.frameWork['settings']['system']['sysname']


        self.parHandle.addingPath('curPlayer')

        self.parHandle.curPlayer['functions']['constructor']      = self.__init__
        self.parHandle.curPlayer['functions']['destructor']       = self.__del__
        self.parHandle.curPlayer['functions']['run']              = self.run
        self.parHandle.curPlayer['functions']['settingsLoading']  = self.loadSettings
        self.parHandle.curPlayer['functions']['settingsDefault']  = self.setDefaultSettings
        self.parHandle.curPlayer['functions']['settingsGui']      = None
          
        self.parHandle.dPrint('playAudio: Leaving displaySingleResult()', 2)

        # get reaction time delay from iniFile configuration and save it under
        self.parHandle.setDefaultCalibration('curPlayer', 'level')
        self.parHandle.readIniFile(mode='curPlayerSettings', module='curPlayer')


    def __del__(self):
        """!
        The destructor of the class will delete the menu of the player. The parameters of curPlayer  will be
        reset. The player path will be reset
        """

        self.parHandle.dPrint('playAudio: __del__()', 2)

        self.parHandle.clearSettingsInMenu('curPlayer')
        self.parHandle.closePath('curPlayer')

        self.parHandle.initializeToDefaults(mode='curPlayer')

        self.parHandle.dPrint('playAudio: Leaving __del__()', 2)


    def run(self, signal):
        """!
        The audio signal is played back after the optional preprocessing. If curPlayer['settings']['visualPreparation']
        is set to true a visual feedback is provided before the presentation to call the subjects attention.
        """

        self.parHandle.dPrint('playAudio: run()', 2)

        if not(self.parHandle.curPreprocessor['functions']['run'] == None):
            try:
                self.parHandle.dPrint('playAudio: Calling preprocessor', 4)
                self.parHandle.showInformation(_translate("playAudio", 'Audio is processed ...', None))
                signal = self.parHandle.curPreprocessor['functions']['run'](signal)
                self.parHandle.showInformation('')
            except:
                self.parHandle.dPrint('playsignal: could not call preprocessor', 1)

        stdPalette = self.parHandle.ui.exerWidget.palette()
        if self.parHandle.curPlayer['settings']['visualPreparation'] and\
                'visualPreparationTime' in self.parHandle.curExercise['settings'].keys():
            newPalette = QtGui.QPalette(QtGui.QColor(145, 145 , 255))
            self.parHandle.changePalette(self.parHandle.ui.exerWidget, newPalette)
            timerPC = QtCore.QTimer(self.parHandle, timerType=QtCore.Qt.PreciseTimer)
            timerPC.setSingleShot(True)
            timerPC.setInterval(self.parHandle.curExercise['settings']['visualPreparationTime'] * 1000)
            timerPC.timeout.connect(lambda: self.parHandle.changePalette(self.parHandle.ui.exerWidget, stdPalette))
            timerPC.start()

        #if not(self.parHandle.curPlayer['settings']['fs'] == signal['fs']) and not(self.parHandle.curPlayer['settings']['fs'] == 0):
        #    print('Implement resampling if requirerd')
        # TODO: calibration of signal

        if self.parHandle.frameWork['settings']['muteSignal']:
            scalFac = 0
        else:
            #scalFac = 1
            dBsystem = self.parHandle.frameWork['calibration']['level']['level']
            #dBplayerCal = 10**(self.parHandle.curExercise['calibration']['level']['level']/20)
            dBplayer = self.parHandle.curPlayer['settings']['level']
            scalFac = 10**(((dBsystem - 144)  + dBplayer) / 20)

        if self.parHandle.curPlayer['settings']['visualPreparation']:
            timerPA = QtCore.QTimer(self.parHandle, timerType=QtCore.Qt.PreciseTimer)
            timerPA.setSingleShot(True)
            if 'visualPreparationTime' in self.parHandle.curExercise['settings'].keys():
                timerPA.setInterval(self.parHandle.curExercise['settings']['visualPreparationTime'] * 1000)
            else:
                timerPA.setInterval(0)
            timerPA.timeout.connect(lambda: self.parHandle.changePalette(self.parHandle.ui.exerWidget, stdPalette))

            timerPA.start()
            try:

                QtCore.QTimer.singleShot(
                    self.parHandle.curPlayer['settings']['visualPreparationTime'] * 1000,
                lambda: sd.play(signal['audio']*scalFac, signal['fs'],
                                blocking=self.parHandle.curPlayer['settings']['waitFlag']))
            except:
                self.parHandle.dPrint(_translate("playAudio", 'playAudio: The player could not be run.',None),
                                      0, guiMode=True)

        self.parHandle.measureReactionTime(self.parHandle, mode='start')

        # test systemReactionTime by calling user input function directly
        if self.parHandle.frameWork['systemCheck']:
            self.parHandle.curExercise['handle'].runButton()


        self.parHandle.dPrint('playAudio: Leaving run()', 2)


    def state(self):
        """!
        Returns state of the player as defined by userAc

        Possible states are:

        0: player is stopped
        1: player is running
        2: player is paused
        -1: player state is undefined
        """

        playerState = -1
        """
        if self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            playerState = 0
        elif self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            playerState = 1
        elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
            playerState = 2
        """

        return playerState


    def setDefaultSettings(self):
        """!
        The default parameters are set.
        """

        self.parHandle.dPrint('playAudio: setDefaultSettings()', 2)

        playerBaseName                      = self.parHandle.frameWork['path']['player']
        playerName                          = 'playAudio'

        self.parHandle.initializeToDefaults(mode='curPlayerSettings')
        
        self.parHandle.curPlayer['settings']['playerName']         = playerName
        self.parHandle.curPlayer['path']         = dict()
        self.parHandle.curPlayer['path']['base'] = os.path.join(playerBaseName, playerName)
        self.parHandle.curPlayer['path']['presets'] = os.path.join(self.parHandle.curPlayer['path']['base'], 'presets')



        self.parHandle.curPlayer['settings']['settingsName']    = 'default'
        self.parHandle.curPlayer['settings']['fs']              = 0
        self.parHandle.curPlayer['settings']['level']           = 65
        self.parHandle.curPlayer['settings']['waitFlag']        = True
        self.parHandle.curPlayer['settings']['comment']         = 'No comment'

        self.parHandle.curPlayer['settings']['visualPreparation']       = True
        self.parHandle.curPlayer['settings']['visualPreparationTime']   = 0.4

        self.parHandle.curPlayer['settingLimits'] = dict()
        self.parHandle.curPlayer['settingLimits']['playerName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['playerName']['type'] = 'string'
        self.parHandle.curPlayer['settingLimits']['playerName']['mandatory'] = True
        self.parHandle.curPlayer['settingLimits']['playerName']['editable'] = False
        self.parHandle.curPlayer['settingLimits']['playerName']['range'] = []

        self.parHandle.curPlayer['settingLimits']['settingsName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['settingsName']['type'] = ['string']
        self.parHandle.curPlayer['settingLimits']['settingsName']['mandatory'] = True
        self.parHandle.curPlayer['settingLimits']['settingsName']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['settingsName']['range'] = []

        self.parHandle.curPlayer['settingLimits']['fs'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['fs']['type'] = 'int'
        self.parHandle.curPlayer['settingLimits']['fs']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['fs']['editable'] = False
        self.parHandle.curPlayer['settingLimits']['fs']['range'] = [8000, 16000, 32000, 44100, 48000, 96000]
        self.parHandle.curPlayer['settingLimits']['fs']['unit'] = 's'
        self.parHandle.curPlayer['settingLimits']['fs']['label'] = _translate("playAudio", "sampling rate", None)
        self.parHandle.curPlayer['settingLimits']['fs']['default'] = 44100

        self.parHandle.curPlayer['settingLimits']['waitFlag'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['waitFlag']['type'] = 'bool'
        self.parHandle.curPlayer['settingLimits']['waitFlag']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['waitFlag']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['waitFlag']['range'] = [True, False]
        self.parHandle.curPlayer['settingLimits']['waitFlag']['comboBoxStyle'] = False
        self.parHandle.curPlayer['settingLimits']['waitFlag']['label'] = _translate("playAudio", "Wait for audio end", None)
        self.parHandle.curPlayer['settingLimits']['waitFlag']['default'] = True

        self.parHandle.dPrint('playAudio: Leaving setDefaultSettings()', 2)


    def loadSettings(self, settings):
        """
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current exercise.
        """

        self.parHandle.dPrint('playAudio: loadSettings()', 2)
        try:
            self.parHandle.loadSettings(settings, module = 'curPlayer')
        except:
            self.setDefaultSettings()
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            print('Could not load settings (' + settingsName + ') loading default settings instead')
        self.parHandle.dPrint('playAudio: Leaving loadSettings()', 2)


