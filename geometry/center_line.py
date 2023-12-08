"""
Module for Center Line Calculation of a Polygon Parcel.

This module contains a function `center_line` that calculates the
center line of a given polygon (parcel), performs various geometric
calculations on it, and saves the resulting geometries as shapefiles.
The calculated center line is based on certain criteria and geometric
relations with other existing features.

Functions:
    center_line(gs_1, logger_1):
        Calculates the center line of a given polygon and saves it to a
        shapefile.

Dependencies:
    This module depends on various Python packages such as shapely for
    geometric operations and geopandas for handling GeoDataFrames and
    GeoSeries.

Note:
    It’s necessary to ensure the availability of certain predefined
    variables and configurations such as OUTPUT_DIR, EB_LINE, and
    WB_LINE that are used within the function.
"""
import os
import os.path
import math
from shapely import wkt
from shapely.affinity import translate
from shapely.geometry import LineString, Point
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from helpers.geom_helper import distance, scaled_line
from dirs_configs.input_vars import EB_LINE, WB_LINE
from helpers.misc_helper import radians_to_degrees
import geopandas as gpd
from dirs_configs.config import OUTPUT_DIR
from dirs_configs.file_paths import (
    OUT_SHP_CENTER,
    OUT_SHP_CENTER_SCALED
    )
from dotenv import load_dotenv
load_dotenv("./main.env")
os.environ["SQLALCHEMY_WARN_20"] = "1"


