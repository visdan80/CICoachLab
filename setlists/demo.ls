# If the same exercise, generator, preProc, or player are used for different 
# settings respectively it is sufficient to  define a single name. Otherwise  
# ensure that the number of items in name and settings are the same within the
# sections.# The entries of preProcs can be empty since the use of preProcs is
# not mandatory. Otherwise enter None, if no preProc should be used, especially 
# if in one instance of settings a preProc should be used and in other 
# instances no preProc is used.
#
# Attention!
# If a preProcessor is defined in the exercise setting the exercise setttings
# overrule the definitions in the set list.
# The same applies for the  generator and player settings.
# In this case you should define those submodules as 'None'.
# For the usage of the default settings define the settings as 'default'
#
# If an exercise item does not end with an accomplished run the setlist will
# stopp after the run and the setlist has to be restarted.
##############################################################################

[exercises]
names = questionaire, quiz, questionaire, scaling
settings = studyInstruction, default, slider, fatigue.py

[generators]
names = genWavreader, genWavreader, genWavreader, genWavreader 
settings = default, default, default, default

[preprocessors]
names = None, None, None, None
settings = default, default, default, default

[player]
names = playQtAudio, playQtAudio, playQtAudio, playQtAudio
settings = default, default, default, default

['description']
short = Inttroduction,  Some exercise, Questionare, Scaling
