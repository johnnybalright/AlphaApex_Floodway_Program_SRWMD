# Filename: research.py
"""
This module contains a function that performs parcel research for a
given parcel ID and county, and saves the resulting flood report as a
PDF file.

The function `parcel_research` takes in the following arguments:
- projectnumber (str): The project number associated with the parcel
research.
- path (str): The path to the directory where the PDF file will be
saved.
- parcelid (str): The parcel ID to be researched.
- clean_parcelid (str): The cleaned version of the parcel ID.
- county (str): The county where the parcel is located.

The function does not return anything.
"""
import time
import os.path
import sqlite3
import os
os.environ['DISPLAY'] = ':99'
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(
    "/home/jpournelle/python_projects/" \
        + "plabz/river_division/main/main.env"
        )
from base64 import b64decode
import subprocess
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, wait
import img2pdf
import undetected_chromedriver as uc
from dirs_configs.config import DATA_DIR, BASE_DIR
from dirs_configs.input_vars import *
from helpers.misc_helper import url_active
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.print_page_options import PrintOptions
import selenium.webdriver.chrome.options as ChromeOptions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import (
    DesiredCapabilities
    )
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import Xlib.display
import pyautogui
from contextlib import contextmanager
disp = Display(visible=True, size=(1366, 768), backend="xvfb", use_xauth=True)
disp.start()
pyautogui._pyautogui_x11._display = Xlib.display.Display(
    os.environ["DISPLAY"]
    )
import signal


def flood_report(projectnumber,
                 clean_parcelid,
                 logger_1,
                 pid
                 ):
    time.sleep(500 / 1000)
    logger = logger_1
    bash_passwd = os.getenv("BASH_PASSWD")
    start_time = time.time()
    with Xvfb():
        try:
            driver_path = "/usr/local/bin/chromedriver"
            service = Service(driver_path)
            service.start()
            options = webdriver.ChromeOptions()
            options.add_argument("--window-size=1920x1080")
            driver = uc.Chrome(
                driver_executable_path=driver_path,
                options=options,
                service=service
            )
            driver_pid = service.process.pid
            pid_str = str(driver_pid)
            nice_value= str(-6)
            logger.debug(f"desired_nice_value: {nice_value}")
            logger.debug(f"pid_str: {pid_str}")
            psswd = f"'{bash_passwd}'"
            cmd = (
                f"echo {psswd} | sudo -S renice" \
                    + f" -n {nice_value} -p {pid_str}"
                    )
            logger.debug(f"cmd: {cmd}")
            subprocess.run([cmd], shell=True, check=True)
            logger.debug("renice complete")
            actions = ActionChains(driver)
            print_options = PrintOptions()
            print_options.page_ranges = ["1-2"]
            width = 1020
            height = 1400
            if url_active(FLOOD_REPORT_URL):
                try:
                    driver.get(FLOOD_REPORT_URL)
                    logger.debug('found chromedriver')
                    time.sleep(5)
                    original_window = driver.current_window_handle
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(5)
                    driver.find_element(
                        By.CSS_SELECTOR,
                        "#showSearchBtn-btnIconEl",
                    ).click()
                    driver.find_element(
                        By.XPATH,
                        '//*[@id="parcelId_CountySearchForm-inputEl"]'
                    ).send_keys(clean_parcelid)
                    time.sleep(5)
                except WebDriverException as e:
                    logger.debug(
                        f"get_flood_report:failed- WebdriverException{e}"
                        )
                    os.kill(pid, signal.SIGKILL)
                driver.find_element(
                    By.CSS_SELECTOR,
                    "#button-1070",
                ).click()
                time.sleep(5)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(15)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(15)
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                base64code_1 = driver.print_page(print_options)
                bytes_1 = b64decode(base64code_1, validate=True)
                with open(
                    str(DATA_DIR / f"{projectnumber}-FloodReport.pdf"),
                    "wb"
                    ) as f:
                    f.write(bytes_1)
                time.sleep(2)
                logger.debug("get_flood_report:complete")
                end_time = time.time()
                execution_time = end_time - start_time
                logger.debug(
                    f"flood_report execution time: {execution_time}"
                    )
                driver.quit()
                # if service:
                #     service.stop()
                # if disp:
                #     disp.stop()
            else:
                logger.debug("get_flood_report:failed- url not active")
                return None
        except(ValueError, TypeError) as e:
            logger.debug(f"get_flood_report:failed- {e}")
        except WebDriverException as e:
            logger.debug(
                f"get_flood_report:failed- WebdriverException{e}"
                )
        result = "flood_report:complete"
        return result
