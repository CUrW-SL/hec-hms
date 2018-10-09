import subprocess

from os import path

from config import HEC_DSSVUE_HOME, HEC_DSSVUE_SH, SCRIPTS_HOME, CSV_TO_DSS_PY, DSS_TO_CSV_PY


def parse_run_id(run_id):
    """
    Parse the given run_id and return the relative path to the resource location for the corresponding run.
    :param run_id: <class str> colon separated string of <FLO2D Base dir>:<model diir>:<day>:<run_name>
    :return: <class str> relative path to the resource location
    """
    if not run_id:
        raise ValueError('run_id should be a non empty string')
    dir_list = run_id.split(':')
    return path.join(*dir_list)


def csv_to_dss(csv_fp, dss_fp):
    """
    Runs the script which converts the input rainfall.csv to .dss.

    :param csv_fp: absolute file path to .csv file.
    :param dss_fp: absolute file path where .dss file should get saved.
    """
    csv_to_dss_py = path.join(SCRIPTS_HOME, CSV_TO_DSS_PY)
    return _run_conversion_script(csv_to_dss_py, csv_fp=csv_fp, dss_fp=dss_fp)


def dss_to_csv(dss_fp, csv_fp):
    """
    Runs the script which converts the output .dss to dischage.csv.

    :param dss_fp: absolute file path to output .dss file.
    :param csv_fp: absolute file path to where .csv file should get saved.
    """
    dss_to_csv_py = path.join(SCRIPTS_HOME, DSS_TO_CSV_PY)
    return _run_conversion_script(dss_to_csv_py, dss_fp=dss_fp, csv_fp=csv_fp)


def _run_conversion_script(python_script_fp, csv_fp, dss_fp):
    """
    Runs the given python script via hec_dssvue.sh with --csv_fp and --dss_fp parameters
    :return: boolean, True if success else False
    """
    dssvue_sh = path.join(HEC_DSSVUE_HOME, HEC_DSSVUE_SH)
    bash_command = '{dssvue_sh} {dss_to_csv_py} --csvfp {csv_fp} --dssfp {dss_fp}' \
        .format(dssvue_sh=dssvue_sh, dss_to_csv_py=python_script_fp, csv_fp=csv_fp, dss_fp=dss_fp)
    ret_code = subprocess.call(bash_command, shell=True)
    return True if ret_code == 0 else False
