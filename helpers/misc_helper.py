import math
import rasterio
import rasterio.mask
import pdfrw
import numpy as np
import subprocess
import os
import signal
import psutil
import glob
import requests


def find_closest_index(arr, target):
    """
    Finds the index of the closest value to target in a numpy array.

    :param arr: Numpy array to search
    :param target: Target value to find the closest to
    :return: Index of the closest value
    """
    distances = np.linalg.norm(arr - target, axis=1)
    return np.argmin(distances)


def custom_round(n):
    """
    Custom rounding function.

    :param n: Number to round
    :return: Rounded number as per the custom rule
    """
    if n > 0:
        return int(n + 0.5)
    else:
        return int(n - 0.5)


def find_nearest_idx(point, array):
    """
    Find the index of the nearest point in an array to a specified
    point.

    Parameters:
    - point: a Shapely Point object
    - array: a numpy array of coordinates

    Returns:
    - Index of the nearest point in the array
    """
    xy_array = array[:, :2]
    result = np.argmin(
        np.sum(
            (xy_array - np.array(point.coords[0][:2]))**2, axis=1
        )
    )
    return result


def interpolate_row(data, specified_z):
    """
    Interpolate a new row (point) at a specified elevation within a
    dataset.

    Parameters:
    - data: a numpy array containing coordinates and elevations
    - specified_z: the specified elevation value to interpolate

    Returns:
    - A new numpy array representing the interpolated point with x, y,
    and z coordinates
    """
    for i in range(len(data) - 1):
        z1 = data[i, 2]
        z2 = data[i + 1, 2]

        if z1 <= specified_z <= z2 or z1 >= specified_z >= z2:
            t = (specified_z - z1) / (z2 - z1)
            x = data[i, 0] + t * (data[i + 1, 0] - data[i, 0])
            y = data[i, 1] + t * (data[i + 1, 1] - data[i, 1])

            new_row = np.array([x, y, specified_z])
            return new_row

    return None


def find_index_of_substring_in_list(string_list, substring):
    """
    Find the index of the first string in a list that contains a
    specified substring.

    Parameters:
    - string_list: a list of strings to search
    - substring: the substring to look for in the strings of string_list

    Returns:
    - The index of the first string that contains the substring or None
    if not found
    """
    for index, string in enumerate(string_list):
        if substring in string:
            return index
    return None


def read_raster(filename):
    """
    Read raster data from a file.

    Parameters:
    - filename: path of the raster file to read

    Returns:
    - data: the raster data as a 2D array
    - transform: affine transformation for the raster data
    """
    with rasterio.open(filename) as src:
        data = src.read(1)
        transform = src.transform
    return data, transform


def interpolate_z_values(line_string, raster_data, raster_transform):
    """
    Interpolates z-values based on raster data for the coordinates in
    a LineString.

    Parameters:
    - line_string: a shapely.geometry.LineString object containing
    x, y coordinates
    - raster_data: a 2D numpy array representing the raster data
    - raster_transform: an affine transformation for the raster data

    Returns:
    - z_values: a numpy array containing interpolated z-values for the
    coordinates in line_string
    """
    line_points = np.array(line_string.coords)
    row, col = rasterio.transform.rowcol(raster_transform,
                                        line_points[:, 0],
                                        line_points[:, 1])
    try:
        z_values = raster_data[row, col]
    except IndexError:
        z_values = np.array([])
    return z_values


def radians_to_degrees(radians):
    """
    Convert an angle from radians to degrees.

    Parameters:
    - radians: angle value in radians

    Returns:
    - degrees: angle value converted to degrees
    """
    degrees = math.degrees(radians)
    return degrees


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    """
    Fill a PDF form with data from a dictionary and save it to a
    new file.

    Parameters:
    - input_pdf_path: str, path to the input PDF file.
    - output_pdf_path: str, path where the output PDF will be saved.
    - data_dict: dict, contains form field names as keys and the data
    to fill in as values.
    """
    ANNOT_KEY = '/Annots'
    ANNOT_FIELD_KEY = '/T'
    ANNOT_VAL_KEY = '/V'
    SUBTYPE_KEY = '/Subtype'
    WIDGET_SUBTYPE_KEY = '/Widget'
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    if key in data_dict:
                        annotation.update(
                            pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                        )
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


