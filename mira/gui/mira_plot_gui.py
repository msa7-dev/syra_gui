import __init__
import numpy as np
import configparser
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from mira.rsys.mira_radar_sys import MIRA_RADAR_PARAMETER

# ==============================================================================
# Class Name: MIRA_PLOTTER
# ==============================================================================
class MIRA_PLOTTER():
    def __init__(self, qt_self):
        self.qt_self = qt_self
        self.radar_param: MIRA_RADAR_PARAMETER = qt_self.radar_param
        self.time_signal = TIME_SIGNAL_PLOTTER(qt_self)  
        self.spectrum = SPECTRUM_PLOTTER(qt_self)
        self.spectrogram = SPECTROGRAM_PLOTTER(qt_self)
        self.range_doppler = RANGE_DOPPLER_PLOTTER(qt_self)
        self.range_azimuth = RANGE_AZIMUTH_PLOTTER(qt_self)
        
    def calc_plot_axis(self):
        padding_len = self.radar_param.dsp.padding_len
        self.time_axis = np.linspace(0, self.radar_param.sys.ramp_time[0]*1e6,
                                     np.uint16(self.radar_param.sys.n_samples_per_chirp[0]))
        self.freq_axis = np.linspace(0, self.radar_param.sys.max_dsp_freq*1e-3,
                                     int((self.radar_param.sys.n_samples_per_chirp[0]+padding_len)/2))
        self.range_axis = np.linspace(0, self.radar_param.sys.max_range,
                                      int((self.radar_param.sys.n_samples_per_chirp[0]+padding_len)/2))
        self.ch_range_doppler_buf = np.zeros((int(self.radar_param.sys.n_frames_range_doppler),
                                              self.radar_param.sys.n_samples_per_chirp[0], 4))
        self._reinit_axis()
        return {'freq_axis': self.freq_axis, 'range_axis': self.range_axis}

    def _reinit_axis(self) -> None:
        self.spectrum.select_axis_unit()
        self.spectrogram.init_plot_parameters()
        self.range_doppler.init_plot_parameters()
        self.range_azimuth.init_plot_parameters()
        