def center_line(gs_1, river_frontage_length, logger_1):
    """
    Calculates the center line of a given polygon and saves it to a
    shapefile.
    Parameters:
        - gs_1 (shapely.geometry.Polygon): The polygon for which to
        calculate the center line.
        - logger_1 (logging.Logger): The logger object to use for
        logging.
    Returns:
        -gs_center(shapely.geometry.LineString): The center line of the
        parcel polygon.
        gdf_center_xs_line_mile(float): The mile marker of the center
        line of the parcel polygon.
    """
    try:
        logger = logger_1
        if river_frontage_length == 0:
            gs_center = None
            gdf_center_xs_line_mile = None
            result = (gs_center, gdf_center_xs_line_mile)
            return result
        gs = gs_1
        gs = gpd.GeoSeries(gs)
        gs.set_crs('epsg:6441')
        gdf_eb = gpd.read_file(EB_LINE)
        gdf_wb = gpd.read_file(WB_LINE)
        gs_eb = gpd.GeoSeries(gdf_eb['geometry'])
        gs_wb = gpd.GeoSeries(gdf_wb['geometry'])
        gs_c = gs.centroid
        logger.debug(gs_c)
        polygon = gs[0]
        points = list(polygon.exterior.coords)[:-1]
        longest_side = LineString([points[0], points[1]])
        max_distance = distance(points[0], points[1])
        for i in range(1, len(points)):
            d = distance(points[i-1], points[i])
            if d > max_distance:
                max_distance = d
                longest_side = LineString([points[i-1], points[i]])
        logger.debug(longest_side)
        line = longest_side
        midpoint = line.interpolate(0.5, normalized=True)
        logger.debug(midpoint)
        point1 = gs_c[0]
        point2 = midpoint
        x_distance = abs(point1.x - point2.x)
        y_distance = abs(point1.y - point2.y)
        logger.debug("X distance: %s", x_distance)
        logger.debug("Y distance: %s", y_distance)
        line = longest_side
        if gs_c.x[0] > midpoint.x:
            dx, dy = (1 * x_distance), y_distance
            translated_line = translate(line, xoff=dx, yoff=dy)
            logger.debug(translated_line)
        else:
            dx, dy = (-1 * x_distance), y_distance
            translated_line = translate(line, xoff=dx, yoff=dy)
            logger.debug(translated_line)
        line = translated_line
        scale_line = scaled_line(line, 10, 10)
        logger.debug(scale_line)
        gs_2 = gpd.GeoSeries(scale_line)
        gs_2.set_crs('epsg:6441')
        logger.debug(gs_2[0])
        gs_2.to_file(OUT_SHP_CENTER_SCALED)
        line = gs_2[0]
        polygon = gs[0]
        intersection_points = line.intersection(polygon)
        logger.debug(intersection_points)
        points = list(intersection_points.coords)
        logger.debug(points)
        point_1x = Point(points[0])
        logger.debug(point_1x)
        point_2x = Point(points[1])
        logger.debug(point_2x)
        line_1 = gs_2[0]
        line_2 = gs_eb[0]
        line_3 = gs_wb[0]
        intersection_point_1 = line_1.intersection(line_2)
        intersection_point_2 = line_1.intersection(line_3)
        logger.debug(intersection_point_1)
        logger.debug(intersection_point_2)
        point1 = gs_c[0]
        point2 = intersection_point_1
        point3 = intersection_point_2
        distance1 = point1.distance(point2)
        distance2 = point1.distance(point3)
        logger.debug("Distance: %s", distance1)
        logger.debug("Distance: %s", distance2)
        center_line_lst = []
        if distance1 > distance2:
            center_line_lst.append(point2)
        else:
            center_line_lst.append(point3)
        for point in center_line_lst:
            point_x = point
        point1 = gs_c[0]
        point2 = intersection_point_1
        point3 = intersection_point_2
        distance1 = point1.distance(point2)
        distance2 = point1.distance(point3)
        center_line_lst = []
        if distance1 > distance2:
            center_line_lst.append(point2)
        else:
            center_line_lst.append(point3)
        for point in center_line_lst:
            point_x = gpd.GeoSeries(point)
        distance3 = point_x[0].distance(point_1x)
        distance4 = point_x[0].distance(point_2x)
        if distance3 > distance4:
            center_line_lst.append(point_1x)
        else:
            center_line_lst.append(point_2x)
        center_line_lst = [(point.x, point.y) for point in center_line_lst]
        center_xs_line = LineString(center_line_lst)
        logger.debug(center_xs_line)
        gs_center = gpd.GeoSeries(center_xs_line)
        gs_center.set_crs('epsg:6441')
        gs_center.to_file(OUT_SHP_CENTER)
        logger.debug(gs_center[0])
        gdf_center = gpd.GeoDataFrame(gs_center)
        gdf_center.columns = ['geometry']
        gdf_center.set_crs('epsg:6441')
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
        session = sessionmaker(bind=engine)
        try:
            with session() as session:
                gdf_center.to_postgis(
                    "gdf_center_xs_line",
                    engine,
                    if_exists="replace"
                    )
                sql_crs = (
                    "UPDATE gdf_center_xs_line SET geometry = \
                        ST_SetSRID(geometry, 6441) \
                            WHERE ST_SRID(geometry) = 0;")
                engine.execute(sql_crs)
                sql_gdf_center_xs_line_section_fid = (
                    'SELECT suw_cut.fid FROM suw_cut, \
                    gdf_center_xs_line WHERE ST_INTERSECTS(\
                        suw_cut.geom, gdf_center_xs_line.geometry);'
                )
                sql_1 = sql_gdf_center_xs_line_section_fid
                result_1 = engine.execute(sql_1)
                geom_text_1 = result_1.fetchone()[0]
                center_line_section_fid = str(geom_text_1)
                sql_center_line_pair = (
                    f"SELECT suw_xs_pt.stream_stn, suw_cut.fid \
                    FROM public.suw_cut JOIN public.suw_xs_pt \
                    ON ST_Touches(suw_xs_pt.geom, suw_cut.geom)\
                    Where suw_cut.fid = {center_line_section_fid};"
                )
                sql_2 = sql_center_line_pair
                result_2 = engine.execute(sql_2)
                geom_text_2 = result_2.fetchall()
                center_line_pair_1 = geom_text_2[0][0]
                center_line_pair_2 = geom_text_2[1][0]
                logger.debug('center_line_pair_1: %s', center_line_pair_1)
                logger.debug('center_line_pair_2: %s', center_line_pair_2)
                sql_gdf_center_xs_line_suw_cut_intersects = (
                    "SELECT ST_ASTEXT(ST_Intersection(\
                    gdf_center_xs_line.geometry, suw_cut.geom)) \
                    FROM suw_cut JOIN gdf_center_xs_line \
                    ON ST_Intersects(\
                        gdf_center_xs_line.geometry, suw_cut.geom);"
                )
                logger.debug('gdf_suw_cut_center_line_intersect created')
                sql_3 = sql_gdf_center_xs_line_suw_cut_intersects
                result_3 = engine.execute(sql_3)
                geom_text_3 = result_3.fetchone()[0]
                shapely_obj_3 = wkt.loads(geom_text_3)
                gdf_3 = gpd.GeoDataFrame(geometry=[shapely_obj_3])
                gdf_center_xs_line_suw_cut_intersects = (
                    gdf_3.set_geometry('geometry').set_crs('epsg:6441'))
                gdf_center_xs_line_suw_cut_intersects.to_postgis(
                    "gdf_center_xs_line_suw_cut_intersects",
                    engine,
                    if_exists="replace"
                    )
                sql_gdf_center_xs_line_suw_cut_line_geometry = (
                    f"SELECT ST_ASTEXT(suw_cut.geom) \
                    FROM public.suw_cut \
                    WHERE suw_cut.fid = {center_line_section_fid};"
                )
                sql_4 = sql_gdf_center_xs_line_suw_cut_line_geometry
                result_4 = engine.execute(sql_4)
                geom_text_4 = result_4.fetchone()[0]
                gdf_center_xs_line_suw_cut_line_geometry = geom_text_4
                shapely_obj_4 = wkt.loads(geom_text_4)
                gdf_4 = gpd.GeoDataFrame(geometry=[shapely_obj_4])
                gdf_center_xs_line_suw_cut_line_geometry = (
                    gdf_4.set_geometry('geometry').set_crs('epsg:6441')
                    )
                gdf_center_xs_line_suw_cut_line_geometry.to_postgis(
                    "gdf_suw_cut_center_line_geometry",
                    engine,
                    if_exists="replace"
                    )
                sql_gdf_center_xs_line_suw_cut_line_geometry_length = (
                    "SELECT ST_Length(\
                        gdf_suw_cut_center_line_geometry.geometry) \
                            FROM gdf_suw_cut_center_line_geometry;"
                )
                sql_5 = sql_gdf_center_xs_line_suw_cut_line_geometry_length
                result_5 = engine.execute(sql_5)
                geom_text_5 = result_5.fetchone()[0]
                gdf_center_xs_line_suw_cut_line_geometry_length = geom_text_5
                center_line_rm_cut = (
                    gdf_center_xs_line_suw_cut_line_geometry_length
                    )
                logger.debug(
                    "center_line_rm_cut_length: %s",
                    center_line_rm_cut
                    )
                engine.execute('DELETE FROM gdf_suw_cut_center_linestring;')
                sql_gdf_center_xs_line_suw_cut_linestring = (
                    "INSERT INTO gdf_suw_cut_center_linestring (geom) \
                    SELECT ST_LineMerge(\
                        gdf_suw_cut_center_line_geometry.geometry) \
                            AS geom FROM gdf_suw_cut_center_line_geometry;"
                            )
                sql_8 = sql_gdf_center_xs_line_suw_cut_linestring
                engine.execute(sql_8)
                sql_gdf_center_xs_line_suw_cut_intersects_ratio = (
                    "SELECT ST_LineLocatePoint(\
                        gdf_suw_cut_center_linestring.geom, \
                            gdf_center_xs_line_suw_cut_intersects.geometry) \
                                FROM gdf_suw_cut_center_linestring, \
                                    gdf_center_xs_line_suw_cut_intersects;"
                                    )
                sql_9 = sql_gdf_center_xs_line_suw_cut_intersects_ratio
                result_9 = engine.execute(sql_9)
                geom_text_9 = result_9.fetchone()[0]
                logger.debug("center_line_ratio: %s", geom_text_9)
                gdf_center_xs_line_suw_cut_intersects_ratio = geom_text_9
                center_line_ratio = (
                    gdf_center_xs_line_suw_cut_intersects_ratio
                    )
                suw_cl_l_merged_azimuth = (
                    "SELECT ST_Azimuth(\
                        ST_StartPoint(suw_cl_l_merged.geom), \
                            ST_EndPoint(suw_cl_l_merged.geom)) \
                                FROM suw_cl_l_merged;"
                                )
                sql_10 = suw_cl_l_merged_azimuth
                result_10 = engine.execute(sql_10)
                geom_text_10 = result_10.fetchone()[0]
                azimuth_radians = geom_text_10
                radians = azimuth_radians
                azimuth = radians_to_degrees(radians)
                logger.debug('azimuth (degrees): %s', azimuth)
                if float(math.degrees(math.pi /2)) > float(azimuth) \
                    or float(azimuth)> float(math.degrees(3 *math.pi /2)):
                    if float(center_line_pair_1) > float(center_line_pair_2):
                        xs_diff = (
                            float(
                                center_line_pair_1)
                            - float(
                                center_line_pair_2)
                            )
                        center_line_calc_1 = (
                            float(
                                xs_diff)
                            * float(
                                center_line_ratio)
                            )
                        gdf_center_xs_line_mile = (
                            float(
                                center_line_pair_2)
                            + center_line_calc_1
                            )
                        logger.debug(
                            'gdf_center_xs_line_mile: %s',
                            gdf_center_xs_line_mile
                            )
                    else:
                        xs_diff = float(
                                center_line_pair_1) - float(
                                    center_line_pair_2)
                        center_line_calc_1 = float(
                            xs_diff) * float(
                                center_line_ratio)
                        gdf_center_xs_line_mile = float(
                            center_line_pair_1) + center_line_calc_1
                        logger.debug(
                            "gdf_center_xs_line_mile: %s",
                            gdf_center_xs_line_mile
                            )
                else:
                    if float(
                        center_line_pair_1) > float(
                            center_line_pair_2):
                        xs_diff = float(
                            center_line_pair_1) - float(
                                center_line_pair_2)
                        center_line_calc_1 = float(
                            xs_diff) * float(
                                center_line_ratio)
                        gdf_center_xs_line_mile = float(
                            center_line_pair_2) + center_line_calc_1
                        logger.debug(
                            "gdf_center_xs_line_mile: %s",
                            gdf_center_xs_line_mile
                            )
                    else:
                        xs_diff = float(
                            center_line_pair_1) - float(
                                center_line_pair_2)
                        center_line_calc_1 = float(
                            xs_diff) * float(
                                center_line_ratio)
                        gdf_center_xs_line_mile = float(
                            center_line_pair_1) + center_line_calc_1
                        logger.debug(
                            "gdf_center_xs_line_mile: %s",
                            gdf_center_xs_line_mile
                            )
                    logger.debug('get_center_line_mile: complete')
        except ValueError as e:
            logger.debug("Error occurred %s", e)
            session.rollback()
            logger.debug("session rolled back")
        finally:
            session.close()
            engine.dispose()
            logger.debug('disposed engine')
        gs_center.set_crs('epsg:6441')
        logger.debug("gs_center[0]: %s",gs_center[0])
        logger.debug("gdf_center_xs_line_mile: %s",gdf_center_xs_line_mile)
        result = (gs_center[0], gdf_center_xs_line_mile)
        return result
    except TypeError as e:
        logger.debug("Error occurred %s", e)
        logger.debug('get_center_line_mile: completed')
