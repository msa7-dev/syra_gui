import numpy as np
from pathlib import Path

# ==============================================================================
# Class Name: MIRA_RADAR_PARAMETER
# ==============================================================================
class MIRA_RADAR_PARAMETER():
    def __init__(self) -> None:
        self.gui  = MIRA_RADAR_GUI_PARAMETER()
        self.dsp  = MIRA_RADAR_DSP_PARAMETER()
        self.sys  = MIRA_RADAR_SYS_PARAMETER()
        self.mon  = MIRA_RADAR_MON_PARAMETER()
        self.meas = MIRA_RADAR_MEAS_PARAMETER()
        self.rply = MIRA_RADAR_RPLY_PARAMETER()
        self.remt = MIRA_RADAR_REMT_PARAMETER()

# ==============================================================================
# Class Name: MIRA_RADAR_DSP_PARAMETER
# ==============================================================================
class MIRA_RADAR_DSP_PARAMETER():
    def __init__(self) -> None:
        self.axis_max_value = np.uint32(0)
        self.padding_len = np.uint16(0)
        self.window_func = str('')
        self.axis_unit = str('')
        
        # DSP HP Filter Parameters
        self.hp_filter_type = str('')
        self.hp_filter_order = np.uint8(0)
        self.hp_filter_cutoff = np.uint32(0)
        

# ==============================================================================
# Class Name: MIRA_RADAR_MON_PARAMETER
# ==============================================================================
class MIRA_RADAR_MON_PARAMETER():
    def __init__(self) -> None:
        self.duration_frame_counter = np.uint32(0)
        self.duration_time = np.float32(0)
        self.sadc_output_mode = np.uint8(0)
        self.datarate = np.float32(0)
        self.sadc_gain = np.uint8(0)
        self.sadc_tx1_power_value = np.float32(0)
        self.sadc_tx2_power_value = np.float32(0)
        self.temperature = np.float32(0)
        self.chip_version_digital_id = str('')
        self.chip_version_rf_id = str('')
        self.chip_id = str('')
        self.manufacturer_usb = str('')
        self.product_usb = str('')
        self.serial_usb = str('')
        self.sykno_product_name = str('')
        
