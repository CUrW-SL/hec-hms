from flask import Flask, request, send_from_directory
from flask_json import FlaskJSON, JsonError, json_response
from flask_uploads import UploadSet, configure_uploads
from os import path

from datetime import datetime

from config import UPLOADS_DEFAULT_DEST, INPUT_RAINFALL_CSV, INPUT_INIT_CONDITION_STATE, HEC_HMS_MODEL_TEMPALTE_DIR, \
    OUTPUT_DISCHARGE_CSV_NAME
from constants import INIT_DATE_TIME_FORMAT, HEC_HMS_ROOT, SINGLE
from utils import \
    is_valid_run_name, \
    is_valid_init_dt, \
    prepare_hec_hms_run_config, \
    prepare_hec_hms_run, \
    parse_run_id, \
    run_hec_hms, \
    is_output_ready, \
    prepare_hec_hms_output

app = Flask(__name__)
flask_json = FlaskJSON()


# Flask-Uploads configs
app.config['UPLOADS_DEFAULT_DEST'] = path.join(UPLOADS_DEFAULT_DEST, HEC_HMS_ROOT)
app.config['UPLOADED_FILES_ALLOW'] = ('csv', 'state')

# upload set creation
hec_single = UploadSet(SINGLE, extensions=('csv', 'state'))

configure_uploads(app, hec_single)
flask_json.init_app(app)


@app.route('/')
def hello_world():
    return 'Welcome to HEC-HMS Server!'


# Gathering required input files to run single hec-hms model.
@app.route('/hec_hms/single/init-run', methods=['POST'])
def init_single_run():
    req_args = request.args.to_dict()
    if 'run-name' not in req_args.keys() or not req_args['run-name']:
        raise JsonError(status_=400, description='run-name is not specified.')

    # Check whether given run-name is a valid one.
    run_name = req_args['run-name']
    if not is_valid_run_name(run_name):
        raise JsonError(status_=400, description='run-name cannot contain spaces or colons.')

    # Valid run-dt must be specified at the initialization phase.
    if 'run-dt' not in req_args.keys() or not req_args['run-dt']:
        raise JsonError(status_=400, description='run-dt is not specified.')
    run_dt = req_args['run-dt']
    if not is_valid_init_dt(run_dt):
        raise JsonError(status_=400, description='Given run-dt is not in the correct format: %s'
                                                 % INIT_DATE_TIME_FORMAT)
    # Valid start-dt (start datetime of the rainfall timeseries) must be specified at the initialization phase.
    if 'start-dt' not in req_args.keys() or not req_args['start-dt']:
        raise JsonError(status_=400, description='start-dt is not specified.')
    start_dt = req_args['start-dt']
    if not is_valid_init_dt(start_dt):
        raise JsonError(status_=400, description='Given start-dt is not in the correct format: %s'
                                                 % INIT_DATE_TIME_FORMAT)

    # Valid end-dt (end datetime of the rainfall including the buffer) must be specified at the initialization phase.
    if 'end-dt' not in req_args.keys() or not req_args['end-dt']:
        raise JsonError(status_=400, description='end-dt is not specified.')
    end_dt = req_args['end-dt']
    if not is_valid_init_dt(end_dt):
        raise JsonError(status_=400, description='Given end-dt is not in the correct format: %s'
                                                 % INIT_DATE_TIME_FORMAT)

    # Valid save-state-dt (state to be saved at) must be specified at the initialization phase.
    if 'save-state-dt' not in req_args.keys() or not req_args['save-state-dt']:
        raise JsonError(status_=400, description='save-state-dt is not specified.')
    save_state_dt = req_args['save-state-dt']
    if not is_valid_init_dt(save_state_dt):
        raise JsonError(status_=400, description='Given save-state-dt is not in the correct format: %s'
                                                 % INIT_DATE_TIME_FORMAT)

    today = datetime.today().strftime('%Y-%m-%d')
    input_dir_rel_path = path.join(today, run_name, 'input')
    # Check whether the given run-name is already taken for today.
    input_dir_abs_path = path.join(UPLOADS_DEFAULT_DEST, HEC_HMS_ROOT, SINGLE, input_dir_rel_path)
    if path.exists(input_dir_abs_path):
        raise JsonError(status_=400, description='run-name: %s is already taken for today: %s.' % (run_name, today))

    req_files = request.files
    if 'init-state' in req_files and 'rainfall' in req_files:
        hec_single.save(req_files['init-state'], folder=input_dir_rel_path, name=INPUT_INIT_CONDITION_STATE)
        hec_single.save(req_files['rainfall'], folder=input_dir_rel_path, name=INPUT_RAINFALL_CSV)
    else:
        raise JsonError(status_=400, description='Missing required input files. Required init-state, rainfall.')

    # Save run configurations.
    prepare_hec_hms_run_config(input_dir_abs_path, run_name, run_dt, start_dt, end_dt, save_state_dt)

    run_id = '%s:%s:%s:%s' % (HEC_HMS_ROOT, SINGLE, today, run_name)  # TODO save run_id in a DB with the status
    return json_response(status_=200, run_id=run_id, description='Successfully saved files.')


