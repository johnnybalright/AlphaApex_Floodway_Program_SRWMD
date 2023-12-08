"""
This module provides utilities to configure directory structures for
projects based on a given project number. It offers functionality to
generate, configure and manipulate directory structures, files, and
template configurations.

Functions:
- configure_directories_structure(project_number: str) -> str:
    Generate and configure a directory structure for a project based on
    the provided project number. It returns a JSON string representing
    the directory structure.

- remove_empty_elements(my_dict: dict) -> dict:
    Recursively remove empty elements, such as None or empty strings,
    and empty lists from a dictionary.

- remove_empty_dicts(template_configs: list) -> list:
    Remove dictionaries from a list of dictionaries where any value in
    a dictionary is falsy.

- generate_config_file(configs: list, config_file_path: str) -> None:
    Generates a JSON configuration file for copying files and
    directories.

- copy_template(src: str, dest_dir: str) -> None:
    Copies a file or a directory to a specified destination directory.

- copy_templates_from_config(config_file: str) -> None:
    Copies multiple files or directories based on the configurations
    in a JSON file.

- execute_template_operations(project_number: int or str) -> None:
    Execute a series of operations to manipulate templates based on a
    specific project number.

Note:
- Some functionalities like configuring and manipulating directories
  and files depend on various configuration variables and templates,
  which should be properly set for correct operation.
"""
import os
import shutil
import json
from .config_vars import *
from .config import PARENT_DIR


def configure_directories_structure(project_number):
    """
    Configure and generate a directory structure for a project based
    on the provided project number. The directory structure includes
    various nested directories and files. Some filenames are generated
    dynamically by incorporating the project number.

    Parameters:
    project_number (str): A string representing the project number,
    used to customize filenames within the directory structure.

    Returns:
    str: A JSON string representing the directory structure, where keys
    are directory or file names and values are nested directories or
    lists of files. Empty directories and files with no names are
    excluded from the output.

    Example:
    --------
    Given a project number 'P123', the function generates a hierarchical
    directory structure as a JSON string where directories like 'Cadd',
    'Correspondence', and files like 'P123-Base-TOPO.dwg',
    'P123-Plan-SITE.dwg' are organized accordingly.

    The returned JSON string can be parsed to recreate the directory
    structure for the project.

    Usage:
    ------
    directory_structure_json = configure_directory_structure('P123')
    """
    file_11 = file_11_template.format(projectnumber=project_number)
    file_12 = file_12_template.format(projectnumber=project_number)
    file_13 = file_13_template.format(projectnumber=project_number)
    file_16 = file_16_template.format(projectnumber=project_number)
    file_311 = file_311_template.format(projectnumber=project_number)
    file_312 = file_312_template.format(projectnumber=project_number)
    file_51 = file_51_template.format(projectnumber=project_number)
    file_521 = file_521_template.format(projectnumber=project_number)
    file_522 = file_522_template.format(projectnumber=project_number)
    file_523 = file_523_template.format(projectnumber=project_number)
    file_524 = file_524_template.format(projectnumber=project_number)
    file_525 = file_525_template.format(projectnumber=project_number)
    file_526 = file_526_template.format(projectnumber=project_number)
    file_527 = file_527_template.format(projectnumber=project_number)
    file_528 = file_528_template.format(projectnumber=project_number)
    file_529 = file_529_template.format(projectnumber=project_number)
    file_529_1 = file_529_1_template.format(projectnumber=project_number)
    file_529_2 = file_529_2_template.format(projectnumber=project_number)
    file_529_3 = file_529_3_template.format(projectnumber=project_number)
    file_71 = file_71_template.format(projectnumber=project_number)
    file_72 = file_72_template.format(projectnumber=project_number)
    file_73 = file_73_template.format(projectnumber=project_number)
    file_74 = file_74_template.format(projectnumber=project_number)
    file_75 = file_75_template.format(projectnumber=project_number)
    file_81 = file_81_template.format(projectnumber=project_number)
    file_82 = file_82_template.format(projectnumber=project_number)
    file_83 = file_83_template.format(projectnumber=project_number)
    directories_structure_ = {
        dir_1: {
            sub_dir_11: {
                sub_dir_111: {},
                sub_dir_112: {}
            },
            "files": [
                file_11,
                file_12,
                file_13,
                file_14,
                file_15,
                file_16
            ]
        },
        dir_2: {},
        dir_3: {
            sub_dir_31: [
                file_311,
                file_312
            ],
            sub_dir_32: {},
            "files": [
                file_31,
                file_32,
                file_33,
                file_34,
                file_35
            ]
        },
        dir_4: {
            sub_dir_41: {},
            sub_dir_42: {}
        },
        dir_5: {
            sub_dir_51: {
                sub_dir_511: {},
                sub_dir_512: {}
            },
            sub_dir_52: {
                "files": [
                    file_521,
                    file_522,
                    file_523,
                    file_524,
                    file_525,
                    file_526,
                    file_527,
                    file_528,
                    file_529,
                    file_529_1,
                    file_529_2,
                    file_529_3
                ]
            },
            "files": [
                file_51,
                file_52,
                file_53,
                file_54,
                file_55
            ]
        },
        dir_6: {
            sub_dir_61: [
                file_611,
                file_612,
                file_613,
                file_614,
                file_615
            ],
            sub_dir_62: [
                file_621,
                file_622,
                file_623,
                file_624,
                file_625
            ],
            sub_dir_63: [
                file_631,
                file_632,
                file_633,
                file_634,
                file_635
            ],
        },
        dir_7: {
            "files": [
                file_71,
                file_72,
                file_73,
                file_74,
                file_75
            ]
        },
        dir_8: {
            "files": [
                file_81,
                file_82,
                file_83,
            ]
        },
        dir_9: {
            sub_dir_91: {},
            sub_dir_92: {},
            sub_dir_93: {}
        },
        dir_10: {
            sub_dir_101: {},
            sub_dir_102: {},
            sub_dir_103: {}
        },
        dir_11: {},
    }
    directories_structure = remove_empty_elements(directories_structure_)
    json_structure = json.dumps(directories_structure, indent=4)
    return json_structure


