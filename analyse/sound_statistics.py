# Import standard functions
import numpy as np
import pandas as pd
import time
from scipy import signal
import scipy.cluster.hierarchy as hcluster
from scipy import optimize

import spectral_statistics as ss

# Vibration analyzer class
class Sound_analyzer:

    def __init__(self, time_serie, sample_rate, optimize_speed, meta_data = []):
        # Flag to detect successful analytics
        self.status = {
                'success': True,
                'message': []}

        self.sample_rate = float(sample_rate)
        self.meta_data = meta_data
        
        # Format time serie: Prend une time serie (format = pd, np, list) en fait une time série pd frame avec 2 colonnes: time et value
        if isinstance(time_serie, pd.core.frame.DataFrame): 
            if len(time_serie.columns) == 1:
                t = np.arange(len(time_serie))/self.sample_rate
                self.time_serie = pd.DataFrame({'time': t, 'value': time_serie.iloc[:,0]}) 
            elif len(time_serie.columns) == 2:
                self.time_serie = time_serie
                self.time_serie.columns = ['time', 'value']
        elif isinstance(time_serie, np.ndarray):
            t = np.arange(len(time_serie))/self.sample_rate
            self.time_serie = pd.DataFrame({'time': t, 'value': time_serie})                
        elif isinstance(time_serie, list):
            t = np.arange(len(time_serie))/self.sample_rate
            self.time_serie = pd.DataFrame({'time': t, 'value': time_serie})
        else:
            self.status['success'] = False
            self.status['message'].append('ERROR: The time_serie has not the good format (pd fram/np array/list)')
            return
        
        # Remove DC component
        self.time_serie['value'] = self.time_serie['value'] - self.time_serie['value'].mean()
        
        self.N = len(self.time_serie)
        fast_lens = ss.get_all_fast_len(self.N)
        
        if optimize_speed: # Cut the time_serie length to optimize fft computation speed. Two methods to do the same
            try:
                self.time_serie = self.time_serie[:ss.get_fast_len(self.N, fast_lens)]
                self.status['message'].append('Optimize method 1')
            except:
                self.time_serie = self.time_serie[:ss.previous_fast_fft_len(self.N)]
                self.status['message'].append('Optimize method 2')
                
        self.N = len(self.time_serie['value'])



        # Vérifie que la time série dure + que 1 sec. (Je sais pas pq, peut être que c'est pour a fft, à tester sans)
        if not len(self.time_serie)/self.sample_rate > 1:
            self.status['success'] = False
            self.status['message'].append('ERROR: Measurement length should be at least 1 second')
            return

        
        

    def run_spectra_analysis(self, height_peaks, clust_dist): 
        if not self.status['success']: return
        self.status = {
            'success': True,
            'message': []}

        # Perform analysis
        self.get_spectra()
        self.get_peaks(height_peaks, clust_dist)
        
    def get_spectra(self):
        if not self.status['success']: return
        try:
            self.fft_data = ss.compute_fft(self.time_serie.copy(), self.sample_rate)
            self.spect_magn = ss.compute_spect_magn(self.fft_data['value'].copy(), self.N, self.sample_rate)
            self.spect_angle = ss.compute_spect_angle(self.fft_data['value'].copy(), self.N, self.sample_rate)
        except:
            self.status['success'] = False
            self.status['message'].append('ERROR: Spectra could not be computed')
            return
        
        
    def get_peaks(self, height_peaks, clust_dist):
    #     Find peaks over a threshold
        # Find peaks in the magnitude spectrum
        peaks_data, _ = signal.find_peaks(self.spect_magn['value'].values, height = height_peaks )
        peaks_idx = [peaks_data][0]
        peaks_freq_raw = self.spect_magn['frequency'].values[peaks_idx]
        peaks_magn_raw = self.spect_magn['value'].values[peaks_idx]
        # Give the angle spectrum's values on the peak's idx
        peaks_angle_raw = self.spect_angle['value'].values[peaks_idx]
