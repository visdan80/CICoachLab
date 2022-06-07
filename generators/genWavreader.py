'''!
The generator reads an audio signal from wav files.


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

import importlib.util
import os, sys
import audio2numpy
import soundfile as sf

class genWavreader():
    def __init__(self, parHandle=None, settings='default'):
        """!
        The constructor of the class, sets the basic default settings, sets the sub directories, sets the calibration if
        required and possible and loads the settings if provided.
        """

        self.parHandle   = parHandle

        if not(self.checkDependencies()):
            self.__exit__()
            return

        self.setDefaultSettings()
        if settings != 'default' and settings != '':
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.loadSettings(settings)

        if self.parHandle == None:
            print('cannot initialize without framework.')

        self.sysname        = self.parHandle.frameWork['settings']['system']['sysname']
        
        self.parHandle.addingPath('curGenerator')

        self.parHandle.curGenerator['functions']['constructor']      = self.__init__
        self.parHandle.curGenerator['functions']['destructor']       = self.__del__
        self.parHandle.curGenerator['functions']['run']              = self.run
        self.parHandle.curGenerator['functions']['settingsLoading']  = self.loadSettings
        self.parHandle.curGenerator['functions']['settingsDefault']  = self.setDefaultSettings
        self.parHandle.curGenerator['functions']['settingsGui']      = None

        self.parHandle.dPrint('Leaving __init__()', 2)

        self.parHandle.setDefaultCalibration('curGenerator', 'level')
        self.parHandle.readIniFile(mode='curGeneratorSettings', module='curGenerator')


    def __exit__(self, exc_type, exc_val, exc_tb):
        """!

        """

    def checkDependencies(self):
        """!
        This function checks if the required ffmpeg dependency is fullfilled. FFMpeg is required by audio2numpy if
        mp3 files are read.
        This function return True if the dependencies are fullfilled and False otherwise.
        """

        try:
            # trying to add ffmpep but it does not suffice
            # sys.path.append(os.path.join(self.parHandle.frameWork['path']['pwd'],'dependencies', 'ffmpeg-master-latest-win64-gpl', 'bin'))
            # trying to load test data
            audio, fs = audio2numpy.audio_from_file(os.path.join(self.parHandle.frameWork['path']['pwd'], 'recources',
                                                 'cicoachlab_sinus.mp3'))
            return True
        except:
            msg = 'Exception: audio2numpy could not load recources cicoachlab_sinus.mp3. \n\n'\
            'Please check the installation of ffmpeg.\n genWavReader module will not be initialized.'
            self.parHandle.dPrint(msg, 0, guiMode=True)
            return False




    def run(self, signalIn):
        """!
        This function reads the audio signal.
        """

        self.parHandle.dPrint('run()', 2)
        if type(signalIn) == type('someString'):
            self.parHandle.dPrint('Audio as filename', 1)
            # this allows a more flexible signal handling in the exercises, which don't have to bother about
            # extensions, which depend on the used generator.
            if not(os.path.isfile(signalIn)) and not('.wav' in signalIn):
                signalIn = signalIn + '.wav' #TODO: make more felxible if other type can be read

            signal               = dict()
            signal['audio']      = None
            signal['fs']         = None

            signal['file']       = signalIn
            signal['name']       = os.path.basename(signalIn)
            
        elif type(signalIn) == type(dict()):
            self.parHandle.dPrint('Audio as dictionary')
            signal = signalIn
        try:
            if '.wav' in signal['file'] or '.WAV' in signal['file']:
                audio, fs = sf.read(signal['file'])
            elif '.mp3' in signal['file']:
                audio, fs = audio2numpy.audio_from_file(signal['file'])
        except:
            self.parHandle.dPrint('Exception:' + signal['file'])
            return
        
        signal['audio']     = audio
        signal['fs']         = fs

        self.parHandle.dPrint('Leaving run()', 2)
        return signal


    def setDefaultSettings(self):
        """!
        The default parameters and settingLimits of the tests will be set.
        Mandatory/default fields are assigned by CICoachLab.py in
        initializeToDefaults() for each exercise, as well als generator, preprocessor and player,
        The default fields are set and extended by the
        repective items provided in this function.
        The settings can be set for single or all fields.
        """

        self.parHandle.dPrint('setDefaultSettings()', 2)

        generatorPathBase = self.parHandle.frameWork['path']['generators']
        generatorName                       = 'genWavreader'

        self.parHandle.initializeToDefaults(mode='curGeneratorSettings')

        self.parHandle.curGenerator['settings']['generatorName']    = generatorName
        self.parHandle.curGenerator['settings']['settingsName']     = 'default'
        self.parHandle.curGenerator['path']['base']     = os.path.join(generatorPathBase, generatorName)
        self.parHandle.curGenerator['path']['presets']  = os.path.join(self.parHandle.curGenerator['path']['base'], 'presets')
        self.parHandle.curGenerator['settings']['comment'] = ''

        self.parHandle.curGenerator['settingLimits'] = dict()
        self.parHandle.curGenerator['settingLimits']['generatorName'] = dict()
        self.parHandle.curGenerator['settingLimits']['generatorName']['type'] = 'string'
        self.parHandle.curGenerator['settingLimits']['generatorName']['mandatory'] = True
        self.parHandle.curGenerator['settingLimits']['generatorName']['range'] = []
        self.parHandle.curGenerator['settingLimits']['generatorName']['editable'] = False

        self.parHandle.curGenerator['settingLimits'] = dict()
        self.parHandle.curGenerator['settingLimits']['settingsName'] = dict()
        self.parHandle.curGenerator['settingLimits']['settingsName']['type'] = 'string'
        self.parHandle.curGenerator['settingLimits']['settingsName']['mandatory'] = True
        self.parHandle.curGenerator['settingLimits']['settingsName']['range'] = []
        self.parHandle.curGenerator['settingLimits']['settingsName']['editable'] = True

        self.parHandle.dPrint('Leaving setDefaultSettings()', 2)


    def loadSettings(self, settings):
        """!
        Loading settings ....
        The settings are searched for in as .set files in the presets path of
        the current exercise.
        """

        self.parHandle.dPrint('genWavreader: loadSettings()', 2)
        try:
            self.parHandle.loadSettings(settings, module='curGenerator')
        except:
            self.setDefaultSettings()
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            self.parHandle.dPrint('Could not load settings ('+settingsName+\
                                  ') loading default settings instead', 1)
            
        self.parHandle.dPrint('Leaving loadSettings()', 2)


    def __del__(self):
        """!
        The destructor of the class will delete the gui of the exercise with
        the function eraseExerciseGui(). The path of the exercise will be unset
        by closePath()
        """

        self.parHandle.dPrint('__del__()', 2)

        self.parHandle.closePath('curGenerator')
        self.parHandle.initializeToDefaults(mode='curGenerator')

        self.parHandle.dPrint('Leaving __del__() ', 2)