def remove_empty_elements(my_dict):
    """
    Recursively remove empty elements (None or empty strings) and empty
    lists from a dictionary.

    This function takes a dictionary as input and returns a new
    dictionary where:
    - Key-value pairs with values as None or empty strings are removed.
    - Lists within the dictionary are cleaned by removing empty
    elements, and empty lists are removed.
    - Nested dictionaries are processed recursively to ensure that
    empty elements at any level are removed.

    Parameters:
    my_dict (dict): The input dictionary from which empty elements need
    to be removed.

    Returns:
    dict: A new dictionary with empty elements removed.

    Example:
    >>> remove_empty_elements({"a": "", "b": None,
    "c": [None, "", "value"], "d": {"e": ""}})

    {'c': ['value']}
    """
    new_dict = {}
    for k, v in my_dict.items():
        if isinstance(v, dict):
            v = remove_empty_elements(v)
        elif isinstance(v, list):
            v = [i for i in v if i or i == 0]
            if not v:
                continue
        if v == "" or v is None:
            continue
        new_dict[k] = v
    return new_dict


def remove_empty_dicts(template_configs):
    """
    Remove dictionaries from a list of dictionaries where any value in
    a dictionary is falsy.

    Parameters:
    - project_number (int): The project number, although not used in
    the function, it might be required for future enhancements or
    overloads.
    - template_configs (list of dict): A list of dictionaries,
    presumably representing configurations or settings.

    Returns:
    - list of dict: A new list of dictionaries, where each dictionary
    has only truthy values.

    Note:
    - A "falsy" value refers to a value which is considered False when
    encountered in a Boolean context (None, False, 0, "", [], {}, etc.)
    """
    config_dict = template_configs
    config_dict = [d for d in config_dict if all(d.values())]
    return config_dict


def generate_config_file(configs,
                        config_file_path=PARENT_DIR / 'config.json'):
    """
    Generates a JSON configuration file for copying files and
    directories.

    Parameters:
    - configs (list): A list of dictionaries, each containing 'src' and
    'dest' keys.
    - config_file_path (str, optional): The path where the
    configuration file will be saved.
    """
    for config in configs:
        config['src'] = str(config['src'])
        config['dest'] = str(config['dest'])
        if os.path.isdir(config['src']):
            config['is_directory'] = True
        elif os.path.isfile(config['src']):
            config['is_directory'] = False
        else:
            print(f"Warning: Source path does not exist: {config['src']}")
    with open(config_file_path, 'w', encoding='utf-8') as file:
        json.dump(configs, file, indent=4)


