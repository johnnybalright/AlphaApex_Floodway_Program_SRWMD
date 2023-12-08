"""
This module includes various geometric and spatial functionalities that
are utilized to manipulate and analyze geometric shapes and points in a
2D space. The module mainly uses the shapely and geopandas libraries to
work with geometric objects like points, lines, and polygons. It
includes functions for creating polygons from lines, scaling lines,
calculating distances between geometric objects, finding closest lines
or vertices, and finding intersections among geometries.

Functions
---------
- create_polygon_from_lines(lines: List[LineString]) -> Polygon:
    Creates a polygon by chaining the coordinates of multiple line
    strings.

- scaled_line(line: LineString, factor_x: float,
    factor_y: float) -> LineString:
    Scales a line by specified factors along the x and y dimensions.

- distance(point1: Tuple[float, float],
    point2: Tuple[float, float]) -> float:
    Calculates the Euclidean distance between two points.

- find_closest_line(target: Geometry, lines_list: List[LineString]) ->
    Tuple[int, LineString]:
    Finds the closest LineString to a target geometry from a list of
    LineStrings.

- distance_to_point(line: Geometry, given_point: Point) -> float:
    Calculates the minimum distance between a point and a geometry.

- find_intersections(data: Tuple) -> List[int]:
    Finds intersecting keys of polygons with a given polygon.

- closest_vertices(vertices: List[Tuple[float, float]],
    line: LineString) -> Tuple[Tuple[float, float],
    Tuple[float, float]]:
    Finds the closest two vertices to a given line from a set of
    vertices.

- distance_between_points(point1: Tuple[float, float],
    point2: Tuple[float, float]) -> float:
    Calculates the distance between two points.
"""
import math
import itertools
import rtree
from shapely.geometry import Point, Polygon, LineString
from shapely import affinity
import geopandas as gpd
import numpy as np


def create_polygon_from_lines(lines):
    """
    Create a polygon from multiple line strings
    by chaining their coordinates.

    Parameters:
    - lines: a list of Shapely LineString objects

    Returns:
    - A Shapely Polygon object
    """
    return Polygon(itertools.chain(*[line.coords for line in lines]))


def scaled_line(line, factor_x, factor_y):
    """
    Scale a line by specified factors along the x and y dimensions.

    Parameters:
    - line: a shapely LineString or LinearRing object
    - factor_x: scaling factor in the x dimension
    - factor_y: scaling factor in the y dimension

    Returns:
    - scaled_line: a new LineString or LinearRing
        scaled by the specified factors
    """
    return affinity.scale(line, xfact=factor_x, yfact=factor_y)


def distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.

    Parameters:
    - point1: a tuple representing the coordinates
    of the first point (x1, y1)
    - point2: a tuple representing the coordinates
    of the second point (x2, y2)

    Returns:
    - distance: the Euclidean distance between point1 and point2
    """
    try:
        return math.sqrt(
            (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    except TypeError as exc:
        raise TypeError("Both points should be tuples or lists with"
                        "numeric values.") from exc


def find_closest_line(target, lines_list):
    """
    Find the closest LineString to a target geometry
    from a list of LineStrings.

    Parameters:
    - target (Shapely Geometry): A Shapely geometry
    object as the reference for finding the closest line.
    - lines_list (list of LineString): A list containing
    LineString objects to search.

    Returns:
    - tuple: A tuple containing the index and the LineString
    that is closest to the target.The tuple structure is
    (index, LineString).
    """
    return min(enumerate(
        lines_list), key=lambda item: item[1].distance(target))


def distance_to_point(line, given_point):
    """
    Calculate the minimum distance between a point and a geometry.

    Parameters:
    - line (Shapely Geometry): A Shapely geometry object.
    - given_point (Shapely Point): A Shapely point object.

    Returns:
    - float: Minimum distance between the geometry and the point.
    """
    return given_point.distance(line.geometry)


def find_intersections(data):
    """
    Returns a list of keys for the polygons that intersect with the
    given polygon.
    """
    given_polygon, polygons_chunk, chunk_dict, sindex = data
    intersecting_keys = []
    gdf = gpd.GeoSeries(polygons_chunk)
    spatial_index = gdf.sindex
    possible_matches_index = list(
                                spatial_index.intersection(
                                    given_polygon.bounds))
    possible_matches = gdf.iloc[possible_matches_index]
    precise_matches = possible_matches[
        possible_matches.intersects(given_polygon)
        ]
    for polygon in precise_matches:
        for key, val in chunk_dict.items():
            if val.equals(polygon):
                intersecting_keys.append(key)

    return intersecting_keys


def distance_between_points(point1, point2):
    """
    Calculates the distance between two points.

    :param point1: The first point as a tuple (x, y).
    :param point2: The second point as a tuple (x, y).
    :return: The distance between the two points.
    """
    return Point(point1).distance(Point(point2))


def closest_vertices(vertices_lst, linestring):
    """
    Find the two vertices from a list that are closest to a given
    linestring.

    This function uses spatial indexing (R-tree) to efficiently find
    the two closest vertices to a specified linestring. The function is
    optimized for performance and is particularly suitable for use
    cases with a large number of vertices.

    Parameters:
    vertices (list of tuple): A list of tuples where each tuple
                                contains the (x, y) coordinates of a
                                vertex.
    line_coords (list of tuple): A list of tuples where each tuple
                                contains the (x, y) coordinates of a
                                point in the linestring.

    Returns:
    list of tuple: Returns a list containing tuples of the (x, y)
    coordinates of
                   the two closest vertices to the linestring.
    """
    idx = rtree.index.Index()
    for i, vertex in enumerate(vertices_lst):
        point = Point(vertex)
        idx.insert(i, point.bounds)
    closest_ids = list(idx.nearest(linestring.bounds, 2))
    result = [vertices_lst[i] for i in closest_ids]
    return result[0], result[1]


def shorten_linestring(line, factor):
    length_to_shorten = line.length * factor / 2
    start_point = line.interpolate(length_to_shorten)
    end_point = line.interpolate(line.length - length_to_shorten)
    new_line = LineString([start_point, end_point])
    return new_line


def order_coords_by_distance(linestring, point_coords):
    line = linestring
    points = [Point(coord) for coord in point_coords]
    distances = [(point, line.distance(point)) for point in points]
    distances.sort(key=lambda x: x[1])
    sorted_coords = [point.coords[0] for point, distance in distances]
    return sorted_coords


def scale_linestring(line, scale_factor):
    centroid_x, centroid_y = line.centroid.x, line.centroid.y
    scaled_coords = []
    for x, y in line.coords:
        scaled_x = centroid_x + scale_factor * (x - centroid_x)
        scaled_y = centroid_y + scale_factor * (y - centroid_y)
        scaled_coords.append((scaled_x, scaled_y))
    return LineString(scaled_coords)


def closest_point(point_list, given_point):
    """
    Find the point in point_list that is closest to given_point.

    :param point_list: List of points (each point is a tuple or list of coordinates).
    :param given_point: The point to which you want to find the closest point (tuple or list of coordinates).
    :return: The closest point from the point_list.
    """
    points = np.array(point_list)
    distances = np.linalg.norm(points - given_point, axis=1)
    min_index = np.argmin(distances)
    return point_list[min_index]
