"""
Module for Topographic Center Line Calculation.

This module contains a function, `center_tob`, which carries out a
series of geospatial operations on a given center line represented as
a GeoSeries object. The primary functionality involves the enhancement
of the input center line by incorporating topographical (elevation)
information derived from a DEM raster.

Functions:
    center_tob(gs_center, logger_1):
        Buffers the input line, clips a DEM raster using the buffered
        line, interpolates z-values using the clipped DEM, smoothes the
        line using cubic spline interpolation, and saves the resultant
        geometries, returning the enhanced center line and smoothed
        points as output.

Dependencies:
    - GeoPandas
    - Shapely
    - Fiona
    - Rasterio
    - NumPy

External Files:
    The function relies on external files such as DEM rasters and
    predefined directories for saving output shapefiles.

Error Handling:
    Error handling is incorporated within the function, allowing it to
    log failures and continue execution.

Note:
    Essential configurations and file paths (e.g., IN_DEM_MAIN,
    OUT_SHP_CENTER_LINE_BUFFER, etc.) should be predefined and
    correctly set before executing the function.
"""
from dirs_configs.file_paths import (
    OUT_DEM_CENTER_LINE_BUFFER,
    OUT_SHP_CENTER,
    OUT_SHP_CENTER_LINE_BUFFER,
    CENTER_XS_LINE_ADDED_PTS,
    CENTER_XS_LINE_Z,
    CENTER_XS_LINE_Z_SMOOTHED)
from dirs_configs.input_vars import IN_DEM_MAIN
from helpers.misc_helper import read_raster, interpolate_z_values
import geopandas as gpd
import fiona
import numpy as np
from shapely.geometry import LineString
import rasterio
import rasterio.mask
from scipy.interpolate import CubicSpline


def center_tob(gs_center, river_frontage_length, logger_1):
    """
    This function takes a GeoSeries object and a logger object as input
    and performs the following operations:
    1. Creates a buffer around the input GeoSeries object and clips a
    DEM raster using the buffered line.
    2. Adds points to the center line and interpolates z-values for
    each point using the clipped DEM.
    3. Smooths the center line using cubic spline interpolation and
    saves the smoothed line to a file. The function returns a tuple
    containing the updated center line and the smoothed points.

    Args:
    - gs_center (GeoSeries): A GeoSeries object representing the
    center line.
    - logger_1 (Logger): A logger object for logging debug information.

    Returns:
    - result (tuple): A tuple containing the updated center line and
    the smoothed points.
    """
    try:
        logger = logger_1
        if river_frontage_length == 0:
            gs_updated_center = None
            smooth_points = None
            result = (gs_updated_center, smooth_points)
            return result
        gs_center_line = gs_center
        gs_center_line_ = gpd.GeoSeries(gs_center_line)
        center_buffer_distance = 100
        buffered_center_line = gs_center_line_.buffer(center_buffer_distance)
        buffered_center_line_out = gpd.GeoDataFrame(buffered_center_line)
        with rasterio.open(IN_DEM_MAIN) as src:
            out_image, out_transform = rasterio.mask.mask(
                src,
                buffered_center_line,
                crop=True
            )
            out_meta = src.meta
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform})
        with rasterio.open(
            OUT_DEM_CENTER_LINE_BUFFER,
            "w",
            **out_meta
            ) as dest:
            dest.write(out_image)
        logger.debug('clipped dem with buffer')
        gs = gs_center
        points = []
        length = gs.length
        for distance in range(0, int(length) + 5):
            point = gs.interpolate(distance)
            points.append(point)
        points_gs = gpd.GeoSeries(points)
        linestring = LineString(points)
        linestring_gs = gpd.GeoSeries(linestring)
        linestring_gs.to_file(CENTER_XS_LINE_ADDED_PTS)
        logger.debug('added points to center line')
        raster_filename = OUT_DEM_CENTER_LINE_BUFFER
        raster_data, raster_transform = read_raster(raster_filename)
        coords = []
        for line in linestring_gs:
            for x, y in line.coords:
                xy = x, y
                coords.append(xy)
        original_coords = coords
        original_linestring = LineString(original_coords)
        z_values = interpolate_z_values(
            original_linestring,
            raster_data,
            raster_transform
            )
        updated_coords = [
            (x, y, z) for (x, y), z in zip(
                original_coords, z_values)
            ]
        updated_linestring = LineString(updated_coords)
        gs_updated_center = gpd.GeoDataFrame(
            geometry=[updated_linestring]
            )
        gs_updated_center.to_file(CENTER_XS_LINE_Z)
        logger.debug('added z values to center line')
        gs = gs_updated_center
        coords = []
        for line in gs.geometry:
            for x, y, z in line.coords:
                xyz = x, y, z
                coords.append(xyz)
        gs_arr = np.array(coords)
        points = gs_arr
        x = points[:, 0]
        y = points[:, 1]
        z = points[:, 2]
        t = np.arange(len(points))
        cs_y = CubicSpline(t, y)
        cs_z = CubicSpline(t, z)
        t2 = np.linspace(t.min(), t.max(), 100)
        y2 = cs_y(t2)
        z2 = cs_z(t2)
        smooth_points = np.vstack([t2, y2, z2]).T
        linestring = LineString(smooth_points)
        gdf = gpd.GeoDataFrame(geometry=[linestring])
        gdf = gdf.set_crs('epsg:6441')
        gdf.to_file(CENTER_XS_LINE_Z_SMOOTHED)
        logger.debug("center_line_tob: complete")
        result = (gs_updated_center, smooth_points)
        return result
    except ValueError as e:
        logger.debug("ValueError occurred %s", e)
    except TypeError as e:
        logger.debug("TypeError occurred %s", e)
