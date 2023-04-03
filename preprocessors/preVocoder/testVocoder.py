import sys
if True:  # TODO remove needed for import of fhe, or move import after setting apllication of path
    sys.path.insert(0, '/home/daniel/Dokumente/programme/pythonSkripte/projekte/ciTrainer/preprocessors/preVocoder')


import vocoder
#import scipy.signal as signal
import matplotlib.pyplot as plt
#import numpy as np
import sounddevice as sd
import soundfile as sf



settings           = dict()
settings['name']   = 'default'
settings['fs']     = 0
settings['comment']= 'No comment'
settings['filterOrder'] = 2
settings['scaleFac'] = 1

settings['fmin']                = 70
settings['fmax']                = 10000
settings['numberOfChannels']    = 12
settings['movAvCF']             = 4410
settings['amplitudeChScaling']    = 'rms'#'rms',max
# noise, signal, pulsetrain, fineStructure
settings['stimSignalType']      = 'noise'# fineStructure, sinus, pulstrain,noise
#settings['stimSignalType']      = 'noise'# fineStructure, sinus, pulstrain,noise
settings['finestructure']              = dict()
settings['finestructure']['mode']      = True
settings['finestructure']['channels']  = [1,1,1,1, 1, 1, 1, 1, 1, 1, 1, 1]
#settings['finestructure']['channels']  = list(np.int_(np.ones(settings['numberOfChannels'],)))
#settings['finestructure']['channels']  = [1,1,1,1, 1, 1, 1, 0, 0, 0, 0, 0]
#settings['finestructure']['channels']  = [1,1,1,1, 0, 0, 0, 0, 0, 0, 0, 0]
#settings['finestructure']['channels']  = [1,0,1,0, 1, 0, 1, 0, 1, 0, 1, 0]

#%% read, generate and here vocoded wav file
if False:
    filename = '/home/daniel/Dokumente/programme/pythonSkripte/projekte/ciTrainer/preprocessors/preVocoder/under.wav'

    wavSignal, fs = sf.read( filename )
    signal = dict()
    signal['audio'] = wavSignal
    signal['fs'] = fs
    
    signalOut = vocoder.vocoder(signal,settings)
    
    sd.play( signalOut['audio'], signalOut['fs'])
    sd.wait()
    #sd.play( signal['audio'], signal['fs'])



#%% Gettings frequency response
if False:

    movAvSamps = int(np.round(fs/settings['movAvCF']))
    
    b = np.ones((movAvSamps,))/movAvSamps
    a = np.array([1])
    #b, a = signal.butter(4, 100, 'low', analog=True)
    wN=128
    wIn = np.arange(0,wN)/wN*np.pi
    w, h = signal.freqz( b , np.array(a), wIn )
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.axvline(100, color='green') # cutoff frequency
    plt.show()

if False:
    #%%
    wavSignalPart = wavSignal[10000:10600]
    
    sOne = wavSignalPart<0
    sOneInt = np.zeros(sOne.shape)
    sOneInt[sOne==True] = 1 
    zeroX = np.diff(sOneInt)
    zeroX[zeroX<0] = 0 
    zeroX = np.concatenate((np.array([0]),zeroX),axis=0)
    
    plt.plot(wavSignalPart,marker='d',color='blue')
    
    #plt.plot(wavSignalPart<0)
    plt.plot(zeroX)
    #plt.title('Butterworth filter frequency response')
    #plt.xlabel('Frequency [radians / second]')
    #plt.ylabel('Amplitude [dB]')
    #plt.axhline(0, color='green') # cutoff frequency
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.show()    
    
    
if False:
    #%% compare original and vocoded signal
    wavSignalPart = wavSignal[10000:10600]
    
    
    plt.plot(signal['audio'],marker='d',color='black')
    
    plt.plot(signalOut['audio'],marker='s',color='r')

    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.show()    
    
if True:
    #%% generate and compare low noise noise to noise
    filtN       = 2
    freqsCut    = (1000, 4000)
    from scipy.signal import hilbert, chirp, butter, lfilter, hilbert2
    import numpy as np
    
    
    fs = 44100
    sigLen  = 8000
    t = np.arange(sigLen) / fs
    
    signal = chirp(t, 20.0, t[-1], 100.0)
    
    plt.plot(signal,color='black')
    plt.plot(np.abs(hilbert(signal)),color='red')
    #%%
    
    np.random.seed()
    noise = np.random.rand(sigLen,1)
    noise = noise-np.mean(noise)
    noise = noise/np.max(np.abs(noise))
    b, a = butter( filtN, (freqsCut[0]/(fs/2),freqsCut[1]/(fs/2)) ,'bandpass')
    
    signal = lfilter(b, a, noise)

    # %%

    #signal = np.zeros(sigLen)
    #signal[int(np.floor(sigLen/2))] = 1
    envHilb = np.abs(hilbert(signal))

    movAvSamps = 1000
    bo = np.ones((movAvSamps,))/movAvSamps
    envRMS = lfilter(bo, 1, np.abs(signal))
    #plt.plot(noise,color='blue')
    plt.plot(signal,color='green')
    plt.plot(envHilb,color='red')
    plt.plot(envRMS, color='black')
    
    #%%
    signal2 = signal.copy()
    signal2 = signal2/np.max(signal2)
    env = np.abs(hilbert2(signal2))
    plt.plot(signal2,color='black')
    plt.plot(env,color='red')
    

    loops = 1
    for loop in range(loops):
        signal2 = signal2/env
        signal2 = lfilter(b,a,signal2)
        env = np.abs(hilbert2(signal2))
    #plt.plot(signal2, color='red')
    plt.plot(signal2,color='green')
    plt.plot(env,color='blue')
        
        
    
    
    