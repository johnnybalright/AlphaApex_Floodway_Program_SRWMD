"""
This module contains the `fema_data` function which processes FEMA
flood report PDFs to extract flood risk data based on project numbers.
It includes a safety check to ensure that the file is not empty before
attempting to open and read from it, preventing errors from processing
invalid or incomplete files.

Functions:
    fema_data(projectnumber, string, logger_1): Opens a PDF file only if
    it has a byte size indicating that it is not empty and extracts
    relevant flood risk data.
"""
import glob
import os
import time
from dirs_configs.config import DATA_DIR
from helpers.misc_helper import find_index_of_substring_in_list
import pdfplumber
import signal


def fema_data(projectnumber, string, logger_1, pid):
    """
    Continuously checks for a non-empty PDF file at a
    specified path based on the project number and
    processes it to extract flood data when found.
    """
    logger = logger_1
    logger.debug('FEMA Data: %s', string)
    found_file = False
    pdf_file_path = None
    timeout = 80
    start_time = time.time()
    while not found_file:
        pdf_file_path = next(
            glob.iglob(
                f"{DATA_DIR}/*{projectnumber}-FloodReport.pdf"),None)
        if pdf_file_path and os.path.getsize(pdf_file_path) >= 1024:
            found_file = True
        else:
            logger.debug(
                f"Waiting for the PDF file for project number" \
                    + " {projectnumber} to become available and" \
                        + " meet size criteria."
                        )
        if time.time() - start_time >= timeout:
            logger.debug(
                f"Timeout reached. Killing process for project" \
                    + f" number {projectnumber}."
                    )
            os.kill(int(os.getpid()), signal.SIGKILL)
        time.sleep(10)
    with pdfplumber.open(pdf_file_path) as pdf:
        first_page = pdf.pages[0]
        txt = first_page.extract_text()
    lst = txt.split('\n')
    string_list = lst
    substring_1 = "1%"
    result_index_1 = find_index_of_substring_in_list(
        string_list,
        substring_1
        )
    substring_2 = "FIRM Panel(s)"
    result_index_2 = find_index_of_substring_in_list(
        string_list,
        substring_2
        )
    substring_3 = "10%"
    result_index_3 = find_index_of_substring_in_list(
        string_list,
        substring_3
        )
    substring_4 = "50%"
    result_index_4 = find_index_of_substring_in_list(
        string_list,
        substring_4
        )
    try:
        lst_str_1 = str(lst[result_index_1])
        lst_1 = lst_str_1.split(' ')
        n = int(len(lst_1) - 2)
        yr100 = lst_1[n]
        logger.debug('100 YR Flood: %s', yr100)
        if yr100 == '(High':
            os.kill(pid, signal.SIGKILL)
            os.kill(int(os.getpid()), signal.SIGKILL)
        else:
            pass
    except:
        yr100 = 'N/A'
        logger.debug(
            f"Error: Unable to extract 100 YR Flood data for" \
                + f" project number {projectnumber}."
                )
    try:
        lst_str_2 = str(lst[result_index_2])
        lst_2 = lst_str_2.split(' ')
        n = int(len(lst_2) - 1)
        firm_panel = lst_2[n]
        logger.debug('Firm Panel(s): %s', firm_panel)
    except:
        firm_panel = 'N/A'
        logger.debug(
            f"Error: Unable to extract Firm Panel data for" \
                + f" project number {projectnumber}."
                )
    try:
        lst_str_3 = str(lst[result_index_3])
        lst_3 = lst_str_3.split(' ')
        n = int(len(lst_3) - 2)
        yr50 = lst_3[n]
        logger.debug('50 YR Flood: %s', yr50)
    except:
        yr50 = 'N/A'
        logger.debug(
            f"Error: Unable to extract 50 YR Flood data for" \
                + f" project number {projectnumber}."
                )
    try:
        lst_str_4 = str(lst[result_index_4])
        lst_4 = lst_str_4.split(' ')
        n = int(len(lst_4) - 2)
        yr10 = lst_4[n]
        logger.debug('10 YR Flood: %s', yr10)
    except:
        yr10 = 'N/A'
        logger.debug(
            f"Error: Unable to extract 10 YR Flood data for" \
                + f" project number {projectnumber}."
                )
    return yr100, yr50, yr10, firm_panel