# ==============================================================================
# Class Name: MIRA_PLOT_CONFIG
# ==============================================================================
class MIRA_PLOT_CONFIG():
    def __init__(self, qt_self):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)

        MIRA_PLOT_TITLE_FONT = int(self.config.get("MIRA_6024_EVAL_GUI",
                                                   "MIRA_PLOT_TITLE_FONT"))
        self.plot_title_font = f'{MIRA_PLOT_TITLE_FONT}pt'

        MIRA_PLOT_AXIS_LABEL_FONT = int(self.config.get("MIRA_6024_EVAL_GUI", 
                                                        "MIRA_PLOT_AXIS_LABEL_FONT"))
        self.axis_label_font = QtGui.QFont()
        self.axis_label_font.setPixelSize(MIRA_PLOT_AXIS_LABEL_FONT)
        
        MIRA_PLOT_AXIS_NUMBERS_FONT = int(self.config.get("MIRA_6024_EVAL_GUI", 
                                                          "MIRA_PLOT_AXIS_NUMBERS_FONT"))
        self.axis_numbers_font = QtGui.QFont()
        self.axis_numbers_font.setPixelSize(MIRA_PLOT_AXIS_NUMBERS_FONT)
        
        self.axis_label_offset = int(self.config.get("MIRA_6024_EVAL_GUI", 
                                                     "MIRA_PLOT_AXIS_LABEL_OFFSET"))

        MIRA_PLOT_BACKGROUND_COLOR = self.config.get('MIRA_6024_EVAL_GUI', 
                                                     'MIRA_PLOT_BACKGROUND_COLOR')
        color_tuple_plot_background = tuple(map(int, MIRA_PLOT_BACKGROUND_COLOR.split(',')))
        self.plot_background = QColor(*color_tuple_plot_background)
        
        MIRA_PLOT_TEXT_COLOR = self.config.get('MIRA_6024_EVAL_GUI', 
                                               'MIRA_PLOT_TEXT_COLOR')
        color_tuple_plot_text = tuple(map(int, MIRA_PLOT_TEXT_COLOR.split(',')))
        self.plot_text_color = QColor(*color_tuple_plot_text)

        MIRA_SHEET_COLOR = self.config.get('MIRA_6024_EVAL_GUI', 'MIRA_SHEET_COLOR')
        color_tuple_sheet_color = tuple(map(int, MIRA_SHEET_COLOR.split(',')))
        qt_self.setStyleSheet(f"background-color: rgb({color_tuple_sheet_color});")
        
        self.mira_plot_pen_width = int(self.config.get("MIRA_6024_EVAL_GUI", 
                                                       "MIRA_PLOT_PEN_WIDTH"))
        MIRA_PLOT_PEN_COSMETIC = str(self.config.get("MIRA_6024_EVAL_GUI", 
                                                     "MIRA_PLOT_PEN_COSMETIC"))
        self.pen_cosmetic_bool = True if MIRA_PLOT_PEN_COSMETIC == "True" else False
        
        self.plot_pens = self.init_pen_colors()
        self.init_color_lut(qt_self.radar_param.sys.plot_ampl_limit_min, qt_self.radar_param.sys.plot_ampl_limit_max)


    def init_pen_colors(self):
        num_pens = 8
        pen_colors = []

        for i in range(1, num_pens + 1):
            config_key = f'MIRA_PLOT_COLOR_PEN_{i}'
            color_str = self.config.get('MIRA_6024_EVAL_GUI', config_key)
            color_tuple = tuple(map(int, color_str.split(',')))

            pen = pg.mkPen(cosmetic=self.pen_cosmetic_bool, 
                           color=QColor(*color_tuple), 
                           width=self.mira_plot_pen_width)
            pen_colors.append(pen)
            
        return pen_colors

    def init_color_lut(self, min, max):
        pos = np.array([0.0, 0.125, 0.375, 0.64, 0.91, 1.0])
        color = np.array([
            [0, 0, 128, 255],    # Dark Blue
            [0, 0, 255, 255],    # Blue
            [0, 255, 255, 255],  # Cyan
            [255, 255, 0, 255],  # Yellow
            [255, 0, 0, 255],    # Red
            [128, 0, 0, 255],    # Dark Red
        ], dtype=np.ubyte)    
        self.lut = pg.ColorMap(pos, color)
# ==============================================================================
# Class Name: TIME_SIGNAL_PLOTTER
# ==============================================================================
class TIME_SIGNAL_PLOTTER():
    def __init__(self, qt_self):
        self.plot_config = MIRA_PLOT_CONFIG(qt_self)
        self.plot_time_list = [qt_self.plot_time_raw_data, 
                               qt_self.plot_time_dsp_output]
        self.init_plot_parameters()

    def init_plot_parameters(self):
        self.plotlines = {}
        titles = ['Raw Data', 'DSP Output']
        for i, plot_time in enumerate(self.plot_time_list):
            self.create_spectrogram_plot(plot_time, titles[i])
             
    def create_spectrogram_plot(self, plot, title):
        names = ['RX1 TX1', 'RX1 TX2', 'RX2 TX1', 'RX2 TX2',
                 'RX3 TX1', 'RX3 TX2', 'RX4 TX1', 'RX4 TX2']
        
        for name, pen in zip(names, self.plot_config.plot_pens):
            plotline = pg.PlotDataItem(name=name, pen=pen)
            plot.addLegend()
            plot.addItem(plotline)
            self.plotlines[title+f' {name}'] = plotline  # Add the plotline to the dictionary with name as the key

        plot.setBackground(self.plot_config.plot_background)
        plot.setTitle(title, size=self.plot_config.plot_title_font)
        
        self.configure_axis(plot)

        plotline.getViewBox().setAutoVisible(x=False, y=False)

    def configure_axis(self, plot):
        # Plot Title
        plot.setTitle("Time Signal", size=self.plot_config.plot_title_font)  
        
        # X-Axis
        x_axis = plot.getAxis("bottom")
        x_axis.label.setFont(self.plot_config.axis_numbers_font)
        x_axis.setPen(self.plot_config.plot_text_color)
        x_axis.setTextPen(self.plot_config.plot_text_color)
        x_axis.setTickFont(self.plot_config.axis_numbers_font)
        x_axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        plot.setLabel("bottom", "Time in us")  

        # Y-Axis
        y_axis= plot.getAxis("left")
        y_axis.label.setFont(self.plot_config.axis_numbers_font)
        y_axis.setPen(self.plot_config.plot_text_color)
        y_axis.setTextPen(self.plot_config.plot_text_color)
        y_axis.setTickFont(self.plot_config.axis_numbers_font)
        y_axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        plot.setLabel("left", "Voltage in mV")  
        plot.setLogMode(x=False, y=False)
        plot.showGrid(True, True)
        
    def set_plot_limits(self, x_min_max: tuple, y_min_max: tuple):
        for plot in self.plot_time_list:
            plot.setXRange(*x_min_max)
            plot.setYRange(*y_min_max)
        
    def reset_plot_lines(self):
        for _, plotline in self.plotlines.items():
            plotline.clear()
            plotline.setData([-9999,-9999])  # Assuming this is how you wish to reset the lines


