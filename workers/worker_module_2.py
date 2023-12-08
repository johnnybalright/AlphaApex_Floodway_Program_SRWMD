import json
import cProfile
import sys
import os
import time
import logging
import logging.handlers
import concurrent.futures
from dirs_configs.config import PARENT_DIR
from loggers.logger_worker_2 import get_worker_2_logger
from geometry.parcel_geometry import parcel_geometry
from research.pdf_fill import pdf_fillable
from geometry.hecras import hecras_calc
from research.river_mile import river_mile
from helpers.multiprocessing_helper import run_with_q_thread
from helpers.misc_helper import write_pid_to_file
from multiprocessing import Process, Queue, current_process, Pipe
import multiprocessing
from threading import Thread
from queue import Queue


def worker_2(
    input_queue1,
    input_queue2,
    output_queue4,
    output_queue6,
    pid_dir_path
    ):
    os.chdir(PARENT_DIR)
    # os.chdir(
    #     os.path.dirname(
    #         os.path.abspath(__file__)))
    time.sleep(1)
    start_time = time.time()
    logger_worker_2 = get_worker_2_logger()
    pid_file_path = os.path.join(pid_dir_path, "worker_2.txt")
    write_pid_to_file(pid_file_path)
    (projectnumber,
     parcelid,
     clean_parcelid,
     county,
     lname) = input_queue1.recv()
    logger_worker_2.debug('Project Number: %s', projectnumber)
    process5, queue5 = run_with_q_thread(
        parcel_geometry,
        projectnumber,
        parcelid,
        logger_worker_2
        )
    # process5.join()
    result5 = queue5.get()
    output_queue4.send(result5)
    output_queue6.send(result5)
    (gs_1,
    river_frontage_length,
    gs_setback) = result5
    process6, queue6 = run_with_q_thread(
        pdf_fillable,
        projectnumber,
        river_frontage_length,
        logger_worker_2
        )
    # process6.join()
    (yr100,
     yr50,
     yr10,
     firm_panel) = input_queue2.recv()
    logger_worker_2.debug('Firm Panel(s): %s', firm_panel)
    process7, queue7 = run_with_q_thread(
        hecras_calc,
        projectnumber,
        gs_1,
        yr100,
        yr50,
        yr10,
        firm_panel,
        logger_worker_2
        )
    process7.join()
    result7 = queue7.get()
    gdf_hxline = result7
    process12, queue12 = run_with_q_thread(
        river_mile,
        projectnumber,
        gs_1,
        gdf_hxline,
        logger_worker_2
        )
    process12.join()
    output_queue4.close()
    output_queue6.close()
    end_time = time.time()
    execution_time = end_time - start_time
    execution_minutes = execution_time // 60
    execution_seconds = execution_time % 60
    logger_worker_2.debug(
        f"Execution Time worker_module_2: {execution_minutes} minutes" \
            + f" and {execution_seconds:.2f} seconds"
            )
