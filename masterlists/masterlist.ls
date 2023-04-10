# This list defines the name of setlists or single runs which which will be run automatically

# The masterist defines a list of setlist which should be run and are defined in the setlist folder.
# The masterlist can be started automatically to run a predefined set of setlist.
# The preconditions and postconditions  define the conditions which have to be met before running a setlist and which have to be met
# after running the setlist to mark a successfull setlist. After a succefull run of a setlist the next setlist can be run if the next
# precondition has been met.
# can be list of string 
# lastItemIDX = -1: no item has been run yet

name = Setlist title
information = This is an example of a setlist
# the index of the last item defines which item will be run at next start, it allows the running of different items across seperated sessions of CITrainer, while CITrainer can be closed between sessions .
# At the begining of a masterlist 'lastItemIDX' is set to -1
lastItemIDX = -1
# list of indices to which the user can jump back if the masterlist crashes or canceled the run
resetIDXs = 


# An item can be a single run exercise or a setlist which are defined by the respective filenames without the file extension '.py'/'.set' or '.lst'
items = setlist1, singleRun1, setlist2
# In case of a single run exercise a setting can be provided by its repective filename with the following line. Default settings will be loaded in case of 'None' or 'default'
settings = None, singleRunSetting1, None
# the runmode can be either setlist or singleRun
runmode = setlist, singleRun, setlist
preconditions = None, None, None
preconditionMessages = '''''','''''',''''''
postconditions = None, None, None
postconditionMessages = '''''','''''',''''''
description = '''One, two and three as a short description.''','''Second description''','''Third description''' 

                
            
        
        
        
        
        
        
