import os
import pathlib
import shutil

PDF_DIR_PATH = 'data/input'
REPORT_DIR_PATH = 'data/output/json'
REPORT_FILENAME = 'paycheck_timechart.json'
TMP_DIR_PATH = 'data/tmp'

"""Get data from storage"""
from primely.models import visualizing

def get_json_timechart():
    json_loader = visualizing.JsonLoaderModel(REPORT_FILENAME, REPORT_DIR_PATH)
    return json_loader.dict_data


"""Operate on directory and files"""
def create_data_dir():
    dir_path = 'data/input'
    os.makedirs(dir_path, exist_ok=True)
    print(f'Directory `{dir_path}` created')

def remove_report():
    file_path = pathlib.Path(REPORT_DIR_PATH, REPORT_FILENAME)
    print(file_path)

    try:
        if os.path.exists(file_path):
            print('exist')
            os.remove(file_path)
            print(f'removed {file_path}')
        else:
            print(f'The file does not exist: {file_path}')
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        return True

    return

def remove_pdf():
    folder = PDF_DIR_PATH
    for filename in os.listdir(folder):
        file_path = pathlib.Path(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}' )

    return True

def remove_tmp():
    if os.path.exists(TMP_DIR_PATH):
        shutil.rmtree(TMP_DIR_PATH)


if __name__ == "__main__":
    remove_tmp()