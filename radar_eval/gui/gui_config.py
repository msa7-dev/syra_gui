from typing import Callable, Dict, List, Any

Function = Callable[[None], None]
# ==============================================================================
# Class Name: MIRA_FUNC_PIPELINE
# ==============================================================================
class MIRA_FUNC_PIPELINE():
    def __init__(self, qt_self) -> None:
        self.qt_self = qt_self
        self._create_func_compose_dict()

    def call_plot_pipeline(self, pipeline_name: str, input_data: Any) -> Any:
        if pipeline_name in self.composed_func_pipeline_dict:
            return self.composed_func_pipeline_dict[pipeline_name](input_data)
        else:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")

    def create_callable_pipeline(self, functions: List[Function]) -> Callable[[Any], Any]:
        def _callable_pipeline(input_data):
            for func in functions:
                input_data = func(input_data)
            return input_data
        return _callable_pipeline
    
    # Helper function for composing functions
    def _compose_functions(self, functions: List[Function]) -> Function:
        def _composed(x):
            for f in functions:
                x = f(x)
            return x
        return _composed

    def _create_func_compose_dict(self) -> None:
        self.func_pipeline_dict: Dict[str, List[Function]] = {
            'Time':                  [self.qt_self.check_plot_shape, 
                                      self.qt_self.set_time_signal,
                                      self.qt_self.plot_ready],
            'Spectrum':              [self.qt_self.check_plot_shape,
                                      self.qt_self.set_spectrum,
                                      self.qt_self.plot_ready],
            'Waterfall Spectrogram': [self.qt_self.check_plot_shape,
                                      self.qt_self.set_spectrogram,
                                      self.qt_self.plot_ready],
            'Range Doppler':         [self.qt_self.check_plot_shape,
                                      self.qt_self.set_range_doppler,
                                      self.qt_self.plot_ready],
            'Range Azimuth':         [self.qt_self.check_plot_shape,
                                      self.qt_self.set_range_azimtuh,
                                      self.qt_self.plot_ready],
            'Waterfall Azimuth':     [self.qt_self.check_plot_shape,
                                      self.qt_self.set_waterfall_azimtuh,
                                      self.qt_self.plot_ready],
            'Range Doppler Azimuth': [self.qt_self.check_plot_shape,
                                      self.qt_self.set_range_doppler_azimtuh,
                                      self.qt_self.plot_ready],
            'Demo':                  [self.qt_self.check_plot_shape,
                                      self.qt_self.set_waterfall_range_doppler_azimtuh,
                                      self.qt_self.plot_ready]
        }
        self.composed_func_pipeline_dict: Dict[str, Function] = {
            name: self._compose_functions(func_list) 
            for name, func_list in self.func_pipeline_dict.items()
        }
        