# ==============================================================================
# Class Name: SPECTRUM_PLOTTER
# ==============================================================================
class SPECTRUM_PLOTTER():
    def __init__(self, qt_self):
        self.plot_config = MIRA_PLOT_CONFIG(qt_self)
        self.plot_spectrum = qt_self.plot_spectrum
        self.radar_param = qt_self.radar_param
        self.init_plot_parameters()

    def init_plot_parameters(self):
        self.plotlines = {}
        names = ['RX1 TX1', 'RX1 TX2', 'RX2 TX1', 'RX2 TX2', 
                 'RX3 TX1', 'RX3 TX2', 'RX4 TX1', 'RX4 TX2']
        for name, pen in zip(names, self.plot_config.plot_pens):
            plotline = pg.PlotDataItem(name=name, pen=pen)
            self.plot_spectrum.addLegend()
            self.plot_spectrum.addItem(plotline)
            self.plotlines['Spectrum'+f' {name}'] = plotline  

        # Set the background
        self.plot_spectrum.setBackground(self.plot_config.plot_background)

        # Plot Title
        self.plot_spectrum.setTitle("Spectrum", size=self.plot_config.plot_title_font)

        # X-Axis
        x_axis = self.plot_spectrum.getAxis("bottom")
        x_axis.label.setFont(self.plot_config.axis_numbers_font)
        x_axis.setPen(self.plot_config.plot_text_color)
        x_axis.setTextPen(self.plot_config.plot_text_color)
        x_axis.setTickFont(self.plot_config.axis_numbers_font)
        x_axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        self.select_axis_unit()
        # Y-Axis
        y_axis = self.plot_spectrum.getAxis("left")
        y_axis.label.setFont(self.plot_config.axis_numbers_font)
        y_axis.setPen(self.plot_config.plot_text_color)
        y_axis.setTextPen(self.plot_config.plot_text_color)
        y_axis.setTickFont(self.plot_config.axis_numbers_font)
        y_axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        self.plot_spectrum.setLabel("left", "Magnitude in dB")
        self.plot_spectrum.setLogMode(x=False, y=False)
        self.plot_spectrum.showGrid(True, True)

    def select_axis_unit(self) -> None:
        if self.radar_param.sys.curr_select_axis_unit == 'freq':
            self.plot_spectrum.setLabel("bottom", "Frequency in kHz")
        else:
            self.plot_spectrum.setLabel("bottom", "Range in m")
            
    def set_plot_limits(self, x_min_max: tuple, y_min_max: tuple) -> None:
        self.plot_spectrum.setXRange(*x_min_max)
        self.plot_spectrum.setYRange(*y_min_max)

    def reset_plot_lines(self):
        for name, plotline in self.plotlines.items():
            plotline.clear()
            plotline.setData([-9999, -9999])
            
