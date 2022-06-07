def defineSettings(parHandle):
    """
    This is a questionare setting for a single slider.
    """

    parHandle.curExercise['settings']['settingsName']       = 'slider.py'


    parHandle.curExercise['settings']['comment'] = 'This is a slider setting'

    questItems = []

    item = dict()
    item['information'] = "Fatigue Assessment"  # some string/question
    item['question'] = ''
    item['group'] = 1
    questItems.append(item)

    item = dict()
    item['information'] = ''
    item['question'] = "How much effort is required for you to listen to music?"  # some string/question
    item['type'] = 'slider'
    item['labels'] = ['no effort', 'extreme effort']
    item['orientation'] = 'Horizontal'
    item['group'] = 3
    item['requested'] = True
    questItems.append(item)

    parHandle.curExercise['settings']['items'] = questItems
