import multiprocessing
import mira.gui.mira_eval_gui as mira_eval_gui

mira_eval_gui_main_process = multiprocessing.Process(
    name='MiRa_Eval_GUI_Main_Process',
    target=mira_eval_gui.MIRA_MAIN_GUI.mira_gui_main, 
    args=())
mira_eval_gui_main_process.daemon = False

mira_eval_gui_main_process.start()
mira_eval_gui_main_process.join()