# ==============================================================================
# Class Name: SPECTROGRAM_PLOTTER
# ==============================================================================
class SPECTROGRAM_PLOTTER():
    def __init__(self, qt_self):
        self.plot_config = MIRA_PLOT_CONFIG(qt_self)
        self.plot_spectrogram_list = [qt_self.plot_spectrogram_1, 
                                      qt_self.plot_spectrogram_2, 
                                      qt_self.plot_spectrogram_3, 
                                      qt_self.plot_spectrogram_4,
                                      qt_self.plot_spectrogram_5, 
                                      qt_self.plot_spectrogram_6,
                                      qt_self.plot_spectrogram_7, 
                                      qt_self.plot_spectrogram_8,
                                      qt_self.plot_waterfall_azimuth_spectrogram]
        self.radar_param = qt_self.radar_param
        
        self.init_plot_parameters()

    def init_plot_parameters(self):
        self.plotlines = {}
        self.plots = {}

        self.titles = ['Channel - RX1 TX1', 'Channel - RX2 TX1', 
                       'Channel - RX3 TX1', 'Channel - RX4 TX1',
                       'Channel - RX1 TX2', 'Channel - RX2 TX2',
                       'Channel - RX3 TX2', 'Channel - RX4 TX2',
                       'Waterfall - RX1_TX1']

        for plot_spectrogram, title in zip(self.plot_spectrogram_list, self.titles):
            self.create_spectrogram_plot(plot_spectrogram, title)

    def create_spectrogram_plot(self, plot, title):
        plotline = pg.ImageItem()
        plotline.setLookupTable(self.plot_config.lut.getLookupTable())

        plot.addItem(plotline)
        plot.setBackground(self.plot_config.plot_background)
        plot.setTitle(title, size=self.plot_config.plot_title_font)
        plotline.getViewBox().setAutoVisible(x=False, y=False)

        self.configure_axis(plot)

        index = title.split(' - ')[1]
        self.plotlines[f"Waterfall Spectrogram {index}"] = plotline
        self.plots[f"Waterfall Spectrogram {index}"] = plot


    def configure_axis(self, plot):
        axis = plot.getAxis("bottom")
        axis.label.setFont(self.plot_config.axis_numbers_font)
        axis.setPen(self.plot_config.plot_text_color)
        axis.setTextPen(self.plot_config.plot_text_color)
        axis.setTickFont(self.plot_config.axis_numbers_font)
        axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        if self.radar_param.sys.curr_select_axis_unit == 'freq':
            plot.setLabel("bottom", "Frequency in kHz")
        else:
            plot.setLabel("bottom", "Range in m")

        axis = plot.getAxis("left")
        axis.label.setFont(self.plot_config.axis_numbers_font)
        axis.setPen(self.plot_config.plot_text_color)
        axis.setTextPen(self.plot_config.plot_text_color)
        axis.setTickFont(self.plot_config.axis_numbers_font)
        axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        plot.setLabel("left", "Time in s")

    def set_plot_limits(self,
                        x_min_max: tuple,
                        y_min_max: tuple,
                        z_min_max: tuple):
        for plot_spectrogram in self.plot_spectrogram_list:
            plot_spectrogram.setXRange(*x_min_max)
            plot_spectrogram.setYRange(*y_min_max)
            
        for _, plotline in self.plotlines.items():
            plotline.setLevels(z_min_max)

    def set_transform(self,
                      x_min_max: tuple,
                      y_min_max: tuple, 
                      z_min_max: tuple,
                      spectogram_map_shape: tuple):

        for plot_spectrogram in self.plot_spectrogram_list:
            plot_spectrogram.setXRange(*x_min_max)
            plot_spectrogram.setYRange(*y_min_max)
            
        for _, plotline in self.plotlines.items():
            plotline.setLevels(z_min_max)

        scale_x = (x_min_max[1] - x_min_max[0]) / spectogram_map_shape[1]
        scale_y = (y_min_max[1] - y_min_max[0]) / spectogram_map_shape[0]
        tr = QtGui.QTransform()
        tr.scale(scale_x, scale_y)
        tr.translate(x_min_max[0] / (scale_x+np.finfo(float).eps), \
                     y_min_max[0] / (scale_y+np.finfo(float).eps))

        for _, plotline_spectrogram in self.plotlines.items():
            plotline_spectrogram.setTransform(tr)
            
    def clear_plot(self):
        for plot_spectrogram, title in zip(self.plot_spectrogram_list, self.titles):
            index = title.split(' - ')[1]
            self.plotlines[f"Waterfall Spectrogram {index}"].clear()
            self.plots[f"Waterfall Spectrogram {index}"].clear()
            self.create_spectrogram_plot(plot_spectrogram, title)

