import subprocess

from os import path
from distutils.dir_util import copy_tree

from config import HEC_HMS_HOME, HEC_HMS_SH, HEC_EVENT_SCRIPT, BASIN_STATES_DIR, HEC_OUTPUT_DSS, \
    OUTPUT_DISCHARGE_CSV_NAME
from .general import create_dir
from .parser import dss_to_csv


def run_hec_hms(run_path):
    """
    Since running of hec-hms does not take take that much time,not making it run on a different de-attached thread
    :return: run_status or failure of model run
    """
    hec_hms_sh_fp = path.join(HEC_HMS_HOME, HEC_HMS_SH)
    model_event_script_fp = path.join(run_path, 'model', HEC_EVENT_SCRIPT)
    bash_command = "{hec_hms_sh} -s {hec_event_script}"\
        .format(hec_hms_sh=hec_hms_sh_fp, hec_event_script=model_event_script_fp)
    ret_code = subprocess.call(bash_command, shell=True)
    run_status = True if ret_code == 0 else False

    # TODO update run_id in the DB with the status

    # Create output directory.
    run_output_path = path.join(run_path, 'output')
    create_dir(run_output_path)

    # Copy inputs to output dir.
    run_input_path = path.join(run_path, 'input')
    copy_tree(run_input_path, run_output_path)

    # Copy basin state to output dir.
    run_model_path = path.join(run_path, 'model')
    run_basin_state_path = path.join(run_model_path, BASIN_STATES_DIR)
    copy_tree(run_basin_state_path, run_output_path)

    # Convert output discharge and place it in output dir.
    output_dss_fp = path.join(run_model_path, HEC_OUTPUT_DSS)
    discharge_csv_fp = path.join(run_output_path, OUTPUT_DISCHARGE_CSV_NAME)
    dss_to_csv(output_dss_fp, discharge_csv_fp)

    # TODO update run_id in the DB with the status
    return run_status
