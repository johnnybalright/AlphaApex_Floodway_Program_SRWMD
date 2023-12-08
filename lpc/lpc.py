import os
import os.path
import time
os.environ['DISPLAY'] = ':99'
import numpy as np
import requests
from bs4 import BeautifulSoup
from dirs_configs.config import OUTPUT_DIR
from dirs_configs.file_paths import *
from helpers.geom_helper import *
from dirs_configs.input_vars import *
from helpers.misc_helper import *
from helpers.multiprocessing_helper import *
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
import uuid
from multiprocessing import Pool, cpu_count
import pyproj
import rasterio.mask
import shapely.geometry
import undetected_chromedriver as uc
import wget
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.by import By
from shapely.geometry import Point, Polygon, LineString
import geopandas as gpd
from urllib3.util.retry import Retry
import selenium.webdriver.chrome.options as ChromeOptions


def download_file(url, out_path):
    try:
        filename = wget.download(url, out=out_path)
        print(f"\nDownloaded {filename} successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")


def lpc(gs_1, county, projectnumber, river_frontage_length, logger_1):
    """
    Extracts metadata from USGS XML files for a given county, and
    converts the bounding coordinates of the corresponding river
    segments to a local projection. The resulting polygons are stored
    in a dictionary with their corresponding metadata links.

    Parameters:
    gs_1 (GeoSeries): A GeoSeries containing the river segments to
    process.
    county (str): The name of the county to process.
    projectnumber (str): The project number to use in the output
    file names.
    logger_1 (Logger): A logger object to use for logging.

    Returns:
    dict: A dictionary mapping the metadata links to the corresponding
    polygons.
    """
    try:
        logger = logger_1
        river_frontage_length = int(river_frontage_length)
        logger.debug(f"river_frontage_length: {river_frontage_length}")
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        driver_path = "/usr/local/bin/chromedriver"
        driver = uc.Chrome(
            driver_executable_path=driver_path,
            options=options
        )
        if river_frontage_length != 0:
            if county == "SUWANNEE":
                usgs_metadata_ftp = [USGS_METADATA_FTP_SUWANNEE]
            if county == "COLUMBIA":
                usgs_metadata_ftp = [USGS_METADATA_FTP_COLUMBIA]
            if county == "LAFAYETTE":
                usgs_metadata_ftp = [
                    USGS_METADATA_FTP_SUWANNEE,
                    USGS_METADATA_FTP_GILCHRIST,
                ]
            if county == "GILCHRIST":
                usgs_metadata_ftp = [USGS_METADATA_FTP_GILCHRIST]
            if county == "DIXIE":
                usgs_metadata_ftp = [
                    USGS_METADATA_FTP_GILCHRIST,
                    USGS_METADATA_FTP_LEVY,
                ]
            if county == "LEVY":
                usgs_metadata_ftp = [USGS_METADATA_FTP_LEVY]
            if county == "MADISON":
                usgs_metadata_ftp = [
                    USGS_METADATA_FTP_SUWANNEE,
                    USGS_METADATA_FTP_MADISON
                ]
            if county == "HAMITLON":
                usgs_metadata_ftp = [
                    USGS_METADATA_FTP_SUWANNEE,
                    USGS_METADATA_FTP_COLUMBIA,
                    USGS_METADATA_FTP_HAMILTON
                ]
        else:
            if county == "SUWANNEE":
                usgs_metadata_ftp = [USGS_METADATA_FTP_SUWANNEE]
            if county == "COLUMBIA":
                usgs_metadata_ftp = [USGS_METADATA_FTP_COLUMBIA]
            if county == "LAFAYETTE":
                usgs_metadata_ftp = [USGS_METADATA_FTP_LAFAYETTE]
            if county == "GILCHRIST":
                usgs_metadata_ftp = [USGS_METADATA_FTP_GILCHRIST]
            if county == "DIXIE":
                usgs_metadata_ftp = [USGS_METADATA_FTP_DIXIE]
            if county == "LEVY":
                usgs_metadata_ftp = [USGS_METADATA_FTP_LEVY]
            if county == "MADISON":
                usgs_metadata_ftp = [USGS_METADATA_FTP_MADISON]
            if county == "HAMITLON":
                usgs_metadata_ftp = [USGS_METADATA_FTP_HAMILTON]
        logger.debug("usgs_metadata_ftp: retrieved")
        logger.debug(print(usgs_metadata_ftp))
        if url_active(usgs_metadata_ftp[0]):
            gdf = gpd.GeoSeries([gs_1])
            gdf = gdf.set_crs("epsg:6441")
            sindex = gdf.sindex
            gs = gs_1.envelope
            with open(XML_LINKS, "w", encoding="utf-8"):
                pass
            with open(BOUND_COORDS, "w", encoding="utf-8"):
                pass
            for i in range(0, len(usgs_metadata_ftp)):
                driver.get(usgs_metadata_ftp[i])
                time.sleep(3)
                lnks = driver.find_elements(By.PARTIAL_LINK_TEXT, ".xml")
                for lnk in lnks:
                    with open(XML_LINKS, "a", encoding="utf-8") as f:
                        href = lnk.get_attribute("href")
                        f.write(href)
                        f.write(",")
            logger.debug("links:complete")
            # if driver:
            #     driver.quit()
            with open(XML_LINKS, "r", encoding="utf-8") as f_in, open(
                BOUND_COORDS, "a", encoding="utf-8"
            ) as f_out:
                urls = f_in.read().split(",")
                logger.debug(len(urls))
                for i in range(0, len(urls) - 2):
                    s = requests.Session()
                    retry = Retry(connect=3, backoff_factor=0.5)
                    adapter = HTTPAdapter(max_retries=retry)
                    s.mount("http://", adapter)
                    s.mount("https://", adapter)
                    r = s.get(str(urls[i]))
                    content = r.text
                    soup = BeautifulSoup(content, "xml")
                    westbc_tag = soup.find("westbc")
                    westbc = westbc_tag.get_text()
                    eastbc_tag = soup.find("eastbc")
                    eastbc = eastbc_tag.get_text()
                    northbc_tag = soup.find("northbc")
                    northbc = northbc_tag.get_text()
                    southbc_tag = soup.find("southbc")
                    southbc = southbc_tag.get_text()
                    networkr_tag = soup.find("networkr")
                    networkr = networkr_tag.get_text()
                    f_out.write(westbc)
                    f_out.write(",")
                    f_out.write(southbc)
                    f_out.write(",")
                    f_out.write(westbc)
                    f_out.write(",")
                    f_out.write(northbc)
                    f_out.write(",")
                    f_out.write(eastbc)
                    f_out.write(",")
                    f_out.write(northbc)
                    f_out.write(",")
                    f_out.write(eastbc)
                    f_out.write(",")
                    f_out.write(southbc)
                    f_out.write(",")
                    f_out.write(westbc)
                    f_out.write(",")
                    f_out.write(southbc)
                    f_out.write(",")
                    f_out.write(networkr)
                    f_out.write(",")
                    f_out.flush()
                f_out.close()
                logger.debug("urls: complete")
            coord_values = None
            with open(BOUND_COORDS, "r", encoding="utf-8") as file:
                for line in file:
                    coord_values = line.strip().split(",")
                time.sleep(2)
            coord_links = coord_values[10::11]
            coord_slices = [
                item
                for index, item in enumerate(coord_values)
                if (index + 1) % 11 != 0
            ]
            logger.debug("coord_slices: started")
            x_coords = []
            y_coords = []
            x_coords = coord_slices[0::2]
            y_coords = coord_slices[1::2]
            x_arr = np.array(x_coords)
            y_arr = np.array(y_coords)
            coordinates = list(zip(x_arr, y_arr))
            coordinates_arr = np.array(coordinates)
            logger.debug("coordinates_arr: started")
            slices = [
                coordinates_arr[i : i + 5]
                for i in range(0, len(coordinates_arr), 5)
            ]
            polygons = [Polygon(slice) for slice in slices]
            original_crs = pyproj.CRS("EPSG:4326")
            target_crs = pyproj.CRS("EPSG:6441")
            transformer = pyproj.Transformer.from_crs(
                original_crs, target_crs, always_xy=True
            )
            transformed_polygons = []
            for polygon in polygons:
                coords = list(polygon.exterior.coords)
                transformed_coords = [
                    transformer.transform(x, y) for x, y in coords
                ]
                transformed_polygon = Polygon(transformed_coords)
                transformed_polygons.append(transformed_polygon)
            logger.debug("transformed_polygons: started")
            polygon_link_dict = dict(
                zip(range(len(transformed_polygons)), coord_links)
            )
            given_polygon = gs
            num_cores = cpu_count()
            chunks = split_into_chunks(transformed_polygons, num_cores)
            with Pool(processes=num_cores) as pool:
                results = pool.map(
                    find_intersections,
                    [
                        (given_polygon, list(chunk.values()), chunk, sindex)
                        for chunk in chunks
                    ],
                )
            logger.debug("split_into_chunks: started")
            intersecting_keys = [item for sublist in results for item in sublist]
            laz_lst = [str(polygon_link_dict[key]) for key in intersecting_keys]
            seen = set()
            unique_lst = [x for x in laz_lst if not (x in seen or seen.add(x))]
            for laz in unique_lst:
                laz_file = str(OUTPUT_DIR / f"{uuid.uuid4()}_{projectnumber}.laz")
                logger.debug(laz_file)
                download_file(laz, laz_file)
                logger.debug("laz download complete")
            logger.debug("laz_files:complete")
            try:
                os.remove(str(BOUND_COORDS))
                logger.debug("bound_coords: removed")
                os.remove(str(XML_LINKS))
                logger.debug("xml_links: removed")
                logger.debug("remove_tmp_files: complete")
            except FileNotFoundError as e:
                logger.debug("get_lpc_laz:failed")
                logger.debug("error: %s", e)
        else:
            logger.debug("usgs_metadata_ftp link: failed")
            return None
    except (FileNotFoundError, PermissionError) as e:
        logger.debug("get_lpc_laz:failed")
        logger.debug("error: %s", e)