def copy_template(src, dest_dir):
    """
    Copies a file or a directory to a specified destination directory.

    Parameters:
    - src (str): Path to the source file or directory.
    - dest_dir (str): Path to the destination directory where the
    source will be copied.

    Output:
    Prints out a message indicating whether the file or directory has
    been copied successfully.
    """
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(dest_dir, os.path.basename(src)))
        print(f"Directory {src} copied to {dest_dir}")
    elif os.path.isfile(src):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy(src, dest_dir)
        print(f"File {src} copied to {dest_dir}")
    else:
        print(f"No such file or directory: {src}")


def copy_templates_from_config(config_file):
    """
    Copies multiple files or directories based on the configurations
    in a JSON file.

    Parameters:
    - config_file (str): Path to the JSON configuration file. The JSON
    file should contain an array of objects, each having a 'src' and
    'dest' attribute.

    Output:
    Utilizes the copy_template function to copy each source to its
    respective destination
    and prints out messages indicating the status of the copying
    process.
    """
    config_file = PARENT_DIR / 'config.json'
    with open(config_file, 'r', encoding='utf-8') as file:
        configs = json.load(file)
        for config in configs:
            copy_template(config['src'], config['dest'])


def execute_template_operations(project_number):
    """
    Execute a series of operations to manipulate templates based on a
    specific project number.

    This function performs several steps:
    1. Format destination paths by injecting the project number into
    predefined template strings.
    2. Configure templates, defining the source and destination for
    each.
    3. Remove any configurations with empty or falsy values.
    4. Generate a configuration file based on the cleaned
    configurations.
    5. Copy templates from the source to destination as per the
    configurations in the generated file.

    Parameters:
    - project_number (int or str): The project number used to customize
    destination paths and configurations.

    Returns:
    - None: The function performs in-place operations and does not
    return any value.
    """
    project_number = str(project_number)
    dst_1 = str(dst_1_template).format(projectnumber=project_number)
    dst_2 = str(dst_2_template).format(projectnumber=project_number)
    dst_3 = str(dst_3_template).format(projectnumber=project_number)
    dst_4 = str(dst_4_template).format(projectnumber=project_number)
    dst_5 = str(dst_5_template).format(projectnumber=project_number)
    dst_6 = str(dst_6_template).format(projectnumber=project_number)
    dst_7 = str(dst_7_template).format(projectnumber=project_number)
    dst_8 = str(dst_8_template).format(projectnumber=project_number)
    dst_9 = str(dst_9_template).format(projectnumber=project_number)
    # dst_10 = str(dst_10_template).format(projectnumber=project_number)
    dst_11 = str(dst_11_template).format(projectnumber=project_number)
    dst_12 = str(dst_12_template).format(projectnumber=project_number)
    dst_13 = str(dst_13_template).format(projectnumber=project_number)
    dst_14 = str(dst_14_template).format(projectnumber=project_number)
    dst_15 = str(dst_15_template).format(projectnumber=project_number)
    template_configs = [
        {
            "src": src_1,
            "dest": dst_1
        },
        {
            "src": src_2,
            "dest": dst_2
        },
        {
            "src": src_3,
            "dest": dst_3
        },
        {
            "src": src_4,
            "dest": dst_4
        },
        {
            "src": src_5,
            "dest": dst_5
        },
        {
            "src": src_6,
            "dest": dst_6
        },
        {
            "src": src_7,
            "dest": dst_7
        },
        {
            "src": src_8,
            "dest": dst_8
        },
        {
            "src": src_9,
            "dest": dst_9
        },
        # {
        #     "src": src_10,
        #     "dest": dst_10
        # },
        {
            "src": src_11,
            "dest": dst_11
        },
        {
            "src": src_12,
            "dest": dst_12
        },
        {
            "src": src_13,
            "dest": dst_13
        },
        {
            "src": src_14,
            "dest": dst_14
        },
        {
            "src": src_15,
            "dest": dst_15
        },
    ]
    config_dict = remove_empty_dicts(template_configs)
    generate_config_file(config_dict)
    copy_templates_from_config(PARENT_DIR / 'config.json')
