import json
import pandas as pd

from datetime import datetime
from distutils.dir_util import copy_tree
from os import path
from shutil import copyfile, make_archive

from constants import INIT_DATE_TIME_FORMAT, COMMON_DATE_TIME_FORMAT, RUN_CONFIG_JSON
from config import HEC_INPUT_DSS, INPUT_INIT_CONDITION_STATE, INPUT_RAINFALL_CSV, BASIN_STATES_DIR, \
    CONTROL_FILE_NAME, GAGE_FILE_NAME, RUN_FILE_NAME, STATE_INDEX_NAME
from .general import create_dir
from .parser import csv_to_dss
from .updator import update_control_file, update_gage_file, update_run_file, update_event_script, \
    update_state_index, update_state_file


def prepare_hec_hms_run_config(input_path, run_name, run_dt, start_dt, end_dt, save_state_dt):
    # Obtain the end datetime from rainfall.csv and put it in the configs.
    last_line = pd.read_csv(path.join(input_path, INPUT_RAINFALL_CSV), skip_blank_lines=True).tail(n=2).values
    one_before_last_dt = datetime.strptime(last_line[0][0], COMMON_DATE_TIME_FORMAT)
    last_dt = datetime.strptime(last_line[1][0], COMMON_DATE_TIME_FORMAT)
    time_interval = int((last_dt - one_before_last_dt).total_seconds()/60)
    run_config = {
        'run-name': run_name,
        'run-date-time': run_dt,
        'save-state-date-time': save_state_dt,
        'start-date-time': start_dt,
        'end-date-time': end_dt,
        'time-interval': time_interval
    }
    json_file = json.dumps(run_config)
    with open(path.join(input_path, RUN_CONFIG_JSON), 'w+') as F:
        F.write(json_file)
        F.close()


def prepare_hec_hms_run(run_path, model_template_path):
    # Create a directory for model run.
    model_path = path.join(run_path, 'model')
    create_dir(model_path)

    # Copy hec-hms model-template to model run dir.
    copy_tree(model_template_path, model_path)

    input_path = path.join(run_path, 'input')

    # Convert the given rainfall.csv to .dss format and store it in the model run dir.
    input_csv_fp = path.join(input_path, INPUT_RAINFALL_CSV)
    input_dss_fp = path.join(model_path, HEC_INPUT_DSS)
    csv_to_dss(input_csv_fp, input_dss_fp)

    # Read run-configs for the current run.
    run_config_path = path.join(run_path, 'input', RUN_CONFIG_JSON)
    with open(run_config_path, 'r') as F:
        run_config = json.load(F)
    start_dt = datetime.strptime(run_config['start-date-time'], INIT_DATE_TIME_FORMAT)
    end_dt = datetime.strptime(run_config['end-date-time'], INIT_DATE_TIME_FORMAT)
    save_state_dt = datetime.strptime(run_config['save-state-date-time'], INIT_DATE_TIME_FORMAT)
    time_interval = run_config['time-interval']

    # Copy the inial-condition.state to model run dir.
    input_init_state_fp = path.join(input_path, INPUT_INIT_CONDITION_STATE)
    model_init_state_fp = path.join(model_path, BASIN_STATES_DIR, INPUT_INIT_CONDITION_STATE)
    copyfile(input_init_state_fp, model_init_state_fp)

    # Prepare the stateIndex such that hec-hms will be able to locate the initial condition state file.
    state_index_fp = path.join(model_path, BASIN_STATES_DIR, STATE_INDEX_NAME)
    update_state_index(state_index_fp, start_dt)

    # Snapshot date time of the given initial condition state file should be the start date time of the current run.
    update_state_file(model_init_state_fp, start_dt, force_state_dt=True)

    # Update model template .control, .gage, and .run files.
    control_fp = path.join(model_path, CONTROL_FILE_NAME)
    update_control_file(control_fp, start_dt, end_dt, time_interval)

    gage_fp = path.join(model_path, GAGE_FILE_NAME)
    update_gage_file(gage_fp, start_dt, end_dt)

    run_fp = path.join(model_path, RUN_FILE_NAME)
    update_run_file(run_fp, save_state_dt, init_state_from_file=True)

    # Prepare the event script such that the model is ready to run.
    update_event_script(model_path)


def prepare_hec_hms_output(run_path):
    output_base = 'output'
    output_zip = output_base + '.zip'
    output_zip_abs_path = path.join(run_path, output_zip)

    # Check whether output.zip is already created.
    if path.exists(output_zip_abs_path):
        return output_zip

    # Check whether the output is ready. If ready, archive and return the .zip, otherwise return None.
    output_dir = path.join(run_path, 'output')
    if path.exists(output_dir):
        make_archive(path.join(run_path, output_base), 'zip', output_dir)
        return output_zip

    return None
