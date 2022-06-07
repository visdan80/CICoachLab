# separate the entries by colons
# default settings can be defined by by an empty value or 'default'
#
# If the same exercise, generator, preprocessor, or player are used for different
# settings respectively it is sufficient to  define a single name. Otherwise  
# ensure that the number of items in name and settings are the same within the
# sections.# The entries of preprocessors can be empty since the use of preprocessors is
# not mandatory. Otherwise enter None, if no preprocessor should be used, especially
# if in one instance of settings a preprocessor should be used and in other
# instances no preprocessor is used.
#
# Attention!
# If a preprocessor is defined in the exercise setting the exercise setttings
# overrule the definitions in the set list.
# The same applies for the  generator and player settings.
##############################################################################

name = Setlist title
information = This is an example of a setlist


[exercises]
names = presenter, questionaire, confusionMatrix, questionaire, presenter
settings = cleanQtMedia, aSetting, ShortCM, FASorig, vocoder

[generators]
names = genQtAudio, None, genWavreader, None, genWavreader
settings = default, None, default, None, default 

[preprocessors]
names = None, None, None, None, preVocoder
settings = None, default, None, None, default

[player]
names = playQtAudio, None, playAudio, None, playAudio
settings = default, default, playAudio1.py, default, default 

['description']
short = Trainingsphase,  Fragebogen, Verwechslungen, Fragebogen Ende, Abschlussphase
