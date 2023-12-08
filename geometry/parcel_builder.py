#Filename: parcel_builder.py
"""
This module provides functionalities to build a parcel using various
shapefiles and data inputs.

Functions:
- parcel_builder: Builds a parcel by processing various geometrical
inputs, such as elevation contours and center lines. It translates the
river frontage line based on these inputs and outputs a GeoDataFrame
containing the translated line.

Usage:
    parcel_builder(projectnumber,
    gs_center,
    yr100,
    yr50,
    yr10,
    delta_water_level_el_1,
    logger_1
    )

Attributes:
    projectnumber (str): The project number, used for identifying
    and saving the processed files.
    gs_center (GeoSeries): A GeoSeries containing the center line
    shapefile data.
    yr100 (str): The file path for the 100-year elevation contour
    shapefile.
    yr50 (str): The file path for the 50-year elevation contour
    shapefile.
    yr10 (str): The file path for the 10-year elevation contour
    shapefile.
    delta_water_level_el_1 (float): The delta water level elevation,
    used in parcel building calculations.
    logger_1 (logger): A logger object for logging debug information
    and errors.

Returns:
    GeoDataFrame: A GeoDataFrame containing the translated river
    frontage line as part of the parcel building process.
"""
import shutil
import os
import os.path
import time
import itertools
from shapely.ops import split
from shapely.geometry import (
    shape,
    Point,
    LineString,
    MultiPoint,
    MultiLineString
    )
from shapely.affinity import translate
import pandas as pd
import geopandas as gpd
import numpy as np
from dirs_configs.config import OUTPUT_DIRx, BASE_DIR
from helpers.misc_helper import find_closest_index, find_nearest_idx
from helpers.geom_helper import (
    find_closest_line,
    create_polygon_from_lines
    )
from dirs_configs.input_vars import EB_LINE, WB_LINE
from dirs_configs.file_paths import (
    CONTOUR_EOW_TEMPLATE,
    CONTOUR_TOB_TEMPLATE,
    CONTOUR_EOW_TEMPLATE_1,
    CONTOUR_TOB_TEMPLATE_1,
    CONTOUR_EOW_TEMPLATE_2,
    CONTOUR_TOB_TEMPLATE_2,
    EOW_CONTOUR_PARCEL,
    HX_LINE_PARCEL_INTERSECTION_PTS,
    HX_LINE_PARCEL_INTERSECTION_PTS_2,
    HX_LINE_Z_SMOOTHED,
    IN_SHP_CONTOURS,
    OUT_SHP_CENTER,
    PARCEL_CONTOURS,
    SETBACK75,
    TOB_CONTOUR_PARCEL,
    WATER_LEVEL_SECTION_LINE,
    XL_POST,
    YR100_CONTOUR,
    YR100_SECTION_LINE,
    IN_SHP,
    PARCEL_BOUNDARY_SITE,
    YR50_CONTOUR,
    YR10_CONTOUR
    )
import signal


