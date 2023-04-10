"""
This function averages the results of the selected runs and displays the results.
"""

import copy


def meanOfSelectedRuns(parHandle):
    exerciseName = 'confusionMatrix'
    # get selected runs
    items = list(parHandle.runData[exerciseName])

    if not(parHandle.curExercise['selectedRunData']):
        return

    resultsMerged = copy.deepcopy(parHandle.runData[exerciseName][items[parHandle.curExercise['selectedRunData'][0]]])
    #resultsMerged = parHandle.runData[exerciseName][items[0]]

    selectedItems = []
    ii = 0
    for idx in parHandle.curExercise['selectedRunData']:
        for jj in range(len(parHandle.runData[exerciseName][items[idx]]['results']['confMat'])):
            resultsMerged['results']['confMat'].append(parHandle.runData[exerciseName][items[idx]]['results']['confMat'][jj])
            resultsMerged['results']['reactMat'].append(parHandle.runData[exerciseName][items[idx]]['results']['reactMat'][jj])
            selectedItems.append(items[idx])
            ii = ii + 1

    resultsMerged['time'] = dict()
    resultsMerged['statusMessage'] = 'Average of runs' + str(selectedItems)

    parHandle.curExercise['functions']['displayResults'](resultsMerged)

