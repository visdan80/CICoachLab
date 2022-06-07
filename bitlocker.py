"""!
In the bitlocker mode usb memory sticks can be encrypted with a set password. The password can be implemented in a
precompiled python script under windows or a shell script whose access rights are restricted.

This provides just a minimum amount of security which prevents the read out of patient data on a lost usb memory stick.
The single predefined password is less secure to using a pgp key authentification with or without password.
The pgp security may be implemented in future versions of CICoachlab if it should be required.

The implementation in Linux is less secure than the windows because the linux version does no support encryption keys yet.

Windows:
    1. You have to use windows 10 to use bitlocker.
    2. Set the correct path to the encryption key in keyPath whithin this script.
    3. if you don't want the CICoachLab user to access the usb memory stick which may be used for the storing of the
    patients data (and which may contain other CICoachLab relevant and protected data as well) precompile this function
    and remove his python script from the CICoachLab user pc.
Linux:
    1. check if the correct mounting paths are provided in ciCoachLab.ini and in the operating system.
    2. adjust password in unlockCICoachStick.sh and  move scripts from directory lib/ to /usr/bin
        sudo cp unlockCICoachStick.sh /usr/bin/
        sudo cp lockCICoachStick.sh /usr/bin/

        # secure it from copying and editing and reading access for other users than the
        sudo chmod 700  /usr/bin/unlockCICoachStick.sh
        sudo chmod 700  /usr/bin/lockCICoachStick.sh

    3. compile this python script and remove it
    4. sudo visudo, add full path of unlockCICoachStick.sh and lockCICoachStick.sh to sudoers file,

    So far, the CICoachLab user may access the information about the called scripts unlockCICoachStick.sh on a linux
    system by monitoring the called processes. This may allow the user to call the script and try out to find the
     correct input parameters to unlock the device. Even smarter can download CICoachLab and look at this documentation
     to provide unlockCICoachStick.sh the required input parameters which is defined in CICoachLab.ini.

     The linux implementation should be used as insecure prove of concept, only.


"""

import subprocess
from time import sleep


def checkingUnlockedState(systemName, device, bitlockerPathClear):
    """!
    This function tries to access the device on windows systems or the unlocked mount point under, bitlockerPathClear
    on linux machines. If the access succeeds the function returns True and False otherwise.
    """

    if systemName == 'Linux':
        cmd = 'touch ' + bitlockerPathClear + '/checkingUnlockedState.txt'
    elif systemName == 'Windows':
        cmd = 'dir ' + device
    # if the unlocking failed, the locked path might be unlocked already, checking this!
    statusUnlocked = subprocess.Popen(cmd, shell=True).wait()
    if not(statusUnlocked):
        return True
    else:
        return False


def unlockBitlocker(systemName, device, bitlockerPathClear, bitlockerPathEncrypt):
    """!
    This function unlocks the defined bitlocked device.
    """

    if systemName == 'Linux':
        scriptPath = '/usr/bin/'
        cmd = 'sudo ' + scriptPath + 'unlockCICoachStick.sh ' + device + ' ' + bitlockerPathEncrypt + ' ' + bitlockerPathClear
    elif systemName == 'Windows':
        # change path according to local setup with the aproriate key
        keyPath = 'U:\\transfer\\2DE5EADD-5C63-4DBB-9359-249CC25396AD.BEK'
        cmd = 'manage-bde -unlock  '+ device + ' -RecoveryKey ' + keyPath
    else:
        raise RuntimeError("systemName '{}' did not match Linux or Windows!".format(systemName))
        return False

    try:
        status = subprocess.Popen(cmd, shell=True).wait()
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return the error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return False

    # self.dPrint('Leaving unlockBitlocker()', 2)
    if status:
        # non zero exit status means the unlocking failedfailed run of script
        # check if the device has been unlocked already.
        return checkingUnlockedState(systemName, device, bitlockerPathClear)
    else:
        # zero exit status means successfull run of script
        return True


def lockBitlocker(systemName, device, bitlockerPathClear, bitlockerPathEncrypt):
    """!
    This function locks the defined bitlocked device.
    """


    if systemName == 'Linux':
        scriptPath = '/usr/bin/'
        cmd = 'sudo ' + scriptPath + 'lockCICoachStick.sh ' + bitlockerPathEncrypt + ' ' + bitlockerPathClear
    elif systemName == 'Windows':
        cmd = 'manage-bde -lock ' + device
    else:
        raise RuntimeError("systemName '{}' did not match Linux or Windows!".format(systemName))
        return False
    try:
        maxCounter = 0
        status = 1
        while status:
            # status: 0 unlock successful,
            # 1 unlocking bitlocker clear mount failed
            # 2 unlocking bitlocker encrypt mount failed
            # 3 unlocking bitlocker clear and encrypted mount failed
            # 0 unlocking bitlocker: nothing failed
            status = subprocess.Popen(cmd, shell=True).wait()
            # check if unmount succeeded
            if status:
                sleep(5)
                maxCounter = maxCounter + 1
                if maxCounter > 5:
                    status = 0

    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return the error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return False

    if status:
        return False
    else:
        return True

