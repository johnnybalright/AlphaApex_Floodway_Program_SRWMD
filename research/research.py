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
from base64 import b64decode
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, wait
import img2pdf
import undetected_chromedriver as uc
from dirs_configs.config import DATA_DIR
from dirs_configs.input_vars import *
from loggers.logger import get_logger
from helpers.misc_helper import start_xvfb
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.print_page_options import PrintOptions
import selenium.webdriver.chrome.options as ChromeOptions
from dotenv import load_dotenv
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import Xlib.display
import pyautogui
from contextlib import contextmanager
import multiprocessing
import threading
disp = Display(
    visible=True, size=(1366, 768), backend="xvfb", use_xauth=True
    )
disp.start()
pyautogui._pyautogui_x11._display = Xlib.display.Display(
    os.environ["DISPLAY"]
    )


def parcel_research(projectnumber,
                    parcelid,
                    county,
                    logger_1
                    ):
    time.sleep(500 / 1000)
    logger = logger_1
    start_time = time.time()
    try:
        results = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=2) as executor:
            futures = []
            futures.append(
                executor.submit(
                    prop_details,
                    projectnumber,
                    parcelid,
                    county,
                    logger_1)
                )
            futures.append(
                executor.submit(
                    directions,
                    projectnumber,
                    parcelid,
                    logger_1)
                )
            concurrent.futures.wait(futures)
            results = [future.result() for future in futures]
    except Exception as e:
        logger.debug(f"parcel_research:failed - {e}")
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time // 60
        execution_seconds = execution_time % 60
        logger.debug(
            f"Execution Time: {execution_minutes} minutes and" \
                + f"{execution_seconds:.2f} seconds"
        )


