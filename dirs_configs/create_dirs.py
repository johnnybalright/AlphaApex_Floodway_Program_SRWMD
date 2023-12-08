"""
This module provides functionality to create a hierarchical directory
structure with specified files within.
The primary function in this module, create_directories, takes a nested
dictionary representing the desired
directory and file hierarchy and creates the corresponding directories
and files in the system.

Functions:
    - create_directories(directory_structure, parent_path=None)
        Given a nested dictionary representing the desired directory
        structure, where directories are dictionary keys
        and files are listed in dictionary values as lists, this
        function recursively creates the specified directories
        and files in the system. The directories and files can be
        created in a specified parent directory or in the
        location where the script is run if no parent directory is
        specified.

Example:
    The following dictionary structure passed to create_directories
    function will create directories and files as per
    the structure represented by the dictionary.

        directory_structure = {
            "dir1": {
                "subdir1": ["file1.txt", "file2.txt"],
                "subdir2": ["file3.txt"]
            },
            "dir2": ["file4.txt"]
        }

    This will create:
    - dir1
        - subdir1
            - file1.txt
            - file2.txt
        - subdir2
            - file3.txt
    - dir2
        - file4.txt

Dependencies:
    - os: This module is used for operating system dependent
    functionality like directory and file creation.
    - config: A configuration module or file containing global
    configurations, like BASE_DIR, used in this module.
"""
import os
from .config import BASE_DIR


def create_directories(directory_structure, parent_path=None):
    """
    Creates a directory structure with empty files.

    Given a nested dictionary representing the desired
    directory structure, where each key-value pair represents a
    directory and its contents, this function creates the
    specified directories and files in the system. Directories
    are represented by dictionary keys, while files are listed in a
    dictionary value as a list. The function can create
    nested directories and files by recursively processing
    the input dictionary.

    Parameters:
    directory_structure (dict):
        A dictionary where keys are directory names and
        values are either dictionaries (representing subdirectories)
        or lists (representing files to be created within
        the directory).

    parent_path (str, optional): The path where the directory
     structure should be created.If not specified, directories
     will be created in the same location as the script.
     Default is None.

    Returns:

    None: The function returns None,
    as its purpose is to perform directory
    and file creations as a side effect.
    """
    if parent_path is None:
        parent_path = BASE_DIR
    for dir_name, contents in directory_structure.items():
        if isinstance(contents, dict):
            new_dir_path = os.path.join(parent_path, dir_name)
            os.makedirs(new_dir_path, exist_ok=True)
            create_directories(contents, new_dir_path)
        elif isinstance(contents, list):
            for filename in contents:
                if filename:
                    file_path = os.path.join(parent_path, filename)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write("")
