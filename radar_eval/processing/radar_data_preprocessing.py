import __init__
import numpy as np
from scipy.signal import butter, filtfilt, sosfiltfilt
from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER
# ==============================================================================
# Class Name: SYRA_DATA_PREPROCESSOR
# ==============================================================================
class SYRA_DATA_PREPROCESSOR():
    def __init__(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        self.radar_param = radar_param
        self.fc_hp = None
        self.window = None
        self.dsp_hp_a_coef = None
        self.dsp_hp_b_coef = None
        self.dsp_hp_sos_coef = None
        self.hp_filtering_flag = None
        self.init_window()
        self.init_dsp_hp_filter()
        
    def init_window(self, window_func: str = 'hanning') -> None:
        num_samples = self.radar_param.sys.n_samples_per_chirp[0]
        self.window_func = window_func
        
        if window_func == 'hanning':
            window = np.hanning(num_samples)
        elif window_func == 'hamming':
            window = np.hamming(num_samples)
        elif window_func == 'blackman':
            window = np.blackman(num_samples)
        elif window_func == 'kaiser':
            window = np.kaiser(num_samples, 0.5)
        elif window_func == 'bartlett':
            window = np.bartlett(num_samples)
        elif window_func == 'gaussian':
            sigma = 0.4 * (num_samples / 2)
            n = np.arange(num_samples)
            window = np.exp(-0.5 * ((n - (num_samples - 1) / 2) / sigma) ** 2)
        elif window_func == 'flattop':
            a0, a1, a2, a3, a4, a5, a6 = 1.0, 1.93, 1.29, 0.388, 0.028, -0.1, 0.05  # Coefficients can be adjusted
            n = np.arange(num_samples)
            window = (a0 - a1 * np.cos(2 * np.pi * n / (num_samples - 1)) 
                    + a2 * np.cos(4 * np.pi * n / (num_samples - 1))
                    - a3 * np.cos(6 * np.pi * n / (num_samples - 1))
                    + a4 * np.cos(8 * np.pi * n / (num_samples - 1))
                    - a5 * np.cos(10 * np.pi * n / (num_samples - 1))
                    + a6 * np.cos(12 * np.pi * n / (num_samples - 1)))
        elif window_func == 'chebyshev':
            attenuation = 0  # in dB
            beta = np.cosh(np.arccosh(10 ** (attenuation / 20)) / (num_samples - 1))
            n = np.arange(num_samples)
            x = beta * np.cos(np.pi * n / (num_samples - 1))
            window = np.cosh(beta * np.arccos(x))
        elif window_func == 'lanczos':
            n = np.arange(num_samples)
            window = np.sinc((2 * n / (num_samples - 1)) - 1)
        else:
            window = np.ones(num_samples)
            
        self.window = np.array(window, dtype=np.float32)
    
    def _window_channels(self, ch_data: np.ndarray) -> np.ndarray:
        reshaped_window = self.window.reshape((-1,) + (1,) * (ch_data.ndim - 1))
        
        return np.array(ch_data * reshaped_window, dtype=np.float32)
    
    def init_dsp_hp_filter(self, 
                        order: int=0,
                        filter_type: str='None',
                        cutoff: int=0) -> None:
        self.fc_hp = cutoff
        
        fcn_bgt_high = cutoff / (self.radar_param.sys.max_dsp_freq + 1e-12)   # normalized upper cutoff frequency
        if order > 0 and cutoff > 0 and filter_type in ['ba', 'sos']:
            if filter_type == 'ba':
                self.dsp_hp_b_coef, self.dsp_hp_a_coef = butter(N=order, Wn=fcn_bgt_high,
                                                                btype='hp', analog=False,
                                                                output=filter_type)
            elif filter_type == 'sos':
                self.dsp_hp_sos_coef = butter(N=order, Wn=fcn_bgt_high, btype='hp',
                                            analog=False, output=filter_type).astype(np.float32)
            self.hp_filtering_flag = filter_type   
        else:
            self.hp_filtering_flag = 'None' 
    def _dsp_hp_filtering(self, ch_data: np.ndarray) -> np.ndarray:
        if self.hp_filtering_flag == 'ba':
            return filtfilt(self.dsp_hp_b_coef, self.dsp_hp_a_coef, ch_data, axis=0).astype(np.float32)
        elif self.hp_filtering_flag == 'sos':
            return sosfiltfilt(self.dsp_hp_sos_coef, ch_data, axis=0).astype(np.float32)
    def preprocess_channels(self, ch_data: np.ndarray) -> np.ndarray:
        scaled_data = np.array(np.divide(ch_data, (np.power(2, 12)-1))*1200, dtype=np.float32)
    
        if self.hp_filtering_flag != 'None':
            if len(scaled_data.shape) > 2:
                for i in range(scaled_data.shape[2]):
                    scaled_data[:,:,i] = self._dsp_hp_filtering(scaled_data[:,:,i])
            else:
                scaled_data[:,:] = self._dsp_hp_filtering(scaled_data[:,:])
                
        if self.window_func != 'None':
            return self._window_channels(scaled_data)
        else:
            return np.array(scaled_data, dtype=np.float32)