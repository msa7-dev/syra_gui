import __init__
import os 
import time
import queue
import psutil
import numpy as np
import configparser
import multiprocessing
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mira.rsys.mira_radar_sys import MIRA6024_RADAR_PARAMETER
from mira.proc.mira_data_preprocessing import MIRA6024_DATA_PREPROCESSOR

Function = Callable[[Any], Any]
# ==============================================================================
# Class Name: MIRA6024_DATA_PROCESSOR
# ==============================================================================
class MIRA6024_DATA_PROCESSOR():
    def __init__(self, radar_param: MIRA6024_RADAR_PARAMETER) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(Path(__init__.MIRA_SYS_CONFIG_PATH).resolve())
        
        self.radar_param = radar_param
        self.data_preprocessor = MIRA6024_DATA_PREPROCESSOR(self.radar_param)
        
        self._init_buffers()
        self.prev_main_index = ''
        
        self.func_pipeline_dict: Dict[str, List[Function]] = {
            'Time':                  [self._scale_raw_data,
                                      self._prepare_time_output_format,
                                      self._move_data_to_gui_queue],
            'Spectrum':              [self.data_preprocessor.preprocess_channels,
                                      self._calc_rfft_channels,
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
                                      self._move_data_to_gui_queue]
        }
        self.processor_callable_dict: Dict[str, Callable[[Any], Any]] = {
            name: self._create_callable_pipeline(func_list) 
            for name, func_list in self.func_pipeline_dict.items()
        }
    
    def _init_buffers(self) -> None:
        self.spectogram_map = np.zeros((1,1,1), dtype=np.float32)
        self.range_doppler_map = np.zeros((1,1,1), dtype=np.float32)
        self.range_azimuth_map = np.zeros((1,1,1), dtype=np.float32)
        self.ch_range_doppler_buf = np.zeros((1,1,1), dtype=np.float32)
        

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
                                radar_data_extraced_queue: multiprocessing.Queue,
                                processed_radar_data_queue: multiprocessing.Queue,
                                gui_parameter_queue: multiprocessing.Queue,
                                stop_event: multiprocessing.Event) -> None:
        self.gui_parameter_queue = gui_parameter_queue
        self.processed_radar_data_queue = processed_radar_data_queue
        MIRA_PROCESSING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                       "MIRA_PROCESSING_CPU_CORE"))
        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                    "MIRA_PROCESS_PRIO"))
        
        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([MIRA_PROCESSING_CPU_CORE])
        current_process.nice(MIRA_PROCESS_PRIO)

        radar_data_cube = np.zeros((np.uint16(self.radar_param.sys.n_samples_per_chirp[0]),       # Dim. 1
                                    np.uint8(4*2), #self.radar_param.sys.rx_active_antennas * # Dim. 2
                                              #self.radar_param.sys.tx_active_antennas), # Dim. 2 
                                    self.radar_param.sys.shape_set_repetition),   # Dim. 3
                                   dtype=np.uint16) 
        self.max_value_type = 'freq'
        self.counter = 0
        while not stop_event.is_set():
            if not radar_data_extraced_queue.empty():
                radar_data = radar_data_extraced_queue.get(block=False)
            else:
                time.sleep(250e-6) # wait 250us << processing time of data_extracting()
                continue
            
            # radar_data.shape = (samples, rx, tx, shape_set), dtype(np.uint16)
            radar_data_cube[:,0:4,:] = radar_data[:,:,0,:] 
            radar_data_cube[:,4:8,:] = radar_data[:,:,1,:]
            
            if not self.gui_parameter_queue.empty():
                self._update_gui_parameter()
                    
            if self.max_value != 0:
                self._call_dsp_pipeline(self.main_tab_index, radar_data_cube)
    
    def _update_gui_parameter(self) -> None:
        gui_parameters = self.gui_parameter_queue.get(block=False)
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
        
        self.data_preprocessor.init_dsp_hp_filter(dsp_hp_parameters['order'],
                                                  dsp_hp_parameters['type'],
                                                  dsp_hp_parameters['cutoff'])
        self.data_preprocessor.init_window(window_func)
        if self.prev_main_index != self.main_tab_index:
            self._init_buffers()
    
    def _move_data_to_gui_queue(self, processed_radar_data: np.ndarray) -> None:
        if self.processed_radar_data_queue.empty():
            self.processed_radar_data_queue.put({'Process Info': {'Process Name': self.main_tab_index,},
                                                 'Processed Data': processed_radar_data})
        return None
    
    def _scale_raw_data(self, raw_radar_data_cube: np.ndarray) -> np.ndarray:
        if self.time_tab_index == 'Raw Data':
            return np.array((np.divide(raw_radar_data_cube, np.power(2, 12)-1) * 1200), dtype=np.float32)[:,:,0]
        elif self.time_tab_index == 'DSP Output':
            return np.mean(np.array(self.data_preprocessor.preprocess_channels(raw_radar_data_cube), 
                                    dtype=np.float32),
                           axis=2, dtype=np.float32)
            
    def _prepare_time_output_format(self, data: np.ndarray) ->  dict:
        if sum(self.radar_param.sys.n_active_shape) == 1:
            return {'Channel 1': data[:, 0:4],
                    'Channel 2': np.zeros((1,1,1), dtype=np.float32)}
        elif sum(self.radar_param.sys.n_active_shape) == 2:
            return {'Channel 1': data[:, 0:4],
                    'Channel 2': data[:, 4:8]}

    def _calc_rfft_channels(self, ch_data: np.ndarray) -> np.ndarray:
        return np.array(20*np.log10(np.abs(
                         np.fft.rfft(ch_data*1e-3,
                              n=(ch_data.shape[0]+self.padding_len)-1,
                              axis=0)) + np.finfo(float).eps), dtype=np.float32)
        
    def _prepare_spectrum_output_format(self, ch_data: np.ndarray) -> dict:
        if sum(self.radar_param.sys.n_active_shape) == 1:
            return {'Channel 1': np.mean(ch_data[:, 0:4,:], axis=2, dtype=np.float32),
                    'Channel 2': np.zeros((1,1,1), dtype=np.float32)}
        elif sum(self.radar_param.sys.n_active_shape) == 2:
            return {'Channel 1': np.mean(ch_data[:,0:4,:], axis=2, dtype=np.float32),
                    'Channel 2': np.mean(ch_data[:,4:8,:], axis=2, dtype=np.float32)}
    
    def _calc_spectogram(self, ch_data: np.ndarray) -> np.ndarray:
        if self.spectrogram_tab_index == 'TX1' or \
           self.main_tab_index == 'Waterfall Azimuth':
            ch_fft = self._calc_rfft_channels(np.mean(ch_data[:,0:4,:], axis=2, dtype=np.float32))
        elif self.spectrogram_tab_index == 'TX2':
            ch_fft = self._calc_rfft_channels(np.mean(ch_data[:,4:8,:], axis=2, dtype=np.float32))
            
        self.radar_param.sys.frame_duration = 103*1e-3
        self.radar_param.sys.shape_set_repetition = 16
        self.n_frames_spectrogram = np.uint32(np.divide(np.abs(self.waterfall_spectrogram_time), 
                                                        self.radar_param.sys.frame_duration))

        if self.max_value_type == 'range':
            fft_len = int(self.max_value/(self.radar_param.sys.max_range/ch_fft.shape[0]))
        elif self.max_value_type == 'freq':
            fft_len = int(self.max_value*1e3/(self.radar_param.sys.max_dsp_freq/ch_fft.shape[0]))
        
        if fft_len != self.spectogram_map.shape[1] or \
           self.n_frames_spectrogram != self.spectogram_map.shape[0]:
            self.spectogram_map = np.zeros((self.n_frames_spectrogram, fft_len, 4), dtype=np.float32)
        
        self.spectogram_map = np.concatenate((ch_fft[np.newaxis,0:fft_len,:],
                                              self.spectogram_map[0:self.n_frames_spectrogram-1,:,:]),
                                             axis=0, dtype=np.float32) 

        return np.array(self.spectogram_map, dtype=np.float32)

    def _prepare_spectrogram_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Waterfall Spectrogram':
            return {'Channel 1': ch_data[:,:], 'Channel 2': np.zeros((1,1,1), dtype=np.float32)}
        
    def _calc_range_doppler(self, ch_data: np.ndarray) -> np.ndarray:
        ch_data = ch_data.transpose(2, 0, 1)
        if self.range_doppler_tab_index == 'TX1' or \
           self.main_tab_index == 'Range Doppler Azimuth':
            ch_data = ch_data[:,:,0:4]
        elif self.range_doppler_tab_index == 'TX2':
            ch_data = ch_data[:,:,4:8]
        
        n_samples = ch_data.shape[1]
        ch_fft_range = np.fft.rfft(ch_data, 
                        n=n_samples+self.padding_len-1, 
                        axis=1)
        
        # hanning_window = np.hanning(ch_data.shape[0])

        # self.fft_window = hanning_window[:, np.newaxis, np.newaxis]
        
        # ch_fft_range_win = ch_fft_range * self.fft_window

        ch_fft_distance = (np.fft.fft(ch_fft_range, n=ch_data.shape[0]+self.padding_len, axis=0))
        # ch_fft_distance = (np.abs(ch_fft_distance) + np.finfo(float).eps).astype(np.float32)

        range_doppler =  (20*np.log10(np.abs(np.fft.fftshift(ch_fft_distance, axes=0)) \
                        + np.finfo(float).eps)).astype(np.float32)
        if self.max_value_type == 'range':
            self.range_doppler_map = (range_doppler[0:range_doppler.shape[0],
                                                    0:int(self.max_value/(self.radar_param.sys.max_range
                                                                        / range_doppler.shape[1])),:])
        elif self.max_value_type == 'freq':
            self.range_doppler_map = (range_doppler[0:range_doppler.shape[0],:,:])
        return np.array(self.range_doppler_map, dtype=np.float32)
    
    def _prepare_range_doppler_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Range Doppler':
            return {'Channel 1': ch_data, 'Channel 2': np.zeros((1,1,1), dtype=np.float32)}

        
    def _calc_range_azimuth(self, processed_data_cube: np.ndarray) -> np.ndarray:
        data_cube = np.array(processed_data_cube[:,:,0], dtype=np.complex64)
        az = np.deg2rad(np.linspace(-90,90,int(18*4+1)))
        n = np.arange(8)
        k = 2 * np.pi / self.radar_param.sys.lambda_freq[0]

        # Steering matrix, shape: (Number of Azimuth Angles, Number of Antenna Elements)
        self.v = np.exp(-1j * k * 0.001 * n * np.sin(az)[:, np.newaxis])
        
        self.range_azimuth_map = np.zeros((len(az), data_cube.shape[0]), dtype = np.float32)
        
        for m in range(len(az)):
            self.range_azimuth_map[m,:] = np.abs(np.sum(
                data_cube * self.v[m,:], axis=1)).astype(np.float32)
        if self.max_value_type == 'range':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value/(self.radar_param.sys.max_range
                                                                                 /self.range_azimuth_map.shape[1]))]
        elif self.max_value_type == 'freq':
            self.range_azimuth_map = self.range_azimuth_map[0:self.range_azimuth_map.shape[0],
                                                            0:int(self.max_value/(self.radar_param.sys.max_dsp_freq * 1e-3
                                                                                /self.range_azimuth_map.shape[1]))]
            
        return np.array(self.range_azimuth_map, dtype=np.float32)

    def _prepare_range_azimuth_output_format(self, ch_data: np.ndarray) -> dict:
        if self.main_tab_index == 'Range Azimuth':
            return {'Channel 1': ch_data, 'Channel 2': np.zeros((1,1,1), dtype=np.float32)}
        
    def _calc_waterfall_azimuth(self, preprocessed_data: np.ndarray) -> dict:
        spectogram_map = self._calc_spectogram(preprocessed_data)
        range_azimuth_map = self._calc_range_azimuth(preprocessed_data)
        return {'Channel 1': range_azimuth_map, 'Channel 2': spectogram_map}
    
    def _calc_range_doppler_azimuth(self, preprocessed_data: np.ndarray) -> dict:
        range_doppler_map = self._calc_range_doppler(preprocessed_data)
        range_azimuth_map = self._calc_range_azimuth(preprocessed_data)
        return {'Channel 1': range_azimuth_map, 'Channel 2': range_doppler_map}
    
    
