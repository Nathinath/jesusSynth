# Import standard functions
import numpy as np
import pandas as pd
from scipy import fftpack
import numbers
import operator

# Helper functions for efficient FFT calculation  
def get_all_fast_len(N):
    # Check input variable
    if not isinstance(N, numbers.Number):
        return False
    
    # Initialize
    x = 0
    fast_lens = []
    
    # Loop over required range
    while x < N:
        x += 1
        fast_lens.append(fftpack.next_fast_len(x))
        x = max(fast_lens)
    fast_lens = np.array(fast_lens)
    return fast_lens

def get_fast_len(N, fast_lens):
        
    # Check input variables
    if not isinstance(fast_lens, np.ndarray):
        fast_lens = np.array(fast_lens)
        
    assert isinstance(N, numbers.Number), 'Length of data (N) should be numeric'
    assert len(fast_lens) > 0, 'Length of list with optimized lengths is empty'
    assert N < max(fast_lens), 'List with all optimized lengths is not suitable for current request'
    
    # Compute index
    i = np.argmin(np.abs(fast_lens - N))
    
    # Make sure the data will be truncated
    if fast_lens[i] > N:
        i -= 1
    
    return fast_lens[i]

def previous_fast_fft_len(N):
    i = 0
    while True:
        res = fftpack.next_fast_len(N-i)
        if res <= N:
            return res
        else:
            i += 1

# Spectral analysis functions
def compute_fft(data, sample_rate):
    # Check input
    if isinstance(data, pd.core.frame.DataFrame):
        data = data['value'].values
        
    assert isinstance(data, np.ndarray), 'Input data is not valid.'
    
    # Compute FFT
    frequency = np.linspace(-sample_rate/2, sample_rate/2, len(data))
    fft_data = fftpack.fft(data)
    
    # Check if Fourier Transform is correct
    try:
        assert (not np.isnan(np.dot(fft_data, fft_data))),  'Data quality issues blocks spectrum calculation'
    except Exception as e:
        print(str(e))
        return
        
    return pd.DataFrame(np.column_stack((frequency, fft_data)), columns=['frequency', 'value'])

