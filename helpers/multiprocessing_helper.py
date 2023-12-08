"""
This module provides utility functions to handle and manipulate
geographic data, especially GeoDataFrames. It includes functionalities
to split GeoDataFrames, perform parallelized geometric searches, query
GeoDataFrames, and create polygons from coordinates.

Functions:
    split_into_chunks(lst, num_chunks, divisible_by=1):
        Splits a list into a specified number of chunks.

    chunk_geodataframe(filename, num_splits):
        Splits a GeoDataFrame into smaller chunks.

    parallel_geom_search(chunks, attribute_name, attribute_value,
    num_cores):
        Performs a parallel search on chunks of a geodataframe based on
        attribute_name and attribute_value.

    query_geodataframe(gdf_chunks, attribute, value):
        Queries a GeoDataFrame chunk based on an attribute and value.

    create_polygons_from_coordinates_file(file_path):
        Creates polygons from a coordinates file and transforms their
        CRS.

    parcel_geom(filename, parcelid):
        Fetches parcel geometry based on parcel id in parallel.

Dependencies:
    multiprocessing, shapely, pyproj, geopandas, dotenv

Author:
    Your Name (your.email@example.com)

"""
from multiprocessing import (
    Pool,
    Pipe,
    Queue,
    Process,
    cpu_count
    )
import multiprocessing
import concurrent.futures
from shapely.geometry import Polygon
import pyproj
import geopandas as gpd
import threading
from threading import Thread


def split_into_chunks(lst, num_chunks, divisible_by=1):
    """
    Splits a list into a given number of chunks.
    """
    chunk_size = (len(lst) - 1) // num_chunks + 1
    while chunk_size % divisible_by != 0:
        chunk_size += 1
    if chunk_size * num_chunks < len(lst):
        raise ValueError(
            "Cannot split list into chunks with given constraints.")
    chunks = []
    for i in range(0, len(lst), chunk_size):
        chunk = {index: value for index,
            value in enumerate(lst[i:i + chunk_size], start=i)
            }
        chunks.append(chunk)

    return chunks


def chunk_geodataframe(filename, num_splits):
    """
    Splits a GeoDataFrame into smaller chunks.

    :param filename: The file path of the GeoDataFrame to read.
    :param num_splits: The number of chunks to split the GeoDataFrame
    into.
    :return: A list containing chunks of the GeoDataFrame.
    """
    gdf = gpd.read_file(filename)
    return [gdf.iloc[i::num_splits] for i in range(num_splits)]


def parallel_geom_search(chunks,
                         attribute_name,
                         attribute_value,
                         num_cores):
    """
    Performs a parallel search on chunks of a geodataframe based on
    attribute_name and attribute_value.

    :param chunks: List of geodataframe chunks
    :param attribute_name: Name of the attribute to be searched
    :param attribute_value: Value of the attribute to be matched
    :param num_cores: Number of cores to use for parallel processing
    :return: List of resulting geodataframes after query
    """
    args = [(chunk, attribute_name, attribute_value) for chunk in chunks]
    with Pool(processes=num_cores) as pool:
        results = pool.starmap(query_geodataframe, args)
        result = [gdf.reset_index(drop=True)
            for gdf in results if not gdf.empty
            ]
    return result


def query_geodataframe(gdf_chunks, attribute, value):
    """
    Queries a GeoDataFrame chunk based on an attribute and value.

    :param gdf_chunks: A chunk of a GeoDataFrame.
    :param attribute: The attribute to query.
    :param value: The value of the attribute to query.
    :return: A DataFrame containing the query result.
    """
    result = gdf_chunks[gdf_chunks[attribute] == value]
    return result


def create_polygons_from_coordinates_file(file_path):
    """
    Creates polygons from a coordinates file and transforms their CRS.

    :param file_path: Path to the file containing coordinates
    :return: List of transformed polygons
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        transformed_polygons = []
        for line in lines:
            values = line.strip().split(",")
            x_coords = values[0::2]
            y_coords = values[1::2]
            coordinates = list(
                zip(
                    map(
                        float, x_coords), map(float, y_coords)
                    )
                )
            polygon = Polygon(coordinates)
            original_crs = pyproj.CRS("EPSG:4326")
            target_crs = pyproj.CRS("EPSG:6441")
            transformer = pyproj.Transformer.from_crs(
                                                    original_crs,
                                                    target_crs,
                                                    always_xy=True
                                                    )
            transformed_coords = [transformer.transform(x, y)
                                for x, y in polygon.exterior.coords
                                ]
            transformed_polygon = Polygon(transformed_coords)
            transformed_polygons.append(transformed_polygon)
    return transformed_polygons


def parcel_geom(filename, parcelid):
    """
    Fetches parcel geometry based on parcel id in parallel.

    :param filename: Filename to read the geodataframe from
    :param parcelid: Parcel ID to be searched for
    :return: List of resulting geodataframes containing the parcel
    geometry
    """
    attribute_1 = 'PARCELID'
    value_1 = parcelid
    num_cores = cpu_count()
    chunks = chunk_geodataframe(filename, num_cores)
    result = parallel_geom_search(chunks,
                                  attribute_1,
                                  value_1,
                                  num_cores
                                  )
    return result


def run_with_q_process(func, *args):
	def q_wrapper(q, *args):
		result = func(*args)
		q.put(result)
	q = Queue()
	p = Process(target=q_wrapper, args=(q,) + args)
	p.start()
	return p, q


def run_with_q_thread(func, *args):
    def q_wrapper(q, *args):
        result = func(*args)
        q.put(result)
    q = Queue()
    t = Thread(target=q_wrapper, args=(q,) + args)
    t.start()
    return t, q
