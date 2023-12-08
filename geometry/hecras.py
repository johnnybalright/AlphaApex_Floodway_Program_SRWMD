import csv
import os
import os.path
import shutil
import time
import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
from dirs_configs.file_paths import (
    CSV_HX_ARR,
    CSV_PATH,
    HX_CADD_TEMPLATE,
    HX_LINE_ADDED_PTS,
    HX_LINE_Z,
    HX_LINE_Z_SMOOTHED,
    OUT_DEM_BUFFER,
    OUT_SHP_BUFFER,
    OUT_SHP_HXLINE,
    XL_XS_DATA,
    XL_XS_EX,
)
from dirs_configs.input_vars import *
from helpers.misc_helper import *
from sqlalchemy import create_engine
os.environ["SQLALCHEMY_WARN_20"] = "1"
import math
import rasterio
import rasterio.mask
import shapely.geometry
from scipy.interpolate import CubicSpline
from shapely import wkt
from shapely.geometry import (
    LineString,
    Point,
    MultiPoint,
    MultiLineString
    )
from sqlalchemy.orm import sessionmaker


def closest_point(geometry, ref_point):
    if isinstance(geometry, MultiPoint):
        return min(geometry.geoms, key=lambda p: p.distance(ref_point))
    elif isinstance(geometry, Point):
        return geometry
    else:
        return None


