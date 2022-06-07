"""!
The genSin class handles the generation of a sinusod.

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

import importlib.util
import os
from PyQt5 import QtCore
from scipy import sin, pi
from numpy import arange, flipud


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)


class genSin():
    def __init__(self, parHandle=None, settings='default'):
        """!
        Default settings are set and settings loaded if a settings other than 'default' or '' is provided.

        """
        self.parHandle   = parHandle

        self.setDefaultSettings()
        if settings != 'default' and settings != '':
            # the loaded settings just may overwrite parts of the defaultSettings....
            self.loadSettings(settings)

        if self.parHandle == None:
            print('cannot initialize without framework.')

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

    def run(self):
        """!
        generation of sinusoids according to self.parHandle.curGenerator['settings']
        """

        self.parHandle.dPrint('run()', 2)

        signal = dict()
        signal['audio'] = None
        signal['fs'] = None

        f0 = self.parHandle.curGenerator['settings']['f0']
        fs = self.parHandle.curGenerator['settings']['fs']
        level = self.parHandle.curGenerator['settings']['level']
        dur = self.parHandle.curGenerator['settings']['dur']
        phase = self.parHandle.curGenerator['settings']['phase']
        rampTime = self.parHandle.curGenerator['settings']['rampTime']
        phi = phase / 360 * 2 * pi

        T = 1 / fs
        t = arange(0, dur - T, T)

        signal['audio'] = sin(t * 2 * pi * f0 + phi)
        signal['fs']    = fs

        if rampTime > 0:
            # checking length of ramp in reference  to duration
            if rampTime > dur / 2:
                rampTime = dur / 2

            ramp = arange(0, 1, 1/(rampTime/( T )))
            rampLen = len(ramp)
            signal['audio'][0:rampLen] = signal['audio'][0:rampLen] * ramp
            signal['audio'][-rampLen:] = signal['audio'][-rampLen:]*flipud(ramp)

        self.parHandle.dPrint('Leaving run()', 2)
        return signal


    def setDefaultSettings(self):
        """!
        defining default settings and 'settingLimits'
        """

        self.parHandle.dPrint('setDefaultSettings()', 2)

        generatorPathBase = self.parHandle.frameWork['path']['generators']
        generatorName                       = 'genSin'

        self.parHandle.initializeToDefaults(mode='curGeneratorSettings')

        self.parHandle.curGenerator['settings']['generatorName']    = generatorName
        self.parHandle.curGenerator['settings']['settingsName']     = 'default'
        self.parHandle.curGenerator['path']['base']     = os.path.join(generatorPathBase, generatorName)
        self.parHandle.curGenerator['path']['presets']  = os.path.join(self.parHandle.curGenerator['path']['base'], 'presets')
        self.parHandle.curGenerator['settings']['comment'] = ''

        self.parHandle.curGenerator['settings']['f0']           = 440
        self.parHandle.curGenerator['settings']['fs']           = 44100
        self.parHandle.curGenerator['settings']['level']        = 0
        self.parHandle.curGenerator['settings']['dur']          = 0.5
        self.parHandle.curGenerator['settings']['phase']        = 0
        self.parHandle.curGenerator['settings']['rampTime']     = 0.025

        self.parHandle.curGenerator['settingLimits']['generatorName']               = dict()
        self.parHandle.curGenerator['settingLimits']['generatorName']['type']       = 'string'
        self.parHandle.curGenerator['settingLimits']['generatorName']['mandatory']  = True
        self.parHandle.curGenerator['settingLimits']['generatorName']['range']      = []
        self.parHandle.curGenerator['settingLimits']['generatorName']['editable']   = False

        self.parHandle.curGenerator['settingLimits']['settingsName']                = dict()
        self.parHandle.curGenerator['settingLimits']['settingsName']['type']        = 'string'
        self.parHandle.curGenerator['settingLimits']['settingsName']['mandatory']   = True
        self.parHandle.curGenerator['settingLimits']['settingsName']['range']       = []
        self.parHandle.curGenerator['settingLimits']['settingsName']['editable']    = False
        self.parHandle.curGenerator['settingLimits']['settingsName']['default']     = 'default'

        self.parHandle.curGenerator['settingLimits']['f0']              = dict()
        self.parHandle.curGenerator['settingLimits']['f0']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['f0']['mandatory'] = True
        self.parHandle.curGenerator['settingLimits']['f0']['range']     = [0, 22100]
        self.parHandle.curGenerator['settingLimits']['f0']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['f0']['unit']      = 'Hz'
        self.parHandle.curGenerator['settingLimits']['f0']['label']     = _translate('genSin', 'fundamental frequency', None) # Grundfrequenz
        self.parHandle.curGenerator['settingLimits']['f0']['condition']  = \
            "self.parHandle.curGenerator['settings']['f0'] > self.parHandle.curGenerator['settings']['fs']/2"
        self.parHandle.curGenerator['settingLimits']['f0']['default']   = 440

        self.parHandle.curGenerator['settingLimits']['fs']              = dict()
        self.parHandle.curGenerator['settingLimits']['fs']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['fs']['mandatory'] = True
        self.parHandle.curGenerator['settingLimits']['fs']['range']     = [8000, 16000, 32000, 44100, 48000, 96000]
        self.parHandle.curGenerator['settingLimits']['fs']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['fs']['unit']      = 'Hz'
        self.parHandle.curGenerator['settingLimits']['fs']['label']     = _translate('genSin', 'sampling rate', None)
        self.parHandle.curGenerator['settingLimits']['fs']['default']   = 44100

        self.parHandle.curGenerator['settingLimits']['level']              = dict()
        self.parHandle.curGenerator['settingLimits']['level']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['level']['mandatory'] = False
        self.parHandle.curGenerator['settingLimits']['level']['range']     = [0, -90]
        self.parHandle.curGenerator['settingLimits']['level']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['level']['unit']      = 'dB'
        self.parHandle.curGenerator['settingLimits']['level']['label']     = _translate('genSin', 'level', None)  # 'Pegel'
        self.parHandle.curGenerator['settingLimits']['level']['comment']   = \
            _translate('genSin', 'level in relation to sinus with amplitude 1', None)
            # 'Pegel relativ zu Sinus mit Amplitude von 1'
        self.parHandle.curGenerator['settingLimits']['level']['default']   = 0

        self.parHandle.curGenerator['settingLimits']['dur']              = dict()
        self.parHandle.curGenerator['settingLimits']['dur']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['dur']['mandatory'] = False
        self.parHandle.curGenerator['settingLimits']['dur']['range']     = [0, 999]
        self.parHandle.curGenerator['settingLimits']['dur']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['dur']['unit']      = 's'
        self.parHandle.curGenerator['settingLimits']['dur']['label']     = _translate('genSin', 'duration', None)  # 'Stimulationslänge'
        self.parHandle.curGenerator['settingLimits']['dur']['default']   = 0.5

        self.parHandle.curGenerator['settingLimits']['phase']              = dict()
        self.parHandle.curGenerator['settingLimits']['phase']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['phase']['mandatory'] = False
        self.parHandle.curGenerator['settingLimits']['phase']['range']     = [0, 360]
        self.parHandle.curGenerator['settingLimits']['phase']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['phase']['unit']      = '°'
        self.parHandle.curGenerator['settingLimits']['phase']['label']     = _translate('genSin', 'phase', None)
        self.parHandle.curGenerator['settingLimits']['phase']['comment'] = \
            _translate('genSin', 'phase defined in degree [°]', None)
        self.parHandle.curGenerator['settingLimits']['phase']['default']   = 0

        self.parHandle.curGenerator['settingLimits']['rampTime']              = dict()
        self.parHandle.curGenerator['settingLimits']['rampTime']['type']      = 0
        self.parHandle.curGenerator['settingLimits']['rampTime']['mandatory'] = False
        self.parHandle.curGenerator['settingLimits']['rampTime']['range']     = [0, 999]
        self.parHandle.curGenerator['settingLimits']['rampTime']['editable']  = True
        self.parHandle.curGenerator['settingLimits']['rampTime']['unit']      = 's'
        self.parHandle.curGenerator['settingLimits']['rampTime']['label']     = _translate('genSin', 'ramp time', None)  # 'Rampenzeit'
        self.parHandle.curGenerator['settingLimits']['rampTime']['comment']   = \
            _translate('genSin', 'maximum length of ramp time is half of stimulation length', None)
            #'Maximale Länge von der Rampenzeit ist die halbe Stimulationslänge'
        self.parHandle.curGenerator['settingLimits']['rampTime']['default']   = 0.025
        self.parHandle.curGenerator['settingLimits']['rampTime']['condition'] = \
            "self.parHandle.curGenerator['settings']['rampTime'] <= self.parHandle.curGenerator['settings']['dur']/2"

        self.parHandle.curGenerator['settingLimits'] = {}

        self.parHandle.dPrint('Leaving setDefaultSettings()', 2)


    def loadSettings(self, settings):
        """!
        settings are loaded. the optional partial definition of parameters requires the intialization with default
        settings beforehand.
        """

        self.parHandle.dPrint('genSin: loadSettings()', 2)
        try:

            self.parHandle.loadSettings(settings, module='curGenerator')

        except:
            self.setDefaultSettings()
            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            self.parHandle.dPrint('Could not load settings (' + settingsName + ') loading default settings instead', 1)

        self.parHandle.dPrint('genSin: Leaving loadSettings()', 2)


    def __del__(self):
        """!
        reset of generator status to status of
        """
        self.parHandle.dPrint('__del__()', 2)
        self.parHandle.initializeToDefaults(mode='curGenerator')

        self.parHandle.closePath('curGenerator')
        self.parHandle.dPrint('Leaving __del__() ', 2)
