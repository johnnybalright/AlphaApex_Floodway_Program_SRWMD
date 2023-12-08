"""
This module is designed to fetch and process water level data for the
Suwannee River. It depends on several libraries such as selenium,
pyautogui, and pdfplumber to interact with web elements, automate GUI
interactions, and extract text content from PDFs, respectively.

Key Functions:
- water_level: Takes a project number and a centerline milepost as
inputs and returns the URLs for two PDFs containing water level data
for the Suwannee River. It utilizes a selenium webdriver to navigate
web pages, fetch necessary data, and saves this data as PDFs.
pdfplumber is then used to extract text from the saved PDFs for further
processing.

Environment Setup:
- The environment variables are loaded from a `.env` file using the
dotenv library.
- A virtual display is set up using pyvirtualdisplay to allow for
browser automation in a headless environment.

External Configurations:
- Configurations such as DATA_DIR are imported from an external config
module.
- undetected_chromedriver is used as a dependency to bypass bot
detection mechanisms on websites.

Error Handling:
- The code includes error-handling mechanisms to manage potential
errors during webdriver interactions,
  logging checkpoints and errors for debugging purposes.

This module is primarily configured to run in a Linux environment,
with paths and configurations
suited to a Linux OS. Adjustments may be necessary to execute this
script in a different OS environment.
"""
import os
import os.path
os.environ['DISPLAY'] = ':99'
from base64 import b64decode
import time
import pdfplumber
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
import selenium.webdriver.chrome.options as ChromeOptions
from selenium.common.exceptions import WebDriverException
from dirs_configs.config import DATA_DIR
from helpers.misc_helper import find_index_of_substring_in_list, url_active
from dotenv import load_dotenv
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import Xlib.display
import pyautogui
disp = Display(
    visible=True,
    size=(1366, 768),
    backend="xvfb",
    use_xauth=True
    )
disp.start()
pyautogui._pyautogui_x11._display = Xlib.display.Display(
    os.environ["DISPLAY"]
    )


