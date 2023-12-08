import json
import cProfile
import sys
import os
import time
import logging
import logging.handlers
import concurrent.futures
from loggers.logger_worker_3 import get_worker_3_logger
from lpc.lpc import lpc
from lpc.lpc_process import lpc_process
from research.research import parcel_research
from helpers.multiprocessing_helper import run_with_q_thread
from helpers.misc_helper import write_pid_to_file
from multiprocessing import Process, Queue, current_process
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from threading import Thread
import threading
from queue import Queue


def worker_3(input_queue3, input_queue4, pid_dir_path):
    start_time = time.time()
    logger_worker_3 = get_worker_3_logger()
    pid_file_path = os.path.join(pid_dir_path, "worker_3.txt")
    write_pid_to_file(pid_file_path)
    (projectnumber,
     parcelid,
     clean_parcelid,
     county,
     lname) = input_queue3.recv()
    (gs_1,
     river_frontage_length,
     gs_setback) = input_queue4.recv()
    process8, queue8 = run_with_q_thread(
        lpc,
        gs_1,
        county,
        projectnumber,
        river_frontage_length,
        logger_worker_3
        )
    process8.join()
    # lpc(gs_1, county, projectnumber, river_frontage_length, logger_worker_3)
    # process15, queue15 = run_with_q_thread(
        # lpc_process,
        # gs_1,
        # logger_1
        # )
    # process15.join()
    process17, queue17 = run_with_q_thread(
        parcel_research,
        projectnumber,
        parcelid,
        county,
        logger_worker_3
    )
    process17.join()
    end_time = time.time()
    execution_time = end_time - start_time
    execution_minutes = execution_time // 60
    execution_seconds = execution_time % 60
    logger_worker_3.debug(
        f"Execution Time worker_module_3: {execution_minutes} minutes" \
            + f" and {execution_seconds:.2f} seconds"
            )
