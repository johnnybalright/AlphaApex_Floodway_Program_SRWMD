"""
This module contains a function that generates a PDF file containing a
map of river mile for a given project number, using the provided
GeoDataFrames.

Functions:
- river_mile(projectnumber, gs_1, gdf_hxline, logger_1):
Generates a PDF file containing a map of river mile for a given
project number, using the provided GeoDataFrames.
"""
import os
import os.path
import time
os.environ['DISPLAY'] = ':99'
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
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import selenium.webdriver.chrome.options as ChromeOptions
import folium
import json
import geopandas as gpd
from shapely.geometry import (
    Polygon,
    Point,
    LineString,
    MultiLineString,
    MultiPolygon,
    MultiPoint,
    mapping,
    shape
    )
from dirs_configs.config import *
from dirs_configs.file_paths import *
from dirs_configs.input_vars import *
from helpers.misc_helper import style_function
from PIL import Image
from reportlab.pdfgen import canvas
import pyproj
from shapely.ops import transform


def river_mile(projectnumber, gs_1, gdf_hxline, logger_1):
    """
    Generates a PDF file containing a map of river mile for a given
    project number, using the provided GeoDataFrames.

    Args:
    - projectnumber (str): The project number to use in the file name.
    - gs_1 (GeoDataFrame): A GeoDataFrame containing the data to be
    used for the map.
    - gdf_hxline (GeoDataFrame): A GeoDataFrame containing the data to
    be used for the map.

    Returns:
    - None
    """
    driver = None
    try:
        logger = logger_1
        crs_source = pyproj.CRS("EPSG:6441")
        crs_target = pyproj.CRS("EPSG:4326")
        project = pyproj.Transformer.from_crs(
            crs_source,
            crs_target,
            always_xy=True).transform
        gdf_gs = transform(project, gs_1)
        gdf_hx = gdf_hxline["geometry"][0]
        gdf_hx_line = transform(project, gdf_hx)
        try:
            gdf_p = gpd.GeoSeries([gdf_gs])
        except Exception as e:
            logger.error(
                f"An error occurred while processing gs_1: {e}"
                )
        try:
            gdf_xs = gpd.GeoSeries([gdf_hx_line])
        except Exception as e:
            logger.error(
                f"An error occurred while processing hx_line: {e}"
                )
    except Exception as e:
        logger.error(
            f"An error occurred while processing data1: {e}"
            )
    try:
        gs_pbound_c = gdf_p.centroid
        lon, lat = gs_pbound_c.x[0], gs_pbound_c.y[0]
        logger.debug(f"Longitude: {lon}, Latitude: {lat}")
    except Exception as e:
        logger.debug(
            f"An error occurred while processing data2: {e}"
            )
    try:
        shapefile_paths = [EFLDWY, WFLDWY, SUW, SUW_XS]
        folium_geoms = []
        for path in shapefile_paths:
            gdf = gpd.read_file(path)
            if not gdf.empty:
                geometry = shape(gdf.geometry.iloc[0])
                reprojected_geometry = transform(project, geometry)
                gs = gpd.GeoSeries(reprojected_geometry)
                folium_geoms.append(gs)
    except Exception as e:
        logger.debug(
            f"An error occurred while processing geographic data3: {e}"
            )
    try:
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.GeoJson(
            gdf_xs.to_json(), style_function=style_function
        ).add_to(m)
        location = [lat, lon]
        icon = folium.DivIcon(
            html='<div style="font-size: 20pt">Proposed HECRAS XS</div>'
        )
        folium.Marker(location=location, icon=icon).add_to(m)
        folium.GeoJson(gdf_p.to_json()).add_to(m)
        folium.GeoJson(folium_geoms[0].to_json()).add_to(m)
        folium.GeoJson(folium_geoms[1].to_json()).add_to(m)
        m.save(str(DATA_DIR / f"{projectnumber}-RiverMile.html"))
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        print_options = PrintOptions()
        print_options.page_ranges = ["1-2"]
        width = 1020
        height = 1400
        driver_path = "/usr/local/bin/chromedriver"
        driver = uc.Chrome(
            driver_executable_path=driver_path,
            options=options
        )
        driver.get(
            str(f"file:///{DATA_DIR}/{projectnumber}-RiverMile.html")
            )
        time.sleep(3)
        driver.save_screenshot(
                str(DATA_DIR / f"{projectnumber}-RiverMile.png")
        )
        driver.quit()
        im = Image.open(
                str(DATA_DIR / f"{projectnumber}-RiverMile.png")
            )
        c = canvas.Canvas(
                str(DATA_DIR / f"{projectnumber}-RiverMile.pdf")
            )
        c.drawImage(
                str(DATA_DIR / f"{projectnumber}-RiverMile.png"),
            0,
            0,
            width,
            height,
        )
        c.showPage()
        c.save()
        logger.debug("get_river_mile_pdf: completed")
    except ValueError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except TypeError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except AttributeError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except FileNotFoundError as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
    except Exception as e:
        logger.debug(f"get_river_mile_pdf: failed- {e}")