def prop_details(projectnumber, parcelid, county, logger_1):
    logger = logger_1
    try:
        with Xvfb():
            DIXIE_PARCEL_URL = (
                "https://qpublic.schneidercorp.com/Application."
                + "aspx?AppID=867&LayerID=16385&PageTypeID=2&PageID=7230&"
                + "KeyValue=03-12-13-6778-000A-0470"
            )
            GILCHRIST_PARCEL_URL = (
                "https://qpublic.schneidercorp.com/"
                + "Application.aspx?AppID=820&LayerID=15174&"
                + f"PageTypeID=4&PageID=6883&KeyValue={parcelid}"
            )
            GILCHRIST_MAP_URL = (
                "https://qpublic.schneidercorp.com/"
                + "Application.aspx?AppID=820&LayerID=15174&"
                + f"PageTypeID=1&PageID=6880&KeyValue={parcelid}"
            )
            DIXIE_MAP_URL = (
                "https://qpublic.schneidercorp.com/Application."
                + "aspx?AppID=867&LayerID=16385&PageTypeID=1&"
                + f"PageID=7229&KeyValue={parcelid}"
            )
            LEVY_PARCEL_URL = (
                "https://qpublic.schneidercorp.com/"
                + "Application.aspx?AppID=930&LayerID=18185&PageTypeID=4&"
                + f"PageID=8127&KeyValue={parcelid}"
            )
            LEVY_MAP_URL = (
                "https://qpublic.schneidercorp.com/Application"
                + ".aspx?AppID=930&LayerID=18185&PageTypeID=1&PageID=8124&"
                + f"KeyValue={parcelid}"
            )
            HAMILTON_PARCEL_URL = (
                "https://beacon.schneidercorp.com/Application"
                + ".aspx?AppID=817&LayerID=14544&PageTypeID=4&PageID=6411"
                + f"&KeyValue={parcelid}"
            )
            HAMILTON_MAP_URL = (
                "https://beacon.schneidercorp.com/Application."
                + "aspx?AppID=817&LayerID=14544&PageTypeID=1&PageID=6408"
                + f"&KeyValue={parcelid}"
            )
            MADISON_PARCEL_URL = (
                "https://qpublic.schneidercorp.com/"
                + "Application.aspx?AppID=911&LayerID=17548&PageTypeID=4&"
                + f"PageID=7848&KeyValue={parcelid}"
            )
            MADISON_MAP_URL = (
                "https://qpublic.schneidercorp.com/Application."
                + "aspx?AppID=911&LayerID=17548&PageTypeID=1&PageID=7845&"
                + f"KeyValue={parcelid}"
            )
            if county == "SUWANNEE":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(SUWANNEE_PARCEL_URL)
                    time.sleep(3)
                    driver.maximize_window()
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(3)
                    actions.send_keys(parcelid).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(5)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody/tr \
                        /td/table/tbody/tr/td[3]/div/table/tbody/tr[1]/td[2]",
                    ).click()
                    time.sleep(5)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Suwannee County \
                            Property Details Completed"
                    )

                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody \
                            /tr/td/table/tbody/tr/td[4]/div/table/ \
                                tbody/tr[1]/td[2]",
                    ).click()
                    time.sleep(3)
                    base64code_2 = driver.print_page(print_options)
                    bytes_2 = b64decode(base64code_2, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropMap.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_2)
                    logger.debug(
                        "checkpoint: Suwannee County Propery Map Completed"
                    )
                    driver.quit()
                except(ValueError, TypeError) as e:
                    logger.debug(
                        f"get_property_data:failed- Suwannee Co.- {e}"
                    )
            else:
                pass

            if county == "COLUMBIA":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(COLUMBIA_PARCEL_URL)
                    time.sleep(3)
                    driver.maximize_window()
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(3)
                    actions.send_keys(parcelid).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(5)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody/tr \
                        /td/table/tbody/tr/td[3]/div/table/tbody/tr[1]/td[2]",
                    ).click()
                    time.sleep(5)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Columbia Co. Property Details Completed"
                    )

                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody/tr/ \
                            td/table/tbody/tr/td[4]/div/table/tbody/ \
                                tr[1]/td[2]",
                    ).click()
                    time.sleep(3)
                    base64code_2 = driver.print_page(print_options)
                    bytes_2 = b64decode(base64code_2, validate=True)
                    with open(
                        str(
                            DATA_DIR / f"{projectnumber}-PropMap.pdf"),
                        "wb") as f:
                        f.write(bytes_2)
                    logger.debug(
                        "checkpoint: Columbia Co. Propery Map Completed"
                        )
                except(ValueError, TypeError) as e:
                    logger.debug(
                        f"get_property_data:failed - Columbia Co.- {e}"
                        )
            else:
                pass

            if county == "LAFAYETTE":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(LAFAYETTE_PARCEL_URL)
                    time.sleep(3)
                    driver.maximize_window()
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(3)
                    actions.send_keys(parcelid).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(5)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody/tr \
                        /td/table/tbody/tr/td[3]/div/table/tbody \
                            /tr[1]/td[2]",
                    ).click()
                    time.sleep(5)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        DATA_DIR / f"{projectnumber}-PropDetails.pdf",
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Lafayette County Property \
                            Details Completed"
                    )
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[11]/div[3]/table/tbody/tr/td/ \
                            table/tbody/tr/td[4]/div/table/tbody/tr[1] \
                                /td[2]",
                    ).click()
                    time.sleep(3)
                    base64code_2 = driver.print_page(print_options)
                    bytes_2 = b64decode(base64code_2, validate=True)
                    with open(
                        str(
                            DATA_DIR / f"{projectnumber}-PropMap.pdf"),
                        "wb") as f:
                        f.write(bytes_2)
                    logger.debug(
                        "checkpoint: Lafayette County \
                        Propery Map Completed"
                    )
                except(ValueError, TypeError) as e:
                    logger.debug(
                        "get_property_data:failed - \
                        Lafayette County"
                    )
            else:
                pass

            if county == "GILCHRIST":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(GILCHRIST_PARCEL_URL)
                    driver.set_window_size(width, height)
                    time.sleep(10)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(3)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(10)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Gilchrist Co. Property Details Completed"
                    )
                    time.sleep(1)
                    driver.get(GILCHRIST_MAP_URL)
                    time.sleep(3)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/form/div[6]/main/div[1]\
                            /div[10]/div[21]/div[15]/i",
                    ).click()
                    time.sleep(5)
                    img_path = str(DATA_DIR / f"{projectnumber}-PropMap.png")
                    pdf_path = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
                    driver.save_screenshot(img_path)
                    image = Image.open(img_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    file = open(pdf_path, "wb")
                    file.write(pdf_bytes)
                    image.close()
                    file.close()
                    driver.quit()
                    logger.debug(
                        "checkpoint: Gilchrist County \
                        Propery Map Completed"
                    )
                except(ValueError, TypeError) as e:
                    logger.debug(
                        "get_property_data:failed -\
                        Gilchrist County"
                    )
            else:
                pass

            if county == "DIXIE":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(DIXIE_PARCEL_URL)
                    driver.set_window_size(width, height)
                    time.sleep(10)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(2)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(10)
                    driver.find_element(
                        By.XPATH,
                        '//*[@id="ctlBodyPane_ctl02_ctl01_txtParcelID"]',
                    ).send_keys(parcelid)
                    time.sleep(3)
                    driver.find_element(
                        By.XPATH,
                        '//*[@id="ctlBodyPane_ctl02_ctl01_btnSearch"]',
                    ).click()
                    time.sleep(3)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Dixie County Property \
                        Details Completed"
                    )
                    driver.find_element(
                        By.XPATH,
                        "/html/body/form/div[5]/div/div[1]/main/\
                            section[1]/div/table/tbody/tr[13]/th/a",
                    ).click()
                    time.sleep(3)
                    img_path = str(DATA_DIR / f"{projectnumber}-PropMap.png")
                    pdf_path = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
                    driver.save_screenshot(img_path)
                    image = Image.open(img_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    file = open(pdf_path, "wb")
                    file.write(pdf_bytes)
                    image.close()
                    file.close()
                    logger.debug(
                        "checkpoint: Dixie Co. Propery Map Completed"
                        )
                except(ValueError, TypeError) as e:
                    logger.debug("get_property_data:failed - Dixie County")
            else:
                pass

            if county == "LEVY":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(LEVY_PARCEL_URL)
                    driver.set_window_size(width, height)
                    time.sleep(10)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(2)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(10)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Levy County Property \
                        Details Completed"
                    )
                    driver.get(LEVY_MAP_URL)
                    time.sleep(3)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/form/div[7]/main/div[1]/div[10]/\
                            div[21]/div[13]/i",
                    ).click()
                    time.sleep(1)
                    img_path = str(DATA_DIR / f"{projectnumber}-PropMap.png")
                    pdf_path = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
                    driver.save_screenshot(img_path)
                    image = Image.open(img_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    file = open(pdf_path, "wb")
                    file.write(pdf_bytes)
                    image.close()
                    file.close()
                    logger.debug(
                        "checkpoint: Levy County Propery Map Completed"
                        )
                except(ValueError, TypeError) as e:
                    logger.debug(
                        "get_property_data:failed - Levy County"
                        )
            else:
                pass

            if county == "HAMILTON":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(HAMILTON_PARCEL_URL)
                    driver.set_window_size(width, height)
                    time.sleep(10)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(2)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(10)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb",
                    ) as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Hamilton Co. Property Details Completed"
                    )
                    driver.get(HAMILTON_MAP_URL)
                    time.sleep(3)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/form/div[7]/main/div[1]/div[10]/\
                            div[21]/div[13]/i",
                    ).click()
                    time.sleep(1)
                    img_path = str(DATA_DIR / f"{projectnumber}-PropMap.png")
                    pdf_path = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
                    driver.save_screenshot(img_path)
                    image = Image.open(img_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    file = open(pdf_path, "wb")
                    file.write(pdf_bytes)
                    image.close()
                    file.close()
                    logger.debug(
                        "checkpoint: Hamilton Co. Propery Map Completed")
                except(ValueError, TypeError) as e:
                    logger.debug("get_property_data:failed - Hamilton Co.")
            else:
                pass

            if county == "MADISON":
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--window-size=1920x1080")
                    driver_path = "/usr/local/bin/chromedriver"
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=options,
                    )
                    actions = ActionChains(driver)
                    print_options = PrintOptions()
                    print_options.page_ranges = ["1-2"]
                    width = 1020
                    height = 1400
                    driver.get(MADISON_PARCEL_URL)
                    driver.set_window_size(width, height)
                    time.sleep(10)
                    actions.send_keys(Keys.TAB).perform()
                    time.sleep(2)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(10)
                    base64code_1 = driver.print_page(print_options)
                    bytes_1 = b64decode(base64code_1, validate=True)
                    with open(
                        str(
                            DATA_DIR / f"{projectnumber}-PropDetails.pdf"),
                        "wb") as f:
                        f.write(bytes_1)
                    logger.debug(
                        "checkpoint: Madison Co. Property Details Completed"
                    )
                    driver.get(MADISON_MAP_URL)
                    time.sleep(3)
                    driver.find_element(
                        By.XPATH,
                        "/html/body/form/div[7]/main/div[1]/div[10]/\
                            div[21]/div[13]/i",
                    ).click()
                    time.sleep(1)
                    img_path = str(DATA_DIR / f"{projectnumber}-PropMap.png")
                    pdf_path = str(DATA_DIR / f"{projectnumber}-PropMap.pdf")
                    driver.save_screenshot(img_path)
                    image = Image.open(img_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    file = open(pdf_path, "wb")
                    file.write(pdf_bytes)
                    image.close()
                    file.close()
                    logger.debug(
                        "checkpoint: Madison County Propery Map Completed"
                        )

                except(ValueError, TypeError) as e:
                    logger.debug(
                        "get_property_data:failed - Madison County"
                        )
            else:
                pass
    except:
        pass



def directions(projectnumber, parcelid, logger_1):
    logger = logger_1
    try:
        with sqlite3.connect(SQLITE_PARCELS_20) as conn:
            c = conn.cursor()
            c.execute(
                f'select GOOGLEMAP from parcels20 where \
                    PARCELID = "{parcelid}";'
            )
            url = c.fetchall()
            c.execute(
                f'select MGRS from parcels20 where PARCELID = "{parcelid}";'
            )
            mgrs = c.fetchall()
            logger.debug(mgrs)
            c.execute(
                f'select LAT_DD from parcels20 where PARCELID = "{parcelid}";'
            )
            lat_dd = c.fetchall()
            logger.debug(lat_dd)
            c.execute(
                f'select LONG_DD from parcels20 where PARCELID = "{parcelid}";'
            )
            long_dd = c.fetchall()
            logger.debug(long_dd)
        url_str = str(url)
        stripped_url = url_str.replace("[('", "").replace("',)]", "")
        directions_url = stripped_url
        logger.debug(directions_url)
        logger.debug("get_google_data:complete")
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        driver_path = "/usr/local/bin/chromedriver"
        driver = uc.Chrome(
            driver_executable_path="/usr/local/bin/chromedriver",
            options=options,
        )
        actions = ActionChains(driver)
        print_options = PrintOptions()
        print_options.page_ranges = ["1-2"]
        width = 1020
        height = 1400
        driver.get(str(directions_url))
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[8]/div[9]/div/div/div[1]/ \
            div[2]/div/div[1]/div/div/div[4]/div[1]/button/span/span",
        ).click()
        logger.debug("got first element")
        time.sleep(3)
        actions.send_keys("Live Oak, FL").perform()
        time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        logger.debug("sent keys")
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/ \
            div/div[1]/div/div/div[4]/div[1]/div[1]/div/div[4]/button/span",
        ).click()
        logger.debug("got second element")
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2] \
            /div/div[1]/div/div/div[2]/div[1]/div/div[3]/button",
        ).click()
        logger.debug("got third element")
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div \
            /div[1]/div/div/div[2]/div[1]/div/div[3]/div/div[2]/div/button[1]",
        ).click()
        logger.debug("got fourth element")
        time.sleep(2)
        base64code_1 = driver.print_page(print_options)
        bytes_1 = b64decode(base64code_1, validate=True)
        logger.debug("starting print to pdf")
        with open(
            str(DATA_DIR / f"{projectnumber}-PropDrivingDirections.pdf"),
            "wb",
        ) as f:
            f.write(bytes_1)
        logger.debug("research_driving_directions: completed")
        driver.quit()
    except(ValueError, TypeError) as e:
        logger.debug("research_driving_directions: failed")
        driver.quit()

