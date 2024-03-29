import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore


def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)

class exerciseBase():
    '''!
    exerciseBase provides the functionality common to all CICoachLab exericises.

    exerciseBase() provides the functions:
    - __init__
    - __exit__
    - prepareRun
    - startRun
    - runButton
    - quitRun (cancel run without marked accomplishment, if a run is accomplished a set/ or masterlist will continue)
    - finishRun (cancel run with marked accomplishment, if a run is accomplished a set/ or masterlist will continue)
    - eraseExerciseGui
    - iniPath
    - closePath
    - loadSettings
    - setDefaultSettings
    
    If you document pip-dependdencies in the comments like "pip install XYZ" the CICoachLab Framework can search for these dependencies by runnning the 
    menu Exper Tools>Finding dependencies. This may help if the gui is not running because of missing dependencies.

    How to use the exercise base?
    Inherit exerciseBase to a new exercise function:
    class newExercise(exerciseBase):
        ...

    exerciseBase defines the required and common functions of newExercise. Do as follows:

        - __init__():
            - first calling super().__init__(parHandle, settings=settings, exerciseName='newExercise')
            for common initialization
            - add exercise specific entries.
            .
        - __exit__():
            - super().__exit__()
            .
        - self.run():
            - handles the reactions to the user input following the
            .
        - self.setDefaultSettings()
            - first calling super().setDefaultSettings(exerciseName='newExercise')
            - define the exercise specific entries with its corresponding settingLimits
            .
        self.prepareRun()
            - define exercise specific result format in self.parHandle.curRunData['results'].
             Do other stuff if requirer.

        - self.iniGui()
            - initialize the gui elements which handle the user input.
            - add gui elements to self.vBLayout. self.widgets in self.vBLayout will be removed from CICoachLab in
            self.eraseExerciseGui()
            .
        - self.loadSettings()
            - it calls CICoachLab loadSettings function to set the settings
            - if the loadign fails default values will be set.
            - if you want or have to erase the exercise gui elements you have to override the function and start
              self.eraseExerciseGui() manually.
              .
        - self.eraseExerciseGui()
            - remove all widgets found in self.vBLayout.
            .
        - add other optional exercise specific function
            - self.prepareRun() whihćh night
            - self.iniSignals()

    # call self.iniPath(exerciseName)
    '''

    def __init__(self, parHandle=None, settings='', exerciseName='undefined'):
        '''!
        Initialization.
        '''

        print('Initializing ')
        try:
            self.parHandle = parHandle
            self.exerciseName = exerciseName

            msg = 'Entering exercise: ' + exerciseName
            parHandle.statusBar().showMessage(msg)
            self.parHandle.dPrint(msg, 2)

            # this has to be initialized first because the resetting of the handle calls the destructor of the class
            # which resets and clears up everything which has been initialized nicely
            self.parHandle.curExercise['handle'] = self

            # define some exerciseSpecific fields here for temprorary data, if required
            self.data = None

            # setting paths to exercise subfolder like "analysis"  "presets"  "results" (and other folders if the
            # exercise requires data like sound files or other
            #self.setDefaultSettings(exerciseName)
            self.setDefaultSettings()
            self.iniPath()

            # making the exercise function available for the frameWork.
            self.parHandle.curExercise['functions']['prepareRun'] = self.prepareRun

            self.parHandle.curExercise['functions']['settingsLoading'] = self.loadSettings
            self.parHandle.curExercise['functions']['settingsDefault'] = self.setDefaultSettings
            self.parHandle.curExercise['functions']['eraseExerciseGui']  = self.eraseExerciseGui
            self.parHandle.curExercise['functions']['destructor'] = self.__exit__

            self.parHandle.curExercise['functions']['displayResults'] = None
            self.parHandle.curExercise['functions']['settingsGui'] = None
            self.parHandle.curExercise['functions']['checkConditions'] = None
            self.parHandle.curExercise['functions']['calibration'] = None
            self.parHandle.curExercise['functions']['getPlayerStatus'] = None
            self.parHandle.curExercise['functions']['xlsxExport'] = None

            self.parHandle.curExercise['settings']['exerciseName'] = exerciseName

            # loading settings or getting default settings
            if settings != 'default' and settings != '':
                # the loaded settings just may overwrite parts of the defaultSettings....
                self.loadSettings(settings)


            # setting default generator and player and their settings if necessary, since they are mandatory
            if self.parHandle.curPlayer['settings']['playerName'] == '':
                playerName = self.parHandle.curExercise['settings']['player']
                playerSettings = self.parHandle.curExercise['settings']['playerSettings']
                if not(playerName):
                    playerName = 'playQtAudio'
                    playerSettings = 'default'

            self.parHandle.iniSubmodule('player', playerName, playerSettings)
            if self.parHandle.curGenerator['settings']['generatorName'] == '':
                generatorName = self.parHandle.curExercise['settings']['generator']
                generatorSettings = self.parHandle.curExercise['settings']['generatorSettings']
                if not(generatorName):
                    generatorName = 'genWavreader'
                    generatorSettings = 'default'
            self.parHandle.iniSubmodule('generator', generatorName, generatorSettings)
            # setting preprocessor if defined in the loaded settings.
            if self.parHandle.curExercise['settings']['preprocessor'] != '':
                preprocessorName = self.parHandle.curExercise['settings']['preprocessor']
                preprocessorSettings = self.parHandle.curExercise['settings']['preprocessorSettings']
                if preprocessorName:
                    self.parHandle.iniSubmodule('preprocessor',
                                            preprocessorName,
                                            preprocessorSettings)

            # this function sets the default calibration values for the exercise.
            self.parHandle.setDefaultCalibration('curExercise', 'time')

            # the default fundamental layout of the exercise should be
            # this is required by self.eraseExerciseGui()
            self.vBLayout   = None
            self.controlbars = None
            self.runCounter = 0
        except:
            self.parHandle.dPrint('Exception: Entering exercise failed: ' + self.exerciseName, 1)


    def __exit__(self):
        '''!
        Remove path, erase gui, reset function links, initialize exercise setting to default values,
        '''

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): __exit__()', 2)

        self.closePath()

        self.parHandle.curExercise['settings']['exerciseName'] = ''
        self.parHandle.curExercise['functions']['destructor'] = None

        self.eraseExerciseGui()

        self.parHandle.curExercise['settings']['exerciseName']              = ''
        # resetting all function handles by constructing new which deletes all functions independent from the number of
        # linked functions by the derived functions.
        self.parHandle.curExercise['functions'] = dict()
        self.parHandle.curExercise['functions']['settingsLoading']  = None
        self.parHandle.curExercise['functions']['settingsDefault']  = None
        self.parHandle.curExercise['functions']['eraseExerciseGui'] = None
        self.parHandle.curExercise['functions']['destructor']       = None

        self.parHandle.curExercise['functions']['displayResults']   = None
        self.parHandle.curExercise['functions']['settingsGui']      = None
        self.parHandle.curExercise['functions']['checkConditions']  = None
        self.parHandle.curExercise['functions']['calibration']      = None
        self.parHandle.curExercise['functions']['getPlayerStatus']  = None
        self.parHandle.curExercise['functions']['xlsxExport']       = None

        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        self.parHandle.showInformation(_translate("MainWindow","Closed: Exercise", None) )

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving __exit__()', 2)

    def prepareRun(self):
        """!
        This function is called if the exercise is started by the central CICoachLab button: start new exercise.
        A possible way to override this function is to start the exercise automatically without additional input of
        the user. This would take the possibility to get accustomed to the test gui before the test starts.
        """

        if len(self.parHandle.curExercise['gui']['exerWidgets']) == 0:
            self.iniGui()
            # intialize audio, movies or other data if required
            #self.iniAudioImagesMovies()
        for item in self.parHandle.curExercise['gui']['exerWidgets']:
            try:
                item.setDisabled(False)
            except:
                # this catches the exception of layout items which cannot be disabled
                self.parHandle.dPrint('Could not disable exercise gui elements', 2)
        #self.run()


    def startRun(self):
        """!
        This function should be called when the start button is pressed or the run is startetd automatically by .
        """
        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): startRun()', 2)

        self.run()

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving startRun()', 2)


    def runButton(self, temp, forcedInput=''):
        """!
        This function should be called if a user provides input by the gui/a button.
        """
        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving runButton()', 2)

        self.parHandle.measureReactionTime(self.parHandle, mode='stop')
        self.run()
        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving runButton', 2)


    def quitRun(self):
        """!
        This functions finalizes the run of the exercise.
        The data will be saved by calling the framework function self.closeDownRun().
        If this function is called the run will be marked as not accomplished.
        """

        self.parHandle.dPrint('exerciseBase: quitRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()
        self.parHandle.dPrint('exerciseBase: Leaving quitRun()', 2)


    def finishRun(self):
        """!
        This functions finalizes the run of the exercise.
        The data will be saved by calling the framework function self.closeDownRun().
        If this function is called the run will be marked as accomplished.
        """

        self.parHandle.dPrint('exerciseBase: finishRun()', 2)
        self.parHandle.frameWork['functions']['closeDownRun']()
        self.parHandle.dPrint('exerciseBase: Leaving finishRun()', 2)


    def eraseExerciseGui(self):
        '''!
        Remove all gui items/widgets which are found in self.vBLayout.
        '''

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): eraseExerciseGui()', 2)

        print('This function might clean up the exercise gui to allocate free space for the next exercise')
        try:
            if self.vBLayout != None:
                for layOutItem in self.vBLayout.children():
                    for i in reversed(range(layOutItem.count())):
                        # This check is required if an exercises adds sublayouts to self.vBLayout
                        if layOutItem.itemAt(i).widget():
                            layOutItem.itemAt(i).widget().setParent(None)
                # the layout which is assigned to the exercise container widget cannot be deleted it just can be moved to
                # another temporary widget
                QtWidgets.QWidget().setLayout(self.parHandle.ui.exerWidget.layout())

            self.parHandle.curExercise['gui']['exerWidgets'] = list()

            # check if the gui of the exercise used a player with a gui controlbar provided by the player. If yes delete
            # the linked to the removed controlbar.
            if self.parHandle.curPlayer['handle']:
                if hasattr(self.parHandle.curPlayer['handle'], 'controlbarLabel'):
                    if self.parHandle.curPlayer['handle'].controlbarLabel:
                        self.parHandle.curPlayer['handle'].controlbarLabel = ''
            self.parHandle.curExercise['gui']['exerWidgetsDisabled'] = []
        except:
            self.parHandle.dPrint('Could not tidy up gui.', 2)
        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving eraseExerciseGui()', 2)

    '''
    def xlsxExportPreparation(self, data):
        """!
        This function prepares the result for the export to xlsx files and provides a datasSeries .
        The returned status can be 'Valid', 'NoAnswer', 'None', 'Failed', 'Warning'
        """
    '''


    def iniPath(self, exerciseName):
        """!
        The dictionary self.parHandle.curExercise['path'] will be filled
        with the 'base', 'preset', 'results' and the confusionmatrix specific
        'signalFiles' path.
        The path entries of the dictionary will be added at the top of the path
        by sys.path in the frameWork.

        CICoachLab can run scripts in defined in the analysis and or scripts path.
        Scripts which are found in these paths will be added to the modules menu entry.
        """
        self.parHandle.dPrint( 'exerciseBase (' + self.exerciseName + '): iniPath()', 2)

        pwd = os.path.join(self.parHandle.frameWork['path']['exercises'], exerciseName)
        self.parHandle.curExercise['path']['base']      = pwd
        self.parHandle.curExercise['path']['presets']   = os.path.join(pwd, 'presets')
        self.parHandle.curExercise['path']['locales']   = os.path.join(pwd, 'locales')
        self.parHandle.curExercise['path']['results']   = os.path.join(pwd, 'results')
        # self.parHandle.curExercise['path']['analysis']  = os.path.join(pwd, 'analysis')
        # self.parHandle.curExercise['path']['scripts']  = os.path.join(pwd, 'scripts')
        # self.parHandle.curExercise['path']['data']      = os.path.join(pwd, 'data')

        self.parHandle.addingPath('curExercise')

        self.parHandle.dPrint( 'exerciseBase (' + self.exerciseName + '): Leaving iniPath()', 2)


    def closePath(self):
        """!
        The path of the exercise will be removed from sys.path by the frameWork.
        Reset the path dictionary in self.parHandle.curExercise by
        setting entries to empty strings and by removing the exercise specific
        'signal'
        """
        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): closePath()', 2)

        self.parHandle.closePath('curExercise')

        delPathItems = []
        # all items in path will be set to an empty string after the removal from the path.
        for pathItem in self.parHandle.curExercise['path']:
            self.parHandle.curExercise['path'][pathItem] = ''
            if not(pathItem in ['base', 'presets', 'locales', 'results']):
                delPathItems.append(pathItem)
        for delPathItem in delPathItems:
            del self.parHandle.curExercise['path'][delPathItem]

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): closePath()', 2)


    def loadSettings(self, settings='default'):
        """
        Loading settings ....
        The settings are searched for as .py files in the presets path of
        the current exercise.
        """

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): loadSettings()', 2)

        if isinstance(settings, str):
            settingsName = settings
        else:
            settingsName = 'settings (dict)'
            self.setDefaultSettings()
        try:
            if settings == 'default':
                if self.parHandle.curExercise['functions']['eraseExerciseGui']:
                    self.parHandle.curExercise['functions']['eraseExerciseGui']()
                self.parHandle.curExercise['functions']['settingsDefault']()
            else:
                # settings will be loaded, the settings of the defined submodules will be loaded as well
                self.parHandle.loadSettings(settings, module='curExercise')
        except:
            self.parHandle.dPrint('Could not load settings ('+settingsName+') loading default settings instead', 1)
            self.setDefaultSettings()
        self.parHandle.curExercise['settings']['settingsName'] = settingsName

        # check if a generator, preprocessor player can be initialized
        self.parHandle.iniSubmodule('generator',  self.parHandle.curExercise['settings']['generator'],
                                 self.parHandle.curExercise['settings']['generatorSettings'])
        self.parHandle.iniSubmodule('preprocessor',  self.parHandle.curExercise['settings']['preprocessor'],
                                 self.parHandle.curExercise['settings']['preprocessorSettings'])
        self.parHandle.iniSubmodule('player',  self.parHandle.curExercise['settings']['player'],
                                 self.parHandle.curExercise['settings']['playerSettings'])

        self.parHandle.dPrint(self.exerciseName + ': Leaving loadSettings()', 2)


        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving loadSettings()', 2)


    def setDefaultSettings(self, exerciseName):
        """!
        The default parameters of the tests will be set.
        """

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): setDefaultSettings()', 2)

        # The 'settingLimits' will be set in CICoachLab.
        # For a detailed description ot the settingLimits options have a look at
        # self.parHandle.setSettingLimitsTemplate()
        self.parHandle.initializeToDefaults(mode='curExerciseSettings')

        self.parHandle.curExercise['settings']['exerciseName'] = exerciseName
        self.parHandle.curExercise['settings']['settingsName'] = 'default'

        self.parHandle.curExercise['settings']['player']             = 'playQtAudio'
        self.parHandle.curExercise['settings']['playerSettings']     = ''
        self.parHandle.curExercise['settings']['preprocessor']          = ''
        self.parHandle.curExercise['settings']['preprocessorSettings']  = ''
        #self.parHandle.curExercise['settings']['generator']          = 'genWavreader'
        #self.parHandle.curExercise['settings']['generatorSettings']  = ''

        self.parHandle.dPrint('exerciseBase (' + self.exerciseName + '): Leaving setDefaultSettings()', 2)
