def defineSettings(parHandle):
    """
    Settings of the template exercise. The variable parHandle.curExercise['settings'].

    Please check if the player, preprocessor and the generator with respective settings are available on the PC.
    Not all settings have to be set, but it is recomended to have all variables set in one file.
    The previously loaded default settings remain untouched for undefined variables.
    """

    parHandle.curExercise['settings']['comment'] = 'This is a template setting'
    parHandle.curExercise['settings']['settingsName']       = 'fatigue.py'

    parHandle.curExercise['settings']['Question'] = 'How exhausting was the exercise?'
    parHandle.curExercise['settings']['noAnswer'] = 'Inaudible'
    parHandle.curExercise['settings']['items'] = dict()
    # if the first item is not empty a separat item is provided on top

    parHandle.curExercise['settings']['items']['values'] = [
                                                                 'Extremely exhausting',
                                                                 '...',
                                                                 'Very exhausting',
                                                                 '...',
                                                                 'Notedly exhausting',
                                                                 '...',
                                                                 'Moderately exhausting',
                                                                 '...',
                                                                 'Little exhausting',
                                                                 '...',
                                                                 'Very little exhausting',
                                                                 '...',
                                                                 'Not exhausting']
    parHandle.curExercise['settings']['items']['widthMax'] = 65
    parHandle.curExercise['settings']['items']['widthMin'] = 20