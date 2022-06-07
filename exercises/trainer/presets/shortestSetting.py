def defineSettings(parHandle):
    """
    Settings of the template exercise. The variable parHandle.curExercise['settings'].

    Please check if the player, preprocessor and the generator with respective settings are available on the PC.
    Not all settings have to be set, but it is recomended to have all variables set in one file.
    The previously loaded default settings remain untouched for undefined variables.
    """

    parHandle.curExercise['settings']['comment'] = 'This is a template trainer-setting where a reasonable minimum of definitions are provided. The rest of the settings is defined by the default settings'
    parHandle.curExercise['settings']['settingsName']       = 'shortestSetting.py'

    parHandle.curExercise['settings']['list'] = []

    item = dict()
    item['wavfile'] = 'cicoachlab_noise.mp3'
    item['solution']= 'CICoachLab noise vocoded version.'
    parHandle.curExercise['settings']['list'].append(item)