# ==============================================================================
# Class Name: MIRA_RADAR_SYS_PARAMETER
# ==============================================================================
class MIRA_RADAR_SYS_PARAMETER():
    def __init__(self) -> None:
        self.rx_active_antennas = np.zeros((8), dtype=np.uint8)
        self.tx_active_antennas = np.zeros((8), dtype=np.uint8)
        self.tx_power = np.zeros((8,2), dtype=np.uint8)
        
        self.fullscale_voltage = np.float32(1200)
        self.waterfall_spectrogram_time = np.float32(1)
        self.plot_axis_max_value = np.float32(0)
        self.curr_plot_ampl_limit = np.uint8(0)
        self.plot_ampl_limit_min = np.zeros((8), dtype=int)
        self.plot_ampl_limit_max = np.zeros((8), dtype=int)
        self.curr_select_axis_unit = str('')
        
        self.min_range = np.float32(0)
        self.max_range = np.float32(0)
        self.resolution_range = np.float32(0)
        
        self.max_velocity = np.zeros((4,), dtype=np.float32)
        self.resolution_velocity = np.zeros((4,), dtype=np.float32)
        
        self.min_angle = np.float32(0)
        self.max_angle = np.float32(0)
        self.resolution_angle = np.float32(0)
        
        self.pulse_repetition_frequency = np.float32(0)
        self.pulse_repetition_interval = np.float32(0)
        self.coherent_pulse_interval = np.float32(0)
        self.n_fifo_overhead = np.uint8(0)
        self.frames_per_second = np.float32(0)
        self.frame_duration = np.float32(0)
        self.mid_frequency = np.zeros((8,), np.float32)
        self.lambda_freq = np.zeros((8,), np.float32)
        self.start_frequency = np.zeros((8,), np.float32)
        self.end_frequency = np.zeros((8,), np.float32)
        self.ramp_bandwidth = np.zeros((8,), np.float32)
        self.ramp_steps = np.zeros((8,), np.float32)
        self.ramp_time = np.zeros((8,), np.float32)
        self.ramp_slope = np.zeros((8,), np.float32)
        self.max_dsp_freq = np.float32(0)
        self.sampling_frequency = np.float32(0)
        self.sampling_interval_time = np.float32(0)
        self.chirp_time = np.zeros((8,), np.float32)
        self.num_chirps_frame = np.float32(0)
        self.frame_samples = np.float32(0)
        self.frame_chirps = np.float32(0)
        self.n_samples_per_chirp = np.zeros((8), np.int16)
        self.shape_set_repetition = np.float32(0)
        self.n_frames_range_doppler = np.uint32(0)
        
        self.sync_word0 = np.uint32(0)
        self.sync_word1 = np.uint32(0)
        self.frame_cnt = np.uint32(0)
        self.max_frame_cnt = np.uint32(0)
        self.shape_grp_cnt = np.uint32(0)
        self.shape_repetition = np.zeros((4,), np.uint32)
        self.shape_set_repetition = np.uint32(0)
        self.n_active_shape = np.zeros((4,), dtype=np.uint8)
        
        # Base Band Settings
        self.bgt_vga_gain = np.zeros((8), dtype=np.uint8)
        self.bgt_hp_fc = np.zeros((8), dtype=np.uint8)
        self.bgt_hp_gain = np.zeros((8), dtype=np.uint8)

        # Chirp Timing - timings 
        self.t_start = np.float32(0)
        self.t_end = np.float32(0)
        self.t_paen = np.float32(0)
        self.t_sstart = np.float32(0)

        # Frame Timing - timings once each frame
        # Wake Up Time
        self.t_wkup = np.uint32(0)
        # Sensor Init Time 0
        self.t_init0 = np.float32(0)
        # Sensor Init Time 1
        self.t_init1 = np.float32(0)
        # Frame End Delay
        self.t_fed = np.float32(0) 
        
        # Shape End Delay - 4 elements one for each shape
        self.t_sed = np.zeros((4,), dtype=np.float32)
        
        # Chirp End Delay - Up-Chirp first 4 elements, Down-Chirp last 4
        self.t_ed = np.zeros((8,), dtype=np.float32)
        
        self.pulse_repetition_time = np.float32(0)
        
        self.rf_test_ton = np.int32(1)
        self.rf_test_mode_en = bool(False)
        self.rf_test_mode_en_channels = [False, False, 
                                         False, False]
        self.rf_antenna = np.uint8(0)

# ==============================================================================
# Class Name: MIRA_RADAR_GUI_PARAMETER
# ==============================================================================
class MIRA_RADAR_GUI_PARAMETER():
    def __init__(self) -> None:
        self.fps = np.uint8(0)
        self.project_name = str('')
        self.root_sys_path = Path()
        self.bgt_register_file_path = Path()
        self.auto_connect_device = False
        self.active_tx = [False, False]
        self.active_rx = [False, False, 
                          False, False]
        self.hp_ch_rx = [False, False,
                         False, False]
        
# ==============================================================================
# Class Name: MIRA_RADAR_MEAS_PARAMETER
# ==============================================================================
class MIRA_RADAR_MEAS_PARAMETER():
    def __init__(self) -> None:
        self.folder_path = Path()
        self.session_label = str('')
        self.record_headless = False
        self.measurement_flag = False
        self.recording_duration = np.uint32(0)
        self.recording_n_frames = np.uint32(0)

# ==============================================================================
# Class Name: MIRA_RADAR_RPLY_PARAMETER
# ==============================================================================
class MIRA_RADAR_RPLY_PARAMETER():
    def __init__(self) -> None:
        self.replay_flag = False
        self.load_path_hdf5 = Path()
        
# ==============================================================================
# Class Name: MIRA_RADAR_REMT_PARAMETER
# ==============================================================================
class MIRA_RADAR_REMT_PARAMETER():
    def __init__(self) -> None:
        self.remote_flag = False
        self.client_flag = False
        self.client_ssh_pwd = ''
        self.client_ip_port = []
        self.client_ssh_name = ''