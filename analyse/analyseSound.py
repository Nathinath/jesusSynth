import pyaudio
import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy import signal


def record(filename, time, sampleRate):
    # Variable definition
    statusOp = {}
    frames = []
    t_raw = []
    rawSignal = pd.DataFrame()

    try:
        # Variable initialisation / Get settings
        wavname = filename + ".wav"
        sampleRate = sampleRate
        sampleRate = 44100
        chunk = 1
        channels = 1       
        FORMAT = pyaudio.paFloat32

        # Create PyAudio object + Set ettings        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=channels,
                        rate=sampleRate,
                        input=True,
                        frames_per_buffer=chunk)
    except:
        statusOp['success'] = False
        statusOp['error'] = "Step: record.1 Settings"
        return rawSignal, statusOp
    
    try:
        # Recod during time
        for i in range(0, int(sampleRate / chunk * time)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
    except:
        statusOp['success'] = False
        statusOp['error'] = "Step: record.2 Recording"
        return rawSignal, statusOp

    try:
        frames=np.array(frames)
        frames=np.frombuffer(frames, dtype=np.float32)

        wavfile.write(wavname,sampleRate,frames)
        
        t_raw = np.arange(len(frames))/sampleRate
        rawSignal = pd.DataFrame({'time': t_raw, 'value': frames})
        
        statusOp['success'] = True
        return rawSignal, sampleRate, statusOp

    except:
        statusOp['success'] = False
        statusOp['error'] = "Step: record.3 Format data"
        return rawSignal, sampleRate, statusOp


def get_wav(wavname):
    statusOp = {}
    # Load data from wav file
    sampleRate, frames = wavfile.read(wavname)
    t_raw = np.arange(len(frames))/sampleRate
    rawSignal = pd.DataFrame({'time': t_raw, 'value': frames})
    return rawSignal, sampleRate, statusOp


def preproc(rawSignal, sampleRate, threshold):
    preprocSignal = pd.DataFrame()
    statusOp = {}

    if isinstance(rawSignal, dict):
        pd.DataFrame.from_dict(rawSignal)

    try:
        # Normalise the data
        meanSignal = np.mean(rawSignal['value'])
        rawSignal = rawSignal['value'] - np.mean(meanSignal)
        maxSignal =  np.amax(rawSignal)
        normSignal = rawSignal/maxSignal

        threshold = threshold - np.mean(meanSignal)
        threshold = threshold/maxSignal

    except:
        statusOp['success'] = False
        statusOp['error'] = "Step: preprocess.1 Normalize"
        return preprocSignal, statusOp

    try:
        # Cut the begin of the signal
        begin, _ = signal.find_peaks(normSignal, height = threshold )
        preprocSignal = normSignal[begin[0]:]
        
    #     t_preproc = rawSignal['time'][0:len(rawSignal['time'])-begin[0]]
        proprocTime = np.arange(len(preprocSignal))/sampleRate
    except:
        statusOp['success'] = False
        statusOp['error'] = "Step: preprocess.2 Cut"
        return preprocSignal, statusOp
    
    preprocSignal = pd.DataFrame({'time': proprocTime, 'value': preprocSignal})
    preprocSignal.reset_index(drop=True, inplace=True)
    statusOp['success'] = True
    return preprocSignal, statusOp

