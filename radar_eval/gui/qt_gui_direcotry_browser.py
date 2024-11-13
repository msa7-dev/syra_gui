import __init__
import configparser
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog
from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER
from typing import Optional


class SYRA_BROWSER:
    """
    A class for handling file and directory browsing in the SYRA Radar System GUI.

    Attributes:
    -----------
    qt_self : any
        Reference to the Qt object containing GUI elements.
    browser_type : str
        Type of the browser (e.g., 'bgt_reg_browser', 'syra_meas_in_browser').
    radar_param : SYRA_RADAR_PARAMETER
        Radar parameters object.
    config : configparser.ConfigParser
        Configuration parser object.
    caption : str
        Caption for the file/directory dialog.
    default_dir : str
        Default directory for the file/directory dialog.
    filter : Optional[str]
        File filter for the dialog (e.g., "Text Files (*.txt)").
    file_path : Path
        Path of the selected file.
    directory : Path
        Path of the selected directory.
    """

    def __init__(self, qt_self, browser_type: str):
        """
        Initializes the SYRA_BROWSER object.

        Parameters:
        -----------
        qt_self : any
            Reference to the Qt object containing GUI elements.
        browser_type : str
            Type of the browser (e.g., 'bgt_reg_browser', 'syra_meas_in_browser').
        """
        self.qt_self = qt_self
        self.browser_type = browser_type
        self.radar_param: SYRA_RADAR_PARAMETER = self.qt_self.radar_param

        # Initialize configuration
        self.config = configparser.ConfigParser()
        self.config.read(__init__.SYRA_SYS_CONFIG_PATH)

        # Set paths and captions based on browser type
        self._initialize_paths_and_captions()

        # Update GUI labels with initial paths
        self.set_path_labels()

    def _initialize_paths_and_captions(self) -> None:
        """Initializes the file and directory paths, captions, and filters based on the browser type."""
        SYRA_MEASUREMENT_PATH = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_MEASUREMENT_PATH")
        SYRA_MEAS_PROJECT_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_MEAS_PROJECT_NAME")
        SYRA_SESSION_LABEL_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_SESSION_LABEL_NAME")
        HEX_FILE_PATH = Path(self.config.get("SYRA_BGT_SETTINGS", "SYRA_SENS_CONF_DIR_PATH")).resolve()

        # Update GUI elements with initial values
        self.qt_self.syra_project_plainTextEdit.setPlainText(f"{SYRA_MEAS_PROJECT_NAME}{self.radar_param.mon.sykno_product_name}")
        self.qt_self.session_label_plainTextEdit.setPlainText(SYRA_SESSION_LABEL_NAME)

        if self.browser_type == "bgt_reg_browser":
            self.caption = f"Select BGT-Register for {self.radar_param.mon.sykno_product_name}"
            self.default_dir = str(HEX_FILE_PATH)
            self.filter = "Text Files (*.txt)"
            self.file_path = HEX_FILE_PATH / f"Default_{self.radar_param.mon.sykno_product_name}.txt"
            self.directory = Path("./")

        elif self.browser_type == "syra_meas_out_browser":
            self.caption = f"Select Measurement Directory {self.radar_param.mon.sykno_product_name}"
            self.default_dir = f"{SYRA_MEASUREMENT_PATH}/{SYRA_MEAS_PROJECT_NAME}"
            self.filter = None
            self.file_path = Path("./radar_eval/measurement/hdf5/")
            self.directory = Path("./radar_eval/measurement/hdf5/")

        elif self.browser_type == "syra_meas_in_browser":
            self.caption = f"Select {self.radar_param.mon.sykno_product_name} Measurement File"
            self.default_dir = f"{SYRA_MEASUREMENT_PATH}/{SYRA_MEAS_PROJECT_NAME}"
            self.filter = "Text Files (*.hdf5)"
            self.file_path = Path(f"./radar_eval/measurement/hdf5/{SYRA_MEAS_PROJECT_NAME}.hdf5")
            self.directory = Path(f"./radar_eval/measurement/hdf5/{SYRA_MEAS_PROJECT_NAME}.hdf5")

        else:
            self.caption = "Select Measurement File"
            self.default_dir = f"{SYRA_MEASUREMENT_PATH}/{SYRA_MEAS_PROJECT_NAME}"
            self.filter = "Text Files (*.hdf5)"
            self.file_path = Path("./radar_eval/measurement/hdf5/")
            self.directory = Path("./radar_eval/measurement/hdf5/")

    def reinit(self, syra_project: str) -> None:
        """
        Reinitializes the SYRA_BROWSER object with a new project name.

        Parameters:
        -----------
        syra_project : str
            The name of the new project.
        """
        self._initialize_paths_and_captions_for_project(syra_project)
        self.set_path_labels()

    def _initialize_paths_and_captions_for_project(self, syra_project: str) -> None:
        """Helper function to reinitialize paths and captions for a specific project."""
        SYRA_MEASUREMENT_PATH = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_MEASUREMENT_PATH")
        SYRA_MEAS_PROJECT_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_MEAS_PROJECT_NAME")
        SYRA_SESSION_LABEL_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", "SYRA_SESSION_LABEL_NAME")

        self.qt_self.syra_project_plainTextEdit.setPlainText(f"{SYRA_MEAS_PROJECT_NAME}{self.radar_param.mon.sykno_product_name}")
        self.qt_self.session_label_plainTextEdit.setPlainText(SYRA_SESSION_LABEL_NAME)

        if self.browser_type == "bgt_reg_browser":
            self.caption = f"Select BGT-Register for {self.radar_param.mon.sykno_product_name}"
            self.default_dir = "./radar_eval/config/register_hex_files/"
            self.filter = "Text Files (*.txt)"
            self.file_path = Path(f"{self.default_dir}/{SYRA_MEAS_PROJECT_NAME}{syra_project}.txt")
            self.directory = Path("./")

        elif self.browser_type == "syra_meas_out_browser":
            self.caption = f"Select Measurement Directory {self.radar_param.mon.sykno_product_name}"
            self.default_dir = f"{SYRA_MEASUREMENT_PATH}/{SYRA_MEAS_PROJECT_NAME}{syra_project}"
            self.filter = None
            self.file_path = Path("./radar_eval/measurement/hdf5/")
            self.directory = Path("./radar_eval/measurement/hdf5/")

        elif self.browser_type == "syra_meas_in_browser":
            self.caption = f"Select {self.radar_param.mon.sykno_product_name} Measurement File"
            self.default_dir = f"{SYRA_MEASUREMENT_PATH}/{SYRA_MEAS_PROJECT_NAME}{syra_project}"
            self.filter = "Text Files (*.hdf5)"
            self.file_path = Path(f"./radar_eval/measurement/hdf5/{syra_project}.hdf5")
            self.directory = Path(f"./radar_eval/measurement/hdf5/{syra_project}.hdf5")

    def open_path_browser(self) -> None:
        """
        Opens a file or directory browser dialog based on the browser type.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        selected_file: Optional[str] = None
        selected_directory: Optional[str] = None

        if self.filter is not None:
            selected_file, _ = QFileDialog.getOpenFileName(self.qt_self,
                                                           caption=self.caption,
                                                           directory=self.default_dir,
                                                           filter=self.filter,
                                                           options=options)
        else:
            selected_directory = QFileDialog.getExistingDirectory(self.qt_self,
                                                                  caption=self.caption,
                                                                  directory=self.default_dir,
                                                                  options=options)

        if selected_file:
            self.file_path = Path(selected_file)

        if selected_directory:
            self.directory = Path(selected_directory)

        self.set_path_labels()

    def set_path_labels(self) -> None:
        """
        Updates the GUI labels with the selected file or directory paths.
        """
        if self.browser_type == "bgt_reg_browser":
            self.qt_self.browse_register_path_textBrowser.setText(str(self.file_path))
            self.radar_param.gui.bgt_register_file_path = self.file_path

        elif self.browser_type == "syra_meas_in_browser":
            self.qt_self.browse_meas_in_path_textBrowser.setText(str(self.file_path))

        elif self.browser_type == "syra_meas_out_browser":
            self.qt_self.browse_meas_out_path_textBrowser.setText(str(self.directory))

        root_path = str(Path('./').resolve())
        self.qt_self.syra_system_path_textBrowser.setText(root_path)
        self.radar_param.gui.root_sys_path = root_path
