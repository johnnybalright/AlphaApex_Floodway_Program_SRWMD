"""
River Bank Geometry Calculation Module.

This module is focused on the calculation and output of river bank
geometry, specifically aligned with project details, water level
variations, and updated centerline geometry. It utilizes geospatial
data processing libraries such as GeoPandas and Shapely to perform
complex geometric operations and analyses.

Functions:
    bank_geom(projectnumber,
    delta_water_level_el,
    gs_updated_center,
    logger_1):
        This function primarily calculates and saves the river bank
        geometry as per the provided project specifics. It manipulates
        and analyzes geometric data corresponding to various aspects
        such as contours, elevations, and distances, integrating all to
        yield the final river bank geometry.

Dependencies:
    - GeoPandas
    - Shapely
    - NumPy
    - Custom modules and functions like `geom_helper` and `misc_helper`

External Files and Constants:
    Utilizes external file paths and constants imported from
    `file_paths` and employs them for reading and writing geospatial
    data, ensuring that the output is appropriately saved and aligned
    with the project’s specifications.

Error Handling:
    The function within this module is fortified with error-handling
    mechanisms ensuring that specific errors, like ValueErrors and
    TypeErrors, are caught and logged, enabling traceability and
    debugging.

Usage:
    Ensure that necessary dependencies are installed and available,
    and that essential files and paths are correctly configured before
    utilizing the function within this module.
"""
import os
import sys
from dirs_configs.file_paths import (
    EOW_PT_1,
    TOB_PT_1,
    EOW_PT_2,
    TOB_PT_2,
    CONTOUR_EOW_TEMPLATE,
    CONTOUR_TOB_TEMPLATE,
    CONTOUR_EOW_TEMPLATE_1,
    CONTOUR_TOB_TEMPLATE_1,
    CONTOUR_EOW_TEMPLATE_2,
    CONTOUR_TOB_TEMPLATE_2,
    IN_SHP_CONTOURS
    )
from helpers.geom_helper import (
    distance_to_point,
    shorten_linestring,
    scale_linestring
    )
from helpers.misc_helper import interpolate_row
import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
from shapely.geometry import (
    Point,
    LineString,
    shape,
    MultiPoint
    )