# ==============================================================================
# Class Name: RANGE_DOPPLER_PLOTTER
# ==============================================================================
class RANGE_DOPPLER_PLOTTER():
    def __init__(self, qt_self):
        self.plot_config = MIRA_PLOT_CONFIG(qt_self)
        self.plot_range_doppler_list = [qt_self.plot_range_doppler_1, 
                                        qt_self.plot_range_doppler_2, 
                                        qt_self.plot_range_doppler_3, 
                                        qt_self.plot_range_doppler_4,
                                        qt_self.plot_range_doppler_5, 
                                        qt_self.plot_range_doppler_6,
                                        qt_self.plot_range_doppler_7, 
                                        qt_self.plot_range_doppler_8, 
                                        qt_self.plot_range_doppler_azimuth_range_doppler] 
        self.radar_param = qt_self.radar_param
        self.init_plot_parameters()

    def init_plot_parameters(self):
        self.plotlines = {}
        self.plots = {}
        self.titles = ['Channel - RX1 TX1', 'Channel - RX2 TX1', 
                       'Channel - RX3 TX1', 'Channel - RX4 TX1',
                       'Channel - RX1 TX2', 'Channel - RX2 TX2', 
                       'Channel - RX3 TX2', 'Channel - RX4 TX2',
                       'Range Doppler - RX1_TX1',]

        for plot_range_doppler, title in zip(self.plot_range_doppler_list, self.titles):
            self.create_range_doppler_plot(plot_range_doppler, title)

    def create_range_doppler_plot(self, plot, title):
        plotline = pg.ImageItem()
        plotline.setLookupTable(self.plot_config.lut.getLookupTable())
        plot.addItem(plotline)
        plot.setBackground(self.plot_config.plot_background)
        plot.setTitle(title, size=self.plot_config.plot_title_font)

        self.configure_axis(plot)

        plotline.getViewBox().setAutoVisible(x=False, y=False)
        # plotline.setLevels((-40,40))
        
        index = title.split(' - ')[1]
        self.plotlines['Range Doppler' + f' {index}'] = plotline
        self.plots[f"Range Doppler {index}"] = plot

    def configure_axis(self, plot):
        axis = plot.getAxis("bottom")
        axis.label.setFont(self.plot_config.axis_numbers_font)
        axis.setPen(self.plot_config.plot_text_color)
        axis.setTextPen(self.plot_config.plot_text_color)
        axis.setTickFont(self.plot_config.axis_numbers_font)
        axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        plot.setLabel("bottom", "Velocity in m/s")

        axis = plot.getAxis("left")
        axis.label.setFont(self.plot_config.axis_numbers_font)
        axis.setPen(self.plot_config.plot_text_color)
        axis.setTextPen(self.plot_config.plot_text_color)
        axis.setTickFont(self.plot_config.axis_numbers_font)
        axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)
        if self.radar_param.sys.curr_select_axis_unit == 'freq':
            plot.setLabel("left", "Frequency in kHz")
        else:
            plot.setLabel("left", "Range in m")

    def set_plot_limits(self,
                        x_min_max: tuple,
                        y_min_max: tuple,
                        z_min_max: tuple):
        for plot_spectrogram in self.plot_range_doppler_list:
            plot_spectrogram.setXRange(*x_min_max)
            plot_spectrogram.setYRange(*y_min_max)
            
        for _, plotline in self.plotlines.items():
            plotline.setLevels(z_min_max)

    def set_transform(self, 
                      y_min_max: tuple,
                      x_min_max: tuple,
                      z_min_max: tuple,
                      range_doppler_map_shape: tuple):
        
        for plot_spectrogram in self.plot_range_doppler_list:
            plot_spectrogram.setXRange(*x_min_max)
            plot_spectrogram.setYRange(*y_min_max)
            
        for _, plotline in self.plotlines.items():
            plotline.setLevels(z_min_max)

        scale_x = (x_min_max[1] - x_min_max[0]) / range_doppler_map_shape[0]
        scale_y = (y_min_max[1] - y_min_max[0]) / range_doppler_map_shape[1]
        tr = QtGui.QTransform()
        tr.scale(scale_x, scale_y)
        tr.translate(x_min_max[0] / (scale_x+np.finfo(float).eps), \
                     y_min_max[0] / (scale_y+np.finfo(float).eps))

        for _, plotline_range_doppler in self.plotlines.items():
            plotline_range_doppler.setTransform(tr)

    def clear_plot(self):
        for plot_spectrogram, title in zip(self.plot_range_doppler_list, self.titles):
            index = title.split(' - ')[1]
            self.plotlines[f"Range Doppler {index}"].clear()
            self.plots[f"Range Doppler {index}"].clear()
            self.create_range_doppler_plot(plot_spectrogram, title)

