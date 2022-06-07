def defineSettings(parHandle):
    """!

    Please check if the player, preprocessor and the generator with respective settings are available on the PC.
    Not all settings have to be set, but it is recomended to have all variables set in one file.
    The previously loaded default settings remain untouched for undefined variables.
    """

    parHandle.curExercise['settings']['settingsName']       = 'studyInstruction.py'
    parHandle.curExercise['settings']['player']             = ''
    parHandle.curExercise['settings']['playerSettings']     = ''
    parHandle.curExercise['settings']['generator']          = ''
    parHandle.curExercise['settings']['generatorSettings']  = ''
    parHandle.curExercise['settings']['preprocessor']            = ''
    parHandle.curExercise['settings']['preprocessorSettings']    = ''
    
    parHandle.curExercise['settings']['prerunCondition']    = ''
    parHandle.curExercise['settings']['postrunCondition']   = ''

    parHandle.curExercise['settings']['comment'] = 'This is a template setting'

    #excercise specific settings

    questItems = []

    item = dict()
    item['information'] = '''This is some informational text which can be provided before the question.
    
    The question will be asked later on.
    '''
    item['question'] = ''
    item['group'] = 1
    questItems.append(item)

    item = dict()
    item['information'] = 'Study agreement'
    item['question'] = 'Do you agree to participate in this study? '  # some string/question
    item['type'] = 'singleChoice'
    item['addSingleComment'] = True  # for all types but text
    item['orientation'] = 'Horizontal'  # for scaling only
    item['noOfPoints'] = 2
    item['allowOther'] = False
    item['labels'] = ['Yes','No']
    item['group'] = 2
    item['requested'] = True
    questItems.append(item)

    item = dict()
    item['information'] = 'Data security'
    item['question'] = 'Did you check read the data security protection contract?'  # some string/question
    item['type'] = 'singleChoice'
    item['addSingleComment'] = True  # for all types but text
    item['orientation'] = 'Horizontal'  # for scaling only
    item['noOfPoints'] = 2
    item['allowOther'] = False
    item['labels'] = ['Yes','No']
    item['group'] = 3
    item['requested'] = True
    questItems.append(item)
    
    item = dict()
    item['information'] = ''
    item['question'] = 'Do you agree to the usage of you private data?'  # some string/question
    item['type'] = 'singleChoice'
    item['addSingleComment'] = True  # for all types but text
    item['orientation'] = 'Horizontal'  # for scaling only
    item['noOfPoints'] = 2
    item['allowOther'] = False
    item['labels'] = ['Yes','No']
    item['group'] = 3
    item['requested'] = True
    questItems.append(item)

    parHandle.curExercise['settings']['items'] = questItems

