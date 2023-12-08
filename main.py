"""
this module runs all the pertinent modules and their functions
"""
import os
import os.path
from pathlib import Path
os.chdir(
    os.path.dirname(
        os.path.abspath(__file__)))
import subprocess
import argparse
import sys
import shutil
import requests
import time
env = os.environ.copy()
bash_path = Path("./bash")
kill_processes = bash_path / "kill_processes.sh"
start_xvfb = bash_path / "start_xvfb.sh"
result1 = subprocess.run([kill_processes], env=env)
time.sleep(1)
result2 = subprocess.run([start_xvfb], env=env)
time.sleep(1)
from dirs_configs.file_paths import (
    WORKER_1_LOG_PATH,
    WORKER_2_LOG_PATH,
    WORKER_3_LOG_PATH,
    WORKER_4_LOG_PATH,
    MAIN_LOG_PATH,
    )
from workers.worker_module_1 import worker_1
from workers.worker_module_2 import worker_2
from workers.worker_module_3 import worker_3
from workers.worker_module_4 import worker_4
from sync.remote_drive import upload_drive, dirs_strings
from helpers.misc_helper import log_rotation
from dotenv import load_dotenv
load_dotenv(
    "/home/jpournelle/python_projects/" \
        + "plabz/river_division/main/main.env"
    )
from multiprocessing import (
    Pool,
    Process,
    Queue,
    current_process,
    Pipe
    )
import multiprocessing
import threading
import logging
from dirs_configs.config import (
    BASE_DIR,
    LOG_DIR,
    OUTPUT_DIR,
    RESULT_DIR,
    TMP_DIR
    )
from loggers.logger_main import get_main_logger
import cProfile
import time
import signal
import uuid
import psutil
from datetime import datetime


