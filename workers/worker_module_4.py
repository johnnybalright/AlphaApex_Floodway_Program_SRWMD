import json
import cProfile
import sys
import os
import time
import logging
import logging.handlers
import concurrent.futures
from loggers.logger_worker_4 import get_worker_4_logger
from geometry.bank_geom import bank_geom
from geometry.center_line import center_line
from geometry.center_tob import center_tob
from research.water_level import water_level
from research.research import parcel_research
from geometry.parcel_builder import parcel_builder
from helpers.multiprocessing_helper import run_with_q_thread
from multiprocessing import Process, Queue, current_process
import multiprocessing
from helpers.misc_helper import write_pid_to_file
from threading import Thread
from queue import Queue


def worker_4(
    input_queue5,
    input_queue6,
    input_queue7,
    pid_dir_path
    ):
    start_time = time.time()
    try:
        logger_worker_4 = get_worker_4_logger()
        pid_file_path = os.path.join(pid_dir_path, "worker_4.txt")
        write_pid_to_file(pid_file_path)
        (projectnumber,
        parcelid,
        clean_parcelid,
        county,
        lname) = input_queue5.recv()
        (gs_1,
        river_frontage_length,
        gs_setback) = input_queue6.recv()
        (yr100,
        yr50,
        yr10,
        firm_panel) = input_queue7.recv()
        process9, queue9 = run_with_q_thread(
            center_line,
            gs_1,
            river_frontage_length,
            logger_worker_4
            )
        process9.join()
        result9 = queue9.get()
        (gs_center,
        gdf_center_xs_line_mile) = result9
        process13, queue13 = run_with_q_thread(
            center_tob,
            gs_center,
            river_frontage_length,
            logger_worker_4
            )
        # process13.join()
        result13 = queue13.get()
        gs_updated_center, smooth_points = result13
        process14, queue14 = run_with_q_thread(
            water_level,
            projectnumber,
            gdf_center_xs_line_mile,
            river_frontage_length,
            logger_worker_4
            )
        # process14.join()
        result14 = queue14.get()
        delta_water_level_el_l, upper_xs, lower_xs = result14
        process10, queue10 = run_with_q_thread(
            bank_geom,
            projectnumber,
            delta_water_level_el_l,
            gs_center,
            gs_updated_center,
            gs_1,
            gs_setback,
            logger_worker_4
            )
        # process10.join()
        result10 = queue10.get()
        gdf_tob = result10
        process16, queue16 = run_with_q_thread(
            parcel_builder,
            projectnumber,
            gs_center,
            gs_setback,
            yr100,
            yr50,
            yr10,
            delta_water_level_el_l,
            river_frontage_length,
            logger_worker_4)
        process16.join()
        # process17, queue17 = run_with_q_thread(
        #     parcel_research,
        #     projectnumber,
        #     parcelid,
        #     county,
        #     logger_worker_4
        # )
        # process17.join()
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        logger_worker_4.debug(
            f"Execution Time worker_module_4: {execution_minutes} minutes" \
                + f" and {execution_seconds:.2f} seconds"
                )
    except Exception as e:
        logger.debug(f"worker_4: failed- {e}")
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        logger_worker_4.debug(
            f"Execution Time worker_module_4: {execution_minutes} minutes" \
                + f" and {execution_seconds:.2f} seconds"
                )