def compute_spect_magn(fft_data, N, sample_rate):
    magnitude = (2/N) * np.abs(fft_data[0:N//2])
    magnitude[0] = magnitude[0]/2
    frequency = np.linspace(0, sample_rate/2, N//2)
    return pd.DataFrame(np.column_stack((frequency, magnitude)), columns=['frequency', 'value'])

def compute_spect_angle(fft_data, N, sample_rate):
    angle = np.angle(fft_data[0:N//2])
    frequency = np.linspace(0, sample_rate/2, N//2)
    return pd.DataFrame(np.column_stack((frequency, angle)), columns=['frequency', 'value'])

def compute_ifft(ft_data, optimize_speed = True):
    # Optimize data length for computation speed
    if optimize_speed:
        global all_fast_len
        if 'all_fast_len' in globals():
            ft_data = ft_data[:get_fast_len(len(ft_data))]
        else:
            ft_data = ft_data[:previous_fast_fft_len(len(ft_data))]
    
    # Compute inverse DFT + filter out small residual imaginary part
    res = {
        'time_serie': np.real(fftpack.ifft(ft_data)),
        'fourier_transform': ft_data
    }
    return res









# def envelope_curve_analysis(ft_data, N, frequency, sample_rate, fc_range):
#     # Check arguments
#     if (not isinstance(fc_range, list)) | (len(fc_range) != 2):
#         fc_range = [0, 0.5*sample_rate]
#     elif (fc_range[0] > fc_range[1]):
#         fc_range = [0, 0.5*sample_rate]
        
#     fc_range[1] = np.min([fc_range[1], 0.5*sample_rate])
    
#     # Alternative for Hilbert transform
#     i_fc_range = [np.argmin(np.abs(np.array(frequency) - fc_range[0])), np.argmin(np.abs(np.array(frequency) - fc_range[1]))]
#     ft_data[:i_fc_range[0]] = 0
#     ft_data[i_fc_range[1]:] = 0
#     ft_data[1:] = 2*ft_data[1:]
    
#     # Get envelope curve
#     time_serie_env = np.abs(fftpack.ifft(ft_data))
    
#     # Calculate spectrum
#     res = compute_fft(time_serie_env, sample_rate)
#     t = np.arange(len(time_serie_env))/sample_rate
#     spectrum_env = compute_spect_magn(res['fourier_transform'], len(time_serie_env), res['frequency'])
    
#     return {'envelope_time_serie': pd.DataFrame({'time':t, 'value':res['time_serie']}), 'envelope_spectrum': spectrum_env}












# # Outils pour sélectionner des bouts de spectres et les classer
# def filter_out_freq(ft_data, N, frequency, sample_rate, fc_range = []):
#     # Check arguments
#     if (not isinstance(fc_range, list)) | (len(fc_range) != 2):
#         fc_range = [0, 0.5*sample_rate]
#     elif (fc_range[0] > fc_range[1]):
#         fc_range = [0, 0.5*sample_rate]
        
#     fc_range[1] = np.min([fc_range[1], 0.5*sample_rate])
    
#     # Cut off spectrum
#     i_fc_range = [np.argmin(np.abs(np.array(frequency) - fc_range[0])), np.argmin(np.abs(np.array(frequency) - fc_range[1]))]
#     ft_data[:i_fc_range[0]] = 0
#     ft_data[i_fc_range[1]:] = 0
    
#     # Remove imaginary part
#     ft_data = ft_data[0:N//2+1]
    
#     # Restore complex DFT
#     ft_flip = ft_data[::-1]
#     ft_flip = np.conj(ft_flip[:-1])
#     ft_data = np.concatenate((ft_data[0:N//2], ft_flip), axis=0)
    
#     # Compute inverse DFT
#     res = compute_ifft(ft_data)
#     t = np.arange(len(res['time_serie']))/sample_rate
    
#     return {'filtered_time_serie': pd.DataFrame({'time':t, 'value':res['time_serie']}), 'filtered_fourier_transform': res['fourier_transform'], 'idx': i_fc_range}


# def band_analyzer(spectrum, frequencies, settings):
#     # Create sorted list with all frequency bands to monitor
#     f_segments = []    
#     for label, freq in frequencies.items():
#         for harmonic in range(settings['f_harmonics']):
#             f_segments.append([label, (harmonic + 1)*freq - settings['f_band'], (harmonic + 1)*freq + settings['f_band'], harmonic + 1])
#     f_segments = sorted(f_segments, key=operator.itemgetter(1))
    
#     n = len(f_segments)
#     if n == 0:
#         return pd.DataFrame(columns=['segment', 'harmonic', 'f1', 'f2', 'rms'])

#     for i in range(n):
#         if i == 0:
#             if f_segments[i][1] <= 0:
#                 f_segments[i][1] = 0
#             else:
#                 f_segments.append(['other', 0, f_segments[i][1], 0])
#         elif i < n:
#             if f_segments[i][1] > f_segments[i-1][2]:
#                 f_segments.append(['other', f_segments[i-1][2], f_segments[i][1], 0])
#     f_segments.append(['other', f_segments[i][2], np.max(spectrum['frequency']), 0])
#     f_segments = sorted(f_segments, key=operator.itemgetter(1))
    
#     spectrum_binned = []
#     for i in range(len(f_segments)):
#         # Filter spectrum for frequency band
#         spectrum_f = spectrum[(spectrum['frequency'] >= f_segments[i][1]) & (spectrum['frequency'] <= f_segments[i][2])]

#     return pd.DataFrame(data=spectrum_binned, columns = ['segment', 'harmonic', 'f1', 'f2', 'rms'])

# def filter_band_analyzer(data, filter):
#     row_filter = data.loc[data['segment'] == filter].sum()
#     row_filter['segment'] = filter
#     row_filter['f1'] = 0
#     row_filter['f2'] = 0

#     data = data.loc[data['segment'] != filter]
#     data = data.append(row_filter, ignore_index = True)

#     return data
