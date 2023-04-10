"""!
If this script is defined in the analysis folder of the exercise an menu entry is dynammically produced in the exercise
menu. If the menu entry is chosen the function defined in this script will be called.
The name of the exercise can be any name. A single function should be defined so far.

This is a simple example file which can be implemented. it prints the exercise name to the console.
"""

def analyse(parHandle):
    """!
    This function will be called when menu entry is chosem.
    """
    print('Hello World. The current exercise is ' + parHandle.curExercise['settings']['exerciseName'] +
          '. Not supprising! Is it.')