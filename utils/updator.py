from os import path

from constants import HEC_DSS_DATE_FORMAT, HEC_DSS_TIME_FORMAT
from config import HEC_EVENT, HEC_EVENT_SCRIPT, INPUT_INIT_CONDITION, BASIN_NAME, RUN_NAME
from .general import get_init_state_name


def update_control_file(control_fp, start_dt, end_dt, time_interval):
    # Control file specific string constants.
    START_DATE = 'Start Date:'
    START_TIME = 'Start Time:'
    END_DATE = 'End Date:'
    END_TIME = 'End Time:'
    TIME_INTERVAL = 'Time Interval:'

    # Separation of datetimes into date and time strings.
    start_date = start_dt.strftime(HEC_DSS_DATE_FORMAT)
    start_time = start_dt.strftime(HEC_DSS_TIME_FORMAT)
    end_date = end_dt.strftime(HEC_DSS_DATE_FORMAT)
    end_time = end_dt.strftime(HEC_DSS_TIME_FORMAT)

    with open(control_fp, 'r') as control_read:
        control_data = control_read.readlines()

    with open(control_fp, 'w') as control_write:
        for line in control_data:
            if START_DATE in line:
                s = line[:line.rfind(START_DATE) + len(START_DATE)]
                s += ' ' + start_date
                control_write.write(s + '\n')
            elif START_TIME in line:
                s = line[:line.rfind(START_TIME) + len(START_TIME)]
                s += ' ' + start_time
                control_write.write(s + '\n')
            elif END_DATE in line:
                s = line[:line.rfind(END_DATE) + len(END_DATE)]
                s += ' ' + end_date
                control_write.write(s + '\n')
            elif END_TIME in line:
                s = line[:line.rfind(END_TIME) + len(END_TIME)]
                s += ' ' + end_time
                control_write.write(s + '\n')
            elif TIME_INTERVAL in line:
                s = line[:line.rfind(TIME_INTERVAL) + len(TIME_INTERVAL)]
                s += ' ' + str(time_interval)
                control_write.write(s + '\n')
            else:
                control_write.write(line)


def update_gage_file(gage_fp, start_dt, end_dt):
    # Gage file specific constants.
    START_TIME = 'Start Time:'
    END_TIME = 'End Time:'

    # Separation of datetimes into date and time strings.
    start_date = start_dt.strftime(HEC_DSS_DATE_FORMAT)
    start_time = start_dt.strftime(HEC_DSS_TIME_FORMAT)
    end_date = end_dt.strftime(HEC_DSS_DATE_FORMAT)
    end_time = end_dt.strftime(HEC_DSS_TIME_FORMAT)

    with open(gage_fp, 'r') as gage_read:
        gage_data = gage_read.readlines()

    with open(gage_fp, 'w') as gage_write:
        for line in gage_data:
            if START_TIME in line:
                s = line[:line.rfind(START_TIME) + len(START_TIME)]
                s += ' ' + start_date + ', ' + start_time
                gage_write.write(s + '\n')
            elif END_TIME in line:
                s = line[:line.rfind(END_TIME) + len(END_TIME)]
                s += ' ' + end_date + ', ' + end_time
                gage_write.write(s + '\n')
            else:
                gage_write.write(line)


def update_run_file(run_fp, state_dt, init_state_from_file=False):
    # Run file specific constants.
    SAVE_STATE_NAME = 'Save State Name:'
    SAVE_STATE_DATE = 'Save State Date:'
    SAVE_STATE_TIME = 'Save State Time:'
    START_STATE_NAME = 'Start State Name:'

    # Separation of datetime to date and time strings.
    state_date = state_dt.strftime(HEC_DSS_DATE_FORMAT)
    state_time = state_dt.strftime(HEC_DSS_TIME_FORMAT)

    with open(run_fp, 'r') as run_read:
        run_data = run_read.readlines()

    with open(run_fp, 'w') as run_write:
        for line in run_data:
            if SAVE_STATE_NAME in line:
                s = line[:line.rfind(SAVE_STATE_NAME) + len(SAVE_STATE_NAME)]
                s += ' ' + get_init_state_name(state_dt)
                run_write.write(s + '\n')
            elif SAVE_STATE_DATE in line:
                s = line[:line.rfind(SAVE_STATE_DATE) + len(SAVE_STATE_DATE)]
                s += ' ' + state_date
                run_write.write(s + '\n')
            elif SAVE_STATE_TIME in line:
                s = line[:line.rfind(SAVE_STATE_TIME) + len(SAVE_STATE_TIME)]
                s += ' ' + state_time
                run_write.write(s + '\n')
            elif START_STATE_NAME in line:
                if init_state_from_file:
                    s = line[:line.rfind(START_STATE_NAME) + len(START_STATE_NAME)]
                    s += ' ' + INPUT_INIT_CONDITION
                    run_write.write(s + '\n')
                else:
                    # Do not set a start state name to avoid reading initial state from file.
                    # Instead 'Initial Baseflow: 100' at basin will be taken as initial state.
                    continue
            else:
                run_write.write(line)


