def conditionCheck(CICoachLabHandle):
    '''Example of an function which can be used to check the succes of a run. This function checks if the phoneme
    recognition measured as confusion matrix is successfull in 75% of the answers'''

    import numpy as np
    df = CICoachLabHandle.curRunData['results']['confMat'][0]
    index = df.index
    confMatDiagMean = np.mean(np.array(df[index][index]).diagonal())

    if confMatDiagMean > 0.75:
        return True, "confMatDiagMean > 0.75: " + str(confMatDiagMean)
    else:
        return False, "confMatDiagMean < 0.75"
