"""!
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
import io

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtMultimedia
from copy import deepcopy
import soundfile as sf

#import numpy as np
def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class playQtAudio():
    def __init__(self, parHandle=None, settings='default'):
        """!
        Initializing the CICoachLab player playQtAudio. This function provides the function to play back audio signals.
        with The signal format is as follows:
        signa['audio']
        signal['fs']
        The recomended field:
        signal['name']

        The recomended field signal['name'] is used to handle the check if the signal has been loaded before and the
        playing an pausing of the signal is possible, or if the signal has to be loaded to start the playing.

        Additionally to the obligatory functions ['run'] , ['settingsLoading'], ['settingsDefault'] and other the
        following functions are provided.

        The function provided with
        self.parHandle.curPlayer['functions']['run']
        takes the argument signal, loads it into the player, and starts the playing.




        The special functions provided by playQtAudio are found in self.parHandle.curPlayer['functions'] and are:

        ['addControlbar']:
        # this function returns a layout with control buttons and a slider which allow to play back different signals.
        # The control bar contains a play, pause and stop button, a slider to see and control the playback position of
        # the played audio. The label at the start and end of the slider indicate the start (0) and end (duration)
        # of the signal.
        # If the signal is played back and play is pressed again, the signal is stopped and started again at the
        # start of the signal.
        # Different control bars can be generated to play back and control different signals.
        # The same qt player is used to play back the different signals. When the control bar is changed a different
        # signal will be loaded. The assignment is handled by the argument controlbarName which defaults to 'main' if
        # no name is provided and a single control bar is used.
        # With layoutMode a 'stacked' and 'inline' version is returned. 'stacked' is used as default if enough place
        # is provided. A less place taking version is returned with the 'inline' version.
        ['getControlbarCaller']
        This function returns the label of the currently controlled signal.
        ['setControlbarLabel']:
        This function takes the input argument, label, to set the controlled signal.
        ['durationChanged']:
        If the widget seekSlider and seekSliderLabelEnd exist the label and and the range of the slider will be set
        to the duration input argument, defined in mili seconds.
        ['setPosition']
        The media pointer is set to position.
        ['playHandler']
        The loaded signal will be played.
        ['pauseHandler']
        The audio signal will be paused.
        ['stopHandler']
        The audio signal will be stopped.
        ['loadAudioSignal']
        The audio signal will be set.

        If a preprocessor is defined the preprocessor will be called and the audio signal processed.
        The default settings will be set or the provided settings will be loaded.

        If the waitFlag is set in the settings of the player, any input widget will block any signal as long as the
        audio is played.
        """

        if parHandle == None:
            print('cannot initilize without framework.')
        self.parHandle = parHandle

        self.parHandle.dPrint('playQtAudio: __init__()', 2)

        self.setDefaultSettings()
        self.parHandle.addingPath('curPlayer')
        if settings != 'default' and settings != '':
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.loadSettings(settings)

        self.sysname     = self.parHandle.frameWork['settings']['system']['sysname']

        self.player = QtMultimedia.QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.player.bufferStatusChanged.connect(self.bufferStatusChanged)
        self.player.stateChanged.connect(self.stateChanged)


        self.player.positionChanged.connect(self.positionChanged)
        self.player.durationChanged.connect(self.durationChanged)

        # self.userAction defines the state of the audio player as follows:
        # initialized: -1
        # stopped: 0
        # playing: 1
        # paused: 2
        self.userAction = -1

        self.buf = None

        self.parHandle.addingPath('curPlayer')

        self.parHandle.curPlayer['functions']['constructor']      = self.__init__
        self.parHandle.curPlayer['functions']['destructor']       = self.__del__
        self.parHandle.curPlayer['functions']['run']              = self.run
        self.parHandle.curPlayer['functions']['applyPreprocessor']=self.applyPreprocessor
        self.parHandle.curPlayer['functions']['settingsLoading']  = self.loadSettings
        self.parHandle.curPlayer['functions']['settingsDefault']  = self.setDefaultSettings
        self.parHandle.curPlayer['functions']['settingsGui']      = None

        self.parHandle.curPlayer['functions']['getControlbarCaller'] = self.getControlbarCaller
        self.parHandle.curPlayer['functions']['setControlbarLabel'] = self.setControlbarLabel
        # this function returns a layout with control buttons and a slider.
        self.parHandle.curPlayer['functions']['addControlbar'] = self.addControlbar
        self.parHandle.curPlayer['functions']['durationChanged'] = self.durationChanged
        self.parHandle.curPlayer['functions']['setPosition'] = self.setPosition
        self.parHandle.curPlayer['functions']['playHandler'] = self.playHandler
        self.parHandle.curPlayer['functions']['pauseHandler'] = self.pauseHandler
        self.parHandle.curPlayer['functions']['stopHandler'] = self.stopHandler
        self.parHandle.curPlayer['functions']['loadAudioSignal'] = self.loadAudioSignal
        self.parHandle.curPlayer['functions']['stateChanged'] = self.stateChanged

        # get reaction time delay from iniFile configuration and save it under
        self.parHandle.setDefaultCalibration('curPlayer', 'level')
        self.parHandle.readIniFile(mode='curPlayerSettings', module='curPlayer')

        self.parHandle.curPlayer['handle'] = self
        # The controlbar label is set if a single controlbar is added, or if a button of a controlbar is pressed which
        # defines the active controlbar. If self.controlbarLabel is empty no controlbar actions, like updating the
        # slider or labeling of the duration, will be allowed or run.
        self.controlbarLabel = ''
        self.playerWidgetConverter = dict()
        self.changedMediaFlag = True
        self.oldMediaName = ''

        self.oldInfoMsg = ''

        self.oldSettings = None

        self.parHandle.dPrint('playQtAudio: Leaving __init__()', 2)


    def __del__(self):
        """!
        The destructor of the class will delete the menu of the player. The parameters of curPlayer  will be
        reset. The player path will be reset
        """

        self.parHandle.dPrint('playQtAudio: __del__()', 2)

        self.parHandle.clearSettingsInMenu('curPlayer')
        self.parHandle.closePath('curPlayer')

        self.parHandle.initializeToDefaults(mode='curPlayer')

        self.parHandle.dPrint('playQtAudio: Leaving __del__()', 2)


    def applyPreprocessor(self, signalIn):
        """!
        This function calculates the preprocessed signal. The calling of this functions allows
        buffering of time intensively preprocessed signals.
        """

        self.parHandle.dPrint('playQtAudio: applyPreprocessor()', 2)

        # set name if name is not defined which allows prebuffering of curPreprocessor
        if not ('name' in signalIn):
            # if no name is defined by the generaotr, as in the genWavreader, which takes the filename, as name
            # the signal name should be unique enough by the settings of the generator.
            signalIn['name'] = str(self.parHandle.curGenerator['settings'])


        if not (self.parHandle.curPreprocessor['functions']['run'] == None) and \
                ('deactivate' in self.parHandle.curPreprocessor['settings'] and
                 not (self.parHandle.curPreprocessor['settings']['deactivate'])):

            try:
                self.oldInfoMsg = self.parHandle.statusBar().currentMessage()
                self.parHandle.dPrint('playQtAudio: Calling preprocessor', 4)
                self.parHandle.showInformation(_translate("playQtAudio", 'audio signal is processed ...', None)
                                               + signalIn['name'])
                signalOut = self.parHandle.curPreprocessor['functions']['run'](signalIn)
                self.parHandle.showInformation(self.oldInfoMsg)
            except:
                self.parHandle.dPrint('playsignal: could not call preprocessor', 1)
        else:
            signalOut = signalIn

        self.parHandle.dPrint('playQtAudio: Leaving applyPreprocessor()', 2)
        return signalOut


    def run(self, signal, enforceReloadedData=False):
        """!
        The audio signal is played back after the optional preprocessing. If curPlayer['settings']['visualPreparation']
        is set to true a visual feedback is provided before the presentation to call the subjects attention.
        """

        self.parHandle.dPrint('playQtAudio: run()', 2)

        self.oldInfoMsg = self.parHandle.statusBar().currentMessage()

        # if the audio player settings have been changed the data will be reloaded.
        if self.oldSettings != self.parHandle.curPlayer['settings']:
            enforceReloadedData = True

        # This distinction allows the handling of pause and rejoin playing at paused position
        if not(enforceReloadedData) and self.oldMediaName and 'name' in signal and signal['name'] == self.oldMediaName:
            # leave loaded media/signal unchanged
            msg = "The old signal is called again. The media won't be reloaded again."
            self.parHandle.dPrint(msg, 2)
            self.playHandler()
        else:
            # reload and/or reprocess media/signal

            self.oldMediaName = signal['name']
            #
            signal = self.applyPreprocessor(signal)

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

            if self.parHandle.frameWork['settings']['muteSignal']:
                scalFac = 0
            else:
                #scalFac = 1
                dBsystem = self.parHandle.frameWork['calibration']['level']['level']
                #dBplayerCal = 10**(self.parHandle.curExercise['calibration']['level']['level']/20)
                dBplayer = self.parHandle.curPlayer['settings']['level']
                scalFac = 10**(((dBsystem - 144)  + dBplayer) / 20)

                self.oldSettings = deepcopy(self.parHandle.curPlayer['settings'])

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
                signalScaled = deepcopy(signal)
                signalScaled['audio'] = signalScaled['audio']*scalFac



                self.loadAudioSignal(signalScaled)

                #self.pauseHandler()
                if 'durationChanged' in dir(self.parHandle.curExercise['handle']):
                    self.durationChanged(self.player.duration())

                self.playHandler()
                #QtCore.QTimer.singleShot(
                #    self.parHandle.curPlayer['settings']['visualPreparationTime'] * 1000, self.playHandler)
            except:
                self.parHandle.dPrint(_translate("playQtAudio", 'playQtAudio: The player could not be run.',None),
                                      0, guiMode=True)

        self.parHandle.measureReactionTime(self.parHandle, mode='start')

        # test systemReactionTime by calling user input function directly
        if self.parHandle.frameWork['systemCheck']:
            self.parHandle.curExercise['handle'].runButton()

        self.parHandle.dPrint('playQtAudio: Leaving run()', 2)


    def loadAudioSignal(self, signal):
        """!
        The audio signal with the signal format
        signal['audio']
        signal['fs']

        This function converts the numpy array to bytes which can be loaded by the player.
        """

        self.parHandle.dPrint('playQtAudio: loadAudioSignal()', 2)

        f = io.BytesIO()
        sf.write(f, signal['audio'], signal['fs'], format='wav', subtype='PCM_24')

        # copy the bytes to a QBuffer
        self.buf = QtCore.QBuffer()
        self.buf.setData(f.getvalue())
        self.buf.open(QtCore.QIODevice.ReadOnly)

        self.player.setMedia(QtMultimedia.QMediaContent(), self.buf)

        self.parHandle.dPrint('playQtAudio: loadAudioSignal()', 2)


    def positionChanged(self, position):
        """!
        If the position is changed the position of at the slider is changed if a control bar is defined and
        if the slider widgets is defined.
        """

        #self.seekSlider.setValue(position)
        # check the exercise provides a controlbar with slider



        if self.controlbarLabel:

            if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.BufferedMedia:
                # introduced to prevent
                """
                if position > 0:
                    status = 'playing'
                else:
                    # why does this happen?!?
                    status = 'buffered'
                """
                status = 'playing'
            else:
                status = 'playing'

            seekSlider = self.parHandle.curExercise['handle'].controlbarRefs[self.controlbarLabel]['seekSlider']
            seekSlider.setValue(position)
            duration = self.player.duration()

            if duration > 0:
                self.providePlayerFeedBack(status=status, position=position/duration)

    def durationChanged(self, duration):
        """!
        If the widget seekSlider and seekSliderLabelEnd exist the label and and the range of the slider will be set.

        duration: length of signal in mili seconds
        """

        self.parHandle.dPrint('playQtAudio: durationChanged()', 2)

        if self.controlbarLabel:
            seekSlider = self.parHandle.curExercise['handle'].controlbarRefs[self.controlbarLabel]['seekSlider']
            seekSliderLabelEnd = \
                self.parHandle.curExercise['handle'].controlbarRefs[self.controlbarLabel]['seekSliderLabelEnd']
            if seekSlider:
                seekSlider.setRange(0, duration)
            if seekSliderLabelEnd:
                msg = '%d:%02d' % (round(duration / 60000), round((duration / 1000) % 60))
                seekSliderLabelEnd.setText(msg)

        self.parHandle.dPrint('playQtAudio: Leaving durationChanged()', 2)


    def pauseHandler(self):
        """!
        The audio signal will be paused and in case of waitFlag == True the disabled gui user input elements will
        enabled again.
        """

        self.parHandle.dPrint('playQtAudio: pauseHandler()', 2)

        self.userAction = 2
        self.player.pause()
        if self.parHandle.curPlayer['settings']['waitFlag']:
            self.parHandle.enableExerciseGui()

        #self.oldInfoMsg = ''
        feedback = _translate("playQtAudio", 'Audio paused ... ', None)
        self.parHandle.showInformation(feedback)
        pos = self.player.position()
        duration = self.player.duration()

        if duration:
            position = pos / duration * 100
        else:
            position = 0
        self.providePlayerFeedBack(status='paused', position=position)

        self.parHandle.dPrint('playQtAudio: Leaving pauseHandler()', 2)

    def playHandler(self):
        """!
        The audio signal will be played back. User input gui elements will be disabled, if the waitFlag was set.
        """

        self.parHandle.dPrint('playQtAudio: playHandler()', 2)

        if self.parHandle.frameWork['settings']['fixMasterVolume']:
            #currentVol = self.parHandle.fixedMasterVol
            currentVol = self.parHandle.getMasterVolume()
            if self.parHandle.fixedMasterVol == currentVol:
                msg = 'Volume control passed.'
                self.parHandle.dPrint(msg, 4)
            else:
                msg = _translate("playQtAudio",
                                     f"Volume control failed. \n\nThe volume found was '{currentVol:02d}%'"
                                     f" and will be set to '{self.parHandle.fixedMasterVol:02d}%'.\n\n" 
                                     "Please don't change the volume settings during the use of CICoach Lab.", None)
                self.parHandle.dPrint(msg, 0, guiMode=True)
                self.parHandle.setMasterVolume(self.parHandle.fixedMasterVol)
        senderWidget = self.parHandle.sender()
        #getControlbarCaller = self.getControlbarCaller(senderWidget)
        #self.parHandle.sender().parent().layout().count()

        self.userAction = 1
        if 'durationChanged' in dir(self.parHandle.curExercise['handle']):
            self.parHandle.curExercise['handle'].durationChanged(self.player.duration())
        # self.statusBar().showMessage('Playing at Volume %d' % self.player.volume())
        if self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.LoadedMedia:
                self.player.play()
            elif self.player.mediaStatus() == QtMultimedia.QMediaPlayer.BufferedMedia:
                self.player.play()
            elif self.player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
                # self.positionChanged(0)
                # self.setPosition(0)
                self.player.play()
            elif self.player.mediaStatus() == QtMultimedia.QMediaPlayer.LoadingMedia:
                # if buffer is used this state persists
                self.player.play()
        elif self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.stop()
            self.player.play()
        elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
            self.player.play()
        if self.parHandle.curPlayer['settings']['waitFlag']:
            # just disabling exercise gui elements to stop user interaction,the rest of the code will continue to run.
            self.parHandle.disableExerciseGui()
        self.providePlayerFeedBack(status='playing')

        #self.oldInfoMsg = ''
        feedback = _translate("playQtAudio", 'Audio playing ... ', None)
        self.parHandle.showInformation(feedback)

        self.parHandle.dPrint('playQtAudio: Leaving playHandler()', 2)


    def stopHandler(self):
        """!
        The audio is stopped and the disabled gui input elements will be enabled again, if they were disabled in
        case of waitFlag == True.
        """

        self.parHandle.dPrint('playQtAudio: stopHandler()', 2)

        self.userAction = 0
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.stop()
        elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
            self.player.stop()
        elif self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            pass
        if self.parHandle.curPlayer['settings']['waitFlag']:
            self.parHandle.enableExerciseGui()
        self.parHandle.showInformation(self.oldInfoMsg)
        self.oldInfoMsg = ''
        self.providePlayerFeedBack(status='stopped')

        self.parHandle.dPrint('playQtAudio: Leaving stopHandler()', 2)


    def stateChanged(self):
        """!
        """

        self.parHandle.dPrint('playQtAudio: stateChanged()', 2)

        if self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            self.player.stop()
            self.parHandle.showInformation(self.oldInfoMsg)
            if self.controlbarLabel:
                if self.player.duration():
                    pos = self.player.position()/self.player.duration()*100
                else:
                    pos = 0
                self.providePlayerFeedBack(status='stopped', position=pos)

        self.parHandle.dPrint('playQtAudio: Leaving stateChanged()', 2)


    def setControlbarLabel(self, newLabel):
        """!
        This function takes the input argument, label, to set the controlled signal.
        """

        self.parHandle.dPrint('playQtAudio: setControlbarLabel()', 2)

        self.controlbarLabel = newLabel

        self.parHandle.dPrint('playQtAudio: Leaving setControlbarLabel()', 2)


    def providePlayerFeedBack(self, status='', position=np.nan):
        """!
        The function turns the status of the player and position, if possible, of the played signal to the feedback
        function of the calling exercise if the exercise has defined a feedback function.
        This function is called by the functions self.mediaStatusChanged(), self.bufferStatusChanged() and
        self.stateChanged()
        If no status can be provided an empty string is provided.
        If no position can be provided np.nan is provided.

        The status can be:
            'playing', 'waiting', 'paused', 'stopped', 'loading' or ''
        The position is returned in percent of the signal length.
        """

        self.parHandle.dPrint('playQtAudio: providePlayerFeedBack()', 4)

        if self.parHandle.curExercise['functions']['getPlayerStatus']:
            self.parHandle.curExercise['functions']['getPlayerStatus'](status, position)

        self.parHandle.dPrint('playQtAudio: Leaving providePlayerFeedBack()', 4)


    def mediaStatusChanged(self):
        """!
        If the data has been loaded and the media should be played as indicated by self.userAction the
        duration of the media will be read and set in the controlbar, if it was defined. The audio is played by
        calling self.playHandler()
        If the media has been ended the disabled input gui elements will be enabled again, if waitFlag == True.

        The function is called when media has been loaded, if media is started to play, when the media ends.
        """

        self.parHandle.dPrint('playQtAudio: mediaStatusChanged()', 2)

        if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.BufferedMedia and self.userAction == 1:
            durationT = self.player.duration()

            if 'durationChanged' in dir(self.parHandle.curExercise['handle']):
                self.player.durationChanged.connect(self.parHandle.curExercise['handle'].durationChanged)
            if self.parHandle.curExercise['handle'].controlbars:
                guiHandlingFailed = False
                # defining the calling controlbar, if several controlbars might exist in exercise
                if self.controlbarLabel:
                    controlbarLabel = self.controlbarLabel
                else:
                    if 'main' in self.parHandle.curExercise['handle'].controlbarRefs:
                        controlbarLabel = 'main'
                    elif len(self.parHandle.curExercise['handle'].controlbars) == 1:
                            [[controlbarLabel, temp]] = self.parHandle.curExercise['handle'].controlbarRefs.items()
                    else:
                        guiHandlingFailed = True
                if guiHandlingFailed:
                    self.controlbarLabel = ''
                    self.parHandle.dPrint('Tried to update controlbar and failed.', 0)
                else:
                    self.controlbarLabel = controlbarLabel
                    #seekSlider = self.parHandle.curExercise['handle'].controlbars[controlbarLabel].children()[0].itemAt(1).widget()

                    self.durationChanged(durationT)
            #self.playHandler()
            self.providePlayerFeedBack(status='waiting', position=0)
            return QtMultimedia.QMediaPlayer.BufferedMedia
        elif self.player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
            # enabling exercise gui elements again after disabling after the playing of the signal
            if self.parHandle.curPlayer['settings']['waitFlag']:
                self.parHandle.enableExerciseGui()
            #self.oldInfoMsg = ''
            feedback = _translate("playQtAudio", 'End of audio.', None)
            self.parHandle.showInformation(feedback)

            self.providePlayerFeedBack(status='stopped', position=100)
            return QtMultimedia.QMediaPlayer.EndOfMedia
        else:
            return -1

        self.parHandle.dPrint('playQtAudio: Leaving mediaStatusChanged()', 2)


    def bufferStatusChanged(self):
        """!
        If the buffer status changes the same code is run as in self.mediaStatusChanged()
        """

        self.parHandle.dPrint('playQtAudio: bufferStatusChanged()', 2)

        if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.LoadedMedia and self.userAction == 1:
            durationT = self.player.duration()
            if 'durationChanged' in dir(self.parHandle.curExercise['handle']):
                self.player.durationChanged.connect(self.parHandle.curExercise['handle'].durationChanged)

            if self.parHandle.curExercise['handle'].controlbars:
                guiHandlingFailed = False
                # defining the calling controlbar, if several controlbars might exist in exercise
                if self.controlbarLabel:
                    controlbarLabel = self.controlbarLabel
                else:
                    if 'main' in self.parHandle.curExercise['handle']['playBtn']:
                        controlbarLabel = 'main'
                    elif len(self.parHandle.curExercise['handle'].controlbars) == 1:
                        [[controlbarLabel, temp]] = self.parHandle.curExercise['handle'].controlbarRefs.items()
                    else:
                        guiHandlingFailed = True
                if guiHandlingFailed:
                    self.controlbarLabel = ''
                    self.parHandle.dPrint('Tried to update controlbar and failed.', 0)
                else:
                    self.controlbarLabel = controlbarLabel
                    seekSlider = self.parHandle.curExercise['handle'].controlbars[controlbarLabel].children()[0].itemAt(1).widget()
                    seekSlider.setRange(0, durationT)
                    seekSlider.setText('%d:%02d' % (int(durationT / 60000), int((durationT / 1000) % 60)))
            self.playHandler()
            self.providePlayerFeedBack(status='playing') #TODO: Check and compare to mediaStatusChanged
            return QtMultimedia.QMediaPlayer.LoadedMedia
        elif self.player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
            # enabling exercise gui elements again after disabling after the playing of the signal
            if self.parHandle.curPlayer['settings']['waitFlag']:
                self.parHandle.enableExerciseGui()

            #self.oldInfoMsg = ''
            feedback = _translate("playQtAudio", 'End of audio.', None)
            self.parHandle.showInformation(feedback)

            self.providePlayerFeedBack(status='stopped', position=100)
            return QtMultimedia.QMediaPlayer.EndOfMedia
        else:
            return -1

        self.parHandle.dPrint('playQtAudio: Leaving bufferStatusChanged()', 2)


    def addControlbar(self, controlbarName='main', layoutMode='stacked'):
        """!
        This function produces a controllbar widget to control the player. The widget controlbar  and
        is returned alongside controlbarRefs which enables the applying exercise an easier access to the control widgets
        (Referencing the control widgets>).
        With this function several controlbars can be generated by the exercises to enable the acces to such an
        specific controlbar, control of the respective audio signal, the controlbarName can be used to address a
        specific controlbar.

        With layoutMode the controlls can be arranged vertically stacked or inline. The belonging options are
         'stacked' or 'inline'.
        In the vertically stacked layout the slider and its labels is found at the top and big control buttons below.
        In the "inline" layout the slider with its labels and the control buttons are in line with smaller control
        buttons.

        Referencing the control widgets:

        To avoid non telling references in the exercises controlbarRefs is returned for easier references
        self.playBtn = controlbar.children()[1].itemAt(0).widget()
        self.pauseBtn = controlbar.children()[1].itemAt(1).widget()
        self.stopBtn = controlbar.children()[1].itemAt(2).widget()
        self.seekSlider = controlbar.children()[0].itemAt(1).widget().objectName()
        self.seekSliderLabelStart = controlbar.children()[0].itemAt(0).widget().objectName()
        self.seekSliderLabelEnd = controlbar.children()[0].itemAt(2).widget().objectName()

        is equal to

        self.playBtn = controlbarRefs['playBtn']
        self.pauseBtn = controlbarRefs['pauseBtn']
        self.stopBtn = controlbarRefs['stopBtn']
        self.seekSlider = controlbarRefs['seekSlider']
        self.seekSliderLabelStart = controlbarRefs['seekSliderLabelStart']
        self.seekSliderLabelEnd = controlbarRefs['seekSliderLabelEnd']

        If other controls like 'volumeDescBtn' or 'volumeIncBtn' will be added or the the order of the control
        changes the references won't change.
        """

        if layoutMode == 'stacked':
            controlbar = QtWidgets.QVBoxLayout()  # centralWidget
        else:
            controlbar = QtWidgets.QHBoxLayout()  # centralWidget

        seekSliderLayout = QtWidgets.QHBoxLayout()
        controls = QtWidgets.QHBoxLayout()
        # playlistCtrlLayout = QtWidgets.QHBoxLayout()

        controlbar.setObjectName(controlbarName)
        seekSliderLayout.setObjectName('seekSliderLayout')
        controls.setObjectName('controls')

        # creating buttons
        if layoutMode == 'stacked':
            playBtn = QtWidgets.QPushButton(_translate("playQtAudio", 'Play', None))  # play button
            pauseBtn = QtWidgets.QPushButton(_translate("playQtAudio", 'Pause', None))  # pause button
            stopBtn = QtWidgets.QPushButton(_translate("playQtAudio", 'Stop', None))  # stop button
            # volumeDescBtn = QtWidgets.QPushButton('V (-)')  # Decrease Volume
            # volumeIncBtn = QtWidgets.QPushButton('V (+)')  # Increase Volume

        else:
            # playButton
            objectName = f"pbPlay_{controlbarName:s}"
            playBtn = QtWidgets.QPushButton(text='', objectName=objectName)
            file  = os.path.join(self.parHandle.curExercise['path']['recources'], 'play.png')
            playBtn.setIcon(QtGui.QIcon(file))
            playBtn.setIconSize(QtCore.QSize(32, 32))
            playBtn.setMaximumSize(32, 32)
            playBtn.setMinimumSize(32, 32)
            playBtn.setStyleSheet("background-image: url('image.jpg'); border: none;")

            # pauseButton
            objectName = f"pbPause_{controlbarName:s}"
            pauseBtn = QtWidgets.QPushButton(text='', objectName=objectName)
            file  = os.path.join(self.parHandle.curExercise['path']['recources'], 'pause.png')
            pauseBtn.setIcon(QtGui.QIcon(file))
            pauseBtn.setIconSize(QtCore.QSize(32, 32))
            pauseBtn.setMaximumSize(32, 32)
            pauseBtn.setMinimumSize(32, 32)
            pauseBtn.setStyleSheet("background-image: url('image.jpg'); border: none;")

            # stopButton
            stopBtn = QtWidgets.QPushButton('Stop')  # stop button
            objectName = f"pbStop_{controlbarName:s}"
            stopBtn = QtWidgets.QPushButton(text='', objectName=objectName)
            file  = os.path.join(self.parHandle.curExercise['path']['recources'], 'stop.png')
            stopBtn.setIcon(QtGui.QIcon(file))
            stopBtn.setIconSize(QtCore.QSize(32, 32))
            stopBtn.setMaximumSize(32, 32)
            stopBtn.setMinimumSize(32, 32)
            stopBtn.setStyleSheet("background-image: url('image.jpg'); border: none;")

        playBtn.setObjectName('playBtn')
        pauseBtn.setObjectName('pauseBtn')
        stopBtn.setObjectName('stopBtn')

        # creating seek slider

        seekSlider = QtWidgets.QSlider()
        seekSlider.setObjectName('seekSlider')
        seekSlider.setMinimum(0)
        seekSlider.setMaximum(100)
        seekSlider.setOrientation(QtCore.Qt.Horizontal)
        seekSlider.setTracking(False)
        seekSlider.sliderMoved.connect(self.setPosition)

        seekSliderLabelStart = QtWidgets.QLabel('0.00')
        seekSliderLabelEnd = QtWidgets.QLabel('0.00')

        seekSliderLabelStart.setObjectName('seekSliderLabelStart')
        seekSliderLabelEnd.setObjectName('seekSliderLabelEnd')

        seekSliderLayout.addWidget(seekSliderLabelStart)
        seekSliderLayout.addWidget(seekSlider)
        seekSliderLayout.addWidget(seekSliderLabelEnd)

        # Add handler for each button. Not using the default slots.
        playBtn.clicked.connect(self.playHandler)
        pauseBtn.clicked.connect(self.pauseHandler)
        stopBtn.clicked.connect(self.stopHandler)

        # Adding to the horizontal layout
        # controls.addWidget(volumeDescBtn)
        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)
        # controls.addWidget(volumeIncBtn)

        # Adding to the vertical layout
        controlbar.addLayout(seekSliderLayout)
        controlbar.addLayout(controls)

        controlbarRefs = dict()
        controlbarRefs['playBtn'] = playBtn
        controlbarRefs['pauseBtn'] = pauseBtn
        controlbarRefs['stopBtn'] = stopBtn
        controlbarRefs['seekSlider'] = seekSlider
        controlbarRefs['seekSliderLabelStart'] = seekSliderLabelStart
        controlbarRefs['seekSliderLabelEnd'] = seekSliderLabelEnd

        self.playerWidgetConverter[playBtn] = controlbarName
        self.playerWidgetConverter[pauseBtn] = controlbarName
        self.playerWidgetConverter[stopBtn] = controlbarName
        self.playerWidgetConverter[seekSlider] = controlbarName
        self.playerWidgetConverter[seekSliderLabelStart] = controlbarName
        self.playerWidgetConverter[seekSliderLabelEnd] = controlbarName

        if not(self.controlbarLabel):
            self.controlbarLabel = controlbarName
        else:
            self.controlbarLabel = ''

        return controlbar, controlbarRefs


    def state(self):
        """!
        Returns state of the player as defined by userAction in playAudio

        Possible states are:

        0: player is stopped
        1: player is running
        2: player is paused
        -1: player state is undefined
        """

        self.parHandle.dPrint('playQtAudio: state()', 2)

        playerState = -1
        if self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            playerState = 0
        elif self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            playerState = 1
        elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
            playerState = 2

        self.parHandle.dPrint('playQtAudio: Leaving state()', 2)

        return playerState


    def setPosition(self, position):
        """!
        The media pointer is set to position.
        """

        self.parHandle.dPrint('playQtAudio: setPosition()', 2)

        self.player.setPosition(position)

        self.parHandle.dPrint('playQtAudio: Leaving setPosition()', 2)


    def getControlbarCaller(self, inputWidget):
        """!
        This function takes the inputWidget (button) and checks for the name of the parent control bar.
        This function can bed used to determine which controlbar has been used, if multiple controlbars are used in the
        callingexercise.
        """

        self.parHandle.dPrint('playQtAudio: getControlbarCaller()', 2)

        if inputWidget in self.playerWidgetConverter:
            return self.playerWidgetConverter[inputWidget]
        else:
            return self.controlbarLabel

        self.parHandle.dPrint('playQtAudio: Leaving sgetControlbarCalleretPosition()', 2)


    def setDefaultSettings(self):
        """!
        The default parameters are set.
        """

        self.parHandle.dPrint('playQtAudio: setDefaultSettings()', 2)

        playerBaseName                      = self.parHandle.frameWork['path']['player']
        playerName                          = 'playQtAudio'

        self.parHandle.initializeToDefaults(mode='curPlayerSettings')
        
        self.parHandle.curPlayer['settings']['playerName']         = playerName
        self.parHandle.curPlayer['path']         = dict()
        self.parHandle.curPlayer['path']['base'] = os.path.join(playerBaseName, playerName)
        self.parHandle.curPlayer['path']['presets'] = os.path.join(self.parHandle.curPlayer['path']['base'], 'presets')

        self.parHandle.curPlayer['settings']['settingsName']    = 'default'
        self.parHandle.curPlayer['settings']['fs']              = 44100
        self.parHandle.curPlayer['settings']['level']           = 65
        self.parHandle.curPlayer['settings']['visualPreparation'] = False
        self.parHandle.curPlayer['settings']['visualPreparationTime'] = 0.4
        self.parHandle.curPlayer['settings']['waitFlag']       = True

        self.parHandle.curPlayer['settings']['comment']         = 'No comment'

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
        self.parHandle.curPlayer['settingLimits']['fs']['comboBoxStyle'] = True
        self.parHandle.curPlayer['settingLimits']['fs']['unit'] = 's'
        self.parHandle.curPlayer['settingLimits']['fs']['label'] = _translate("playQtAudio", "sampling rate", None)
        self.parHandle.curPlayer['settingLimits']['fs']['default'] = 44100

        self.parHandle.curPlayer['settingLimits']['level'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['level']['type'] = 'float'
        self.parHandle.curPlayer['settingLimits']['level']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['level']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['level']['range'] = [0, 85]
        self.parHandle.curPlayer['settingLimits']['level']['unit'] = 'dB'
        self.parHandle.curPlayer['settingLimits']['level']['label'] = _translate("playQtAudio", "level", None)
        self.parHandle.curPlayer['settingLimits']['level']['default'] = 65

        self.parHandle.curPlayer['settingLimits']['visualPreparation'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['type'] = 'bool'
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['range'] = [True, False]
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['comboBoxStyle']= True
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['unit'] = ''
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['label'] = _translate("playQtAudio", "Visual preparation", None)
        self.parHandle.curPlayer['settingLimits']['visualPreparation']['default'] = 44100

        self.parHandle.curPlayer['settingLimits']['visualPreparationTime'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['type'] = 'float'
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['range'] = [0, 20]
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['unit'] = 's'
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['label'] = _translate("playQtAudio", "Preparation time", None)
        self.parHandle.curPlayer['settingLimits']['visualPreparationTime']['default'] = 0.4

        self.parHandle.curPlayer['settingLimits']['waitFlag'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPlayer['settingLimits']['waitFlag']['type'] = 'bool'
        self.parHandle.curPlayer['settingLimits']['waitFlag']['mandatory'] = False
        self.parHandle.curPlayer['settingLimits']['waitFlag']['editable'] = True
        self.parHandle.curPlayer['settingLimits']['waitFlag']['range'] = [True, False]
        self.parHandle.curPlayer['settingLimits']['waitFlag']['comboBoxStyle'] = True
        self.parHandle.curPlayer['settingLimits']['waitFlag']['label'] = _translate("playQtAudio", "Wait for audio end", None)
        self.parHandle.curPlayer['settingLimits']['waitFlag']['default'] = True

        self.parHandle.dPrint('playQtAudio: Leaving setDefaultSettings()', 2)


    def loadSettings(self, settings):
        """
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current exercise.
        """

        self.parHandle.dPrint('playQtAudio: loadSettings()', 2)
        try:
            self.parHandle.loadSettings(settings, module = 'curPlayer')
        except:
            self.setDefaultSettings()
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            print('Could not load settings (' + settingsName + ') loading default settings instead')
        self.parHandle.dPrint('playQtAudio: Leaving loadSettings()', 2)


