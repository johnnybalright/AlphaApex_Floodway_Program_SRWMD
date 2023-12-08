import os
import shutil
import sqlite3
import time
from dirs_configs.config import (
    BASE_DIR,
    RESULT_DIR,
    TMP_DIR,
    OUTPUT_DIR,
    LOG_DIR
    )
from pathlib import Path
from datetime import datetime
import glob
import subprocess
from multiprocessing import (
    Process,
    Queue,
    current_process,
    Pipe
    )
import multiprocessing
import threading
import logging
from loggers.logger_worker_4 import get_worker_4_logger
import zipfile


def dirs_strings(db_file):
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM project_data;")
        projectnumber = str(c.fetchone()[0])
        c.execute("SELECT lname FROM project_data;")
        lname = str(c.fetchone()[0])
    return projectnumber, lname


def dirs_transfer(projectnumber, lname, logger_worker_4):
    try:
        logger = logger_worker_4
        fp_in = BASE_DIR
        directory = f"{lname}-{projectnumber}"
        fp_out = RESULT_DIR / f"{lname}-{projectnumber}"
        fp_zip = str(
            RESULT_DIR / f"{directory}" / f"{directory}.zip"
            )
        if os.path.exists(fp_out):
            shutil.rmtree(fp_out)
        shutil.copytree(fp_in, fp_out)
        fpath_in = str(LOG_DIR / "main_py.log")
        fpath_out = str(OUTPUT_DIR / "main_py.log")
        shutil.copy(fpath_in, fpath_out)
    except shutil.Error as e:
        print(f"dirs_transfer: failed {e}")
    return fp_out, fp_zip, directory


def compress_directory(source_dir, output_zip):
    """
    Compress a directory (source_dir) into a zip file (output_zip).
    :param source_dir: Path to the directory to compress=fp_out from
    dirs_transfer function
    :param output_zip: Path of the output zip file
    """
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(
                    file_path,
                    os.path.relpath(
                        file_path,
                        start=source_dir)
                    )


def find_binary(binary_name):
    potential_paths = ["/usr/bin", "/usr/local/bin", "/opt/bin"]
    for path in potential_paths:
        full_path = os.path.join(path, binary_name)
        if os.path.isfile(full_path):
            return full_path
    print("find_binary(rclone): complete")
    return None


def upload_drive(db_file):
    try:
        logger_worker_4 = get_worker_4_logger()
        project_number, l_name = dirs_strings(db_file)
        new_fp_out, fp_zip, new_dirs = dirs_transfer(
            project_number,
            l_name,
            logger_worker_4
            )
        compress_directory(new_fp_out, fp_zip)
        full_pathx = find_binary("rclone")
        print("upload_drive: complete")
    except Exception as e:
        print(f"upload_drive: failed {e}")
    return fp_zip, new_dirs, full_pathx

if __name__ == "__main__":
    upload_drive()
