#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 09:27:13 2020

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
"""

import scipy as scp
import scipy.signal
import numpy as np
from scipy.signal import hilbert, butter, lfilter, sosfilt

checkClipping = True


def butterLNN(signal, N, freqsCut, fs, filterType='bandpass', analog=True, filterDesign='sos', LNNreps  = 10, nfftHilb = None):
    """!
    This function filters the signal as a butter worth filter and tries to reduce the amplitude.
    TODO: This functionality should be regarded as beta version and should be tested before implementation.
    """
    
    movAvSamps = int(np.round(fs / 100))
    filterCoef = np.ones((movAvSamps,)) / movAvSamps

    if filterDesign == 'sos':
        sos = butter(N, (freqsCut[0] / (fs / 2), freqsCut[1] / (fs / 2)), filterType, output=filterDesign, analog=analog)
    else:
        b, a = butter(N, (freqsCut[0] / (fs / 2), freqsCut[1] / (fs / 2)), filterType, output=filterDesign, analog=analog)

    for ii in range(LNNreps + 1):

        if filterDesign == 'sos':
            signal2 = sosfilt(sos, signal, axis=0)
        else:
            signal2 = lfilter(b, a, signal, axis=0)
        del signal
        signal = signal2
        # don't normalize data in the last iteration
        if ii < LNNreps:
            #env = np.abs(hilbert(signal, nfftHilb, 1))
            env = np.convolve(abs(signal.flatten()), filterCoef, mode='same')
            signal = signal.flatten() / env

    return signal


def vocoder(signalIn, settings):
    """!
    For detailed description of this vocoder implementation see preVocoder.py
    """
    
    
    signalOut = signalIn.copy()
    # get settings
    fs = signalIn['fs'] # sampling frequency
    # initialize memory for output signal
    resultSignal = np.zeros((signalIn['audio'].shape))

    if len(signalIn['audio'].shape) == 1:
        channelNumber = 1
    else:
        channelNumber = signalIn['audio'].shape[1]

    for chIdx in range(channelNumber):
        if channelNumber == 1:
            signal = signalIn['audio']
        else:
            signal = signalIn['audio'][:,chIdx]

        fmin = settings['fmin'] # lower and ..
        fmax = settings['fmax'] # upper frequency limit of filter bands
        numberOfChannels = settings['numberOfChannels'] # number of bandpass filters
        # style of acoustic stimulation of vocoder signal. Another idea for the future
        # is to extract fine structure and degrade it to some extent.
        stimSignalType = settings['stimSignalType']

        # filter order of bandpass filters
        filtN = settings['filterOrder']
        # getting cut off frequencies of filter bands
        #TODO logspace
        movAvCF = settings['movAvCF']
        movAvSamps = int(np.round(fs/movAvCF))

        freqsCut = np.logspace(np.log10(fmin), np.log10(fmax), numberOfChannels+1)
        # time step between two samples
        dt = 1/fs

        lowNoiseNoise = settings['lowNoiseNoise']
        lowNoiseNoiseReps = settings['lowNoiseNoiseReps']
        # make it as loud as it should be

        sigLen = len(signal)

         # initializing the matrix which will contain the instantaneous amplitude of
        # a signal.
        #amps = np.zeros((sigLen, numberOfChannels))
        # getting filter bands
        if  stimSignalType == 'sinus':
            # time vector of signal
            t = np.arange(0, len(signal))*dt

        filterCoef = np.ones((movAvSamps,)) / movAvSamps
        for ii in range(numberOfChannels):
            #getting filter coefficients
            b, a = scipy.signal.butter(filtN, (freqsCut[ii]/(fs/2), freqsCut[ii+1]/(fs/2)), 'bandpass')

            # filtering
            sigFilt = scipy.signal.lfilter(b, a, signal)
            # getting envelope
            #amps[:,ii] =  np.abs(scipy.signal.hilbert(sigFilt))

            amps = np.convolve(abs(sigFilt), filterCoef, mode='same')
            # generate vocoding signal
            if stimSignalType == 'noise' or\
                        (stimSignalType == 'finestructure' and \
                        settings['finestructureChannels'][ii] == False):
                np.random.seed()
                noise = np.random.rand(sigLen, 1)
                if lowNoiseNoise:
                    carrierFilt = butterLNN(noise, filtN, freqsCut, fs, filterType='bandpass', filterDesign='sos',
                                            LNNreps=lowNoiseNoiseReps)
                else:

                    carrierFilt = scipy.signal.lfilter(b, a, noise)

            elif stimSignalType == 'sinus':
                fc = scp.stats.gmean((freqsCut[ii], freqsCut[ii+1]))
                carrierFilt = np.sin(2*scp.pi*fc*t)
            elif stimSignalType == 'pulsetrain':
                fc = scp.stats.gmean((freqsCut[ii], freqsCut[ii+1]))
                carrier = np.zeros((sigLen, 1))
                carrier[ np.int_(np.round(np.arange(1, sigLen, fs/fc)))] = 1
                carrierFilt = scipy.signal.lfilter(b, a, carrier)
            elif stimSignalType == 'finestructure' and \
                settings['finestructureChannels'][ii] == True:

                sigFiltIsNegative = sigFilt < 0
                sigFiltIsNegativeInt  = np.zeros(sigFiltIsNegative.shape)
                sigFiltIsNegativeInt[sigFiltIsNegative == True] = 1
                # indicate all zero crossing by 1 and -1
                zeroX = np.diff(sigFiltIsNegativeInt)
                #just get every other corssing, removing -1 entries
                zeroX[zeroX < 0] = 0
                zeroX = np.concatenate((np.array([0]), zeroX), axis=0)
                carrierFilt = scipy.signal.lfilter(b, a, zeroX)

            else:
                print('unknown option: '+stimSignalType)

            tempSig = carrierFilt.flatten() * amps
            # refilter noise after applying envelope to cut off introduced higher
            # and lower frequencies.
            tempSig = scipy.signal.lfilter(b, a, tempSig)
            if settings['amplitudeChScaling'] == 'rms':
                tempSig = tempSig * np.sqrt(np.mean(sigFilt**2))/np.sqrt(np.mean(tempSig**2))
            elif settings['amplitudeChScaling'] == 'max':
                tempSig = tempSig * np.max(sigFilt)/np.max(tempSig)

            if channelNumber == 1:
                resultSignal[:] = resultSignal[:] + tempSig
            else:
                resultSignal[:, chIdx] = resultSignal[:, chIdx] + tempSig
        if checkClipping:
            if channelNumber == 1:
                ## get the same level as the input signal
                resultSignal[:] = resultSignal[:] * np.sqrt(np.mean(signal ** 2)) / np.sqrt(
                    np.mean(resultSignal[:] ** 2))

                if np.max(np.abs(resultSignal[:])) > 1:
                    print('clipping of played signal!'.format(np.count_nonzero(np.abs(resultSignal[:]) > 1)))
            else:
                ## get the same level as the input signal
                resultSignal[:, chIdx] = resultSignal[:, chIdx] * np.sqrt(np.mean(signal ** 2)) / np.sqrt(
                    np.mean(resultSignal[:, chIdx] ** 2))

                if np.max(np.abs(resultSignal[:, chIdx])) > 1:
                    print('clipping of played signal!'.format(np.count_nonzero(np.abs(resultSignal[:, chIdx]) > 1)))

    signalOut['audio'] = resultSignal
    
    return signalOut

