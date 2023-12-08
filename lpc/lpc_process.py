#Filename: lpc_process.py
"""
lpc_process.py

This module contains a function to process LiDAR (Light Detection and
Ranging) data. The main function, `lpc_process`, performs various
operations such as filtering, clipping, unzipping, and converting the
LiDAR data to ASCII format and then to a GeoDataFrame. It saves the
final processed data as a shapefile.

Functions:
- lpc_process(projectnumber, logger_1): Processes LiDAR data by
performing filtering, clipping, unzipping, and converting to ASCII
format. The ASCII data is then converted to a GeoDataFrame and saved as
a shapefile. The function uses configurations defined in an external
config file and also interacts with the file system to read and write
files as necessary. Logging is incorporated within the function to
track the execution flow and debug any issues that may arise during
processing.
"""
import os
import os.path
import subprocess
from datetime import datetime
import glob
from dirs_configs.config import OUTPUT_DIR
import pandas as pd
import geopandas as gpd
import whitebox_workflows as wbw


def lpc_process(projectnumber, logger_1):
    """
    This function processes lidar data by filtering, clipping,
    unzipping, and converting to ASCII format. It then converts the
    ASCII data to a GeoDataFrame and saves it as a shapefile.

    Args:
    - projectnumber (str): The project number.
    - logger_1 (logger): The logger object.

    Returns:
    - None
    """
    try:
        logger = logger_1
        lastools_directory = os.environ.get('LASTOOLS_DIRECTORY')
        input_directory = OUTPUT_DIR
        output_directory = OUTPUT_DIR
        clip_polygon = str(OUTPUT_DIR / "parcelboundary_scaled.shp")
        wbe = wbw.WbEnvironment()
        os.chdir(input_directory)
        laz_filtered = []
        for file in os.listdir(input_directory):
            if file.endswith(".laz") and not file.endswith('.copc.laz'):
                lidar_in_filter = wbe.read_lidar(f'./{file}')
                xcld_cls = list(range(3, 10)) + list(range(12, 18))
                result_filter = wbe.filter_lidar_classes(
                    lidar_in_filter,
                    exclusion_classes = xcld_cls
                    )
                current_datetime =str(
                    datetime.now()).replace(' ', '_').replace('-', '')
                file_name = current_datetime + "_" + projectnumber + ".laz"
                output_file_filter = str(OUTPUT_DIR / f"{file_name}")
                wbe.write_lidar(
                    result_filter,
                    output_file_filter
                    )
        logger.debug('filter process complete')
        for file in glob.glob(output_directory + "/*.laz"):
            laz_filtered.append(file)
        os.chdir(output_directory)
        laz_clipped = []
        for file in os.listdir(output_directory):
            if file.endswith(".laz") and not file.endswith('.copc.laz'):
                lidar_in_clip = wbe.read_lidar(f'./{file}')
                clipping_polygon = wbe.read_vector(clip_polygon)
                result_clip = wbe.clip_lidar_to_polygon(
                    lidar_in_clip,
                    clipping_polygon
                    )
                current_datetime =str(
                    datetime.now()).replace(' ', '_').replace('-', '')
                str_current_datetime = str(current_datetime)
                file_name = str_current_datetime + "clip.laz"
                output_file_clip = str(OUTPUT_DIR / f"{file_name}")
                wbe.write_lidar(
                    result_clip,
                    output_file_clip
                    )
        logger.debug('clip process complete')
        for file in glob.glob(output_directory + "/*clip.laz"):
            laz_clipped.append(file)
        os.chdir(lastools_directory)
        las_unzipped = []
        for file in laz_clipped:
            subprocess.run([f"./laszip {file}"], shell=True, check=True)
        for file in glob.glob(output_directory + "/*.las"):
            las_unzipped.append(file)
        logger.debug('points process complete')
        os.chdir(output_directory)
        las_points = []
        for file in las_unzipped:
            lidar_in_points = wbe.read_lidar(file)
            wbe.las_to_ascii(lidar_in_points)
        for file in glob.glob(output_directory + "/*.csv"):
            las_points.append(file)
        df = pd.concat(map(pd.read_csv, las_points), ignore_index=True)
        crs = (
            'PROJCS["NAD_1983_2011_StatePlane_Florida_North_FIPS_0903_Ft_US",'
            ' GEOGCS["GCS_NAD_1983_2011",DATUM["D_NAD_1983_2011",'
            ' SPHEROID["GRS_1980",6378137.0,298.257222101]],'
            ' PRIMEM["Greenwich",0.0], UNIT["Degree",0.0174532925199433]],'
            ' PROJECTION["Lambert_Conformal_Conic"],'
            ' PARAMETER["False_Easting",1968500.0],'
            ' PARAMETER["False_Northing",0.0],'
            ' PARAMETER["Central_Meridian",-84.5],'
            ' PARAMETER["Standard_Parallel_1",30.75],'
            ' PARAMETER["Standard_Parallel_2",29.5833333333333],'
            ' PARAMETER["Latitude_Of_Origin",29.0],'
            ' UNIT["US survey foot",0.304800609601219]]')
        gdf_2 = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['X'], df['Y'], df['Z']),
            crs=crs
            )
        current_datetime =str(
            datetime.now()).replace(' ', '_').replace('-', '')
        str_current_datetime = str(current_datetime)
        file_name = (
            str_current_datetime \
                + f"_{projectnumber}-ground_multipoints.shp"
                )
        output_file_points = str(OUTPUT_DIR / f"{file_name}")
        gdf_2.to_file(output_file_points)
        logger.debug('process_lidar_data: complete')
        return None
    except ValueError as e:
        logger.debug('ValueError occurred %s', e)
        logger.debug('process_lidar_data: failed')
    except TypeError as e:
        logger.debug('TypeError occurred %s', e)
        logger.debug('process_lidar_data: failed')