# ==============================================================================
# Class Name: MIRA_WIDGET_VALUES
# ==============================================================================
class MIRA_WIDGET_VALUES():
    def __init__(self) -> None:
        self._create_values_combo_box()
        
    def _create_values_combo_box(self):
        self.axis_unit_select_list = ['range', 'freq']
        
        self.axis_range_select_list = ['rmax', '1 m', '2 m', '3 m', 
                                       '4 m', '5 m', '10 m', '15 m',
                                       '20 m', '25 m', '30 m']
        
        self.axis_freq_select_list = ['fmax', '100 kHz', '150 kHz',
                                      '200 kHz', '250 kHz','300 kHz',
                                      '400 kHz', '500 kHz', '600 kHz',
                                      '700 kHz', '800 kHz', '900 kHz',
                                      '1000 kHz', '1100 kHz', '1200 kHz',
                                      '1300 kHz', '1400 kHz', '1500 kHz']
        
        self.window_func_list = ['hanning', 'hamming', 'blackman', 
                                 'kaiser', 'bartlett', 'gaussian',
                                 'flattop', 'chebyshev', 'lanczos', 'None']
        
        self.padding_len_list = ['0', '2', '4', '8', '16', '32', '64', '128', 
                                 '256', '512', '1024', '2048', '4096', '8192']
        
        self.vga_gain_list = ['0 dB', '5 dB', '10 dB', '15 dB', '20 dB', '25 dB', '30 dB']
        
        self.bgt_hp_fc_list = ['20 kHz', '45 kHz', '70 kHz', '80 kHz']
        
        self.bgt_hp_gain_list = ['18 dB', '30 dB']
        
        self.dsp_hp_filter_order_list = ['2', '1', '2', '3', '4', '5', '6', '7', '8', '0']
        
        self.dsp_hp_filter_type_list = ['sos', 'ba', 'None']
        
        self.dsp_hp_filter_cutoff_list = ['20 kHz', '5 kHz', '10 kHz', '15 kHz', '20 kHz', '25 kHz', 
                                          '30 kHz', '35 kHz', '40 kHz', '45 kHz', '50 kHz',
                                          '55 kHz', '60 kHz', '65 kHz', '70 kHz', '75 kHz',
                                          '80 kHz', '85 kHz', '95 kHz', '100 kHz', '0 kHz']
        
        self.measurement_duration_list = ['Inf.', '1 s', '10 s', '30 s', '1 min', '2 min',
                                          '5 min', '15 min', '30 min', '1 h', '2 h', '3 h']
        
        self.recodring_n_frames_list = ['Inf.', '1', '2', '4', '8', '16', '32', '64', '128',
                                        '256', '512', '1024', '2048', '4096', '8192',
                                        '16384', '32768', '65536', '132072', '262144']
        
        self.plot_select_dbfs_min_list = ['30 dBFS', '100 dBFS', '90 dBFS', '80 dBFS',
                                          '70 dBFS', '60 dBFS', '50 dBFS', '40 dBFS',
                                          '30 dBFS', '20 dBFS', '10 dBFS', '0 dBFS', 
                                          '-10 dBFS', '-20 dBFS', '-30 dBFS', '-40 dBFS',
                                          '-50 dBFS', '-60 dBFS', '-70 dBFS', '-80 dBFS']
        
        self.plot_select_dbfs_max_list = ['-60 dBFS', '0 dBFS', '-10 dBFS', '-20 dBFS',
                                          '-30 dBFS', '-40 dBFS', '-50 dBFS', '-60 dBFS', 
                                          '-70 dBFS', '-80 dBFS', '-90 dBFS', '-110 dBFS', 
                                          '-110 dBFS', '-120 dBFS', '-130 dBFS',
                                          '-140 dBFS', '-150 dBFS']

        self.plot_select_mv_max_raw_data_list = ['0 mV', '50 mV', '100 mV', '150 mV',
                                               '200 mV', '250 mV', '300 mV', '350 mV', 
                                               '400 mV', '450 mV', '500 mV', '550 mV', '600 mV']
        
        self.plot_select_mv_min_raw_data_list = ['1200 mV', '1150 mV', '1100 mV', '1050 mV', 
                                                 '1000 mV', '950 mV', '900 mV', '850 mV',
                                                 '800 mV', '750 mV', '700 mV', '650 mV', '600 mV']

        self.plot_select_mv_max_dsp_data_list = ['-1000 mV', '-950 mV', '-900 mV', '-850 mV',
                                                 '-800 mV', '-750 mV', '-700 mV', '-650 mV',
                                                 '-600 mV', '-550 mV', '-500 mV', '-450 mV',
                                                 '-400 mV', '-350 mV', '-300 mV', '-250 mV',
                                                 '-200 mV', '-150 mV', '-100 mV', '-50 mV','0 mV']
        
        self.plot_select_mv_min_dsp_data_list = ['1000 mV', '950 mV','900 mV', '850 mV',
                                                 '800 mV', '750 mV', '700 mV', '650 mV',
                                                 '600 mV', '550 mV', '500 mV', '450 mV',
                                                 '400 mV', '350 mV', '300 mV', '250 mV',
                                                 '200 mV', '150 mV', '100 mV', '50 mV','0 mV']
        
        self.waterfall_spectrogram_time_list = ['5 s', '10 s', '15 s', '20 s', 
                                                '25 s', '30 s', '35 s', '40 s',
                                                '45 s', '50 s', '55 s', '1 min',
                                                '2 min', '3 min', '4 min', '5 min']

        self.if_test_ton_list = ['50 kHz', '100 kHz', '200 kHz', 
                                 '300 kHz', '400 kHz', '500 kHz',
                                 '600 kHz', '700 kHz', '800 kHz',
                                 '900 kHz', '1000 kHz', '1100 kHz',
                                 '1200 kHz', '1200 kHz', '1300 kHz',
                                 '1400 kHz', '1500 kHz']
        
        self.rf_antenna_combo_box_list = ['Antenna type 1', 'Antenna type 2']
        
        self.gui_fps_list = ['60', '1', '5', '10', '15', '20', '25',
                             '30', '35', '40', '45', '50', '55', '60']
        
        
        self.set_sample_rate_list = ['1.00000 MHz', '2.00000 MHz', '2.10526 MHz',
                                     '2.22222 MHz', '2.28571 MHz',
                                     '2.42424 MHz', '2.50000 MHz',
                                     '2.58065 MHz', '2.66667 MHz', 
                                     '2.75862 MHz', '2.85714 MHz']
        
        self.set_bandwidth_lower_list = ['58.00 GHz', '58.25 GHz', '58.50 GHz', '58.75 GHz',
                                         '59.00 GHz', '59.25 GHz', '59.50 GHz', '59.75 GHz',
                                         '60.00 GHz', '60.25 GHz', '60.50 GHz', '60.75 GHz',
                                         '61.00 GHz', '61.25 GHz', '61.50 GHz', '61.75 GHz',
                                         '62.00 GHz', '62.25 GHz', '62.50 GHz', '62.75 GHz',]
        
        self.set_bandwidth_upper_list = ['63.00 GHz', '62.75 GHz', '62.50 GHz', '62.25 GHz',  
                                         '62.00 GHz', '61.75 GHz', '61.50 GHz', '61.25 GHz',  
                                         '61.00 GHz', '60.75 GHz', '60.50 GHz', '60.25 GHz',  
                                         '60.00 GHz', '59.75 GHz', '59.50 GHz', '59.25 GHz', 
                                         '59.00 GHz', '58.75 GHz', '58.50 GHz', '58.25 GHz', ] 

        self.set_chirp_samples_list = ['64', '128', '256', '512', '1024', '2048']
        
        self.set_chirp_end_delay_list = ['10.0375 µs', '25.0375 µs', '50.0500 µs', '100.0620 µs', 
                                         '249.7120 µs', '499.3250 µs', '748.9130 µs', '998.538 µs']
        
        self.set_shape_repetition_list = ['1', '2', '4', '8', '16', '32', 
                                          '64', '128', '256', '512', '1024']
        
        self.set_shape_end_delay_list = ['10.0375 µs', '25.0375 µs', '50.0500 µs', '100.0620 µs', 
                                         '249.7120 µs', '499.3250 µs', '748.9130 µs', '998.538 µs']
        
        self.set_shape_set_repetition_list = ['1', '2', '4', '8', '16', '32', 
                                              '64', '128', '256', '512', '1024']
        
        self.set_shape_set_end_delay_list = ['249.7120 µs', '499.3250 µs', '748.9130 µs', '998.538 µs',
                                             '1.49772 ms', '2.49613 ms', '4.99214 ms', '7.47536 ms',
                                             '9.98415 ms']
        