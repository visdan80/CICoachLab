"""!
Created on Tue Jan 21 22:23:43 2020

@author: Daniel Leander
"""


import os
import importlib.util
from time import asctime
# TODO: channel wise rms amplitude correction?


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class preAudioEffects():
    def __init__(self, parHandle=None, settings = 'default'):
        """!
        Initializing the CICoachLab vocoder. The module vocoder.py will be used and initialized here and passed in
        self.vocoder to the calculating function run().
        The default settings will be set or the provided settings will be loaded.
        The format of the audio signal is:
        signal['audio']
        signal['fs']
        optional:
        signal['name']

        """

        if parHandle == None:
            print('preAudioEffects: cannot initilize without framework.')
        self.parHandle   = parHandle     

        self.parHandle.dPrint('preAudioEffects: __init__()', 2)
        
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

        self.parHandle.dPrint('preAudioEffects: Leaving __init__()', 2)
        audioEffects = self.parHandle.curPreprocessor['settings']['audioEffects']
        if isinstance(audioEffects, str):
            audioEffects = [audioEffects]

        self.audioEffect = {}
        for effect in audioEffects:
            # load the vocoder module from the preprocessor path.
            modulePath = os.path.join(self.parHandle.curPreprocessor['path']['effects'], effect + ".py")
            spec = importlib.util.spec_from_file_location(effect + ".py", modulePath)
            fx = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fx)

            self.audioEffect[effect] = getattr(fx,effect)

    def __del__(self):
        """!
        The destructor of the class will delete the menu of the preprocessor. The parameters of curPreprocessor  will be
        reset.
        """

        self.parHandle.dPrint('preAudioEffects: __del__()', 2)
        self.parHandle.clearSettingsInMenu('curPreprocessor')
        self.parHandle.closePath('curPreprocessor')
        
        self.parHandle.initializeToDefaults(mode='curPreprocessor')
        
        self.parHandle.dPrint('preAudioEffects: Leaving __del__()', 2)
    
    def setDefaultSettings(self):
        """!
        The default parameters of the tests will be set.
        """

        self.parHandle.dPrint('preAudioEffects: setDefaultSettings()', 2)

        self.parHandle.initializeToDefaults(mode='curPreprocessorSettings')
        preprocessorBase                                            = self.parHandle.frameWork['path']['preprocessors']
        preprocessorName                                            = 'preAudioEffects'
        self.parHandle.curPreprocessor['settings']['preprocessorName'] = preprocessorName
        self.parHandle.curPreprocessor['path']                   = dict()
        self.parHandle.curPreprocessor['path']['base']           = os.path.join(preprocessorBase, preprocessorName)
        self.parHandle.curPreprocessor['path']['presets']        = \
            os.path.join(self.parHandle.curPreprocessor['path']['base'], 'presets')
        self.parHandle.curPreprocessor['path']['effects']        = \
            os.path.join(self.parHandle.curPreprocessor['path']['base'],'effects')

        self.parHandle.curPreprocessor['settings']['settingsName']   = 'default'
        self.parHandle.curPreprocessor['settings']['audioEffects']   = 'normalizePeak'

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

        self.parHandle.curPreprocessor['settingLimits']['audioEffects'] = self.parHandle.setSettingLimitsTemplate()
        self.parHandle.curPreprocessor['settingLimits']['audioEffects']['type'] = 'string'
        self.parHandle.curPreprocessor['settingLimits']['audioEffects']['mandatory'] = True
        self.parHandle.curPreprocessor['settingLimits']['audioEffects']['range'] = ['normalizePeak', 'normalizeRMS']
        self.parHandle.curPreprocessor['settingLimits']['audioEffects']['default'] = ''
        self.parHandle.curPreprocessor['settingLimits']['audioEffects']['editable'] = True


        self.parHandle.dPrint('preAudioEffects: Leaving setDefaultSettings()', 2)

    def loadSettings(self, settings = 'default'):
        """!
        Loading settings ....
        The settings are searched for in as .py files in the presets path of
        the current preprocessor.
        """
        self.parHandle.dPrint('preAudioEffects: loadSettings()', 2)
        try:
            self.parHandle.loadSettings(settings, module='curPlayer')
        except:

            self.setDefaultSettings()

            if isinstance(settings, str):
                settingsName = settings
            else:
                settingsName = 'settings (dict)'
            self.parHandle.dPrint('Could not load settings (' + settingsName + ') loading default settings instead', 1)
        self.parHandle.dPrint('preAudioEffects: Quit loadSettings()', 2)

    def run(self, signalIn):
        """!
        This functions provides the signal with the applied oudio effects on signalIn.
        """
        self.parHandle.dPrint('preAudioEffects: run()', 2)

        signalOut = signalIn

        if self.audioEffect:

            signal = signalIn
            for effect in self.audioEffect:
                try:
                    self.parHandle.dPrint('preAudioEffects: applying effect: ' + effect, 2)
                    signal = self.audioEffect[effect](signal)
                except:
                    msg = _translate("preAudioEffects", 'preAudioEffects: Could not apply effect: ' + effect)
                    self.parHandle.dPrint(msg, 0, guiMode=True)
            signalOut = signal

            if not('name' in signalOut):
                name = asctime()
                signalOut['name'] = name

            self.parHandle.dPrint('preAudioEffects: Quit run()', 2)

        return signalOut