def bank_geom(projectnumber,
              delta_water_level_el,
              gs_center,
              gs_updated_center,
              gs_1,
              gs_setback,
              logger_1
              ):
    """
    Calculates the geometry of a river bank based on the given project
    number, delta water level elevation, and updated centerline
    geometry.

    Args:
    - projectnumber (str): The project number.
    - delta_water_level_el (float): The difference in water level
    elevation.
    - gs_updated_center (GeoSeries): The updated centerline
    geometry.

    Returns:
    - gdf_tob (GeoDataFrame): The geometry of the river bank.
    """
    try:
        logger = logger_1
        if gs_updated_center is None:
            gdf_tob = None
            return gdf_tob
        contour_eow = CONTOUR_EOW_TEMPLATE.format(
            projectnumber=projectnumber
            )
        contour_tob = CONTOUR_TOB_TEMPLATE.format(
            projectnumber=projectnumber
            )
        scaled_line = scale_linestring(gs_center, 2)
        intersection_setback = scaled_line.intersection(gs_setback)
        parcel_centroid = gs_1.centroid
        dist_1 =  parcel_centroid.distance(Point(scaled_line.coords[0]))
        dist_2 = parcel_centroid.distance(Point(scaled_line.coords[1]))
        if dist_1 < dist_2:
            new_point = Point(scaled_line.coords[1])
            logger.debug(f"dist_2 is greater")
        else:
            new_point = Point(scaled_line.coords[0])
            logger.debug(f"dist_1 is greater")
        pt_1 = Point(intersection_setback)
        pt_2 = new_point
        new_line = LineString((pt_1, pt_2))
        logger.debug(f"new_line: {new_line}")
        gdf_contours = gpd.read_file(IN_SHP_CONTOURS)
        target_elevation = round(float(delta_water_level_el))
        logger.debug(f"target_elevation: {target_elevation}")
        elevations = []
        if 'ELEV' not in gdf_contours.columns:
            gdf_contours['ELEV'] = gdf_contours['geometry'].apply(
                lambda contour: sum(
                    point[2] for point in contour.coords) / len(contour.coords)
                if contour.coords else None
            )
            matching_contours = gdf_contours[
                gdf_contours['ELEV'] == target_elevation
                ]
        else:
            matching_contours = gdf_contours[
                gdf_contours['ELEV'] == target_elevation
                ]
        intersection_points = []
        intersecting_contour = []
        for contour in matching_contours.geometry:
            if contour.intersects(new_line):
                intersecting_contour.append(contour)
                intersection = contour.intersection(new_line)
                if isinstance(intersection, Point):
                    intersection_points.append(intersection)
                else:
                    for geom in intersection:
                        if isinstance(geom, Point):
                            intersection_points.append(geom)
        if len(intersection_points) == 2:
            dist_3 =  parcel_centroid.distance(
                Point(
                    intersection_points[0])
                )
            dist_4 = parcel_centroid.distance(
                Point(
                    intersection_points[1])
                )
            if dist_3 < dist_4:
                eow_contour = intersecting_contour[0]
                eow_pt = intersection_points[0]
            else:
                eow_contour = intersecting_contour[1]
                eow_pt = intersection_points[1]
            gdf_contour_eow = gpd.GeoDataFrame(
                geometry=[eow_contour],
                crs="epsg:6441"
                )
            gdf_contour_eow.to_file(contour_eow)
            gdf_eow_pt = gpd.GeoDataFrame(
                geometry=[eow_pt],
                crs="epsg:6441"
                )
            gdf_eow_pt.to_file(EOW_PT_1)
        else:
            logger.debug(
                "Error: No intersection points found or more " \
                    + "than 2 points found."
                    )
            sys.exit(1)
    except Exception as e:
        logger.debug(f"Error: {e}")
        sys.exit(1)
    try:
        coord_lst = []
        for geom in gs_updated_center['geometry']:
            if isinstance(geom, LineString):
                for coord in geom.coords:
                    x, y, z = coord
                    coordinates = (x, y, z)
                    coord_lst.append(coordinates)
        center_arr = np.array(coord_lst)
        flattened_arr = center_arr[:, :2]
        eow_arr = np.array([[eow_pt.x, eow_pt.y]])
        arr_setback = np.array(
            [[intersection_setback.x, intersection_setback.y]]
            )
        distance_1 =  np.linalg.norm(flattened_arr - eow_arr, axis=1)
        distance_2 =  np.linalg.norm(flattened_arr - arr_setback, axis=1)
        index_eow = np.argmin(distance_1)
        logger.debug(f"index_eow: {index_eow}")
        index_setback = np.argmin(distance_2)
        logger.debug(f"index_setback: {index_setback}")
        if index_eow < index_setback:
            bank_arr = center_arr[index_eow:index_setback]
        else:
            bank_arr = center_arr[index_setback:index_eow]
        bank_z_arr = bank_arr[:, 2]
        derivative_1 = np.diff(bank_z_arr)
        logger.debug(f"derivative_1: {derivative_1}")
        derivative_2 = np.diff(derivative_1)
        logger.debug(f"derivative_2: {derivative_2}")
        slope_change = np.argmax(np.abs(derivative_2))
        logger.debug(f"slope_change: {slope_change}")
        adjusted_slope = slope_change + 1
        tob_arr = bank_arr[adjusted_slope]
        tob_pt = Point(tob_arr[0], tob_arr[1], tob_arr[2])
        closest_contour = None
        min_distance = float('inf')
        tob_point = tob_pt
        for contour in gdf_contours['geometry']:
            distance = contour.distance(tob_point)
            if distance < min_distance:
                min_distance = distance
                tob_closest_contour = contour
        gs_tob = gpd.GeoSeries([tob_closest_contour])
        gdf_tob = gpd.GeoDataFrame(geometry=gs_tob, crs='epsg:6441')
        gdf_tob.to_file(contour_tob)
    except Exception as e:
        logger.debug(f"Error: {e}")
        sys.exit(1)
    return gdf_tob
