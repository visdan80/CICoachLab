# CICoachLab
CICoachLab provides a graphical user interface for the conduction of listening exercises at our facility where Cochlear Implant users attend rehabilitation programms.


The exercises can be used to obtain information about the user, e.g. listening performance and its testing circumstances.  Alternatively,  the exercises may be used to train the listening abilities of the user.  The user should be able to conduct the exercises independently after a  short introduction. 

CICoachLab provides the framework functions like saving and backuping data, the gui framework, the settings dialog.  Preconditions can be defined which have to be fulfilled before a specific excercise or setting can be run. The field of application of CICoachLab depends on the implemented or available exercises, generators, preprocessors and players and their provided settings and is not restricted to the field of listening. 

Please note that the exerises and settings which are provided in the CICoachLab repository  just might be a basic subset of exercises and settings so far. The goal is to add further exercises, generators, preprocessors and player to allow a broader range of applications.


## Installation
To install the CICOachLab-framework download source code in any directory.
Install python with its standard packages and PyQt5.

CICoachlab depends on 
- Python 3.8 or higher but not higher than  but not higher than 3.8.XX
- PyQt5
- Windows 7 or Windows10 if the bitlocker mode is used.

External dependencies:
- ffmpeg
- doxygen
- pip
- awk                     on Linux machines only
- amixer                  on Linux machines only
- find                    on Linux machines only
- bash                    on Linux machines only


Second party python package dependencies:
    For the installation the second party python package enter into the downloaded directory and run
```bash
pip install -r requirements.txt
```

If the application run should fails please check if the installed exercises and module require specific dependencies. For the determination of python dependencies installed by other modules you can use the Menu "Expert Tools">"Finding dependencies" which is enabled in in the expert mode. All imported python packages and documented external dependencies will be extracted 
Pip Packages will be documented seperately if the modules document the installation of pip-modules with 'pip install packageName'.
Non python external dependencies will be found if they are documented in comments with 'dependencies: packageName'.  
The found dependencies will be written to "dependencies.txt"
The file lib/archive/Linux/CITrainerRequirements.txt or lib/archive/Linux/CITrainerRequirements.txt document the installed dependencies as they were used in the development stage.
Please update and commit the file CITrainerRequirements.txt or provide feedback if you find any version of packages which breaks the application.

How to  setup CICOachLab ?
1) rename the template file ciCoachLab.in to ciCoachLab.ini and edit it according to the local setup. Take a look at the template file for further information.
2) optionally rename the template file filter.in to filter.ini and edit it according to the local setup, for an easy start the usage of filter.ini can be ignored. filter.ini can be used to translate the exercise names and to define the exercise user access. The template file provides information about the usage of this file.
3) if you want use the  bitlock mode to provide some data protection of the stored data see bitlocker.py for the usage and setup.
    the bitlocker mode requires windows 10

Run CICOachLab:
With the following command you should be able to start CICoachLab.
```bash
python3 CICoachLab.py
```
    
Now you can write and add your own exercises and modules to the repository. "Share and enjoy" :)

Target Operating Environments:
Linux and windwos are the target operating systems so far. Only few operating system dependent system calls and python code is required to optain the CICoachLab features.
If you want to extend the range of the target operating feel free to adjust and commit the code.


## Getting help
If you wonder how the application works?:
- try it out
- Check the menu help>Documentation.
  Some information about the usage of the framework is provided.
  More information is provided for developers in an extra section. The source code can be browsed using the automatically generated help using doxygen.
  
If you wonder why the application doesn't work?:
- Summary: "Well, there could be lots of reasons"* *primaScan documentation
- check the dependencies
- check the debugFile for some information.
- check the settings of your exercises (e.g. paths, systemPath, )

Up to now the the code is provided as it is and no support or help can be guaranteed. If you find issues or an error in the code please submit the issue.


## Target group
Since no support can be provided and the code is provided as is it might be helpfull for the usage of the code, if you or your administrator knows how to handle the intallation process.
The frameworks will be most interesting for you if you can modify the existing code or write new exercises, generators, preprocessors and player.
With the GPL license no fees are required which might help users which don't have the financial backup for closed source development software

## Development:
If you want to develop your own code check out the Help>Documentation menu, which will generate an up to date documentation of the code usding doxygen.


## Goal of this project:
I hope that this project is helpfull for anyone who likes to implement graphically guided exercises and I would appreciate any contribution which improves and extends the provided code.


## Contribution:
Any contribution is welcome

## License:
CICoachLab is released under the [General Public License v3.0](license/GPLv3_license.txt)