def parcel_builder(
    projectnumber,
    gs_center,
    gs_setback,
    yr100,
    yr50,
    yr10,
    delta_water_level_el_1,
    river_frontage_length,
    logger_1
    ):
    """
    Builds a parcel using various shapefiles and data inputs.
    Args:
    - projectnumber (str): The project number.
    - gs_center (GeoSeries): A GeoSeries containing the center line
    shapefile data.
    - yr100 (str): The file path for the 100-year elevation contour
    shapefile.
    - yr50 (str): The file path for the 50-year elevation contour
    shapefile.
    - yr10 (str): The file path for the 10-year elevation contour
    shapefile.
    - delta_water_level_el (float): The delta water level elevation.
    Returns:
    - gdf_trans (GeoDataFrame): A GeoDataFrame containing the
    translated river frontage line.
    """
    try:
        logger = logger_1
        if river_frontage_length == 0:
            logger.debug('river_frontage = 0-parcel_bulder: stopped')
            return None
        delta_water_level_el = delta_water_level_el_1
        target_line_shp_path = CONTOUR_EOW_TEMPLATE.format(
            projectnumber=projectnumber)
        gdf_eb = gpd.read_file(EB_LINE)
        gdf_wb = gpd.read_file(WB_LINE)
        gs_eb = gpd.GeoSeries(gdf_eb['geometry'])
        gs_wb = gpd.GeoSeries(gdf_wb['geometry'])
        gdf_center_line = gpd.read_file(OUT_SHP_CENTER)
        gs_center_line = gpd.GeoSeries(gdf_center_line['geometry'])
        gdf_polygon = gpd.read_file(IN_SHP)
        gs_polygon = gpd.GeoSeries(gdf_polygon['geometry'])
        gs_centroid = gpd.GeoSeries(gdf_polygon['geometry'].centroid)
        simplified_polygon = gdf_polygon.geometry[0].simplify(1)
        center_line = shape(gdf_center_line.geometry.iloc[0])
        logger.debug(f"center_line: {center_line}")
        gdf_target_line = gpd.read_file(target_line_shp_path)
        target_line = shape(gdf_target_line.geometry.iloc[0])
        gdf_line_75 = gpd.read_file(SETBACK75)
        line_75 = shape(gdf_line_75.geometry.iloc[0])
        coords_lst = []
        lines = [line for line in simplified_polygon.exterior.coords]
        for line in lines:
            coords_lst.append(line)
        lines_lst = [
            LineString(
                coords_lst[i:i+2]
                ) for i in range(len(coords_lst)-1)]
        closest_index, closest_line = find_closest_line(
            target_line,
            lines_lst
            )
        intersection_point_closest = center_line.intersection(line_75)
        logger.debug(
            f"intersection_point_closest: {intersection_point_closest}"
            )
        intersection_point_target = center_line.intersection(target_line)
        logger.debug(
            f"intersection_point_target: {intersection_point_target}"
            )
        center_coords = np.array(center_line.coords)
        idx_closest = find_nearest_idx(
            intersection_point_closest,
            center_coords
            )
        logger.debug(f"idx_closest: {idx_closest}")
        idx_target = find_nearest_idx(
            intersection_point_target,
            center_coords
            )
        logger.debug(f"idx_target: {idx_target}")
        try:
            if idx_closest > idx_target:
                idx_trans = idx_target - 15
            else:
                idx_trans = idx_target + 15
            coords_trans = center_coords[idx_trans]
        except:
            idx_trans = idx_closest
            coords_trans = center_coords[idx_trans]
        midpoint = closest_line.interpolate(0.5, normalized=True)
        translation_vector = np.array(
            center_coords[idx_trans][:2]) - np.array(
                midpoint.coords[0]
                )
        translated_line = translate(
            closest_line,
            xoff=translation_vector[0],
            yoff=translation_vector[1]
            )
        gdf_trans = gpd.GeoDataFrame(geometry=[translated_line])
        gdf_trans.crs = gdf_polygon.crs
        line1 = LineString(
            [closest_line.coords[0],
             translated_line.coords[0]]
            )
        line2 = LineString(
            [closest_line.coords[-1],
             translated_line.coords[-1]]
            )
        lines_lst.remove(closest_line)
        multi_trans_line = MultiLineString(
            [line1, translated_line,
             line2]
            )
        gdf_multi_1 = gpd.GeoDataFrame(geometry=[multi_trans_line])
        poly_multi_line = MultiLineString(lines_lst)
        gdf_multi_2 = gpd.GeoDataFrame(geometry=[poly_multi_line])
        lines_1 = [line for mls in gdf_multi_1.geometry for line in mls.geoms]
        lines_2 = [line for mls in gdf_multi_2.geometry for line in mls.geoms]
        mls_1 = MultiLineString(lines_1)
        mls_2 = MultiLineString(lines_2)
        valid_polygons = []
        for combo in itertools.product(mls_1.geoms, mls_2.geoms):
            potential_polygon = create_polygon_from_lines(combo)
            if potential_polygon.is_valid:
                valid_polygons.append(potential_polygon)
        if valid_polygons:
            largest_polygon = max(valid_polygons, key=lambda p: p.area)
            logger.debug('checkpoint: found largest_polygon')
        else:
            logger.debug("No valid polygons found!")
        try:
            polygon = largest_polygon
            line = target_line
            split_polygons = split(polygon, line)
            clipped_polygon1 = split_polygons.geoms[1]
            gdf1 = gpd.GeoDataFrame(geometry=[clipped_polygon1])
            clipped_polygon2 = split_polygons.geoms[0]
            gdf2 = gpd.GeoDataFrame(geometry=[clipped_polygon2])
            gdf1['area'] = gdf1.geometry.area
            gdf2['area'] = gdf2.geometry.area
            largest_geometry_gdf1 = gdf1.loc[gdf1['area'].idxmax()]
            largest_geometry_gdf2 = gdf2.loc[gdf2['area'].idxmax()]
            logger.debug('checkpoint: splitting polygon(crucial point)-passed')
        except:
            logger.debug('splitting polygon(crucial point)-failed')
            logger.debug('parcel_builder: failed')
            os.kill(int(os.getpid()), signal.SIGTERM)
        if largest_geometry_gdf1['area'] > largest_geometry_gdf2['area']:
            gdf1.to_file(PARCEL_BOUNDARY_SITE)
            gdf_parcel_boundary = gdf1
        else:
            gdf2.to_file(PARCEL_BOUNDARY_SITE)
            gdf_parcel_boundary = gdf2
        logger.debug('checkpoint: parcel_boundary_sp created')
        tob_line = gpd.read_file(
            CONTOUR_TOB_TEMPLATE.format(projectnumber=projectnumber)
        )
        eow_line = gpd.read_file(
            CONTOUR_EOW_TEMPLATE.format(projectnumber=projectnumber)
        )
        contours = gpd.read_file(IN_SHP_CONTOURS)
        clipped_tob_line = tob_line.geometry[0].intersection(
            gdf_parcel_boundary.geometry[0]
            )
        gdf_tob_clipped = gpd.GeoDataFrame(geometry=[clipped_tob_line])
        gdf_tob_clipped.to_file(TOB_CONTOUR_PARCEL)
        logger.debug('checkpoint: tob_contour_parcel created')
        clipped_eow_line = eow_line.geometry[0].intersection(
            gdf_parcel_boundary.geometry[0]
            )
        gdf_eow_clipped = gpd.GeoDataFrame(geometry=[clipped_eow_line])
        gdf_eow_clipped.to_file(EOW_CONTOUR_PARCEL)
        logger.debug('checkpoint: eow_contour_parcel created')
        clipped_contours = contours[contours.geometry.intersects(
            gdf_parcel_boundary.geometry[0])]
        gdf_clipped_contours = gpd.GeoDataFrame(
            geometry=clipped_contours.geometry
            )
        gdf_clipped_contours.to_file(PARCEL_CONTOURS)
        logger.debug('checkpoint: contour_parcels created')
        time.sleep(5)
        shutil.copy(
            PARCEL_CONTOURS, str(
                OUTPUT_DIRx / f"{projectnumber}-countours_parcel.shp")
        )
        shutil.copy(
            TOB_CONTOUR_PARCEL, str(
                OUTPUT_DIRx / f"{projectnumber}-tob_contour_parcel.shp")
        )
        shutil.copy(
            EOW_CONTOUR_PARCEL, str(
                OUTPUT_DIRx / f"{projectnumber}-eow_contour_parcel.shp")
        )
        #change this to have same name as layer in c3d
        shutil.copy(
            PARCEL_BOUNDARY_SITE,str(
                OUTPUT_DIRx / f"{projectnumber}-\
                    parcel_boundary_siteplan.shp")
        )
        gdf = gpd.read_file(IN_SHP_CONTOURS)
        gdf['ELEV'] = None
        yr100_elev = yr100
        yr50_elev = yr50
        yr10_elev = yr10
        yr100_contour = gdf[gdf['ELEV'] == yr100_elev]
        yr50_contour = gdf[gdf['ELEV'] == yr50_elev]
        yr10_contour = gdf[gdf['ELEV'] == yr10_elev]
        if not (yr100_contour.is_empty).empty:
            yr100_contour.to_file(YR100_CONTOUR)
        else:
            logger.debug('yr100_contour is not found on parcel')
        if not (yr50_contour.is_empty).empty:
            yr50_contour.to_file(YR50_CONTOUR)
        else:
            logger.debug('yr50_contour is not found on parcel')
        if not (yr10_contour.is_empty).empty:
            yr10_contour.to_file(YR10_CONTOUR)
        else:
            logger.debug('yr10_contour is not found on parcel')
        gdf = gpd.read_file(HX_LINE_Z_SMOOTHED)
        gs = gpd.GeoSeries(gdf.geometry)[0]
        arr = np.array(gs.coords)
        value = float(delta_water_level_el)
        index = np.argmin(np.abs(arr[:, 2] - value))
        water_level_arr = arr[index:]
        water_level_arr[:, 2] = float(delta_water_level_el)
        water_level_line = LineString(water_level_arr)
        gs_water_level_line = gpd.GeoSeries(water_level_line)
        gs_water_level_line.to_file(WATER_LEVEL_SECTION_LINE)
        yr100_arr = np.copy(arr)
        yr100_arr[:, 2] = yr100
        yr100_line = LineString(yr100_arr)
        gs_yr100_line = gpd.GeoSeries(yr100_line)
        gs_yr100_line.to_file(YR100_SECTION_LINE)
        gdf1 = gpd.read_file(SETBACK75)
        gdf2 = gpd.read_file(HX_LINE_Z_SMOOTHED)
        gdf3 = gpd.read_file(IN_SHP)
        geom1 = gdf1.geometry.all()
        geom2 = gdf2.geometry.all()
        geom3 = gdf3.geometry.all()
        if geom2.intersects(geom1):
            logger.debug('hxline intersects setback75 = True')
            intersection_1 = geom2.intersection(geom1)
            gdf3_centroid = gdf3.geometry.centroid
        else:
            logger.debug('hxline intersects setback75 = False')
        if geom2.intersects(geom3):
            logger.debug('hxline intersects parcel boundary = True')
            intersection_2 = geom2.intersection(geom3)
            intersection_lst = []
            for coord in intersection_2.coords:
                intersection_lst.append(coord)
            hx_xx_parcel_pt_1 = intersection_lst[0]
            x = len(intersection_lst) - 1
            hx_xx_parcel_pt_2 = intersection_lst[x]
            hx_xx_parcel_pt_1_arr = np.array(hx_xx_parcel_pt_1)
            hx_xx_parcel_pt_2_arr = np.array(hx_xx_parcel_pt_2)
            hx_xx_parcel_pt_1_arr[2] = yr100
            hx_xx_parcel_pt_2_arr[2] = yr100
            combined_arr = np.vstack(
                (hx_xx_parcel_pt_1_arr, hx_xx_parcel_pt_2_arr)
                )
            obstruction_arr = combined_arr
            xx_points = MultiPoint(combined_arr)
            gs_xx = gpd.GeoSeries(xx_points)
            gs_xx.to_file(HX_LINE_PARCEL_INTERSECTION_PTS)
        else:
            logger.debug('hxline intersects parcel boundary = False')
        gdf_center_line = gpd.read_file(OUT_SHP_CENTER)
        geom4 = gdf_center_line.geometry[0]
        gdf3_centroid = gdf3.geometry.centroid[0]
        center_line_arr = np.array(geom4.coords)
        gdf5 = gpd.read_file(
            CONTOUR_TOB_TEMPLATE.format(projectnumber=projectnumber)
            )
        geom5 = gdf5.geometry[0]
        gdf_setback75 = gpd.read_file(SETBACK75)
        gs_setback = gpd.GeoSeries(gdf_setback75.geometry)[0].centroid
        setback_arr = np.array([gs_setback.x, gs_setback.y])
        if geom4.intersects(geom1):
            logger.debug('center_line_shp intersects setback75 = True')
            try:
                intersection_3 = geom2.intersection(geom3)
            except:
                logger.debug('hxline intersects parcel_polygon = True')
            try:
                intersection_4 = geom2.intersection(geom1)
            except:
                logger.debug(
                    "hxline intersects parcels 75ft_setback line = False"
                    )
            try:
                intersection_5 = geom2.intersection(geom5)
            except:
                logger.debug('hxline intersects tob_line = False')
            try:
                if not (intersection_5.is_empty).empty:
                    hx_xx_tob_pt = Point(intersection_5.x, intersection_5.y)
                    intersection_lst_2 = []
                    for coord in intersection_3.coords:
                        intersection_lst_2.append(coord)
                    hx_xx_parcel_2_pt_1 = Point(
                        intersection_lst_2[0][0],
                        intersection_lst_2[0][1]
                        )
                    x2 = len(intersection_lst_2) - 1
                    hx_xx_parcel_2_pt_2 = Point(
                        intersection_lst_2[x2][0],
                        intersection_lst_2[x2][1]
                        )
                    distance_1 = hx_xx_parcel_2_pt_1.distance(hx_xx_tob_pt)
                    distance_2 = hx_xx_parcel_2_pt_2.distance(hx_xx_tob_pt)
                    if distance_1 > distance_2:
                        hx_xx_parcel_2_pt_1_arr = np.array(
                            hx_xx_parcel_2_pt_1.coords
                            )
                        post_hx_arr = np.copy(arr[:, :2])
                        post_hx_arr_2 = np.copy(arr[:, :2])
                        index_hx_parcel_pt = find_closest_index(
                            post_hx_arr, hx_xx_parcel_2_pt_1_arr
                            )
                        index_setback75_pt = find_closest_index(
                            post_hx_arr_2, setback_arr
                            )
                        hx_parcel_arr_pt = arr[index_hx_parcel_pt]
                        hx_parcel_arr_pt[2] = yr100
                        setback75_arr_pt = arr[index_setback75_pt]
                        setback75_arr_pt[2] = yr100
                        combined_arr_2 = np.vstack(
                            (hx_parcel_arr_pt, setback75_arr_pt)
                            )
                        obstruction_arr = combined_arr_2
                        xx_points_2 = MultiPoint(combined_arr_2)
                        gs_xx_2 = gpd.GeoSeries(xx_points_2)
                        gs_xx.to_file(HX_LINE_PARCEL_INTERSECTION_PTS_2)
                    else:
                        hx_xx_parcel_2_pt_2_arr = np.array(
                            hx_xx_parcel_2_pt_2.coords
                            )
                        post_hx_arr = np.copy(arr[:, :2])
                        post_hx_arr_2 = np.copy(arr[:, :2])
                        index_hx_parcel_pt = find_closest_index(
                            post_hx_arr,
                            hx_xx_parcel_2_pt_2_arr
                            )
                        index_setback75_pt = find_closest_index(
                            post_hx_arr_2,
                            setback_arr
                            )
                        hx_parcel_arr_pt = arr[index_hx_parcel_pt]
                        hx_parcel_arr_pt[2] = yr100
                        setback75_arr_pt = arr[index_setback75_pt]
                        setback75_arr_pt[2] = yr100
                        combined_arr_2 = np.vstack(
                            (hx_parcel_arr_pt, setback75_arr_pt)
                            )
                        obstruction_arr = combined_arr_2
                        xx_points_2 = MultiPoint(combined_arr_2)
                        gs_xx_2 = gpd.GeoSeries(xx_points_2)
                        gs_xx.to_file(HX_LINE_PARCEL_INTERSECTION_PTS_2)
                else:
                    logger.debug(
                        "intersection_5 geometry is is_empty because hxline \
                            does not intersect parcel_tob"
                        )
            except:
                logger.debug(
                    "hxline is outside the boundaries of the parcel"
                    )
        else:
            logger.debug('center_line_shp intersects setback75 = False')
        try:
            if geom2.intersects(
                geom3) == True and geom2.intersects(
                    geom1) == True:
                gdf_hx = gpd.read_file(HX_LINE_Z_SMOOTHED)
                coords_hx = list(gdf_hx.iloc[0].geometry.coords)
                hx_arr = np.array(coords_hx)
                combined_arr = np.vstack((hx_arr, obstruction_arr))
                sorted_combined_arr = combined_arr[
                    combined_arr[:, 0].argsort()
                    ]
                first_col = sorted_combined_arr[:, 0]
                value_1 = obstruction_arr[0][0]
                value_2 = obstruction_arr[1][0]
                indices_1 = np.where(first_col == value_1)[0]
                indices_2 = np.where(first_col == value_2)[0]
                sorted_combined_arr[:, 0] -= sorted_combined_arr[0][0]
                sorted_combined_arr[:, 0] += 10000
                sorted_combined_arr = sorted_combined_arr[:, [0, 2]]
                sorted_combined_arr[:, 1] = sorted_combined_arr[::-1, 1]
                arr_obs1 = sorted_combined_arr[indices_1]
                arr_obs2 = sorted_combined_arr[indices_2]
                arr_obs = np.vstack((arr_obs1, arr_obs2))
                arr_obs_transposed = arr_obs.T
                df = pd.DataFrame(
                    arr_obs_transposed,
                    columns=['obstruction_1_scenario_1',
                            'obstruction_2_scenario_1']
                    )
                if not os.path.exists(XL_POST):
                    empty_df = pd.DataFrame()
                    empty_df.to_excel(XL_POST, index=False)
                df_2 = pd.read_excel(
                    XL_POST,
                    engine='openpyxl',
                    sheet_name='Sheet1'
                    )
                combined_df = pd.concat([df_2, df], axis=1)
                combined_df.to_excel(
                    XL_POST,
                    index=False,
                    engine='openpyxl'
                    )
                logger.debug('plabz_parcel_builder: complete')
            else:
                logger.debug('plabz_parcel_builder: complete')
                pass
        except:
            logger.debug('plabz_parcel_builder: complete')
            pass
    except ValueError as e:
        logger.debug('ValueError occurred %s', e)
        logger.debug('plabz_parcel_builder: failed')
    except TypeError as e:
        logger.debug('TypeError occurred %s', e)
        logger.debug('plabz_parcel_builder: failed')
    return None