def water_level(
    projectnumber,
    gdf_center_xs_line_mile,
    river_frontage_length,
    logger_1
    ):
    """
    Given a project number and a centerline milepost, returns the URLs
    for two PDFs containing water level data for the Suwannee River.
    The URLs are determined based on the centerline milepost value,
    which is used to determine which section of the river the project
    is located in. The function returns None if the centerline milepost
    is outside the range of the river's sections.

    Args:
    - projectnumber: str, the project number
    - gdf_center_xs_line_mile: float, the centerline milepost

    Returns:
    - water_level_url_1: str or None, the URL for the first PDF
    containing water level data
    - water_level_url_2: str or None, the URL for the second PDF
    containing water level data
    """
    try:
        logger = logger_1
        if river_frontage_length == 0:
            logger.debug("get_water_level_data: skipped")
            delta_water_level_el = None
            upper_xs = None
            lower_xs = None
            result = (delta_water_level_el, upper_xs, lower_xs)
            return result
        logger.debug(gdf_center_xs_line_mile)
        water_level_path_1 = DATA_DIR / f"{projectnumber}-WaterLevel1.pdf"
        water_level_path_2 = DATA_DIR / f"{projectnumber}-WaterLevel2.pdf"
        if float(221) >= float(gdf_center_xs_line_mile) >= float(196):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02314500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02315000"
            upper_xs = int(221)
            lower_xs = int(196)
        else:
            pass
        if float(196) >= float(gdf_center_xs_line_mile) >= float(171):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315500"
            upper_xs = int(196)
            lower_xs = int(171)
        else:
            pass
        if float(171) >= float(gdf_center_xs_line_mile) >= float(150):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315550"
            upper_xs = int(171)
            lower_xs = int(150)
        else:
            pass
        if float(150) >= float(gdf_center_xs_line_mile) >= float(135):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315550"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315650"
            upper_xs = int(150)
            lower_xs = int(135)
        else:
            pass
        if float(135) >= float(gdf_center_xs_line_mile) >= float(127):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02315650"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319500"
            upper_xs = int(135)
            lower_xs = int(127)
        else:
            pass
        if float(127) >= float(gdf_center_xs_line_mile) >= float(113):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319800"
            upper_xs = int(127)
            lower_xs = int(113)
        else:
            pass
        if float(113) >= float(gdf_center_xs_line_mile) >= float(103):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02319800"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            upper_xs = int(113)
            lower_xs = int(103)
        else:
            pass
        if float(103) >= float(gdf_center_xs_line_mile) >= float(98):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime" \
               + "river-30-day.php?id=02320000"
            upper_xs = int(103)
            lower_xs = int(98)
        else:
            pass
        if float(98) >= float(gdf_center_xs_line_mile) >= float(76):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320500"
            upper_xs = int(98)
            lower_xs = int(76)
        else:
            pass
        if float(76) >= float(gdf_center_xs_line_mile) >= float(57):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02320500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323000"
            upper_xs = int(76)
            lower_xs = int(57)
        else:
            pass
        if float(57) >= float(gdf_center_xs_line_mile) >= float(43):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323000"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323150"
            upper_xs = int(57)
            lower_xs = int(43)
        else:
            pass
        if float(43) >= float(gdf_center_xs_line_mile) >= float(34):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323150"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323500"
            upper_xs = int(43)
            lower_xs = int(34)
        else:
            pass
        if float(34) >= float(gdf_center_xs_line_mile) >= float(25):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323500"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323567"
            upper_xs = int(34)
            lower_xs = int(25)
        else:
            pass
        if float(25) >= float(gdf_center_xs_line_mile) >= float(17):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323567"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323590"
            upper_xs = int(25)
            lower_xs = int(17)
        else:
            pass
        if float(17) >= float(gdf_center_xs_line_mile) >= float(9):
            water_level_url_1 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323590"
            water_level_url_2 = "http://www.mysuwanneeriver.org/realtime/" \
                + "river-30-day.php?id=02323592"
            upper_xs = int(17)
            lower_xs = int(9)
        else:
            pass
        logger.debug("starting webdriver")
        with Xvfb():
            if upper_xs == 43:
                response = requests.get(water_level_url_1)
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find('table')
                last_row = tables.find_all('tr')[-1]
                gag_ht_1 = last_row.find_all('td')[1].get_text()
                date_1 = last_row.find_all('td')[0].get_text()
            else:
                if url_active(water_level_url_1):
                    try:
                        options = webdriver.ChromeOptions()
                        options.add_argument("--window-size=1920x1080")
                        print_options = PrintOptions()
                        print_options.page_ranges = ["1-2"]
                        driver_path = "/usr/local/bin/chromedriver"
                        driver = uc.Chrome(
                            driver_executable_path=driver_path,
                            options=options
                        )
                        driver.get(water_level_url_1)
                        time.sleep(5)
                        driver.find_element(
                            By.XPATH, "/html/body/font/font/div[1]/a[2]"
                        ).click()
                        time.sleep(20)
                        all_windows = driver.window_handles
                        driver.switch_to.window(all_windows[1])
                        base64code_1 = driver.print_page(print_options)
                        bytes_1 = b64decode(base64code_1, validate=True)
                        with open(water_level_path_1, "wb") as f:
                            f.write(bytes_1)
                        driver.quit()
                        logger.debug("checkpoint: Water Level Data 1 Completed")
                    except WebDriverException as e:
                        logger.debug("checkpoint: Water Level Data 1 Failed")
                        logger.debug(f"Error: {e}")
                        driver.quit()
                else:
                    logger.debug("Water Level Data 1 url failed")
                    return None
            if lower_xs == 43:
                response = requests.get(water_level_url_2)
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find('table')
                last_row = tables.find_all('tr')[-1]
                gag_ht_2 = last_row.find_all('td')[1].get_text()
                date_2 = last_row.find_all('td')[0].get_text()
            else:
                if url_active(water_level_url_2):
                    try:
                        options = webdriver.ChromeOptions()
                        options.add_argument("--window-size=1920x1080")
                        print_options = PrintOptions()
                        print_options.page_ranges = ["1-2"]
                        driver_path = "/usr/local/bin/chromedriver"
                        driver = uc.Chrome(
                            driver_executable_path=driver_path,
                            options=options,
                        )
                        driver.get(water_level_url_2)
                        time.sleep(5)
                        driver.find_element(
                            By.XPATH, "/html/body/font/font/div[1]/a[2]"
                        ).click()
                        time.sleep(20)
                        all_windows = driver.window_handles
                        driver.switch_to.window(all_windows[1])
                        base64code_1 = driver.print_page(print_options)
                        bytes_1 = b64decode(base64code_1, validate=True)
                        with open(water_level_path_2, "wb") as f:
                            f.write(bytes_1)
                        driver.quit()
                        logger.debug("checkpoint: Water Level Data 2 Completed")
                    except WebDriverException as e:
                        logger.debug("checkpoint: Water Level Data 2 Failed")
                        logger.debug(f"Error: {e}")
                        driver.quit()
                else:
                    logger.debug("Water Level Data 2 url failed")
                    return None
            if upper_xs == 43:
                water_level_1_at_date = gag_ht_1
                water_level_1_date = date_1
            else:
                with pdfplumber.open(water_level_path_1) as pdf:
                    first_page = pdf.pages[0]
                    second_page = pdf.pages[1]
                    text_1 = first_page.extract_text()
                    text_2 = second_page.extract_text()
                lst_1 = text_1.split("\n")
                lst_2 = text_2.split("\n")
                string_list_comb_1 = lst_1 + lst_2
                substring_1 = "EST"
                result_index_1 = find_index_of_substring_in_list(
                    string_list_comb_1, substring_1
                )
                result_lst_1 = str(string_list_comb_1[result_index_1]).split("-")
                water_level_1_date = str(result_lst_1[1])
                water_level_1_at_date = (
                    str(result_lst_1[0]).replace("\x00", "").strip()
                )
            if lower_xs == 43:
                water_level_2_at_date = gag_ht_2
                water_level_2_date = date_2
            else:
                with pdfplumber.open(water_level_path_2) as pdf:
                    third_page = pdf.pages[0]
                    fourth_page = pdf.pages[1]
                    text_3 = third_page.extract_text()
                    text_4 = fourth_page.extract_text()
                lst_3 = text_3.split("\n")
                lst_4 = text_4.split("\n")
                string_list_comb_2 = lst_3 + lst_4
                substring_2 = "EST"
                result_index_2 = find_index_of_substring_in_list(
                    string_list_comb_2, substring_2
                )
                result_lst_2 = str(string_list_comb_2[result_index_2]).split("-")
                water_level_2_date = str(result_lst_2[1])
                water_level_2_at_date = (
                    str(result_lst_2[0]).replace("\x00", "").strip()
                )
            logger.debug("water_level_1_at_date: %s", water_level_1_at_date)
            logger.debug("water_level_1_date: %s", water_level_1_date)
            logger.debug("water_level_2_at_date: %s", water_level_2_at_date)
            logger.debug("water_level_2_date: %s", water_level_2_date)
            run = float(upper_xs) - float(lower_xs)
            logger.debug("run: %s", run)
            rise = float(water_level_1_at_date) - float(water_level_2_at_date)
            logger.debug("rise: %s", rise)
            slope = float(rise) / float(run)
            logger.debug("slope: %s", slope)
            df_run = float(upper_xs) - float(gdf_center_xs_line_mile)
            logger.debug("df_run: %s", df_run)
            delta = float(df_run) * float(slope)
            logger.debug("delta: %s", delta)
            delta_water_level = float(lower_xs) + float(delta)
            logger.debug("delta_water_level: %s", delta_water_level)
            delta_water_level_el = float(water_level_1_at_date) - float(delta)
            logger.debug(delta_water_level_el)
            logger.debug("get_water_level_data: complete")
    except ValueError as e:
        logger.debug("get_water_level_data: failed")
        logger.debug("ValueError: %s", e)
    result = (delta_water_level_el, upper_xs, lower_xs)
    return result
