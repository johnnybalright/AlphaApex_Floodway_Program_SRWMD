"""
This module is dedicated to the processing and generation of
parcel-specific geographical and geometrical data. It includes
functionalities to read, process, and manipulate spatial datasets,
execute geographical computations, and handle related files and outputs.

The central functionality is encompassed within the `parcel_geometry`
function, which takes a project number and parcel ID as inputs and
conducts a series of operations, including:
- Loading and processing of shapefiles and geographical datasets.
- Execution of spatial computations such as finding the closest
vertices, distances between points, and calculating river frontage
length.
- Manipulating, scaling, and saving geometrical shapes.
- Executing external processes and shell commands for advanced
geographical computations.
- Generating and saving new files, as well as handling the copying of
specific results for further use or reference.

The module utilizes various external modules and libraries such as
rasterio, shapely, and geopandas for sophisticated spatial operations,
and also interfaces with shell processes and external commands for
certain calculations and file manipulations.

Module Attributes:
- Various constants representing file and directory paths used
throughout the module's functions.
- A logger for capturing debug information and exceptions during
execution.

Note:
Adjustments to paths, environment variables, and external command
invocations might be necessary based on the specific execution
environment and available datasets.
"""
import shutil
import subprocess
import time
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from shapely.affinity import translate
from shapely.ops import nearest_points
import rasterio
import rasterio.mask
from skimage.morphology import medial_axis
from skimage.draw import polygon
from scipy.spatial import ConvexHull
from dirs_configs.config import OUTPUT_DIR, OUTPUT_DIRx
from dirs_configs.file_paths import *
from dirs_configs.input_vars import *
from helpers.multiprocessing_helper import *
from helpers.misc_helper import *
from helpers.geom_helper import *
import geopandas as gpd
import fiona
import numpy as np
from scipy.ndimage import convolve


