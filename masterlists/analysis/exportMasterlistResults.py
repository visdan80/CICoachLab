def exporteMastrlistResults(parHandle):
    import os
    from PyQt5 import QtWidgets, QtCore
    import pandas as pd
    """
    This function exports the masterlist run data of the currently loaded masterlsit as defined in CICoachLab.ini and
    provided in self.curMasterlist['name']
      
    The user is asked for a base
    name of the result file or files. The base name is extended by an number according to the selected items.
    If the result files exist another counter is added to the file name until a unique file name is found.
    The user will be informed about the renaming of the  basename of the  result file. 
    The data will be exported into an excel file with the sheets confusion matrix and reaction time. 

    The exported data is extracted from. 
    parHandle.runData[exerciseName][items[item]]['results']['confMat'] and 
    parHandle.runData[exerciseName][items[item]]['results']['reactionTime'] The 

    The dynamically called functions can be updated while CICoachLab is running.
    """

    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)

    #def excelExport(parHandle):
        # define sub function here: otherwise the dynmically called function could not access the out-of-function definition

    # check if masterlist has been finished

    # get items defined in masterlist
    items = parHandle.curMasterlist['settings']['items']
    parHandle.curMasterlist['settings']['items']
    parHandle.curMasterlist['settings']['runmode']
    parHandle.curMasterlist['settings']['lastItemIDX']
    # get runs which have been run in masterlist mode by searching for masterlist name
    runDataExercises = parHandle.runData.keys()
    for exercise in runDataExercises:
        print(parHandle.runData[exercise])
    # get subject id from study

    # check if only one masterlist was run

    # get order of runs run in masterlist mode


    #okPressed = False
    baseName, okPressed = QtWidgets.QInputDialog.getText(parHandle,
                                                         _translate("MainWindow",
                                                                    "Enter base name to save results.", None),
                                                         _translate("MainWindow", "Saving name:", None)
                                                         , QtWidgets.QLineEdit.Normal, "")

    if not (okPressed):
        baseName = 'results'

    exerciseName = parHandle.curExercise['settings']['exerciseName']
    resultsPath = parHandle.curExercise['path']['results']
    items = list(parHandle.runData[exerciseName])

    ic = 0
    for item in parHandle.curExercise['selectedRunData']:
        resultFile = os.path.join(resultsPath, baseName + f"{ic:02d}" + '.xlsx')
        # ensuring that no existing data will be overwritten by CICoachLab.

        if os.path.isfile(resultFile):
            renameFlag = False
            newBaseName = baseName
            newResultFile = resultFile
            nc = 1
            while os.path.isfile(newResultFile):
                newResultFile = os.path.join(resultsPath, newBaseName + f"{ic:02d}" + f"_{nc:02d}" + '.xlsx')
                msg = 'Result file already exists: ' + resultFile + ' renaming to ' + newResultFile
                parHandle.dPrint(msg, 4)
                # print(msg)
                renameFlag = True
                nc = nc + 1
            if renameFlag:
                msg = _translate("MainWindow", 'Result file already existed: ', None) \
                      + resultFile + \
                      _translate("MainWindow", ' renamed to ', None) + newResultFile
                parHandle.dPrint(msg, 0, guiMode=True)
            resultFile = newResultFile


        # TODO:
        # move function to CICoachLab.py
        # before selection of file name ask if the selected data should be exported
        #   one or more runs can be selected for the export
        # if no run is selected as if the masterlsit or setlist data should be exported.
        #   provide selection of date of masterlist/setlist
        # or export all available data?
        #
        # for the excel export each exercise has to provide an excel export function
        #   introduce in confusionMatrix, questionaire, scaling, quiz
        #   the function should return a list of single line dictionary, and
        #       should the occasion arise a none empty dictionary of pandas dataframees
        #       is returned.
        #       The first arguement
        #       should be of the format:
        #       dict or dataseries?
        #       dict('subject': string [study Label of subjcect]
        #           'exercise': string
        #           'date': string
        #           'setting': string
        #           'setlist': string
        #           'masterlist': string
        #           'dataTitle1': string or number representing a data point
        #           'dataTitle2': string or number representing a data point
        #           ...
        #       The second argument should be of the format:
        #       dict('exercise:' list[Dataframe1, Dataframe2....]
        #       list
        #       is returned  as extra data sheet/table.
        # introduce in self.initializeToDefaults()
        #   self.curExercise['functions']['exportResultsToExcel']    = None
        #   introduce menu>File>Export results which points to this function.




        with pd.ExcelWriter(resultFile) as writer:
            parHandle.runData[exerciseName][items[item]]['results']['confMat'][0].to_excel(
                writer, sheet_name='confusion matrix')
            parHandle.runData[exerciseName][items[item]]['results']['reactMat'][0].to_excel(
                writer, sheet_name='reaction time')
        ic = ic + 1
        writer.save()
