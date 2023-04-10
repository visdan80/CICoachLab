import os
import audio2numpy
import soundfile as sf
from PyQt5 import QtWidgets, QtCore
import importlib
import scipy.io.wavfile

"""
This function vocodes wav files which are found in a defined 
"""
from PyQt5 import QtCore

def vocodeDirectory(parHandle):
    # print('Hello World')

    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)
    parHandle.dPrint('vocodeDirectory', 2)

    modulePath = os.path.join(parHandle.frameWork['path']['lib'], 'fhe.py')
    spec = importlib.util.spec_from_file_location('fhe.py', modulePath)
    fhe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fhe)

    title = _translate("preVocoder","Define source directory with audio files", None)
    sourceStartDir = parHandle.frameWork['path']['pwd']
    sourceFiledirectory = QtWidgets.QFileDialog.getExistingDirectory(parHandle,
        title, sourceStartDir)
    title = _translate("preVocoder", "Define directory for vocoded audio", None)
    outputStartdir = sourceFiledirectory
    outputFiledirectory = QtWidgets.QFileDialog.getExistingDirectory(parHandle,
                        title, outputStartdir)

    fileList = fhe.getListOfFiles(sourceFiledirectory, depthOfDir=1, namePart='.wav') +\
        fhe.getListOfFiles(sourceFiledirectory, depthOfDir=1, namePart='.mp3')

    generatorName = parHandle.curGenerator['settings']['generatorName']

    for filename in fileList:
        inputFilename = os.path.join(sourceFiledirectory, filename)
        parHandle.dPrint('processing: ' + inputFilename, 3)
        if generatorName == 'genWavreader':
            signal = parHandle.curGenerator['functions']['run'](inputFilename)
        else:
            signal = dict()
            signal['audio'] = None
            signal['fs'] = None

            signal['file'] = filename
            signal['name'] = os.path.basename(filename)

            if '.wav' in signal['file'] or '.WAV' in signal['file']:
                signal['audio'], signal['fs'] = sf.read(signal['file'])
            elif '.mp3' in signal['file'] or '.MP3' in signal['file']:
                signal['audio'], signal['fs'] = audio2numpy.audio_from_file(signal['file'])

        signal = parHandle.curPreprocessor['functions']['run'](signal)

        # output filename takes
        outputFilename = os.path.join(outputFiledirectory,filename.split('.')[0]+'.wav')
        scipy.io.wavfile.write(outputFilename, signal['fs'], signal['audio'])

        
