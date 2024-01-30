import __init__ 
import configparser
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog

class MIRA6024_BROWSER():
    def __init__(self, qt_self, browser_type: str):
        self.qt_self = qt_self
        self.browser_type = browser_type
        self.radar_param = self.qt_self.radar_param
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        MIRA_MEASUREMENT_PATH = self.config.get("MIRA_SAVE_MEASUREMENT",
                                                "MIRA_MEASUREMENT_PATH")
        MIRA_MEAS_PROJECT_NAME = self.config.get("MIRA_SAVE_MEASUREMENT",
                                                 "MIRA_MEAS_PROJECT_NAME")
        MIRA_SESSION_LABEL_NAME = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                 "MIRA_SESSION_LABEL_NAME")
        
        self.qt_self.mira_project_plainTextEdit.setPlainText(MIRA_MEAS_PROJECT_NAME)
        self.qt_self.session_label_plainTextEdit.setPlainText(MIRA_SESSION_LABEL_NAME)
        
        if self.browser_type == "bgt_reg_browser":
            caption="Select BGT-Register for MiRa6024|1A"
            default_dir = f"./mira/cfg/mira6024_projects/" 
            filter = "Text Files (*.txt)"
            file_path = f"{default_dir}/reg_bgt_default.txt"
            direcotry = "./"
            
        elif self.browser_type == "mira_meas_out_browser":
            caption="Select Measurement Dicretory MiRa6024|1A"
            default_dir = f"{MIRA_MEASUREMENT_PATH}/{MIRA_MEAS_PROJECT_NAME}"
            filter = None
            file_path = "./mira/meas/hdf5/"
            direcotry = "./mira/meas/hdf5/"
            
        elif self.browser_type == "mira_meas_in_browser":
            caption="Select MiRa6024|1A Measurement File"
            default_dir = f"{MIRA_MEASUREMENT_PATH}/{MIRA_MEAS_PROJECT_NAME}"
            filter = "Text Files (*.hdf5)"
            file_path = f"./mira/meas/hdf5/{MIRA_MEAS_PROJECT_NAME}.hdf5"
            direcotry = f"./mira/meas/hdf5/{MIRA_MEAS_PROJECT_NAME}.hdf5"
        
        self.caption = caption
        self.default_dir = default_dir
        self.filter = filter
        
        self.file_path = Path(file_path)
        self.direcotry = Path(direcotry)
        
        self.set_path_labels()
    
    def reinit(self, mira_project: str) -> None:
        
        MIRA_MEASUREMENT_PATH = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                "MIRA_MEASUREMENT_PATH")

        if self.browser_type == "bgt_reg_browser":
            caption="Select BGT-Register for MiRa6024|1A"
            default_dir = f"./mira/cfg/mira6024_projects/" 
            filter = "Text Files (*.txt)"
            file_path = f"{default_dir}/{mira_project}.txt"
            direcotry = "./"
            
        elif self.browser_type == "mira_meas_out_browser":
            caption="Select Measurement Dicretory MiRa6024|1A"
            default_dir = f"{MIRA_MEASUREMENT_PATH}/{mira_project}"
            filter = None
            file_path = "./mira/meas/hdf5/"
            direcotry = "./mira/meas/hdf5/"
            
        elif self.browser_type == "mira_meas_in_browser":
            caption="Select MiRa6024|1A Measurement File"
            default_dir = f"{MIRA_MEASUREMENT_PATH}/{mira_project}"
            filter = "Text Files (*.hdf5)"
            file_path = f"./mira/meas/hdf5/{mira_project}.hdf5"
            direcotry = f"./mira/meas/hdf5/{mira_project}.hdf5"
        
        self.caption = caption
        self.default_dir = default_dir
        self.filter = filter
        
        self.file_path = Path(file_path)
        self.direcotry = Path(direcotry)
        
        self.set_path_labels()
        
    def open_path_browser(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path = None
        directory = None
        if self.filter is not None:
            file_path, _ = QFileDialog.getOpenFileName(self.qt_self, 
                                                         caption=self.caption, 
                                                         directory=self.default_dir, 
                                                         filter=self.filter, 
                                                         options=options)
        else:
            directory = QFileDialog.getExistingDirectory(self.qt_self, 
                                                         caption=self.caption,
                                                         directory=self.default_dir,
                                                         options=options)
        
        if file_path is not None:  
            self.file_path = file_path
            
        if directory is not None:
            self.direcotry = directory
            
        self.set_path_labels()
        
    def set_path_labels(self):
        if self.browser_type == "bgt_reg_browser":
            self.qt_self.browse_register_path_textBrowser.setText(f"{self.file_path}")
            self.radar_param.gui.bgt_register_file_path = self.file_path
        elif self.browser_type == "mira_meas_in_browser":
            self.qt_self.browse_meas_in_path_textBrowser.setText(f"{self.file_path}")
        elif self.browser_type == "mira_meas_out_browser":
            self.qt_self.browse_meas_out_path_textBrowser.setText(f"{self.direcotry}")
        
        root_path = f"{Path('./').resolve()}"
        self.qt_self.mira_system_path_textBrowser.setText(root_path)
        self.radar_param.gui.root_sys_path = root_path