def parcel_geometry(projectnumber, parcelid, logger_1):
    """
    Process and generate parcel-specific geographic and geometric data.

    This function conducts a series of operations to process spatial
    data related to a specific
    parcel, including:
    - Loading and processing shapes and geographical datasets.
    - Manipulating, scaling, and saving shapes.
    - Executing external processes for geographic calculations.
    - Handling and saving results, including the generation and copying
    of files.

    A specific parcel is identified and its geometry is processed,
    scaled, and various
    geographic operations are executed such as the calculation of river
    frontage length.
    Various files are generated and saved in specified paths during
    this process.

    Parameters:
    - projectnumber (str): An identifier related to the project.
    - path (str): The base path where files are read from and saved to.
    - parcelid (str or int): An identifier of the specific parcel to be
    processed.

    Returns:
    - tuple: A tuple containing the processed geometry and the
    calculated river frontage length.

    Raises:
    - Various exceptions: Handles exceptions gracefully by logging
    errors when processing fails.

    Note:
    - This function involves a sleep operation to presumably manage
    execution timing or rate.
    - It uses external environment variables and relies on external
    file paths and datasets.
    - It executes external shell commands for specific geographic
    computations.
    - Paths and environment variable names may need to be adjusted
    based on execution environment.
    """
    try:
        logger = logger_1
        OUT_DEM = OUT_DEM_TEMPLATE.format(
            projectnumber=projectnumber
            )
        OUT_SHP = OUT_SHP_TEMPLATE.format(
            projectnumber=projectnumber
            )
        OUT_SHP_SCALED = OUT_SHP_SCALED_TEMPLATE.format(
            projectnumber=projectnumber
            )
        time.sleep(500 / 1000)
        gdf_eb = gpd.read_file(EB_LINE)
        gdf_wb = gpd.read_file(WB_LINE)
        gs_eb = gpd.GeoSeries(gdf_eb["geometry"])
        gs_wb = gpd.GeoSeries(gdf_wb["geometry"])
        filename = IN_SHP_MAIN_SUBSET
        parcel_id = parcelid
        result = parcel_geom(filename, parcel_id)
        in_gdf_shp = result[0].geometry[0]
        gdf = gpd.GeoDataFrame(geometry=[in_gdf_shp])
        gdf.to_file(OUT_SHP)
        gs = gdf["geometry"]
        gs = gs.reset_index(drop=True)
        coords = gs[0].exterior.coords
        polygon_arr = np.array(coords)
        point = gs[0].centroid
        distance1 = point.distance(gs_eb[0])
        distance2 = point.distance(gs_wb[0])
        if float(distance1) > float(distance2):
            target_line = gs_wb[0]
            logger.debug("target_line: gs_wb")
        else:
            target_line = gs_eb[0]
            logger.debug("target_line: gs_eb")
        vertices = polygon_arr
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        img_shape = (max_coords - min_coords + 1).astype(int)
        adjusted_vertices = vertices - min_coords
        img = np.zeros(img_shape, dtype=np.uint8)
        rr, cc = polygon(adjusted_vertices[:, 0], adjusted_vertices[:, 1])
        img[rr, cc] = 1
        skeleton, _ = medial_axis(img, return_distance=True)
        # scaling_factor = 5
        # scaled_vertices = polygon_arr * scaling_factor
        # min_coords = scaled_vertices.min(axis=0)
        # max_coords = scaled_vertices.max(axis=0)
        # img_shape = (max_coords - min_coords + 1).astype(int)
        # adjusted_vertices = scaled_vertices - min_coords
        # img = np.zeros(img_shape, dtype=np.uint8)
        # rr, cc = polygon(adjusted_vertices[:, 0], adjusted_vertices[:, 1])
        # img[rr, cc] = 1
        # skeleton, _ = medial_axis(img, return_distance=True)
        skeleton_coords = np.column_stack(np.where(skeleton))
        skeleton_coords_original = skeleton_coords + min_coords
        skeleton_coords_list = [(x, y) for y, x in skeleton_coords_original]
        points = np.array(skeleton_coords_list)
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        input_line = target_line
        input_vertices = hull_points
        logger.debug(f"vertices count for parcel hull:{len(input_vertices)}")
        input_vertices = input_vertices[:, ::-1]
        input_vertices = input_vertices.tolist()
        logger.debug(f"input_vertices={input_vertices}")
        sorted_coords = order_coords_by_distance(input_line, input_vertices)
        gs_convex = gs[0].convex_hull
        gs_convex_coords_lst = [coord for coord in gs_convex.exterior.coords]
        closest_point_1 = closest_point(gs_convex_coords_lst, sorted_coords[0])
        closest_point_2 = closest_point(gs_convex_coords_lst, sorted_coords[1])
        vertices_distance = distance_between_points(
            closest_point_1,
            closest_point_2
            )
        # vertices_distance = distance_between_points(sorted_coords[0],
        #                                             sorted_coords[1]
        #                                             )
        river_frontage_value = float(vertices_distance)
        river_frontage_length = round_to_five(river_frontage_value)
        logger.debug("river_frontage_length complete:" \
            + f"{river_frontage_length}")
        frontage_arr = np.array([sorted_coords[0], sorted_coords[1]])
        closest_vert1 = Point(sorted_coords[0])
        closest_vert2 = Point(sorted_coords[1])
        frontage_gs = gpd.GeoSeries([closest_vert1, closest_vert2])
        frontage_gs.set_crs("epsg:6441", inplace=True)
        frontage_line = LineString(frontage_gs)
        gs_frontage = gpd.GeoSeries([frontage_line])
        gs_frontage.set_crs("epsg:6441", inplace=True)
        gs_frontage.to_file(FRONTAGE_LINE)
        frontage_midpoint = frontage_line.interpolate(0.5, normalized=True)
        set1 = set(map(tuple, input_vertices))
        set2 = set(map(tuple, frontage_arr))
        unique_elements = list(set1.difference(set2))
        if len(unique_elements) == 2:
            oppo_line = LineString(unique_elements)
            print(oppo_line)
        else:
            print("There are no two exactly unique points to form a line.")
        oppo_midpoint = oppo_line.interpolate(0.5, normalized=True)
        midpoints = gpd.GeoSeries([frontage_midpoint, oppo_midpoint])
        midpoints.set_crs("epsg:6441", inplace=True)
        mid_line = LineString(midpoints)
        distance = 75
        setback_point = mid_line.interpolate(distance)
        dx = setback_point.x - frontage_midpoint.x
        dy = setback_point.y - frontage_midpoint.y
        translated_frontage_line = translate(frontage_line, xoff=dx, yoff=dy)
        gs_setback = translated_frontage_line
        gs_setback75 = gpd.GeoSeries([gs_setback])
        gs_setback75.set_crs("epsg:6441", inplace=True)
        gs_setback75.to_file(SETBACK75)
        gs_scale = gs.scale(8, 8)
        gs_scale.to_file(OUT_SHP_SCALED)
        with fiona.open(OUT_SHP_SCALED, "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]
        with rasterio.open(IN_DEM_MAIN) as src:
            out_image, out_transform = rasterio.mask.mask(
                src,
                shapes,
                crop=True
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
            with rasterio.open(OUT_DEM, "w", **out_meta) as dest:
                dest.write(out_image)
        logger.debug("new_dem_scaled:complete")
        subprocess.run(
            [
                f"gdal_contour -a ELEV -3d -b 1 -i 1 \
            {OUTPUT_DIR}/{projectnumber}-dem_clipped.tiff \
                {OUTPUT_DIR}/{projectnumber}-contours.shp"
            ],
            shell=True,
            check=True
        )
        logger.debug(f"gdal_contour: complete")
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-dem_clipped.tiff",
            OUTPUT_DIR / f"{projectnumber}-dem_clipped_2.tiff"
        )
        logger.debug("new_contours:complete")
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shp",
            OUTPUT_DIRx / f"{projectnumber}-parcel_boundary.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shp",
            OUTPUT_DIR / "parcel_boundary.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shx",
            OUTPUT_DIR / "parcel_boundary.shx"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shp",
            OUTPUT_DIRx / f"{projectnumber}-contours_2.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shp",
            OUTPUT_DIR / "contours_2.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shx",
            OUTPUT_DIR / "contours_2.shx"
        )
        logger.debug(
            "parcelboundary&contours_2.shp copied to map_imports"
            )
        #is the parcel adjacent to the river?
        #or is there other parcels in between?
        frontage_distance = frontage_midpoint.distance(target_line)
        if frontage_distance >= 200:
            river_frontage_length = 0
            gs_setback = None
            result = (gs[0], river_frontage_length, gs_setback)
            logger.debug("river_frontage_length: 0 FT")
            logger.debug("parcel_geometry:complete")
            return result
        else:
            pass
        logger.debug("new_parcel_boundary_shp:complete")
        logger.debug("parcel_geometry:complete")
    except shutil.Error as e:
        logger.debug(f"parcel_geometry:failed-{e}")
    except Exception as e:
        logger.debug(f"parcel_geometry:failed-{e}")
        gs_scale = gs.scale(8, 8)
        gs_scale.to_file(OUT_SHP_SCALED)
        with fiona.open(OUT_SHP_SCALED, "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]
        with rasterio.open(IN_DEM_MAIN) as src:
            out_image, out_transform = rasterio.mask.mask(
                src,
                shapes,
                crop=True
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
            with rasterio.open(OUT_DEM, "w", **out_meta) as dest:
                dest.write(out_image)
        logger.debug("new_dem_scaled:complete")
        subprocess.run(
            [
                f"gdal_contour -a ELEV -3d -b 1 -i 1 \
            {OUTPUT_DIR}/{projectnumber}-dem_clipped.tiff \
                {OUTPUT_DIR}/{projectnumber}-contours.shp"
            ],
            shell=True,
            check=True
        )
        logger.debug(f"gdal_contour: complete")
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-dem_clipped.tiff",
            OUTPUT_DIR / f"{projectnumber}-dem_clipped_2.tiff"
        )
        logger.debug("new_contours:complete")
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shp",
            OUTPUT_DIRx / f"{projectnumber}-parcel_boundary.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shp",
            OUTPUT_DIR / "parcel_boundary.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-parcel_boundary.shx",
            OUTPUT_DIR / "parcel_boundary.shx"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shp",
            OUTPUT_DIRx / f"{projectnumber}-contours_2.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shp",
            OUTPUT_DIR / "contours_2.shp"
        )
        shutil.copy(
            OUTPUT_DIR / f"{projectnumber}-contours.shx",
            OUTPUT_DIR / "contours_2.shx"
        )
        logger.debug(
            "parcelboundary&contours_2.shp copied to map_imports"
            )
        river_frontage_length = 0
        gs_setback = None
        result = (gs[0], river_frontage_length, gs_setback)
        logger.debug("river_frontage_length: 0 FT due to exception/unknownerror")
        logger.debug("parcel_geometry:complete")
        return result
    result = (gs[0], river_frontage_length, gs_setback)
    return result