def update_event_script(model_path):
    # Event script constants.
    OPEN_PROJECT = 'OpenProject'

    event_script_fp = path.join(model_path, HEC_EVENT_SCRIPT)

    with open(event_script_fp, 'r') as script_read:
        script_data = script_read.readlines()

    with open(event_script_fp, 'w') as script_write:
        for line in script_data:
            if OPEN_PROJECT in line:
                s = OPEN_PROJECT + '("%s", "%s")' % (HEC_EVENT, model_path)
                script_write.write(s + '\n')
            else:
                script_write.write(line)


def update_state_index(state_index_fp, snaphot_dt):
    # stateIndex constants.
    SNAPSHOT_DATE = 'Snapshot Date:'
    SNAPSHOT_TIME = 'Snapshot Time:'

    with open(state_index_fp, 'r') as si_read:
        si_data = si_read.readlines()

    with open(state_index_fp, 'w') as si_write:
        for line in si_data:
            if SNAPSHOT_DATE in line:
                s = line[:line.rfind(SNAPSHOT_DATE) + len(SNAPSHOT_DATE)]
                s += ' ' + snaphot_dt.strftime(HEC_DSS_DATE_FORMAT)
                si_write.write(s + '\n')
            elif SNAPSHOT_TIME in line:
                s = line[:line.rfind(SNAPSHOT_TIME) + len(SNAPSHOT_TIME)]
                s += ' ' + snaphot_dt.strftime(HEC_DSS_TIME_FORMAT)
                si_write.write(s + '\n')
            else:
                si_write.write(line)


def update_state_file(state_fp, state_dt, force_state_dt=False):
    # State file specific constants.
    SNAPSHOT = 'Snapshot:'
    RUN_ID = 'Run ID:'
    SNAPSHOT_TIME = 'Snapshot Time:'
    EXECUTION_TIME = 'Execution Time:'
    BASIN_MODEL = 'Basin Model:'
    END = 'End:'
    with open(state_fp, 'r') as state_read:
        state_data = state_read.readlines()

    inside_header = False
    header_updated = False
    with open(state_fp, 'w') as state_write:
        for line in state_data:
            if inside_header:
                if RUN_ID in line:
                    s = line[:line.rfind(RUN_ID) + len(RUN_ID)]
                    s += ' ' + RUN_NAME
                    state_write.write(s + '\n')
                elif SNAPSHOT_TIME in line:
                    if force_state_dt:
                        s = line[:line.rfind(SNAPSHOT_TIME) + len(SNAPSHOT_TIME)]
                        snap_t = state_dt.strftime(HEC_DSS_DATE_FORMAT) + ', ' + state_dt.strftime(HEC_DSS_TIME_FORMAT)
                        s += ' ' + snap_t
                        state_write.write(s + '\n')
                    else:
                        state_write.write(line)
                elif EXECUTION_TIME in line:
                    s = line[:line.rfind(EXECUTION_TIME) + len(EXECUTION_TIME)]
                    state_write.write(s + '\n')
                elif BASIN_MODEL in line:
                    s = line[:line.rfind(BASIN_MODEL) + len(BASIN_MODEL)]
                    s += ' ' + BASIN_NAME
                    state_write.write(s + '\n')
                elif END in line:
                    inside_header = False
                    header_updated = True
                    state_write.write(line)
                else:
                    state_write.write(line)
            else:
                if SNAPSHOT in line:
                    inside_header = not header_updated
                    if inside_header:
                        s = line[:line.rfind(SNAPSHOT) + len(SNAPSHOT)]
                        s += ' ' + INPUT_INIT_CONDITION
                        state_write.write(s + '\n')
                    else:
                        state_write.write(line)
                else:
                    state_write.write(line)


if __name__ == '__main__':
    from datetime import datetime
    # update_control_file('/home/nira/PycharmProjects/hechms/resources/updates/Control_1.control',
    #                     datetime(2018, 3, 5, 5, 6, 7), datetime(2018, 3, 5, 5, 6, 7), 15)

    # update_gage_file('/home/nira/PycharmProjects/hechms/resources/updates/hec_event.gage',
    #                  datetime(2018, 3, 5, 5, 6, 7), datetime(2018, 3, 5, 5, 6, 7))

    # update_run_file('/home/nira/PycharmProjects/hechms/resources/updates/hec_event.run',
    #                 datetime(2018, 3, 5, 5, 6, 7))
    # update_event_script('/home/nira/PycharmProjects/hechms/resources/updates')
    # update_state_index('/home/nira/PycharmProjects/hechms/resources/updates/hec_event.stateIndex',
    #                    datetime(2018, 3, 5, 5, 6, 7))
    # update_state_file('/home/nira/PycharmProjects/hechms/resources/updates/state_at_2018_09_25_23_00.state',
    #                   datetime(2018, 3, 5, 5, 6, 7), True)
