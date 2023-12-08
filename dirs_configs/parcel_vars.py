"""
This module is designed to fetch project variables from a SQLite
database located in a specified directory. It consists of a function
that retrieves various attributes related to a project such as the
project number, parcel ID, county name, and last name. The retrieved
variables are essential for initializing and setting up a new project.

Functions:
----------
parcel_vars() -> tuple or None:
    Fetches and returns essential project variables like project number,
    parcel ID, county name, and last name from a SQLite database. If an
    exception occurs during database interaction, it returns None.

Imports:
--------
- sqlite3: A module that provides an interface to the SQLite database.
- glob: A module that finds all the pathnames matching a specified
pattern.
- config: A module where configurations like TMP_DIR are specified.
"""
import sqlite3
import glob
from .config import TMP_DIR, BASE_DIR
import os
import os.path
from pathlib import Path


def parcel_vars(db_file, logger_1):
    """
    Get variables for a new project from a database.

    The function fetches various project attributes from a SQLite
    database, such as project number, parcel ID, county name, and last
    name.

    :return: A tuple containing the project attributes or None if an
    exception occurs.
    """
    try:
        logger = logger_1
        logger.debug(f"file_path: {BASE_DIR}")
        with sqlite3.connect(str(db_file)) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM project_data;")
            projectnumber = str(c.fetchone()[0])
            logger.debug("projectnumber: %s", projectnumber)
            c.execute("SELECT parcelid FROM project_data;")
            parcelid = str(c.fetchone()[0])
            logger.debug("parcelid: %s", parcelid)
            clean_parcelid = (parcelid.replace("-", "") \
                if "-" in parcelid else parcelid)
            c.execute("SELECT cntyname FROM project_data;")
            county = str(c.fetchone()[0])
            logger.debug("county: %s", county)
            c.execute("SELECT lname FROM project_data;")
            lname = str(c.fetchone()[0])
            logger.debug("lname: %s", lname)
            db_file = str(db_file)
    except sqlite3.Error:
        logger.debug("parcel_variables: failed")
    result = (
        projectnumber,
        parcelid,
        clean_parcelid,
        county,
        lname
        )
    return result
