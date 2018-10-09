from constants import INIT_DATE_TIME_FORMAT
from datetime import datetime
from os import path


def is_valid_run_name(run_name):
    """
    Checks the validity of the run_name. run_name cannot have spaces or colons.
    :param run_name: <class str> provided run_name.
    :return: <bool> True if valid False if not.
    """
    return run_name and not (' ' in run_name or ':' in run_name)


def is_valid_init_dt(date_time):
    """
    Checks the validity of given date_time. Given date_time should be of "yyyy-mm-dd_HH:MM:SS"
    :param date_time: datetime instance
    :return: boolean, True if valid False otherwise
    """
    try:
        datetime.strptime(date_time, INIT_DATE_TIME_FORMAT)
        return True
    except ValueError:
        return False


def is_output_ready(run_path):
    """
    Checks whether the output is ready for a given run.
    :param run_path: str, absolute path to the run resources and configs
    :return: boolean, True if output is ready to be consumed, False otherwise
    """
    output_dir = path.join(run_path, 'output')
    # TODO check in the database for the status for further assurance.
    return path.exists(output_dir)
