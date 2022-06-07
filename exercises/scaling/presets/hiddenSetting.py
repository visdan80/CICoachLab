def defineSettings(parHandle):
    """
    This is test setting which is doing nothing after the defaults settings were loaded previously.
    """

    parHandle.curExercise['settings']['comment'] = 'This is a "setting" file which does nothing but to to show this information in the status bar. The default settings were loaded as base setting beforehand.'
    parHandle.curExercise['settings']['settingsName']       = 'hiddenSetting.py'
    
    parHandle.showInformation(parHandle.curExercise['settings']['comment'])

    