def kill_python3_processes(exclude_pid=None):
    current_process_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python3' or 'python3' in proc.info['cmdline']:
            if proc.info['pid'] not in (current_process_pid, exclude_pid):
                try:
                    proc.kill()
                    print(f"Killed python3 process with PID: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error) as e:
                    print(f"Error killing process {proc.info['pid']}: {e}")


def combine_text_files(directory, output_filename):
    text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    file_path = os.path.join(directory, output_filename)
    with open(os.path.join(file_path), 'w') as output_file:
        for text_file in text_files:
            file_path = os.path.join(directory, text_file)
            with open(file_path, 'r') as file:
                output_file.write(file.read())
                output_file.write("\n")
            return file_path


def read_pids_from_file(file_path):
    with open(file_path, 'r') as file:
        pids = [int(line.strip()) for line in file]
    return pids


def terminate_processes(pids):
    for pid in pids:
        try:
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process.terminate()
                print(f"Terminated PID {pid}")
            else:
                print(f"PID {pid} does not exist")
        except psutil.NoSuchProcess:
            print("The process does not exist.")
        except psutil.AccessDenied:
            print("Permission denied to terminate the process.")
        except Exception as e:
            print(f"An error occurred: {e}")


def handle_sigterm(sig, frame):
    sys.exit(0)


def rclone_copy(fp_zip, directory, full_path):
    rclone = full_path
    remote2 = f"dropbox:/PROJECTS/_aa_Most-Recent/{directory}/"
    cmd = str(f"{rclone}")
    arg1 = str("copy")
    arg2 = str(fp_zip)
    arg3 = str(remote2)
    arg4 = str("--progress")
    arg5 = str("--verbose")
    process = subprocessPopen = subprocess.Popen(
        [
            cmd,
            arg1,
            arg2,
            arg3,
            arg4,
            arg5
            ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("Rclone copy successful.")
        signal.signal(signal.SIGTERM, handle_sigterm)
    else:
        print("Rclone copy failed:", stderr.decode())


def main(dbfile, pid):
    try:
        excld_pid = pid
        kill_python3_processes(excld_pid)
        unique_id = uuid.uuid4()
        pid_dirname = f"{unique_id}_pid"
        pid_dir_path = TMP_DIR / pid_dirname
        os.makedirs(pid_dir_path, exist_ok=True)
        lock_dir = TMP_DIR
        os.makedirs(lock_dir, exist_ok=True)
        lock_file = lock_dir / "lock.txt"
        with open(lock_file, 'w') as f:
            f.write("lock")
        logger_main = get_main_logger()
        print("--------------------")
        print("--------------------")
        print("main: main started")
        print(f"{str(datetime.now())}")
        db_file = dbfile
        try:
            start_time = time.time()
            # error_event = multiprocessing.Event()
            processes = []
        except Exception as e:
            logger_main.debug(f"main: first block failed-{e}")
            print(f"main: first block failed-{e}")
        try:
            parent_conn1, child_conn1 = multiprocessing.Pipe()
            parent_conn2, child_conn2 = multiprocessing.Pipe()
            parent_conn3, child_conn3 = multiprocessing.Pipe()
            parent_conn4, child_conn4 = multiprocessing.Pipe()
            parent_conn5, child_conn5 = multiprocessing.Pipe()
            parent_conn6, child_conn6 = multiprocessing.Pipe()
            parent_conn7, child_conn7 = multiprocessing.Pipe()
            logger_main.debug("main: pipes created")
            # print("main: pipes created")
            # error_event_1 = threading.Event()
            # # error_event_2 = threading.Event()
            # # error_event_3 = threading.Event()
            # # error_event_4 = threading.Event()
            # print("main: error_events created")
            pid = os.getpid()
            print(f"main: pid: {pid}")
            p1 = Process(
                target=worker_1,
                args=(
                    parent_conn1,
                    parent_conn2,
                    parent_conn3,
                    parent_conn5,
                    parent_conn7,
                    pid,
                    db_file,
                    pid_dir_path
                    ))
            p1.start()
            processes.append(p1)
            # if error_event_1.is_set():
            #     p1.terminate()
            #     os.kill(pid, signal.SIGTERM)
            logger_main.debug("main: worker_1 started")
            print("main: worker_1 started")
            p2 = Process(
                target=worker_2,
                args=(
                    child_conn1,
                    child_conn2,
                    parent_conn4,
                    parent_conn6,
                    pid_dir_path
                    ))
            p2.start()
            processes.append(p2)
            logger_main.debug("main: worker_2 started")
            print("main: worker_2 started")
            p3 = Process(
                target=worker_3,
                args=(
                    child_conn3,
                    child_conn4,
                    pid_dir_path
                    ))
            p3.start()
            processes.append(p3)
            logger_main.debug("main: worker_3 started")
            print("main: worker_3 started")
            p4 = Process(
                target=worker_4,
                args=(
                    child_conn5,
                    child_conn6,
                    child_conn7,
                    pid_dir_path
                    ))
            p4.start()
            processes.append(p4)
            logger_main.debug("main: worker_4 started")
            print("main: worker_4 started")
            # while not error_event.is_set() and any(
                # p.is_alive() for p in processes):
            #     time.sleep(0.5)
            # if error_event.is_set():
            #     for p in processes:
            #         p.terminate()
            #         p.join()
            #     sys.exit(1)
            for p in processes:
                p.join()
                # p1.join()
                # p2.join()
                # p3.join()
                # p4.join()
        except Exception as e:
            logger_main.debug(f"main: second block failed-{e}")
            print(f"main: second block failed-{e}")
        try:
            fp = str(BASE_DIR)
        except Exception as e:
            logger_main.debug(f"main: third block failed-{e}")
            print(f"main: third block failed-{e}")
        try:
            project_number, l_name = dirs_strings(db_file)
            fp_out = RESULT_DIR / "logs"
            log_paths_combined = [
                MAIN_LOG_PATH,
                WORKER_1_LOG_PATH,
                WORKER_2_LOG_PATH,
                WORKER_3_LOG_PATH,
                WORKER_4_LOG_PATH,
                ]
            max_file_size = 1024
            log_rotation(fp_out, log_paths_combined, max_file_size)
            fp_zip, new_dirs, full_pathx = upload_drive(db_file)
            logger_main.debug("main: upload_drive complete")
            print("main: upload_drive complete")
            end_time = time.time()
            execution_time = end_time - start_time
            execution_minutes = execution_time // 60
            execution_seconds = execution_time % 60
            logger_main.debug(
                f"Execution Time main: {execution_minutes} minutes" \
                    + f" and {execution_seconds:.2f} seconds"
                    )
            print(
                f"Execution Time main: {execution_minutes} minutes" \
                    + f" and {execution_seconds:.2f} seconds"
                    )
        except Exception as e:
            logger_main.debug(f"main: fouth(final) block failed-{e}")
            print(f"main: fourth(final) block failed-{e}")
        try:
            print(f"main: {fp}")
            shutil.rmtree(fp)
            rclone_copy(
                    fp_zip,
                    new_dirs,
                    full_pathx,
                    )
            fp_proj = RESULT_DIR / f"{l_name}-{project_number}"
            shutil.rmtree(fp_proj)
            url = os.getenv("SLACK_URL")
            headers = {
                "Content-Type": "application/json",
            }
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data = {
                "text":f"AlphApex Floodway Program Complete. Project" \
                    + f" {l_name}-{project_number} has been uploaded to Dropbox" \
                        + f" directory _aa_Most-Recent at {current_time}. Please" \
                            + " unzip, download, and move all files to the" \
                                + " appropriate folder in the ACE Dropbox" \
                                    + " directory PROJECTS."
                }
            response = requests.post(url, json=data, headers=headers)
            print(response.text)
        except Exception as e:
            print(f"main: fifth block failed-{e}")
    except Exception as e:
        print(f"main: main failed-{e}")
    finally:
        try:
            pids = "pids_comb.txt"
            pids_path = os.path.join(pid_dir_path, pids)
            file_path = combine_text_files(pid_dir_path, pids_path)
            pids_lst = read_pids_from_file(file_path)
            terminate_processes(pids_lst)
        except:
            pass
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass
        try:
            if os.path.exists(pid_dir_path):
                shutil.rmtree(pid_dir_path)
        except:
            pass
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlphApex Floodway Program")
    parser.add_argument("dbfile", help="sqlite3 database file with data" \
        + "inputs needed to run program. ex. PARCELID, LAT/LON"
        )
    parser.add_argument("pid", help="pid of pre_main.py process")

    args = parser.parse_args()
    main(args.dbfile, args.pid)