#         peaks_raw = pd.DataFrame(np.column_stack((peaks_freq_raw, peaks_magn_raw, peaks_angle_raw)), columns=['frequency', 'magnitude', 'angle'])


    #     #### Clustering
    #     Le clustering nous permet de savoir quelles données sont liées a quelle harmonique. Ainsi, on peut faire le calcule complexe directement sur les données. 

    #     ##### Clustering hierarchique
    #     Trouve des clusters basé sur une distance min entre clusters (clust_dist)
    #     => Permet de ne pas devoir entrer un nombre prédéfini de clusters

        # Create a 2d array containing the peaks freq and magn (preprocess data for cluster function)
        peaks_coord = np.vstack((peaks_freq_raw, peaks_magn_raw)).T
        # clustering
        clusters = hcluster.fclusterdata(peaks_coord, clust_dist, criterion="distance")

    #     Ici on a les peaks à utiliser et leur classification en clusters dans le désordre. Après, on classe chaque peak dans son cluster puis on trie les clusters par ordre croissant de fréquence.

        nbrHarmo = len(set(clusters))

        peaks_freq_clustered = [[] for y in range(nbrHarmo)]
        peaks_magn_clustered = [[] for y in range(nbrHarmo)]
        peaks_angle_clustered = [[] for y in range(nbrHarmo)]

        # Regroup the data by clusters
        for idx in range(len(clusters)):
            peaks_freq_clustered[clusters[idx]-1].append(peaks_freq_raw[idx])
            peaks_magn_clustered[clusters[idx]-1].append(peaks_magn_raw[idx])
            peaks_angle_clustered[clusters[idx]-1].append(peaks_angle_raw[idx])

        # Sort the clusters by ascending frequencies
        peaks_clustered = pd.DataFrame(np.column_stack((peaks_freq_clustered, peaks_magn_clustered, peaks_angle_clustered)), columns=['frequency', 'magnitude', 'angle'])
        peaks_clustered = peaks_clustered.sort_values('frequency', ignore_index=True)
        
        # Keep only the highest peak of each cluster
        peaks_freq = []
        peaks_magn = []
        peaks_angle = []
        idx_max = [np.argmax(clust) for clust in peaks_clustered['magnitude']]
        for i in range(len(peaks_clustered['magnitude'])):
            peaks_freq.append(peaks_clustered['frequency'][i][idx_max[i]])
            peaks_magn.append(peaks_clustered['magnitude'][i][idx_max[i]])
            peaks_angle.append(peaks_clustered['angle'][i][idx_max[i]])
        peaks = pd.DataFrame(np.column_stack((peaks_freq, peaks_magn, peaks_angle)), columns=['frequency', 'magnitude', 'angle'])

        return peaks_clustered, peaks
    
    
        

         # Function to get the envelope
    def get_envelope(self, cutoff_signal, cutoff_hilbert, order=5):
        sound_filt = self.butter_lowpass_filter(self.time_serie['value'], cutoff_signal, order)
        hil = signal.hilbert(sound_filt)
        self.env = np.abs(hil)
        self.env = self.butter_lowpass_filter(self.env, cutoff_hilbert, order)
        return sound_filt
    
    def butter_lowpass_filter(self, data, cutoff, order=5):
        b, a = self.butter_lowpass(cutoff, order)
        y = signal.lfilter(b, a, data)
        return y
    
    def butter_lowpass(self, cutoff, order=5):
        nyq = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def env_synth(self, time, envelope_set, full_output=0):
        # Envlope_set = [attack, decay, sustheight, sustatta, sustdec]

        # Parts of envelope creation
        atta = (1-np.exp(-envelope_set[0]*time))
        dec = (np.exp(-envelope_set[1]*time))

        suat = (envelope_set[2]*(1-np.exp(-envelope_set[3]*time)))
        sudec = envelope_set[2]*np.exp(-envelope_set[4]*time)

        # Envelope creation and normalisation
        envelope = ((atta*dec)+(suat*sudec))
        max_envelope =  np.amax(envelope)
        envelope = envelope/max_envelope
        envelope = envelope.astype(np.float32)

        if full_output == 0:
            return envelope
        if full_output == 1:
            return [envelope, atta*dec/max_envelope, suat*sudec/max_envelope]
        
    def opt_envelope_set(self, time_serie, x_init, tol = 50):
        envelope_cost = lambda x: sum(np.sqrt((self.env_synth(self.time_serie['time'], x) - self.env)**2))
        xopt = optimize.fmin(func=envelope_cost, x0 = x_init, xtol=50)
        return xopt
        
        
        



    # # Coupe et renvoie un bout de spectre
    # def get_spect_band(self, band):
    #     if not self.status['success']: return

    #     try:
    #         fourier = ss.filter_out_freq(self.fft_data['value'].copy(), self.N, self.spect_magn['frequency'], 
    #                                 self.sample_rate, fc_range = band)
    #         spect_magn = ss.compute_spect_magn(fourier['filtered_fft_data'].copy(), self.N, self.spect_magn['frequency'])
    #     except:
    #         self.status['success'] = False
    #         self.status['message'].append('ERROR: System was unable to calculate frequency filtered time serie and spectrum')

    #     return (fourier['filtered_time_serie'], spect_magn, fourier['idx'])




    # # Ca sert à découper une série de bout de spectres du magnitude spectrum et enveloppe magnitude spectrum et les stoquer dans un pandaframe
    # def run_spectrum_index(self):
    #     if not self.status['success']: return
        
    #     self.spectrum_index = {}
    #     try:
    #         rc_acc_bin = ss.band_analyzer(self.spect_magn.copy(), self.meta_data['rc_freq_bands']['f_acc'], self.meta_data['binning_settings'])
    #         if len(rc_acc_bin) > 0:
    #             rc_acc_bin = ss.filter_band_analyzer(rc_acc_bin, 'other')
    #             self.spectrum_index['acc'] = rc_acc_bin.to_dict('r')
    #     except:
    #         self.status['message'].append('WARNING: Root cause on acceleration spectrum was not successful')
    #         print('WARNING: Root cause on acceleration spectrum was not successful')

    #     try:
    #         res = ss.envelope_curve_analysis(self.fft_data['value'].copy(), self.N, 
    #                                         self.spect_magn['frequency'], self.sample_rate, self.meta_data['filter_envspec'])
    #         self.env_spectrum = res['envelope_spectrum']
    #         self.env_time_serie = res['envelope_time_serie']
    #         rc_env_bin = ss.band_analyzer(self.env_spectrum.copy(), self.meta_data['rc_freq_bands']['f_env'], self.meta_data['binning_settings'])
    #         if len(rc_env_bin) > 0:
    #             rc_env_bin = ss.filter_band_analyzer(rc_env_bin, 'other')
    #             self.spectrum_index['env'] = rc_env_bin.to_dict('r')
    #     except:
    #         self.status['message'].append('WARNING: Root cause on envelope curve was not successful')
    #         print('WARNING: Root cause on envelope curve was not successful')