# ==============================================================================
# Class Name: RANGE_AZIMUTH_PLOTTER
# ==============================================================================
class RANGE_AZIMUTH_PLOTTER():
    def __init__(self, qt_self):
        self.plot_config = MIRA_PLOT_CONFIG(qt_self)
        self.plot_range_azimuth_list = [qt_self.plot_range_azimuth, 
                                        qt_self.plot_waterfall_azimuth_range_azimuth,
                                        qt_self.plot_range_doppler_azimuth_azimuth]
        self.radar_param = qt_self.radar_param
        self.init_plot_parameters()

    def init_plot_parameters(self):
        self.plotlines = {}
        self.plots = {}
        self.indexs = ['Range Azimuth', 'Waterfall Azimuth', 'Range Doppler Azimuth']
        self.titles = ['Range Azimuth', 'Range Azimuth', 'Range Azimuth']
        for plot_range_azimuth, title, index in zip(self.plot_range_azimuth_list, self.titles, self.indexs):
            self.create_range_azimuth_plot(plot_range_azimuth, title, index)

    def create_range_azimuth_plot(self, plot, title, index):
        plotline = pg.ImageItem()
        plotline.setLookupTable(self.plot_config.lut.getLookupTable())
        plot.addItem(plotline)
        plot.setBackground(self.plot_config.plot_background)
        plot.setTitle(title, size=self.plot_config.plot_title_font)

        self.configure_axis(plot)

        plotline.getViewBox().setAutoVisible(x=False, y=False)
        plotline.setLevels((-40, 40))
        self.plotlines[f'{index}'] = plotline        
        self.plots[f"{index}"] = plot


    def configure_axis(self, plot):
        for axis_position in ["bottom", "left"]:
            axis = plot.getAxis(axis_position)
            axis.label.setFont(self.plot_config.axis_numbers_font)
            axis.setPen(self.plot_config.plot_text_color)
            axis.setTextPen(self.plot_config.plot_text_color)
            axis.setTickFont(self.plot_config.axis_numbers_font)
            axis.setStyle(tickTextOffset=self.plot_config.axis_label_offset)

        plot.setLabels(bottom="Azimuth Angle in Degree")
        
        if self.radar_param.sys.curr_select_axis_unit == 'freq':
            plot.setLabel("left", "Frequency in kHz")
        else:
            plot.setLabel("left", "Range in m")
            
    def set_plot_limits(self,
                        x_min_max: tuple,
                        y_min_max: tuple,
                        z_min_max: tuple):
        for plot in self.plot_range_azimuth_list:
            plot.setXRange(*x_min_max)
            plot.setYRange(*y_min_max)

        for _, plotline in self.plotlines.items():
            plotline.setLevels(z_min_max)

    def set_transform(self,
                      y_min_max: tuple,
                      x_min_max: tuple,
                      z_min_max: tuple,
                      range_azimuth_map_shape: tuple):
        self.set_plot_limits(x_min_max, y_min_max, z_min_max)
        scale_x = (x_min_max[1] - x_min_max[0]) / range_azimuth_map_shape[0]
        scale_y = (y_min_max[1] - y_min_max[0]) / range_azimuth_map_shape[1]
        tr = QtGui.QTransform()
        tr.scale(scale_x, scale_y)
        tr.translate(x_min_max[0] / (scale_x + np.finfo(float).eps), 
                     y_min_max[0] / (scale_y + np.finfo(float).eps))

        for _, plotline in self.plotlines.items():
            plotline.setTransform(tr)

    def clear_plot(self):
        for plot, index, title in zip(self.plot_range_azimuth_list, self.indexs, self.titles):
            self.plotlines[f"{index}"].clear()
            self.plots[f"{index}"].clear()
            self.create_range_azimuth_plot(plot, title, index)
