def defineSettings(parHandle):
    """
    Settings of the template exercise. The variable parHandle.curExercise['settings'].

    Please check if the player, preprocessor and the generator with respective settings are available on the PC.
    Not all settings have to be set, but it is recomended to have all variables set in one file.
    The previously loaded default settings remain untouched for undefined variables.
    """

    parHandle.curExercise['settings']['comment'] = 'This is a template setting'
    parHandle.curExercise['settings']['settingsName']       = 'Ermüdung.py'

    parHandle.curExercise['settings']['Question'] = 'Wie anstrengend fanden Sie die Übung?'
    parHandle.curExercise['settings']['noAnswer'] = 'Unhörbar'
    parHandle.curExercise['settings']['items'] = dict()
    # if the first item is not empty a separat item is provided on top
    parHandle.curExercise['settings']['items']['values'] = [
                                                                 'Extrem anstrengend',
                                                                 '...',
                                                                 'sehr anstrengend',
                                                                 '...',
                                                                 'deutlich anstrengend',
                                                                 '...',
                                                                 'mittelgradig anstrengend',
                                                                 '...',
                                                                 'wenig anstrengend',
                                                                 '...',
                                                                 'sehr wenig anstrengend',
                                                                 '...',
                                                                 'nicht anstrengend']
    parHandle.curExercise['settings']['items']['widthMax'] = 65
    parHandle.curExercise['settings']['items']['widthMin'] = 20