def hecras_calc(
    projectnumber,
    gs_1,
    yr100,
    yr50,
    yr10,
    firm_panel,
    logger_1
    ):
    """
    Generates HECRAS cross section line and river
    river stations/elevations.

    Args:
    projectnumber (str): The project number.
    path (str): The path to the project folder.
    gs_1 (GeoSeries): The GeoSeries object containing
    the geometry of the project.
    yr100 (float): The year 100 flood level.
    yr50 (float): The year 50 flood level.
    yr10 (float): The year 10 flood level.
    firm_panel (str): The path to the firm panel file.

    Returns:
    """
    try:
        logger = logger_1
        start_time = time.time()
        HX_CADD = HX_CADD_TEMPLATE.format(projectnumber=projectnumber)
        db_connection_string = (
            "postgresql+psycopg2://linpostgres:HJYkgHL74!t6nXJ9"
            "@lin-18909-6549-pgsql-primary.servers.linodedb.net"
            "/postgres"
        )
        engine = create_engine(
            db_connection_string,
            pool_size=30,
            max_overflow=100,
        )
        gs = gs_1
        gs = gpd.GeoSeries(gs)
        gs = gs.set_crs("epsg:6441")
        gs_pbound_p = gs
        gs_pbound_c = gs_pbound_p.centroid
        gdf_pbound_p = gpd.GeoDataFrame(geometry=gs_pbound_p)
        gdf_pbound_c = gpd.GeoDataFrame(geometry=gs_pbound_c)
        session = sessionmaker(bind=engine)
        try:
            with session() as session:
                gdf_pbound_p.to_postgis(
                    "gdf_pbound_p",
                    engine,
                    if_exists="replace"
                    )
                gdf_pbound_c.to_postgis(
                    "gdf_pbound_c",
                    engine,
                    if_exists="replace"
                    )
                sql_gdf_pbound_c_wfldwy_shortestline = (
                    "SELECT ST_ASTEXT(ST_SHORTESTLINE(gdf_pbound_c.geometry, wfldwy_pt.geom)) "
                    "FROM gdf_pbound_c, wfldwy_pt ORDER BY "
                    "wfldwy_pt.geom <-> gdf_pbound_c.geometry;"
                )
                result_1 = engine.execute(sql_gdf_pbound_c_wfldwy_shortestline)
                geom_text_1 = result_1.fetchone()[0]
                shapely_obj_1 = wkt.loads(geom_text_1)
                gdf_1 = gpd.GeoDataFrame(geometry=[shapely_obj_1])
                gdf_pbound_c_wfldwy_shortestline = gdf_1.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_pbound_c_wfldwy_shortestline.to_postgis(
                    "gdf_pbound_c_wfldwy_shortestline",
                    engine,
                    index=True,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_pbound_c_efldwy_shortestline = (
                    "SELECT ST_ASTEXT(ST_SHORTESTLINE(gdf_pbound_c.geometry, efldwy_pt.geom)) "
                    "FROM gdf_pbound_c, efldwy_pt ORDER BY "
                    "efldwy_pt.geom <-> gdf_pbound_c.geometry;"
                )
                result_2 = engine.execute(sql_gdf_pbound_c_efldwy_shortestline)
                geom_text_2 = result_2.fetchone()[0]
                shapely_obj_2 = wkt.loads(geom_text_2)
                gdf_2 = gpd.GeoDataFrame(geometry=[shapely_obj_2])
                gdf_pbound_c_efldwy_shortestline = gdf_2.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_pbound_c_efldwy_shortestline.to_postgis(
                    "gdf_pbound_c_efldwy_shortestline",
                    engine,
                    index=True,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_pbound_c_efldwy_intersection_pt = (
                    "SELECT ST_AsText(ST_ClosestPoint("
                    "gdf_pbound_c_efldwy_shortestline.geometry,"
                    "efldwy_l.geom)) FROM gdf_pbound_c_efldwy_shortestline, efldwy_l;"
                )
                sql_3 = sql_gdf_pbound_c_efldwy_intersection_pt
                result_3 = engine.execute(sql_3)
                geom_text_3 = result_3.fetchone()[0]
                shapely_obj_3 = wkt.loads(geom_text_3)
                gdf_3 = gpd.GeoDataFrame(geometry=[shapely_obj_3])
                gdf_pbound_c_efldwy_intersection_pt = gdf_3.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_pbound_c_efldwy_intersection_pt.to_postgis(
                    "gdf_pbound_c_efldwy_intersection_pt",
                    engine,
                    index=False,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_pbound_c_wfldwy_intersection_pt = (
                    "SELECT ST_AsText(ST_ClosestPoint("
                    "gdf_pbound_c_wfldwy_shortestline.geometry, wfldwy_l.geom))"
                    "FROM gdf_pbound_c_wfldwy_shortestline, wfldwy_l;"
                )
                sql_4 = sql_gdf_pbound_c_wfldwy_intersection_pt
                result_4 = engine.execute(sql_4)
                geom_text_4 = result_4.fetchone()[0]
                shapely_obj_4 = wkt.loads(geom_text_4)
                gdf_4 = gpd.GeoDataFrame(geometry=[shapely_obj_4])
                gdf_pbound_c_wfldwy_intersection_pt = gdf_4.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_pbound_c_wfldwy_intersection_pt.to_postgis(
                    "gdf_pbound_c_wfldwy_intersection_pt",
                    engine,
                    index=False,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_hline_1 = (
                    "SELECT ST_AsText(ST_MakeLine" \
                        + "(gdf_pbound_c_efldwy_intersection_pt.geometry, "
                    "gdf_pbound_c_wfldwy_intersection_pt.geometry)) "
                    "FROM gdf_pbound_c_efldwy_intersection_pt, gdf_pbound_c_wfldwy_intersection_pt;"
                )
                sql_5 = sql_gdf_hline_1
                result_5 = engine.execute(sql_5)
                geom_text_5 = result_5.fetchone()[0]
                shapely_obj_5 = wkt.loads(geom_text_5)
                gdf_5 = gpd.GeoDataFrame(geometry=[shapely_obj_5])
                gdf_hline_1 = gdf_5.set_geometry("geometry").set_crs("epsg:6441")
                gdf_hline_1.to_postgis(
                    "gdf_hline_1",
                    engine,
                    index=False,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_hline_1_translate_l = (
                    "SELECT ST_AsText(ST_ShortestLine("
                    "gdf_pbound_c.geometry, gdf_hline_1.geometry)) "
                    "FROM gdf_pbound_c, gdf_hline_1 ORDER BY gdf_hline_1.geometry"
                    "<-> gdf_pbound_c.geometry limit 1;"
                )
                sql_6 = sql_gdf_hline_1_translate_l
                result_6 = engine.execute(sql_6)
                geom_text_6 = result_6.fetchone()[0]
                shapely_obj_6 = wkt.loads(geom_text_6)
                gdf_6 = gpd.GeoDataFrame(geometry=[shapely_obj_6])
                gdf_hline_1_translate_l = gdf_6.set_geometry("geometry").set_crs(
                    "epsg:6441"
                )
                gdf_hline_1_translate_l.to_postgis(
                    "gdf_hline_1_translate_l",
                    engine,
                    index=False,
                    index_label="Index",
                    if_exists="replace",
                )
                sql_gdf_hline_1_translate_l_closest_point = (
                    "SELECT ST_AsText(ST_ClosestPoint("
                    "gdf_hline_1_translate_l.geometry, gdf_hline_1.geometry)) "
                    "FROM gdf_hline_1_translate_l, gdf_hline_1;"
                )
                sql_7 = sql_gdf_hline_1_translate_l_closest_point
                result_7 = engine.execute(sql_7)
                geom_text_7 = result_7.fetchone()[0]
                shapely_obj_7 = wkt.loads(geom_text_7)
                gdf_7 = gpd.GeoDataFrame(geometry=[shapely_obj_7])
                gdf_hline_1_translate_l_closest_point = gdf_7.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hline_1_translate_l_closest_point.to_postgis(
                    "gdf_hline_1_translate_l_closest_point",
                    engine,
                    index=False,
                    index_label="Index",
                    if_exists="replace",
                )
                gdf_hline_lst = [
                    gdf_hline_1_translate_l_closest_point.geometry.x[0],
                    gdf_hline_1_translate_l_closest_point.geometry.y[0],
                ]
                gdf_hline_arr = np.asarray(gdf_hline_lst)
                gs_pbound_c.reset_index(drop=True, inplace=True)
                gdf_pbound_c_lst = [
                    gs_pbound_c.geometry.x[0],
                    gs_pbound_c.geometry.y[0],
                ]
                gdf_pbound_c_arr = np.asarray(gdf_pbound_c_lst)
                # begin with pbound_arr
                translation_diff = np.subtract(gdf_pbound_c_arr, gdf_hline_arr)
                pos_count, neg_count = 0, 0
                for num in translation_diff:
                    if num >= 0:
                        pos_count += 1
                    else:
                        neg_count += 1
                logger.debug("positive_count: %s", pos_count)
                logger.debug("negative_count: %s", neg_count)
                sql_gdf_hline_2 = (
                    f"SELECT ST_AsText(ST_Translate(gdf_hline_1.geometry, "
                    f"{translation_diff[0]}, {translation_diff[1]}, 0)) FROM gdf_hline_1;"
                )
                sql_9 = sql_gdf_hline_2
                result_9 = engine.execute(sql_9)
                geom_text_9 = result_9.fetchone()[0]
                shapely_obj_9 = wkt.loads(geom_text_9)
                gdf_9 = gpd.GeoDataFrame(geometry=[shapely_obj_9])

                gdf_hline_2 = gdf_9.set_geometry("geometry").set_crs("epsg:6441")
                gdf_hline_2.to_postgis("gdf_hline_2", engine, if_exists="replace")
                sql_gdf_hline_2_efldwy_pt_shortestline = (
                    "SELECT ST_AsText(ST_ShortestLine("
                    "efldwy_l.geom, gdf_hline_2.geometry)) FROM efldwy_l, gdf_hline_2;"
                )
                sql_10 = sql_gdf_hline_2_efldwy_pt_shortestline
                result_10 = engine.execute(sql_10)
                geom_text_10 = result_10.fetchone()[0]
                shapely_obj_10 = wkt.loads(geom_text_10)
                gdf_10 = gpd.GeoDataFrame(geometry=[shapely_obj_10])
                gdf_hline_2_efldwy_pt_shortestline = gdf_10.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hline_2_efldwy_pt_shortestline.to_postgis(
                    "gdf_hline_2_efldwy_pt_shortestline",
                    engine,
                    if_exists="replace",
                )
                sql_gdf_hline_2_wfldwy_pt_shortestline = (
                    "SELECT ST_AsText(ST_ShortestLine("
                    "wfldwy_l.geom, gdf_hline_2.geometry))"
                    "FROM wfldwy_l, gdf_hline_2;"
                )
                sql_11 = sql_gdf_hline_2_wfldwy_pt_shortestline
                result_11 = engine.execute(sql_11)
                geom_text_11 = result_11.fetchone()[0]
                shapely_obj_11 = wkt.loads(geom_text_11)
                gdf_11 = gpd.GeoDataFrame(geometry=[shapely_obj_11])
                gdf_hline_2_wfldwy_pt_shortestline = gdf_11.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hline_2_wfldwy_pt_shortestline.to_postgis(
                    "gdf_hline_2_wfldwy_pt_shortestline",
                    engine,
                    if_exists="replace",
                )
                sql_gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2 = (
                    "SELECT ST_AsText(ST_ClosestPoint("
                    "gdf_hline_2_efldwy_pt_shortestline.geometry, efldwy_l.geom)) "
                    "FROM gdf_hline_2_efldwy_pt_shortestline, efldwy_l;"
                )
                sql_12 = sql_gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2
                result_12 = engine.execute(sql_12)
                geom_text_12 = result_12.fetchone()[0]
                shapely_obj_12 = wkt.loads(geom_text_12)
                gdf_12 = gpd.GeoDataFrame(geometry=[shapely_obj_12])
                gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2 = (
                    gdf_12.set_geometry("geometry").set_crs("epsg:6441")
                )
                gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2.to_postgis(
                    "gdf_hline_2_efw_pt_shrtstln_clsst_pt_v2",
                    engine,
                    if_exists="replace",
                )
                xefldwy = (
                    gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2.geometry.x[0]
                )
                yefldwy = (
                    gdf_hline_2_efldwy_pt_shortestline_closest_point_ver2.geometry.y[0]
                )
                gdf_hxline_v3_efldwy_pt_arr = np.asarray([xefldwy, yefldwy])
                sql_gdf_hline_2_wfldwy_pt_shortestline_closest_point_ver2 = (
                    "SELECT ST_AsText(ST_ClosestPoint("
                    "gdf_hline_2_wfldwy_pt_shortestline.geometry, wfldwy_l.geom)) "
                    "FROM gdf_hline_2_wfldwy_pt_shortestline, wfldwy_l;"
                )
                sql_13 = sql_gdf_hline_2_wfldwy_pt_shortestline_closest_point_ver2
                result_13 = engine.execute(sql_13)
                geom_text_13 = result_13.fetchone()[0]
                shapely_obj_13 = wkt.loads(geom_text_13)
                gdf_13 = gpd.GeoDataFrame(geometry=[shapely_obj_13])
                gdf_hline_2_wfldwy_pt_shortestline_closest_point_ver2 = (
                    gdf_13.set_geometry("geometry").set_crs("epsg:6441")
                )
                gdf_hline_2_wfldwy_pt_shortestline_closest_point_ver2.to_postgis(
                    "gdf_hline_2_wfw_pt_shrtstln_clsst_pt_v2",
                    engine,
                    if_exists="replace",
                )
                sql_gdf_hxline_v3 = (
                    "SELECT ST_AsText(ST_MakeLine("
                    "gdf_hline_2_wfw_pt_shrtstln_clsst_pt_v2.geometry, "
                    "gdf_hline_2_efw_pt_shrtstln_clsst_pt_v2.geometry)) "
                    "FROM gdf_hline_2_wfw_pt_shrtstln_clsst_pt_v2, "
                    "gdf_hline_2_efw_pt_shrtstln_clsst_pt_v2;"
                )
                sql_14 = sql_gdf_hxline_v3
                result_14 = engine.execute(sql_14)
                geom_text_14 = result_14.fetchone()[0]
                shapely_obj_14 = wkt.loads(geom_text_14)
                gdf_14 = gpd.GeoDataFrame(geometry=[shapely_obj_14])
                gdf_hxline_v3 = gdf_14.set_geometry("geometry").set_crs("epsg:6441")
                gdf_hxline_v3.to_file(OUT_SHP_HXLINE)
                gdf_hxline_v3.to_postgis("gdf_hxline_v3", engine, if_exists="replace")
                gs_hxline_v3 = gpd.GeoSeries(gdf_hxline_v3.geometry)
                hx_line = gs_hxline_v3.geometry[0]
                sql_gdf_hxline_v3_suw_eb_line_intersects = (
                    "SELECT ST_AsText(ST_Intersection("
                    "gdf_hxline_v3.geometry, suw_eb_line.geom)) "
                    "FROM gdf_hxline_v3, suw_eb_line;"
                )
                sql_24 = sql_gdf_hxline_v3_suw_eb_line_intersects
                result_24 = engine.execute(sql_24)
                geom_text_24 = result_24.fetchone()[0]
                shapely_obj_24 = wkt.loads(geom_text_24)
                gdf_24 = gpd.GeoDataFrame(geometry=[shapely_obj_24])
                gdf_hxline_v3_suw_eb_line_intersects = gdf_24.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hxline_v3_suw_eb_line_intersects.to_postgis(
                    "gdf_hxline_v3_suw_eb_line_intersects",
                    engine,
                    if_exists="replace",
                )
                hxline_ebline_interx = gdf_hxline_v3_suw_eb_line_intersects
                gdf = hxline_ebline_interx
                logger.debug(f"hx_line_intersects_eb_line: {hxline_ebline_interx}")
                reference_point = gs_1.centroid
                gdf['closest_point'] = gdf['geometry'].apply(
                    lambda geom: closest_point(
                        geom, reference_point)
                    )
                xe = gdf['closest_point'].x[0]
                ye = gdf['closest_point'].y[0]
                # xe = gdf_hxline_v3_suw_eb_line_intersects.geometry.x[0]
                # ye = gdf_hxline_v3_suw_eb_line_intersects.geometry.y[0]
                gdf_eb_line_arr = np.asarray([xe, ye])
                sql_gdf_hxline_v3_suw_wb_line_intersects = (
                    "SELECT ST_AsText(ST_Intersection("
                    "gdf_hxline_v3.geometry, suw_wb_line.geom)) "
                    "FROM gdf_hxline_v3, suw_wb_line;"
                )
                sql_25 = sql_gdf_hxline_v3_suw_wb_line_intersects
                result_25 = engine.execute(sql_25)
                geom_text_25 = result_25.fetchone()[0]
                shapely_obj_25 = wkt.loads(geom_text_25)
                gdf_25 = gpd.GeoDataFrame(geometry=[shapely_obj_25])
                gdf_hxline_v3_suw_wb_line_intersects = gdf_25.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hxline_v3_suw_wb_line_intersects.to_postgis(
                    "gdf_hxline_v3_suw_wb_line_intersects",
                    engine,
                    if_exists="replace",
                )
                xw = gdf_hxline_v3_suw_wb_line_intersects.geometry.x[0]
                yw = gdf_hxline_v3_suw_wb_line_intersects.geometry.y[0]
                gdf_wb_line_arr = np.asarray([xw, yw])
                hecras_lb = gdf_hxline_v3_efldwy_pt_arr[0] - gdf_eb_line_arr[0]
                hecras_rb = gdf_hxline_v3_efldwy_pt_arr[0] - gdf_wb_line_arr[0]
                logger.debug("hecras_LB: %s", hecras_lb)
                logger.debug("hecras_RB: %s", hecras_rb)
                sql_gdf_river_section_fid = (
                    "SELECT suw_cut.fid FROM suw_cut, "
                    "gdf_hxline_v3 WHERE ST_INTERSECTS(suw_cut.geom, gdf_hxline_v3.geometry);"
                )
                sql_15 = sql_gdf_river_section_fid
                result_15 = engine.execute(sql_15)
                geom_text_15 = result_15.fetchone()[0]
                river_section_fid = str(geom_text_15)
                sql_river_xs_pair = (
                    "SELECT suw_xs_pt.stream_stn, suw_cut.fid "
                    "FROM public.suw_cut JOIN public.suw_xs_pt "
                    "ON ST_Touches(suw_xs_pt.geom, suw_cut.geom) "
                    f"Where suw_cut.fid = {river_section_fid};"
                )
                sql_16 = sql_river_xs_pair
                result_16 = engine.execute(sql_16)
                geom_text_16 = result_16.fetchall()
                river_xs_pair_1 = geom_text_16[0][0]
                river_xs_pair_2 = geom_text_16[1][0]
                logger.debug("river_xs_pair_1: %s", river_xs_pair_1)
                logger.debug("river_xs_pair_2: %s", river_xs_pair_2)
                sql_gdf_hxline_v3_suw_cut_intersects = (
                    "SELECT ST_ASTEXT(ST_Intersection("
                    "gdf_hxline_v3.geometry, suw_cut.geom)) "
                    "FROM suw_cut JOIN gdf_hxline_v3 "
                    "ON ST_Intersects(gdf_hxline_v3.geometry, suw_cut.geom);"
                )
                sql_17 = sql_gdf_hxline_v3_suw_cut_intersects
                result_17 = engine.execute(sql_17)
                geom_text_17 = result_17.fetchone()[0]
                shapely_obj_17 = wkt.loads(geom_text_17)
                gdf_17 = gpd.GeoDataFrame(geometry=[shapely_obj_17])
                gdf_hxline_v3_suw_cut_intersects = gdf_17.set_geometry(
                    "geometry"
                ).set_crs("epsg:6441")
                gdf_hxline_v3_suw_cut_intersects.to_postgis(
                    "gdf_hxline_v3_suw_cut_intersects",
                    engine,
                    if_exists="replace",
                )
                sql_gdf_suw_cut_line_geometry = (
                    f"SELECT ST_ASTEXT(suw_cut.geom) "
                    "FROM public.suw_cut "
                    f"WHERE suw_cut.fid = {river_section_fid};"
                )
                sql_18 = sql_gdf_suw_cut_line_geometry
                result_18 = engine.execute(sql_18)
                geom_text_18 = result_18.fetchone()[0]
                gdf_suw_cut_line_geometry = geom_text_18
                shapely_obj_18 = wkt.loads(geom_text_18)
                gdf_18 = gpd.GeoDataFrame(geometry=[shapely_obj_18])
                gdf_suw_cut_line_geometry = gdf_18.set_geometry("geometry").set_crs(
                    "epsg:6441"
                )
                gdf_suw_cut_line_geometry.to_postgis(
                    "gdf_suw_cut_line_geometry", engine, if_exists="replace"
                )
                sql_gdf_suw_cut_line_geometry_length = (
                    "SELECT ST_Length(gdf_suw_cut_line_geometry.geometry)"
                    "FROM gdf_suw_cut_line_geometry;"
                )
                sql_19 = sql_gdf_suw_cut_line_geometry_length
                result_19 = engine.execute(sql_19)
                geom_text_19 = result_19.fetchone()[0]
                gdf_suw_cut_line_geometry_length = geom_text_19
                hx_rm_cut = gdf_suw_cut_line_geometry_length
                logger.debug("hx_rm_cut_length: %s", hx_rm_cut)
                sql_gdf_suw_cut_linestring_drop_table = (
                    "DROP TABLE IF EXISTS gdf_suw_cut_linestring;"
                )
                sql_26 = sql_gdf_suw_cut_linestring_drop_table
                result__26 = engine.execute(sql_26)
                sql_gdf_suw_cut_linestring_create_table = (
                    "CREATE TABLE gdf_suw_cut_linestring"
                    "(id SERIAL PRIMARY KEY, geom geometry(LineString, 6441));"
                )
                sql_20 = sql_gdf_suw_cut_linestring_create_table
                result_20 = engine.execute(sql_20)
                sql_gdf_suw_cut_linestring = (
                    "INSERT INTO gdf_suw_cut_linestring (geom) "
                    "SELECT ST_LineMerge(gdf_suw_cut_line_geometry.geometry) "
                    "AS geom FROM gdf_suw_cut_line_geometry;"
                )
                sql_21 = sql_gdf_suw_cut_linestring
                result_21 = engine.execute(sql_21)
                sql_gdf_hxline_v3_suw_cut_intersects_ratio = (
                    "SELECT ST_LineLocatePoint(gdf_suw_cut_linestring.geom, "
                    "gdf_hxline_v3_suw_cut_intersects.geometry) "
                    "FROM gdf_suw_cut_linestring, gdf_hxline_v3_suw_cut_intersects;"
                )
                sql_22 = sql_gdf_hxline_v3_suw_cut_intersects_ratio
                result_22 = engine.execute(sql_22)
                geom_text_22 = result_22.fetchone()[0]
                logger.debug("hx_ratio: %s", geom_text_22)
                gdf_hxline_v3_suw_cut_intersects_ratio = geom_text_22
                hx_ratio = gdf_hxline_v3_suw_cut_intersects_ratio
                suw_cl_l_merged_azimuth = (
                    "SELECT ST_Azimuth(ST_StartPoint(suw_cl_l_merged.geom), "
                    "ST_EndPoint(suw_cl_l_merged.geom)) FROM suw_cl_l_merged;"
                )
                sql_23 = suw_cl_l_merged_azimuth
                result_23 = engine.execute(sql_23)
                geom_text_23 = result_23.fetchone()[0]
                azimuth_radians = geom_text_23
                radians = azimuth_radians
                azimuth = radians_to_degrees(radians)
                logger.debug("azimuth (degrees): %s", azimuth)
                if float(math.degrees(math.pi / 2)) > float(azimuth) or float(
                    azimuth
                ) > float(math.degrees(3 * math.pi / 2)):
                    if float(river_xs_pair_1) > float(river_xs_pair_2):
                        xs_diff = float(river_xs_pair_1) - float(river_xs_pair_2)
                        hx_xs_calc_1 = float(xs_diff) * float(hx_ratio)
                        gdf_river_mile = float(river_xs_pair_2) + hx_xs_calc_1
                        logger.debug("gdf_river_mile: %s", gdf_river_mile)
                    else:
                        xs_diff = float(river_xs_pair_1) - float(river_xs_pair_2)
                        hx_xs_calc_1 = float(xs_diff) * float(hx_ratio)
                        gdf_river_mile = float(river_xs_pair_1) + hx_xs_calc_1
                        logger.debug("gdf_river_mile: %s", gdf_river_mile)
                else:
                    if float(river_xs_pair_1) > float(river_xs_pair_2):
                        xs_diff = float(river_xs_pair_1) - float(river_xs_pair_2)
                        hx_xs_calc_1 = float(xs_diff) * float(hx_ratio)
                        gdf_river_mile = float(river_xs_pair_2) + hx_xs_calc_1
                        logger.debug("gdf_river_mile: %s", gdf_river_mile)
                    else:
                        xs_diff = float(river_xs_pair_1) - float(river_xs_pair_2)
                        hx_xs_calc_1 = float(xs_diff) * float(hx_ratio)
                        gdf_river_mile = float(river_xs_pair_1) + hx_xs_calc_1
                        logger.debug("gdf_river_mile: %s", gdf_river_mile)
                sql_gdf_hxline_v3_length = (
                    "SELECT ST_Length(gdf_hxline_v3.geometry) FROM gdf_hxline_v3;"
                )
                sql_27 = sql_gdf_hxline_v3_length
                result_27 = engine.execute(sql_27)
                geom_text_27 = result_27.fetchone()[0]
                hx_length = str(geom_text_27)
                gdf = gpd.GeoDataFrame(geometry=[hx_line])
                line = gdf.geometry
                buffer_distance = 100
                buffered_line = line.buffer(buffer_distance)
                buffered_line.to_file(OUT_SHP_BUFFER)
                with fiona.open(OUT_SHP_BUFFER, "r"):
                    with rasterio.open(IN_DEM_MAIN) as src:
                        out_image, out_transform = rasterio.mask.mask(
                            src, buffered_line, crop=True
                        )
                        out_meta = src.meta
                        out_meta.update(
                            {
                                "driver": "GTiff",
                                "height": out_image.shape[1],
                                "width": out_image.shape[2],
                                "transform": out_transform,
                            }
                        )
                        with rasterio.open(
                            OUT_DEM_BUFFER,
                            "w",
                            **out_meta
                            ) as dest:
                            dest.write(out_image)
                logger.debug("clipped dem with buffer")
                gs = gpd.GeoSeries(gdf.geometry)
                points = []
                for line in gs:
                    length = line.length
                    for distance in range(0, int(length) + 5):
                        point = line.interpolate(distance)
                        points.append(point)
                points_gs = gpd.GeoSeries(points)
                coords = []
                for line in points_gs:
                    for x, y in line.coords:
                        xy = x, y
                        coords.append(xy)
                original_coords = coords
                original_linestring = LineString(original_coords)
                gdf = original_linestring
                gs = gpd.GeoSeries(gdf)
                gs.to_file(f"{HX_LINE_ADDED_PTS}")
                logger.debug("added points to hecras line")
                raster_filename = OUT_DEM_BUFFER
                raster_data, raster_transform = read_raster(raster_filename)
                shapefile_path = HX_LINE_ADDED_PTS
                gdf = gpd.read_file(shapefile_path)
                gs = gpd.GeoSeries(gdf.geometry[0])
                coords = []
                for line in gs:
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
                    (x, y, z) for (x, y), z in zip(original_coords, z_values)
                ]
                updated_linestring = LineString(updated_coords)
                gs_updated = gpd.GeoDataFrame(geometry=[updated_linestring])
                gs_updated.to_file(HX_LINE_Z)
                shutil.copy(f"{HX_LINE_Z}", f"{HX_CADD}")
                logger.debug("added z values to hecras line")
                coords = []
                for line in gs_updated.geometry:
                    for x, y, z in line.coords:
                        xyz = x, y, z
                        coords.append(xyz)
                gs_arr = np.array(coords)
                adjust_value = gs_arr[0][0]
                points = gs_arr
                x = points[:, 0]
                y = points[:, 1]
                z = points[:, 2]
                t = np.arange(len(points))
                cs_y = CubicSpline(t, y)
                cs_z = CubicSpline(t, z)
                # 500 is the number of points to make for hecras cross section
                t2 = np.linspace(t.min(), t.max(), 500)
                y2 = cs_y(t2)
                z2 = cs_z(t2)
                smooth_points = np.vstack([t2, y2, z2]).T
                smooth_points[:, 0] += adjust_value
                linestring = LineString(smooth_points)
                gdf = gpd.GeoDataFrame(geometry=[linestring])
                gdf.to_file(HX_LINE_Z_SMOOTHED)
                shutil.copy(f"{HX_LINE_Z_SMOOTHED}", f"{HX_CADD}")
                smooth_arr = np.copy(smooth_points)
                smooth_arr[:, 0] -= smooth_arr[0][0]
                smooth_arr[:, 0] += 10000
                hecras_arr = smooth_arr[:, [0, 2]]
                hecras_arr[:, 1] = hecras_arr[::-1, 1]
                np.savetxt(CSV_HX_ARR, hecras_arr, delimiter=",")
                df = pd.DataFrame(hecras_arr)
                df.to_excel(XL_XS_EX, index=False)
                xl = pd.ExcelFile(XL_XS_EX)
                df = xl.parse("Sheet1")
                df = df.drop(df.index[0])
                df.to_excel(f"{XL_XS_EX}", index=False)
                hecras_left_bank_station = hecras_arr[0][0] + int(hecras_lb)
                hecras_right_bank_station = hecras_arr[0][0] + int(hecras_rb)
                headers = [
                    "RiverMile",
                    "LeftBankStation",
                    "RightBankStation",
                    "RiverMileLength",
                    "RiverMileRatio",
                    "100yrElevation",
                    "50yrElevation",
                    "10yrElevation",
                    "FirmPanel",
                ]
                data = [
                    (
                        f"{gdf_river_mile}",
                        f"{hecras_left_bank_station}",
                        f"{hecras_right_bank_station}",
                        f"{hx_length}",
                        f"{hx_ratio}",
                        f"{yr100}",
                        f"{yr50}",
                        f"{yr10}",
                        f"{firm_panel}",
                    )
                ]
                with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(data)
                df_xs = pd.read_csv(CSV_PATH)
                df_xs.to_excel(XL_XS_DATA, index=False)
                logger.debug("hecras calculations:complete")
                session.commit()
                end_time = time.time()
                execution_time = end_time - start_time
                logger.debug(f"parcel_hecras_calcs execution time: {execution_time}")
        except pd.errors.EmptyDataError:
            logger.debug("hecras calculations:empty data error")
            session.rollback()
        finally:
            engine.dispose()
            logger.debug("disposed engine")
            logger.debug("get_hecras_calc: completed")
    except ValueError as e:
        logger.debug("get_hecras_calc: failed")
        logger.debug("error: %s", e)
    return gdf_hxline_v3
