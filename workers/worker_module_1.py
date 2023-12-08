import json
import sys
import shutil
import os
import time
import logging
import logging.handlers
import concurrent.futures
from dirs_configs.config import (
    TMP_DIR,
    BASE_DIR,
    OUTPUT_DIR,
    PARENT_DIR
    )
from loggers.logger_worker_1 import get_worker_1_logger
from dirs_configs.parcel_vars import parcel_vars
from dirs_configs.config_dir import (
                    execute_template_operations,
                    configure_directories_structure)
from dirs_configs.create_dirs import create_directories
from research.flood_report import flood_report
from research.flood_data import fema_data
from research.pdf_fill import pdf_fillable
from helpers.multiprocessing_helper import run_with_q_thread
from helpers.misc_helper import write_pid_to_file
from research.river_mile import river_mile
from multiprocessing import Process, Queue, current_process
import multiprocessing
from threading import Thread
from queue import Queue


def configure_main(projectnumber):
    time.sleep(5/100)
    json_string = configure_directories_structure(projectnumber)
    dir_structure = json.loads(json_string)
    create_directories(dir_structure)
    execute_template_operations(projectnumber)


def worker_1(
    output_queue1,
    output_queue2,
    output_queue3,
    output_queue5,
    output_queue7,
    pid,
    db_file,
    pid_dir_path
    ):
    try:
        pid = pid
        start_time = time.time()
        os.chdir(PARENT_DIR)
        # os.chdir(
        #     os.path.dirname(
        #         os.path.abspath(__file__))
        #     )
        logger_worker_1 = get_worker_1_logger()
        pid_file_path = os.path.join(pid_dir_path, "worker_1.txt")
        write_pid_to_file(pid_file_path)
        process1, queue1 = run_with_q_thread(
            parcel_vars,
            db_file,
            logger_worker_1
            )
        # process1.join()
        result1 = queue1.get()
        output_queue1.send(result1)
        output_queue3.send(result1)
        output_queue5.send(result1)
        (projectnumber,
        parcelid,
        clean_parcelid,
        county,
        lname) = result1
        process2, queue2 = run_with_q_thread(
            configure_main,
            projectnumber
            )
        # process2.join()
        time.sleep(1)
        process3, queue3 = run_with_q_thread(
            flood_report,
            projectnumber,
            clean_parcelid,
            logger_worker_1,
            pid
            )
        logger_worker_1.debug(
            "flood_report should be running now'")
        # process3.join()
        result3 = queue3.get()
        string = result3
        if string == "1":
            logger_worker_1.debug("flood_report: chromedriver failed")
            sys.exit(1)
        else:
            pass
        process4, queue4 = run_with_q_thread(
            fema_data,
            projectnumber,
            string,
            logger_worker_1,
            pid
            )
        process4.join()
        result4 = queue4.get()
        (yr100,
        yr50,
        yr10,
        firm_panel) = result4
        output_queue2.send(result4)
        output_queue7.send(result4)
        output_queue1.close()
        output_queue2.close()
        output_queue3.close()
        output_queue5.close()
        output_queue7.close()
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        logger_worker_1.debug(
            f"Execution Time worker_module_1: {execution_minutes}" \
                + f"minutes and {execution_seconds:.2f} seconds")
        pass
    except Exception as e:
        logger_worker_1.debug(f"worker_1 error_event-{e}")
