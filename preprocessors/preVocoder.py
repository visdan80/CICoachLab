"""!
Created on Tue Jan 21 22:23:43 2020

@author: Daniel Leander
"""


import os
import importlib.util
from time import asctime
from PyQt5 import QtCore
import soundfile as sf
import re
# TODO: channel wise rms amplitude correction?

def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class preVocoder():
    def __init__(self, parHandle=None, settings = 'default'):
        """!
        Initializing the CICoachLab vocoder.  vocoder.py will be used to calculate the vocoder signal in self.run().
        The default settings will be set or the provided settings will be loaded.
        The format of the audio signal is:
        signal['audio']
        signal['fs']
        optional:
        signal['name']
        
        The vocoder implements different types of vocoders:
        The envelopes of the vocoded can be sampled with bandpassed noise ('noise') sinusoids with ('sinus') or pulse train ('pulsetrain') with a frequencies corresponding to the center frequencies of the bandpassed filter. 
        The noise and the pulse train are bandpass filtered according to the represented frequency range.
        
        The last type of vocoder ('finestructure') can represent the envelope and temporal fine structure 
        (see also: https://en.wikipedia.org/wiki/Temporal_envelope_and_fine_structure) in each frequency band of the vocoder.
        The envelope of the frequency band is determined as in the other vocoder types. The additional signal dependent temporal fine structure is determined ) by every other zero crossing from the band pass filtered signal.
        Not every frequency band of the vocoder has to implement this temporal finestructure. In the finestructure type the none finestrucuture channels will be vocoded as noise-vocoded bandpass singla. The  The number of channels which are encoded using this temporal fine structure can be defined. The default value of the vocoder type defaults to stimSignalType   = 'noise'.
    
        The vocoded signal is calculated by splitting the input signal into a specified number of bandpass signal. The used bandpass filter is a butterworth filter. 
        The bandpass filters are distributed evenly according along thenp.logspace() between the settings 'fmin' and 'fmax'.
        Of each bandpass filter the envelope is calculated with a moving average filter. Its characteristic is described as a lowpass filter which is defined by its cut off frequency ('movAvCF').
        
        If signalIn is provided the vocoded signal can be buffered by preVocoder for a quicker reload
        later. The signal can be buffered  by the exercise by calling 
        signalOut = self.parHandle.curPlayer['functions']['applyPreprocessor'](signal) and saving the variable in any variable
        or as as precalculated wav-file which is stored with the the extension. woc. The woc files are stored and reloaded by the preprocessor.
        
        
        The settings and default values are:
        stimSignalType ('noise':)
        # type of vocoder. Possible values types are: noise, signal, pulsetrain, finestructure
        
        filterOrder (2):
        # Order of the butterworth filter which calculates the bandpass signals
        
        fmin (70):
        # lower cutofffrequency of the lowest bandpass filter
        
        fmax (10000):
        # upper cutofffrequency of the highest bandpass filter
        
        movAvCF (300):
        # cuftoff frequency of the lowpass, moving average filter which calculates the envelopes of the bandpass signals
        
        amplitudeChScaling ('max'):
        # the amplitudes of the vocoded bandpass filters signals are matched to the bandpass signals of input by matching its maximum or rms values.
        
        numberOfChannels (12):
        # numbe of bandpass channels
        
        finestructureChannels ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        # number of channels using the temporal fine structure if stimSignalType is set to 'finestructure'
        
        lowNoiseNoise (False):
        # If stimSignalType is set to 'noise' this settings tries to reduce the amplitude fluctuations wihtin the noise signal. The ranodom character of the noise is maintained by 
        # introducing a higher variability wthin the frequency spectrum.
        # This is a beta version and has not been tested throuroughly, yet.
        
        lowNoiseNoiseReps (10):
        # number of iterations to reduce the amplitude fluctuations
        
        useBuffer (False):
        # the processor may buffer the vocoded signal. A possible Drawback: The random character of the vocoded signal is reduced across repetitions until the next (re)start of the preprocessor.
        # Handle wih care especially in case of short presentations.
        
        useFileBuffering (False):
        # the processor may buffer the vocoded signal in a file. A possible Drawback: The random character of the vocoded signal is reduced to none across repetitions. Even a restart (re)start of the preprocessor does not
        # introduce different fluctuations. Handle wih care especially in case of short presentations.
        
        For more information on the settings like the range of the possible parameters take a look at the settingLimits in  function setDefaultSettings(self)
        
        
        
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

        if parHandle == None:
            print('preVocoder: cannot initialize without framework.')
        self.parHandle   = parHandle     

        self.parHandle.dPrint('preVocoder: __init__()', 2)
        
        if settings != 'default':
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.setDefaultSettings()
            self.loadSettings(settings)
        else:
            self.setDefaultSettings()

        self.parHandle.addingPath('curPreprocessor')

        self.parHandle.curPreprocessor['functions']['constructor']      = self.__init__
        self.parHandle.curPreprocessor['functions']['destructor']       = self.__del__
        self.parHandle.curPreprocessor['functions']['run']              = self.run
        self.parHandle.curPreprocessor['functions']['settingsLoading']  = self.loadSettings
        self.parHandle.curPreprocessor['functions']['settingsDefault']  = self.setDefaultSettings
        self.parHandle.curPreprocessor['functions']['settingsGui']      = None

        self.parHandle.dPrint('preVocoder: Leaving __init__()', 2)

        # load the vocoder module from the preprocessor path.
        modulePath = os.path.join(self.parHandle.curPreprocessor['path']['base'], "vocoder.py")
        spec = importlib.util.spec_from_file_location("vocoder.py", modulePath)
        vocoder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vocoder)

        self.vocoder = vocoder.vocoder

        self.finishedBufferfileImport = False

        self.parHandle.curPreprocessor['buffer'] = dict()

    def __del__(self):
        """!
        The destructor of the class will delete the menu of the preprocessor. The parameters of curPreprocessor  will be
        reset.
        """

        self.parHandle.dPrint('preVocoder: __del__()', 2)
        self.parHandle.clearSettingsInMenu('curPreprocessor')
        self.parHandle.closePath('curPreprocessor')
        
        self.parHandle.initializeToDefaults(mode='curPreprocessor')
        
        self.parHandle.dPrint('preVocoder: Leaving __del__()', 2)
    
    def setDefaultSettings(self):
        """!
        The default parameters of the vocoder will be set.
        """

        self.parHandle.dPrint('preVocoder: setDefaultSettings()', 2)

        self.parHandle.initializeToDefaults(mode='curPreprocessorSettings')
        preprocessorBase = self.parHandle.frameWork['path']['preprocessors']
        preprocessorName                                                     = 'preVocoder'
        self.parHandle.curPreprocessor['settings']['preprocessorName']            = preprocessorName
        self.parHandle.curPreprocessor['path']                   = dict()
        self.parHandle.curPreprocessor['path']['base']           = os.path.join(preprocessorBase, preprocessorName)
        self.parHandle.curPreprocessor['path']['presets']        = os.path.join(self.parHandle.curPreprocessor['path']['base'], 'presets')
        self.parHandle.curPreprocessor['path']['scripts']        = os.path.join(self.parHandle.curPreprocessor['path']['base'],
                                                                         'scripts')

        self.parHandle.curPreprocessor['settings']['settingsName']   = 'default'
        self.parHandle.curPreprocessor['settings']['comment']        = 'No comment'

        # for a description of the settings see description in __init__
        self.parHandle.curPreprocessor['settings']['filterOrder']    = 2
        self.parHandle.curPreprocessor['settings']['fmin']               = 70
        self.parHandle.curPreprocessor['settings']['fmax']               = 10000
        self.parHandle.curPreprocessor['settings']['movAvCF']            = 300 # 100
        self.parHandle.curPreprocessor['settings']['amplitudeChScaling'] = 'max' #'rms',max
        self.parHandle.curPreprocessor['settings']['numberOfChannels']   = 12
        self.parHandle.curPreprocessor['settings']['stimSignalType']     = 'noise'
        self.parHandle.curPreprocessor['settings']['finestructureChannels']  = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.parHandle.curPreprocessor['settings']['useBuffer']              = True
        self.parHandle.curPreprocessor['settings']['useFileBuffering']       = True
        # reduce amplitude fluctuations within the noise
        self.parHandle.curPreprocessor['settings']['lowNoiseNoise']          = False
        # number of filter iterations used for the reduction of amplitude fluctuations
        self.parHandle.curPreprocessor['settings']['lowNoiseNoiseReps']      = 10

        self.parHandle.curPreprocessor['settingLimits'] = dict()
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName']['mandatory'] = True
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName']['range'] = []
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName']['default'] = 'preVocoder'
        self.parHandle.curPreprocessor['settingLimits']['preprocessorName']['editable'] = False

        self.parHandle.curPreprocessor['settingLimits']['settingsName'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['settingsName']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['settingsName']['mandatory'] = True
        self.parHandle.curPreprocessor['settingLimits']['settingsName']['range'] = []
        self.parHandle.curPreprocessor['settingLimits']['settingsName']['default'] = None
        self.parHandle.curPreprocessor['settingLimits']['settingsName']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['comment'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['comment']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['comment']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['comment']['range'] = []
        self.parHandle.curPreprocessor['settingLimits']['comment']['default'] = ''
        self.parHandle.curPreprocessor['settingLimits']['comment']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['filterOrder'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['filterOrder']['type'] = 'int'
        self.parHandle.curPreprocessor['settingLimits']['filterOrder']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['filterOrder']['range'] = [2, 128]
        self.parHandle.curPreprocessor['settingLimits']['filterOrder']['default'] = 2
        self.parHandle.curPreprocessor['settingLimits']['filterOrder']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['fmin'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['fmin']['type'] = 'float'
        self.parHandle.curPreprocessor['settingLimits']['fmin']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['fmin']['range'] = [0, 10000]
        self.parHandle.curPreprocessor['settingLimits']['fmin']['default'] = 70
        self.parHandle.curPreprocessor['settingLimits']['fmin']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['fmax'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['fmax']['type'] = 'float'
        self.parHandle.curPreprocessor['settingLimits']['fmax']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['fmax']['range'] = [0, 98000]
        self.parHandle.curPreprocessor['settingLimits']['fmax']['default'] = 10000
        self.parHandle.curPreprocessor['settingLimits']['fmax']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['movAvCF'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['movAvCF']['type'] = 'float'
        self.parHandle.curPreprocessor['settingLimits']['movAvCF']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['movAvCF']['range'] = [10, 98000]
        self.parHandle.curPreprocessor['settingLimits']['movAvCF']['default'] = 100
        self.parHandle.curPreprocessor['settingLimits']['movAvCF']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['range'] = ['max', 'rms']
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['default'] = 'max'
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['comboBoxStyle'] = True
        self.parHandle.curPreprocessor['settingLimits']['amplitudeChScaling']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels']['type'] = 'int'
        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels']['range'] = [1, 10000]
        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels']['default'] = 12
        self.parHandle.curPreprocessor['settingLimits']['numberOfChannels']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['stimSignalType'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['range'] = ['noise', 'sinus', 'pulsetrain', 'finestructure']
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['default'] = 'noise'
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['comboBoxStyle'] = True
        self.parHandle.curPreprocessor['settingLimits']['stimSignalType']['editable'] = True

        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['type'] = 'int'
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['range'] = [0, 1]
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['default'] = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['editable'] = True
        self.parHandle.curPreprocessor['settingLimits']['finestructureChannels']['displayed'] = False

        self.parHandle.curPreprocessor['settingLimits']['useBuffer'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['type'] = 'bool'
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['range'] = [True, False]
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['comboBoxStyle'] = True
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['default'] = False
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['editable'] = True
        self.parHandle.curPreprocessor['settingLimits']['useBuffer']['displayed'] = True
        
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['type'] = 'bool'
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['range'] = [True, False]
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['comboBoxStyle'] = True
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['default'] = False
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['editable'] = True
        self.parHandle.curPreprocessor['settingLimits']['useFileBuffering']['displayed'] = True


        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['type'] = 'bool'
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['range'] = [True, False]
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['default'] = False
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['comboBoxStyle'] = True
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['editable'] = True
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoise']['displayed'] = True

        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['type'] = 'int'
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['mandatory'] = False
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['range'] = [1, 32]
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['default'] = 2
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['editable'] = True
        self.parHandle.curPreprocessor['settingLimits']['lowNoiseNoiseReps']['displayed'] = True

        self.parHandle.dPrint('preVocoder: Leaving setDefaultSettings()', 2)

    def loadSettings(self, settings = 'default'):
        """!
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current preprocessor.
        """
        self.parHandle.dPrint('preVocoder: loadSettings()', 2)
        try:
            self.parHandle.loadSettings(settings, module='curPreprocessor')
        except:

            self.setDefaultSettings()
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            self.parHandle.dPrint('Could not load settings (' + settingsName + ') loading default settings instead', 1)
        self.parHandle.dPrint('preVocoder: Quit loadSettings()', 2)

    def run(self, signalIn):
        """!
        This functions provides the vocoded signal of signalIn.
        If the vocoded signal has been calculated before and if self.parHandle.curPreprocessor['settings']['useBuffer'] is set
        to true the buffered signal is used. A signal can buffered only if the sigal provides a ifentifiying name
        (eg. an identifying filename) which effectively distinguishes incoming signals.
        self.clearBuffer can be used to reset the buffer. In doubt, don't use the buffer.
        """
        self.parHandle.dPrint('preVocoder: run()', 2)
        #self.parHandle.curPreprocessor['buffer'] = dict()

        if self.parHandle.curPreprocessor['settings']['useBuffer'] and 'name' in signalIn\
                and signalIn['name'] in list(self.parHandle.curPreprocessor['buffer']):
            signalOut = self.parHandle.curPreprocessor['buffer'][signalIn['name']]
        else:
            if self.parHandle.curPreprocessor['settings']['useFileBuffering']:
                replaceExtensions = '.woc'
                if '.wav' in signalIn['file']:
                    vocFilename = re.sub('.wav', replaceExtensions, signalIn['file'])
                elif '.WAV' in signalIn['file']:
                    vocFilename = re.sub('.WAV', replaceExtensions, signalIn['file'])
                elif '.mp3' in signalIn['file']:
                    vocFilename = re.sub('.mp3', replaceExtensions, signalIn['file'])
                elif '.MP3' in signalIn['file']:
                    vocFilename = re.sub('.MP3', replaceExtensions, signalIn['file'])
                else:
                    vocFilename = signalIn['file']+replaceExtensions

                if os.path.isfile(vocFilename):
                    try:
                        self.parHandle.showInformation(_translate("preVocoder", 'vocoder signal is read ...', None)
                                                       + vocFilename)
                        signalOut = dict()
                        signalOut['audio'], signalOut['fs'] = sf.read(vocFilename)
                        self.parHandle.showInformation('')
                        self.finishedBufferfileImport = True
                    except:
                        self.parHandle.dPrint('playsignal: could not read preprocessor file' + vocFilename, 1)
                        self.finishedBufferfileImport = False
                else:
                    self.finishedBufferfileImport = False
            if not(self.parHandle.curPreprocessor['settings']['useFileBuffering']) or \
                    self.finishedBufferfileImport == False:
                signalOut = self.vocoder(signalIn, self.parHandle.curPreprocessor['settings'])
                if self.parHandle.curPreprocessor['settings']['useFileBuffering']:
                    sf.write(vocFilename, signalOut['audio'], signalOut['fs'], subtype='PCM_24', format='WAV')
            if not('name' in signalOut):
                name = signalIn['name'] + '_preProc_' +asctime()
                signalOut['name'] = name
            self.parHandle.curPreprocessor['buffer'][signalOut['name']] = signalOut

        self.parHandle.dPrint('preVocoder: Quit run()', 2)
        return signalOut

    def clearBuffer(self):
        """:
        This function clears the buffered vocoded signal.
        """
        self.parHandle.dPrint('preVocoder: clearBuffer()', 2)

        self.parHandle.curPreprocessor['buffer'] = dict()

        self.parHandle.dPrint('preVocoder: Quit clearBuffer()', 2)