# Running hec-hms
@app.route('/hec_hms/single/start-run', methods=['GET', 'POST'])
def start_single_run():
    req_args = request.args.to_dict()
    # check whether run_id is specified and valid.
    if 'run-id' not in req_args.keys() or not req_args['run-id']:
        raise JsonError(status_=400, description='run-id is not specified')

    run_id = req_args['run-id']
    try:
        rel_run_path = parse_run_id(run_id)
    except:
        raise JsonError(status_=400, description='Error in the given run-id: %s' % run_id)
    run_path = path.join(UPLOADS_DEFAULT_DEST, rel_run_path)

    prepare_hec_hms_run(run_path, HEC_HMS_MODEL_TEMPALTE_DIR)
    success = run_hec_hms(run_path)

    # TODO update the run_id in the DB with the status
    if success:
        return json_response(status_=200, run_id=run_id, run_status='Started and Completed!',
                             description='Model run successful!.')
    else:
        return json_response(status_=500, run_id=run_id, run_status='Failed!',
                             description='Model run failure. Please check your inputs.')


# Create zip file with input files, run configurations and output files
@app.route('/hec_hms/single/get-output/output.zip', methods=['GET', 'POST'])
def get_single_output():
    req_args = request.args.to_dict()
    # check whether run_id is specified and valid.
    if 'run-id' not in req_args.keys() or not req_args['run-id']:
        raise JsonError(status_=400, description='run-id is not specified')

    run_id = req_args['run-id']
    try:
        rel_run_path = parse_run_id(run_id)
    except:
        raise JsonError(status_=400, description='Error in the given run-id: %s' % run_id)
    run_path = path.join(UPLOADS_DEFAULT_DEST, rel_run_path)

    # TODO check the DB for the status of run_id
    # TODO if status is not finished prepare error response saying so.
    if not is_output_ready(run_path):
        raise JsonError(status_=503, run_id=run_id, run_status='Running', description='output is not ready yet.')

    output_zip = prepare_hec_hms_output(run_path)
    return send_from_directory(directory=run_path, filename=output_zip)


@app.route('/hec_hms/single/extract/discharge.csv', methods=['GET', 'POST'])
def extract_data():
    req_args = request.args.to_dict()
    # check whether run_id is specified and valid.
    if 'run-id' not in req_args.keys() or not req_args['run-id']:
        raise JsonError(status_=400, description='run-id is not specified')

    run_id = req_args['run-id']
    try:
        rel_run_path = parse_run_id(run_id)
    except:
        raise JsonError(status_=400, description='Error in the given run-id: %s' % run_id)
    run_path = path.join(UPLOADS_DEFAULT_DEST, rel_run_path)

    # TODO check the DB for the status of run_id
    # TODO if status is not finished prepare error response saying so.
    if not is_output_ready(run_path):
        raise JsonError(status_=503, run_id=run_id, run_status='Running', description='output is not ready yet.')

    run_output_path = path.join(run_path, 'output')
    return send_from_directory(directory=run_output_path, filename=OUTPUT_DISCHARGE_CSV_NAME)


if __name__ == '__main__':
    app.run()
