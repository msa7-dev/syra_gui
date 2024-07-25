import __init__
import os 
import time
import psutil
import numpy as np
import configparser
import setproctitle
import multiprocessing
# from numba import jit, njit, vectorize
from pathlib import Path
from typing import Any, Callable, Dict, List
from scipy.interpolate import griddata
from scipy.signal import find_peaks, convolve, convolve2d

from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER
from radar_eval.processing.radar_data_preprocessing import MIRA_DATA_PREPROCESSOR
from radar_eval.control.multiprocessing import distribute_cores_to_process
from radar_eval.rf_antenna.MIRA6024I1A import MIRA6024_RF_ANTENNA

Function = Callable[[Any], Any]
# ==============================================================================
# Class Name: MIRA_DATA_PROCESSOR
# ==============================================================================
class MIRA_DATA_PROCESSOR():
    def __init__(self, radar_param: MIRA_RADAR_PARAMETER) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(Path(__init__.MIRA_SYS_CONFIG_PATH).resolve())
        
        self.radar_param = radar_param
        self.data_preprocessor = MIRA_DATA_PREPROCESSOR(self.radar_param)
        
        self._init_buffers()
        self.prev_main_index = ''
        
        self.func_pipeline_dict: Dict[str, List[Function]] = {
            'Time':                  [self._scale_raw_data,
                                      self._prepare_time_output_format,
                                      self._move_data_to_gui_queue],
            'Spectrum':              [self.data_preprocessor.preprocess_channels,
                                      self._calc_rfft_channels,
                                    #   self._calc_rfft_channels_njit_wrapper,
                                      self._prepare_spectrum_output_format,
                                      self._move_data_to_gui_queue],
            'Waterfall Spectrogram': [self.data_preprocessor.preprocess_channels, 
                                      self._calc_spectogram,
                                      self._prepare_spectrogram_output_format,
                                      self._move_data_to_gui_queue],
            'Range Doppler':         [self.data_preprocessor.preprocess_channels,
                                      self._calc_range_doppler,
                                      self._prepare_range_doppler_output_format,
                                      self._move_data_to_gui_queue],
            'Range Azimuth':         [self.data_preprocessor.preprocess_channels,
                                      self._calc_range_azimuth,
                                      self._prepare_range_azimuth_output_format,
                                      self._move_data_to_gui_queue],
            'Waterfall Azimuth':     [self.data_preprocessor.preprocess_channels,
                                      self._calc_waterfall_azimuth,
                                      self._move_data_to_gui_queue],
            'Range Doppler Azimuth': [self.data_preprocessor.preprocess_channels,
                                      self._calc_range_doppler_azimuth,
                                      self._move_data_to_gui_queue],
            'Demo':                  [self.data_preprocessor.preprocess_channels,
                                      self._calc_waterfall_range_doppler_azimuth,
                                      self._move_data_to_gui_queue]
        }
        self.processor_callable_dict: Dict[str, Callable[[Any], Any]] = {
            name: self._create_callable_pipeline(func_list) 
            for name, func_list in self.func_pipeline_dict.items()
        }
    
    def _init_buffers(self) -> None:
        self.spectogram_map = np.zeros((1,1,1), dtype=np.float32)
        self.range_doppler_map = np.zeros((1,1,1), dtype=np.float32)
        self.prev_range_azimuth_shape = (0,0,0)
        self.range_azimuth_map = np.zeros((1,1,1), dtype=np.float32)
        self.ch_range_doppler_buf = np.zeros((1,1,1), dtype=np.float32)
        self.prev_range_doppler_map = np.zeros((1,1,1), dtype=np.float32)
        self.prev_range_doppler_mean = np.zeros((1,1,1), dtype=np.float32)
        

    def _create_callable_pipeline(self, functions: List[Function]) -> Callable[[Any], Any]:
        def _callable_pipeline(input_data):
            for func in functions:
                input_data = func(input_data)
            return input_data
        return _callable_pipeline

    def _call_dsp_pipeline(self, pipeline_name: str, input_data: Any) -> Any:
        if pipeline_name in self.processor_callable_dict:
            return self.processor_callable_dict[pipeline_name](input_data)
        else:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")

    def data_processing_process(self, 
                                extracted_processing_data_queue: multiprocessing.Queue,
                                processed_gui_data_queue: multiprocessing.Queue,
                                gui_parameter_queue: multiprocessing.Queue,
                                process_stop_event: multiprocessing.Event) -> None:
        self.gui_parameter_queue = gui_parameter_queue
        self.processed_gui_data_queue = processed_gui_data_queue
        MIRA_PROCESSING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                       "MIRA_PROCESSING_CPU_CORE"))
        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                    "MIRA_PROCESS_PRIO"))
        
        mira_data_processing_process = psutil.Process(os.getpid())
        mira_data_processing_process.cpu_affinity([MIRA_PROCESSING_CPU_CORE])
        mira_data_processing_process.nice(MIRA_PROCESS_PRIO)
        distribute_cores_to_process(mira_data_processing_process, 2)
        setproctitle.setproctitle("Sykno - Radar Eval GUI - Processing Process")

        radar_data_cube = np.zeros((np.uint16(self.radar_param.sys.n_samples_per_chirp[0]), # Dim. 1
                                    int(8),
                                    self.radar_param.sys.shape_set_repetition),             # Dim. 3
                                   dtype=np.uint16) 
        self.counter = 0
        self.rf_antenna = MIRA6024_RF_ANTENNA()
        while not process_stop_event.is_set():
            if not extracted_processing_data_queue.empty():
                radar_data = np.asarray(extracted_processing_data_queue.get(), dtype=np.uint16)
            else:
                time.sleep(20e-6) # wait 250us << processing time of data_extracting()
                continue
            
            if not np.any(radar_data):
                continue
            
            radar_data_cube[:, 0:self.radar_param.sys.rx_active_antennas[0], :] = radar_data[:, :, 0, :]
            if self.radar_param.mon.sykno_product_name == 'MiRa6024I1A':
                radar_data_cube[:, 4:4+self.radar_param.sys.rx_active_antennas[0], :] = radar_data[:, :, 1, :]
            
            if not self.gui_parameter_queue.empty():
                self._update_gui_parameter()
                    
            if self.max_value != 0:
                self._call_dsp_pipeline(self.main_tab_index, radar_data_cube)
    
    def _update_gui_parameter(self) -> None:
        gui_parameters = self.gui_parameter_queue.get_nowait()
        self.main_tab_index = gui_parameters['main_tab_index']
        self.time_tab_index = gui_parameters['time_tab_index']
        self.spectrogram_tab_index = gui_parameters['spectrogram_tab_index']
        self.range_doppler_tab_index = gui_parameters['range_doppler_tab_index']
        
        window_func = gui_parameters['window_function']
        self.padding_len = gui_parameters['padding_length']
        dsp_hp_parameters = gui_parameters['dsp_hp_filter_params']
        self.max_value = gui_parameters['system_params']['plot_axis_max_value']
        self.max_value_type = gui_parameters['system_params']['current_selected_axis_unit']
        self.waterfall_spectrogram_time = gui_parameters['system_params']['waterfall_spectrogram_time']
        self.rf_aperature_select = gui_parameters['rf_antenna']
        
        self.data_preprocessor.init_dsp_hp_filter(dsp_hp_parameters['order'],
                                                  dsp_hp_parameters['type'],
                                                  dsp_hp_parameters['cutoff'])
        self.data_preprocessor.init_window(window_func)
        
        if self.prev_main_index != self.main_tab_index:
            self._init_buffers()
    
    def _move_data_to_gui_queue(self, processed_radar_data: np.ndarray) -> None:
        if self.processed_gui_data_queue.empty():
            self.processed_gui_data_queue.put({'Process Info': {'Process Name': self.main_tab_index,},
                                                      'Processed Data': processed_radar_data})
        return None

    def scale_raw_data(self, raw_radar_data_cube: np.ndarray,
                       preprocessing: bool=False,
                       output_mean: bool=False) -> np.ndarray:
        if preprocessing and output_mean:
            return np.mean(np.asarray(self.data_preprocessor.preprocess_channels(raw_radar_data_cube), 
                                    dtype=np.float32),
                           axis=3, dtype=np.float32)
        elif preprocessing and not output_mean:
            return np.asarray(self.data_preprocessor.preprocess_channels(raw_radar_data_cube), dtype=np.float32)
        elif not preprocessing and output_mean:
            return np.mean(np.asarray((np.divide(raw_radar_data_cube, np.power(2, 12)-1) * 1200), dtype=np.float32), axis=3, dtype=np.float32)
        elif not preprocessing and not output_mean:
            return np.asarray((np.divide(raw_radar_data_cube, np.power(2, 12)-1) * 1200), dtype=np.float32)
    
    def _scale_raw_data(self, raw_radar_data_cube: np.ndarray) -> np.ndarray:
        if self.time_tab_index == 'DSP Output':
            return np.mean(np.asarray(self.data_preprocessor.preprocess_channels(raw_radar_data_cube), 
                                    dtype=np.float32),
                           axis=2, dtype=np.float32)
        elif self.time_tab_index == 'Raw Data':
            return np.asarray((np.divide(raw_radar_data_cube, np.power(2, 12)-1) * 1200), dtype=np.float32)[:,:,0]

    def _prepare_time_output_format(self, data: np.ndarray) ->  dict:
        if sum(self.radar_param.sys.n_active_shape) == 1:
            return {'Channel 1': data[:, 0:4],
                    'Channel 2': np.zeros((1,1,1), dtype=np.float32),
                    'Channel 3': np.mean(data, axis=1, dtype=np.float32)}
        elif sum(self.radar_param.sys.n_active_shape) == 2:
            return {'Channel 1': data[:, 0:4],
                    'Channel 2': data[:, 4:8],
                    'Channel 3': np.mean(data, axis=1, dtype=np.float32)}

    def _calc_rfft_channels_njit_wrapper(self, ch_data: np.ndarray) -> np.ndarray:
        return _calc_rfft_channels_njit(ch_data, self.padding_len)
        
    def _calc_rfft_channels(self, ch_data: np.ndarray) -> np.ndarray:
        return np.asarray(20*np.log10(np.abs(
                          np.fft.rfft(ch_data*1e-3,
                          n=(ch_data.shape[0]+self.padding_len)-1,
                          axis=0)) + np.finfo(float).eps), dtype=np.float32)
    

    
    def detect_peaks(self, x, num_train, num_guard, rate_fa):
        """
        Detect peaks with CFAR algorithm.

        num_train: Number of training cells.
        num_guard: Number of guard cells.
        rate_fa: False alarm rate.
        """
        num_cells = x.size
        num_train_half = round(num_train / 2)
        num_guard_half = round(num_guard / 2)
        num_side = num_train_half + num_guard_half

        alpha = num_train*(rate_fa**(-1/num_train) - 1) # threshold factor

        has_peak = np.zeros(num_cells, dtype=bool)
        peak_at = []
        for i in range(num_side, num_cells - num_side):
            if i != i-num_side+np.argmax(x[i-num_side:i+num_side+1]):
                continue

            sum1 = np.sum(x[i-num_side:i+num_side+1])
            sum2 = np.sum(x[i-num_guard_half:i+num_guard_half+1])
            p_noise = (sum1 - sum2) / num_train
            threshold = alpha * p_noise

            if x[i] > threshold:
                has_peak[i] = True
                peak_at.append(i)

        peak_at = np.array(peak_at, dtype=int)

        return peak_at
    
    def cfar_ca_1d(self, RDM, Tr=8, Gr=4, offset=0):
        radius_range = Tr + Gr
        Nrange_cells = RDM.size - 2 * radius_range

        grid_size = 2 * (Tr + Gr) + 1
        Nguard_cut_cells = 2 * Gr + 1
        Ntrain_cells = grid_size - Nguard_cut_cells

        # Vectorized implementation for noise level estimation
        cfar_signal = np.zeros_like(RDM)

        for r in range(radius_range, Nrange_cells + radius_range):
            # Extract the noise level from the training cells
            training_cells = RDM[r - radius_range:r + radius_range + 1]
            guard_cells = RDM[r - Gr:r + Gr + 1]

            # Calculate noise level by excluding the guard cells and CUT
            noise_level = np.sum(10**(training_cells / 10)) - np.sum(10**(guard_cells / 10))
            noise_level /= Ntrain_cells

            threshold = 10 * np.log10(noise_level) + offset

            if RDM[r] > threshold:
                cfar_signal[r] = RDM[r]
        return cfar_signal

    
    def _prepare_spectrum_output_format(self, ch_data: np.ndarray) -> dict:        
        
        # for n_shape in range(ch_data.shape[2]):
        # cfar = self.cfar_ca_1d(np.mean(np.mean(ch_data, axis=2, dtype=np.float32), axis=1, dtype=np.float32), 8, 4, -20)
        
        if sum(self.radar_param.sys.n_active_shape) == 1:
            return {'Channel 1': np.mean(ch_data[:, 0:4,:], axis=2, dtype=np.float32),
                    'Channel 2': np.zeros((1,1,1), dtype=np.float32),
                    'Channel 3': np.mean(np.mean(ch_data, axis=2, dtype=np.float32), axis=1, dtype=np.float32)}
        elif sum(self.radar_param.sys.n_active_shape) == 2:
            # peaks, _ = find_peaks(np.mean(np.mean(ch_data, axis=2, dtype=np.float32), axis=1, dtype=np.float32), height=-20)
            return {'Channel 1': np.mean(ch_data[:,0:4,:], axis=2, dtype=np.float32),
                    'Channel 2': np.mean(ch_data[:,4:8,:], axis=2, dtype=np.float32),
                    # 'Channel 3': cfar}
                    'Channel 3': np.mean(np.mean(ch_data, axis=2, dtype=np.float32), axis=1, dtype=np.float32)}
    
    def _calc_spectogram(self, ch_data: np.ndarray) -> np.ndarray:
        try:
            temp = self.main_tab_index
            temp = self.spectrogram_tab_index
        except:
            self.main_tab_index = None
            self.spectrogram_tab_index = None
            self.max_value_type = None
        
        if self.spectrogram_tab_index == 'TX1' or \
           self.main_tab_index == 'Waterfall Azimuth':
            ch_fft = self._calc_rfft_channels(np.mean(ch_data[:,0:4,:], axis=2, dtype=np.float32))
        elif self.spectrogram_tab_index == 'TX2':
            ch_fft = self._calc_rfft_channels(np.mean(ch_data[:,4:8,:], axis=2, dtype=np.float32))
        else:
            self.waterfall_spectrogram_time = 1
            self.padding_len = 0
            ch_fft = self._calc_rfft_channels(np.mean(ch_data[:,0:4,:], axis=2, dtype=np.float32))
                
        self.n_frames_spectrogram = np.uint32(np.divide(np.abs(self.waterfall_spectrogram_time), 
                                                        self.radar_param.sys.frame_duration))

        if self.max_value_type == 'range':
            fft_len = int(self.max_value/(self.radar_param.sys.max_range/ch_fft.shape[0]))
        elif self.max_value_type == 'freq':
            fft_len = int(self.max_value*1e3/(self.radar_param.sys.max_dsp_freq/ch_fft.shape[0]))
        else: 
            fft_len = ch_fft.shape[0]

        if fft_len != self.spectogram_map.shape[1] or \
           self.n_frames_spectrogram != self.spectogram_map.shape[0]:
            self.spectogram_map = np.zeros((self.n_frames_spectrogram, fft_len, ch_fft.shape[1]), dtype=np.float32)
        
        self.spectogram_map = np.concatenate((ch_fft[np.newaxis,0:fft_len,:],
                                              self.spectogram_map[0:self.n_frames_spectrogram-1,:,:]),
                                             axis=0, dtype=np.float32) 

        return np.asarray(self.spectogram_map, dtype=np.float32)

    def _prepare_spectrogram_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Waterfall Spectrogram':
            dummy = np.zeros((1,1,1))
            return {'Channel 1': ch_data[:,:], 'Channel 2': np.zeros((1,1,1), dtype=np.float32), 'Channel 3': dummy}
    
    
    def detect_peaks_2d(self, array, threshold_abs=0, neighborhood_size=3):
        import scipy.ndimage as ndimage
        """
        Detect peaks in a 2D array.

        Parameters:
        - array (2D numpy array): The input array in which to detect peaks.
        - threshold_abs (float): Minimum intensity threshold for a peak.
        - neighborhood_size (int): Size of the neighborhood to search for peaks.

        Returns:
        - peak_coords (list of tuples): List of (x, y) coordinates of the detected peaks.
        - peak_values (list of floats): List of values of the detected peaks.
        """
        # Apply maximum filter
        neighborhood_size = neighborhood_size
        data_max = ndimage.maximum_filter(array, size=neighborhood_size, mode='constant')

        # Create a mask of the peaks
        maxima = (array == data_max)
        diff = (data_max > threshold_abs)
        maxima[diff == 0] = 0

        # Get the coordinates of the peaks
        peak_coords = np.argwhere(maxima)

        # Get the values of the peaks
        peak_values = array[maxima]

        return peak_coords, peak_values
    
    def _calc_range_doppler(self, ch_data: np.ndarray) -> np.ndarray:
        ch_data = ch_data.transpose(2, 0, 1)
        
        # data splitting for TX selection
        if self.range_doppler_tab_index == 'TX1' or \
           self.main_tab_index == 'Range Doppler Azimuth' or \
           self.main_tab_index == 'Demo':
            ch_data = ch_data[:,:,0:4]
        elif self.range_doppler_tab_index == 'TX2':
            ch_data = ch_data[:,:,4:8]
        
        # simple static target oppression 
        ch_data -= np.mean(ch_data, axis=0, keepdims=True)
        
        n_samples = ch_data.shape[1]
        ch_fft_range = np.fft.rfft(ch_data, n=n_samples+self.padding_len-1, axis=1)    
        
        hanning_window = np.hanning(ch_data.shape[0])

        self.fft_window = hanning_window[:, np.newaxis, np.newaxis]
        
        ch_fft_range_win = ch_fft_range * self.fft_window

        ch_fft_distance = (np.fft.fft(ch_fft_range_win, n=ch_data.shape[0]+self.padding_len, axis=0))

        range_doppler =  (20*np.log10(np.abs(np.fft.fftshift(ch_fft_distance, axes=0)) \
                        + np.finfo(float).eps)).astype(np.float32)
            
        if self.max_value_type == 'range':
            self.range_doppler_map = (range_doppler[0:range_doppler.shape[0],
                                                    0:int(self.max_value/(self.radar_param.sys.max_range
                                                                        / range_doppler.shape[1])),:])
        elif self.max_value_type == 'freq':
            self.range_doppler_map = (range_doppler[0:range_doppler.shape[0],:,:])

        if self.main_tab_index == 'Range Doppler Azimuth':
            self.range_doppler_map = np.mean(self.range_doppler_map, axis=2, keepdims=True)
        
        # self.range_doppler_map[:,:,0] = self.cfar_ca_2d(self.range_doppler_map[:,:,0])
        # self.range_doppler_map[:,:,0] = self.cfar_ca_2d(np.mean(self.range_doppler_map, axis=2, dtype=np.float32))

        return np.asarray(self.range_doppler_map, dtype=np.float32)


    def cfar_ca_2d(self, RDM, Tr=16, Td=16, Gr=16, Gd=16, offset=5):
        # Define the size of training and guard cells
        radius_doppler = Td + Gd
        radius_range = Tr + Gr
        # 
        # Pre-define the size of the output CFAR signal
        cfar_signal = np.zeros_like(RDM)
        # 
        # Compute noise level estimation and threshold calculation
        for r in range(radius_range, RDM.shape[0] - radius_range):
            for d in range(radius_doppler, RDM.shape[1] - radius_doppler):
                # Define the boundaries of the training cells and guard cells
                r_start, r_end = r - radius_range, r + radius_range + 1
                d_start, d_end = d - radius_doppler, d + radius_doppler + 1
                gr_start, gr_end = r - Gr, r + Gr + 1
                gd_start, gd_end = d - Gd, d + Gd + 1
                # 
                # Extract training and guard cells
                training_cells = RDM[r_start:r_end, d_start:d_end]
                guard_cells = RDM[gr_start:gr_end, gd_start:gd_end]
                # 
                # Exclude guard cells and CUT from training cells
                noise_level = np.sum(10**(training_cells / 10)) - np.sum(10**(guard_cells / 10))
                noise_level /= (training_cells.size - guard_cells.size)
                # 
                # Calculate threshold and apply CFAR
                threshold = 10 * np.log10(noise_level) + offset
                if RDM[r, d] > threshold:
                    cfar_signal[r, d] = RDM[r, d]
        return cfar_signal
    
    def _prepare_range_doppler_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Range Doppler':
            dummy = np.zeros((1,1,1))
            return {'Channel 1': ch_data, 'Channel 2': np.zeros((1,1,1), dtype=np.float32), 'Channel 3': dummy}
    
    
    def transform_range_azimuth_to_half_circle(self, range_azimuth_map, data_cube_shape):    
        if self.prev_range_azimuth_shape != data_cube_shape:
            num_ranges, num_azimuths = range_azimuth_map.shape
            ranges = np.linspace(0, 1, num_ranges)  # Normalize range to [0, 1] for simplicity
            azimuths = np.linspace(-90, 90, num_azimuths)  # Azimuth angles from -90 to 90 degrees
            # Create a grid in polar coordinates
            r, az = np.meshgrid(ranges, np.radians(azimuths))

            # Adjust the conversion to orient the half-circle upwards
            # Swap x and y roles, and adjust azimuth angles for upward orientation
            x = r * np.sin(az)
            y = r * np.cos(az)  # This will orient the half-circle with the flat side up
            # Create the Cartesian output grid
            self.grid_x, self.grid_y = np.mgrid[
                np.min(x):np.max(x):complex(500),  #complex(num_ranges),  # size of the grid can be adjusted arbitrarily!
                np.min(y):np.max(y):complex(500)   #complex(num_azimuths)
            ]
            # Flatten the arrays for interpolation
            self.points = np.vstack((x.flatten(), y.flatten())).T
            self.prev_range_azimuth_shape = data_cube_shape
            
        values = range_azimuth_map.T.flatten()
        # Interpolate the data onto the Cartesian grid
        cartesian_map = griddata(self.points, values, (self.grid_x, self.grid_y), method='nearest', fill_value=np.nan)

        #prüfe für jeden Punkt Abstand vom Nullpunkt; wenn größer als halbe Achsenlänge -> nan; nur nötig bei "nearest"

        # dim0 = cartesian_map.shape[0]
        # dim1 = cartesian_map.shape[1]
        # for m in range(dim0):
        #     for n in range(dim1):
        #         curr_r = np.sqrt((m-dim0/2)**2+(n/dim1*dim0/2-0)**2) # vereinfachbar, wenn Plot quadratisch ist (dim1/dim0=1)
                
        #         if curr_r>dim0/2:
        #             cartesian_map[m,n]=np.nan

        rows, cols = cartesian_map.shape
        m, n = np.ogrid[:rows, :cols]
        curr_r = np.sqrt((m - rows / 2) ** 2 + (n / cols * rows / 2 - 0) ** 2)
        cartesian_map[curr_r > rows / 2] = np.nan

        return cartesian_map 

    def _calc_range_azimuth(self, processed_data_cube: np.ndarray) -> np.ndarray:
        processed_data_cube_fft = np.fft.rfft(processed_data_cube, n=processed_data_cube.shape[0]+self.padding_len-1, axis=0)
        data_cube = np.asarray(processed_data_cube_fft[:,:,0], dtype=np.complex64)
        
        if self.prev_range_azimuth_shape != data_cube.shape:
            self.az = np.deg2rad(np.linspace(-90,90,int(18*10+1)))
            self.k = 2 * np.pi / self.radar_param.sys.lambda_freq[0]
            self.lambda0 = self.radar_param.sys.lambda_freq[0]
            
            self.virtuel_array = np.empty((len(self.az), 8), dtype=np.cdouble)
            for m in range(len(self.az)):
                for k in range(8):
                    self.virtuel_array[m,k] = np.exp(-1j*2*np.pi/self.lambda0*(self.rf_antenna.antenna_spacing[self.rf_aperature_select][k]* \
                                                     np.sin(self.az[m])))*np.exp(1j*self.rf_antenna.phase_calibration[self.rf_aperature_select][k])
        
        self.range_azimuth_map = np.zeros((len(self.az), data_cube.shape[0]), dtype = np.float32)
        
        for m in range(len(self.az)):
            self.range_azimuth_map[m,:] = np.abs(np.sum(data_cube * self.virtuel_array[m,:], axis=1)).astype(np.float32)

        if self.max_value_type == 'range':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value/(self.radar_param.sys.max_range
                                                                                 /self.range_azimuth_map.shape[1]))]
        elif self.max_value_type == 'freq':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value/(self.radar_param.sys.max_dsp_freq * 1e-3
                                                                                /self.range_azimuth_map.shape[1]))]
        self.range_azimuth_map = self.transform_range_azimuth_to_half_circle(self.range_azimuth_map.T, data_cube.shape)
        return np.asarray(self.range_azimuth_map, dtype=np.float32)

    def _calc_range_azimuth_music(self, processed_data_cube: np.ndarray) -> np.ndarray:
        from pyargus.directionEstimation import DOA_Bartlett, DOA_MUSIC, corr_matrix_estimate
        processed_data_cube_fft = np.fft.rfft(processed_data_cube, n=processed_data_cube.shape[0] + self.padding_len - 1, axis=0)
        data_cube = np.asarray(processed_data_cube_fft, dtype=np.complex64)

        if self.prev_range_azimuth_shape != data_cube.shape:
            self.az = np.deg2rad(np.linspace(-90, 90, int(18 * 10 + 1)))
            self.k = 2 * np.pi / self.radar_param.sys.lambda_freq[0]
            self.lambda0 = self.radar_param.sys.lambda_freq[0]

            self.virtual_array = np.empty((len(self.az), 8), dtype=np.cdouble)
            for m in range(len(self.az)):
                for k in range(8):
                    self.virtual_array[m, k] = np.exp(-1j * 2 * np.pi / self.lambda0 * (
                        self.rf_antenna.antenna_spacing[self.rf_aperature_select][k] * np.sin(self.az[m]))
                    ) * np.exp(1j * self.rf_antenna.phase_calibration[self.rf_aperature_select][k])

        self.range_azimuth_map = np.zeros((len(self.az), data_cube.shape[0]), dtype=np.float32)

        # Ensure data_cube is correctly reshaped to form a valid correlation matrix
        for r in range(data_cube.shape[0]):
            range_bin_data = data_cube[r, :, :].reshape(-1, data_cube.shape[1])

            if range_bin_data.shape[0] < range_bin_data.shape[1]:
                range_bin_data = range_bin_data.T

            R = corr_matrix_estimate(range_bin_data, imp="fast")
            signal_dimension = 2  # Adjust based on actual number of sources

            ula_scanning_vectors = np.empty((8, len(self.az)), dtype=np.cdouble)
            for m in range(len(self.az)):
                for k in range(8):
                    ula_scanning_vectors[k, m] = np.exp(-1j * 2 * np.pi / self.lambda0 * (
                        self.rf_antenna.antenna_spacing[self.rf_aperature_select][k] * np.sin(self.az[m])))

            MUSIC_spectrum = DOA_MUSIC(R, ula_scanning_vectors, signal_dimension=signal_dimension)

            self.range_azimuth_map[:, r] = np.abs(MUSIC_spectrum).astype(np.float32)

        if self.max_value_type == 'range':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value / (self.radar_param.sys.max_range / self.range_azimuth_map.shape[1]))]
        elif self.max_value_type == 'freq':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value / (self.radar_param.sys.max_dsp_freq * 1e-3 / self.range_azimuth_map.shape[1]))]

        self.range_azimuth_map = self.transform_range_azimuth_to_half_circle(self.range_azimuth_map.T, data_cube.shape)
        return np.asarray(self.range_azimuth_map*100, dtype=np.float32)

    def _prepare_range_azimuth_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Range Azimuth':
            dummy = np.zeros((1,1,1))
            return {'Channel 1': ch_data, 'Channel 2': np.zeros((1,1,1), dtype=np.float32), 'Channel 3': dummy}
        
    def _calc_waterfall_azimuth(self, preprocessed_data: np.ndarray) -> dict:
        spectogram_map = self._calc_spectogram(preprocessed_data)
        range_azimuth_map = self._calc_range_azimuth(preprocessed_data)
        dummy = np.zeros((1,1,1))
        return {'Channel 1': range_azimuth_map, 'Channel 2': spectogram_map, 'Channel 3': dummy}
    
    def _calc_range_doppler_azimuth(self, preprocessed_data: np.ndarray) -> dict:
        range_doppler_map = self._calc_range_doppler(preprocessed_data)
        range_azimuth_map = self._calc_range_azimuth(preprocessed_data)
        dummy = np.zeros((1,1,1))
        return {'Channel 1': range_azimuth_map, 'Channel 2': range_doppler_map, 'Channel 3': dummy}
    
    def _calc_waterfall_range_doppler_azimuth(self, preprocessed_data: np.ndarray) -> dict:
        waterfall_map = self._calc_spectogram(preprocessed_data)
        range_doppler_map = self._calc_range_doppler(preprocessed_data)
        range_azimuth_map = self._calc_range_azimuth(preprocessed_data)
        return {'Channel 1': range_azimuth_map, 'Channel 2': range_doppler_map, 'Channel 3': waterfall_map}
    
# @njit(fastmath=True)
# def _calc_rfft_channels_njit(ch_data: np.ndarray, padding_len) -> np.ndarray:
#     return (20*np.log10(np.abs(
#                      np.fft.rfft(ch_data*1e-3,
#                           n=(ch_data.shape[0]+padding_len)-1,
#                           axis=0)) + np.finfo(np.float32).eps))