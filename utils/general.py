from distutils.dir_util import remove_tree
from os import path, makedirs


def create_dir(dir_path):
    try:
        if path.exists(dir_path):
            remove_tree(dir_path)
        makedirs(dir_path)
    except OSError:
        print('Error: Creating directory. ' + dir_path)
        raise


def get_init_state_name(state_dt):
    return 'state_at_%s' % state_dt.strftime('%Y_%m_%d_%H_%M')