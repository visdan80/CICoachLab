'''

# running script with root privileges
# linux:
# https://kofler.info/sudo-ohne-passwort/
# 1) sudo visudo
# 2) add something like this:
#  ALL ALL=(ALL) NOPASSWD: /home/daniel/Dokumente/programme/pythonSkripte/projekte/ciTrainer/testing/testingPrivileges.sh
# all people can run the script(s) from all hosts
# in future version a user CICoach should be defined which
# 3) copy shell script unlockCICoachStick.sh and unlockCICoachStick.sh to /usr/bin/,
#       check if script is callable, change owner

# run script as user
# create user
# sudo adduser cicoach --no-create-home





Copyright (C) 2019-2022 Daniel Leander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

GPL-3.0-or-later
'''

import sys
import os
from PyQt5 import QtWidgets, QtCore
import importlib

def _translate(context, text, disambig):
    return QtCore.QCoreApplication.translate(context, text, disambig)



def prepareBitlocker(parHandle):
    """!
    This function helps to setup the bitlocker partition.

    1) check if bitlocker partition (e.g. usb-stick is mounted/exists)
    2) create directory mount point for bitlocked encrypted data if necessary
    3) create directory mount point for bitlocked decrypted data if necessary
    4) check if dislocker has been installed


    This script asks for the adminstrator password.

    in case of linux
        The script assumes that the locking and unlocking scripts ly within /usr/bin
    in case
    """
    systemName = parHandle.frameWork['settings']['system']['sysname']  # Linux/Windows
    bitlockerSource = parHandle.frameWork['settings']['bitlockerSource']
    bitlockerPathClear = parHandle.frameWork['settings']['bitlockerPathClear']
    bitlockerPathEncrypt = parHandle.frameWork['settings']['bitlockerPathEncrypt']

    bitlockerStatusSuccess = False
    if systemName == 'Linux':
        scriptPath = '/usr/bin/'

        bitlockerScriptPYC = 'unlockBitlockerLinux.pyc'
        bitlockerScriptPY = 'unlockBitlockerLinux.py'
        bitlockerScriptPYFullPath = os.path.join(scriptPath, bitlockerScriptPY)
        bitlockerScriptPYCFullPath = os.path.join(scriptPath, bitlockerScriptPYC)

        # check if bitlocker partition (e.g. usb-stick is mounted/exists)
        if not (os.path.isfile(bitlockerSource)):
            msg = _translate("MainWindow",
                             'Unlocking USBStick: Could not find bitlocker partition.', None)
            parHandle.dPrint(msg, 0, guiMode=True)
            return bitlockerStatusSuccess


        # create directory mount point for bitlocked encrypted data if necessary
        if not(os.path.ismount(bitlockerPathClear)):
            password, status = QtWidgets.QInputDialog.getText(None,
                _translate("MainWindow", 'Administrator password', None),
                _translate("MainWindow", 'Specify the administrator password.', None),
                QtWidgets.QLineEdit.Password)

            if password and status:
                # check if mounting point
                if not (os.path.isdir(bitlockerPathEncrypt)):
                    if os.system('echo ' + password + '|sudo -S mkdir -p ' + bitlockerPathEncrypt):
                        msg = _translate("MainWindow",
                                    'Unlocking USBStick: Generation of mounting point for encrypted data failed.', None)
                        parHandle.dPrint(msg, 0, guiMode=True)
                        return bitlockerStatusSuccess

        # create directory mount point for bitlocked decrypted data if necessary
        if not (os.path.isdir(bitlockerPathClear)):
            password, status = QtWidgets.QInputDialog.getText(None,
                                                              _translate("MainWindow", 'Administrator password',
                                                                         None),
                                                              _translate("MainWindow",
                                                                         'Specify the administrator password.',
                                                                         None),
                                                              QtWidgets.QLineEdit.Password)

            if password and status:
                if os.system('echo ' + password + '|sudo -S mkdir -p ' + bitlockerPathClear):
                    msg = _translate("MainWindow",
                                'Unlocking USBStick: Generation of mounting point for decrypted data failed.', None)
                    parHandle.dPrint(msg, 0, guiMode=True)
                    return bitlockerStatusSuccess

        # check if dislocker has been installed
        statusDL = os.system('dislocker --help')
        if statusDL:
            password, status = QtWidgets.QInputDialog.getText(None,
                                                              _translate("MainWindow", 'Administrator password',
                                                                         None),
                                                              _translate("MainWindow",
                                                                         'Specify the administrator password.',
                                                                         None),
                                                              QtWidgets.QLineEdit.Password)
            if password and status:
                # implementation of automated installation for debian based linux distributions only
                if os.system('echo ' + password + '| sudo -S apt install dislocker'):
                    msg = _translate("Mainwindow", 'Unlocking USBStick: Installation of bitlocker failed.')
                    parHandle.dPrint(msg, 0, guiMode=True)
                    return bitlockerStatusSuccess

    else:
        scriptPath = '/usr/bin/'
        bitlockerScriptPYC = 'unlockBitlockerWindows.pyc'
        bitlockerScriptPY = 'unlockBitlockerWindows.py'
        bitlockerScriptPYFullPath = os.path.join(scriptPath, bitlockerScriptPY)
        bitlockerScriptPYCFullPath = os.path.join(scriptPath, bitlockerScriptPYC)

        if not (os.path.ismount(bitlockerPathClear)):
            password, status = QtWidgets.QInputDialog.getText(None,
                _translate("MainWindow", 'Administrator password', None),
                _translate("MainWindow", 'Specify the administrator password.', None),
                QtWidgets.QLineEdit.Password)

            #import windows_tools.bitlocker
            #result = windows_tools.bitlocker.get_bitlocker_full_status()
            # Warning bitlocker needs to be run as admin. Running as non administrator will produce the following logs
            #windows_utils.users

            # Doing the same fancy stuff in windows:
            # check if usb stick is mounted
            # check if bitlocker is available.

    '''
    # check if the unlock py-script has to be precompiled and removed. The compiled file is system independent.
    # It will be removed only if the debugMode is set to False.
    import py_compile
    if not (os.path.isfile(os.path.join(scriptPath, bitlockerScriptPYC))):
        try:
            py_compile.compile(bitlockerScriptPYFullPath, cfile=bitlockerScriptPYCFullPath)
        except:
            msg = _translate("Mainwindow", 'Unlocking of USBStick failed. Compilation error.')
            parHandle.dPrint(msg, 0, guiMode=True)
            return bitlockerStatusSuccess
        else:
            try:
                if not (parHandle.frameWork['settings']['debug']['mode']):
                    os.remove(bitlockerScriptPYFullPath)
            except:
                msg = 'Unlocking USBStick: Removement of script failed.'
                parHandle.dPrint(msg, 2)
            else:
                msg = 'Unlocking USBStick: Removement of script succeeded.'
                parHandle.dPrint(msg, 2)


    # The python script 'bitlockerScript' should contain the functions lock and unlock which will be called here to check the 
    
    spec = importlib.util.spec_from_file_location(
        bitlockerScriptPYC, bitlockerScriptPYFullPath)
    bitlockerScript = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bitlockerScript)
    if systemName == 'Linux':
        # loading the pyc file and  unlocking the USB-Memory Stick
        try:
            bitlockerStatusSuccess = bitlockerScript.unlockBitlocker()
            bitlockerStatusSuccess = bitlockerScript.lockBitlocker()
        except:
            msg = 'Unlocking of USBStick failed.'
            parHandle.dPrint(msg, 0, guiMode=True)
    else:
        try:
            bitlockerStatusSuccess = bitlockerScript.unlock()
            bitlockerStatusSuccess = bitlockerScript.lock()
        except:
            msg = 'Unlocking of USBStick failed.'
            parHandle.dPrint(msg, 0, guiMode=True)
    '''
    return bitlockerStatusSuccess