def style_function(feature, color='red', weight=2, fill_opacity=0):
    """
    Style a GeoJSON feature for visualization.

    Parameters:
    - feature: GeoJSON feature to be styled.
    - color (optional): Color of the boundary/line. Default is 'red'.
    - weight (optional): Weight/thickness of the boundary/line. Default
    is 2.
    - fill_opacity (optional): Opacity of the fill color.
    Default is 0 (transparent).

    Returns:
    A dictionary containing the styling information.
    """
    return {
        'fillOpacity': fill_opacity,
        'weight': weight,
        'color': color
    }


def get_key_for_value(d, value):
    """
    Retrieve a key corresponding to a given value from a dictionary.

    Parameters:
    - d (dict): The dictionary from which to retrieve the key.
    - value: The value corresponding to which the key is to be found.

    Returns:
    - The key corresponding to the given value or None if not found.
    """
    for key, val in d.items():
        if val == value:
            return key
    return None


def get_value_for_key(d, key_):
    """
    Retrieve a value corresponding to a given key from a dictionary.

    Parameters:
    - d (dict): The dictionary from which to retrieve the value.
    - key_: The key corresponding to which the value is to be found.

    Returns:
    - The value corresponding to the given key or None if the key is
    not found.
    """
    for key, val in d.items():
        if key_ == key:
            return val
    return None


def round_to_five(number):
    """
    Rounds a number to the nearest multiple of five.

    :param number: The number to round.
    :return: The number rounded to the nearest multiple of five.
    """
    return round(number/5) * 5


def start_xvfb():
    """
    Starts an Xvfb process with display :99 and screen resolution
    1024x768x24. Sets the DISPLAY environment variable to ':99'.

    Returns:
    xvfb_process (subprocess.Popen): The Xvfb process object.
    """
    if not is_xvfb_running():
        xvfb_process = subprocess.run(
            ["Xvfb :99 -screen 0 1024x768x16 &"]
            )
        subprocess.run(["export DISPLAY=:99"])
        os.environ['DISPLAY'] = ':99'
        print("Xvfb started successfully.")
        return xvfb_process
    else:
        print("Xvfb is already running.")
        return None


def is_xvfb_running():
    """
    Checks if Xvfb (X virtual framebuffer) is running on the system.

    Returns:
    -------
    bool:
        True if Xvfb is running, False otherwise.
    """
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'Xvfb' in process.info['name']:
            return True
    return False


def cumulative_file_size(file_list):
    total_size = 0
    for file in file_list:
        if os.path.isfile(file):
            total_size += os.path.getsize(file)
        else:
            print(f"File not found: {file}")
    return total_size


def log_rotation(base_directory, file_list, max_size, max_files=5):
    """
    Writes data to a rotating set of log files. Creates
    new files or appends to existing ones, respecting
    the maximum file size and count.

    :param base_directory: Directory where the log
    files are stored
    :param data: Data to be written
    :param max_size: Maximum size of each log file in bytes
    :param max_files: Maximum number of log files to keep
    """
    data = cumulative_file_size(file_list)
    pattern = os.path.join(base_directory, 'comb_log_*.txt')
    log_files = sorted(glob.glob(pattern))
    target_file = None
    for file_path in log_files:
        if os.path.getsize(file_path) + data <= max_size:
            target_file = file_path
            break
    if target_file is None:
        if log_files:
            latest_file_number = int(
                log_files[-1].split('_')[-1].split('.')[0]
                )
            new_file_number = latest_file_number + 1
        else:
            new_file_number = 1
        target_file = os.path.join(
            base_directory, f'comb{new_file_number}.log'
            )
    with open(target_file, 'a') as outfile:
        for fname in file_list:
            with open(fname, 'r') as infile:
                outfile.write(infile.read())
                outfile.write("\n\n\n")
                print(f"Data written to {target_file}")
            log_files = sorted(glob.glob(pattern))
            if len(log_files) > max_files:
                os.remove(log_files[0])
                print(f"Deleted oldest log file: {log_files[0]}")
    return None


def write_pid_to_file(file_path):
    pid = os.getpid()
    with open(file_path, 'w', encoding="utf-8") as file:
        pass
    with open(file_path, 'a', encoding="utf-8") as file:
        file.write(f"{pid}\n")


def url_active(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code >= 200 and response.status_code < 300
    except requests.RequestException as e:
        return False
