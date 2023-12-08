"""
This module is responsible for filling PDF forms with data retrieved
from a MySQL database. It includes configurations
and environment variables loading, as well as the main function
`pdf_fill` which performs the primary operations.

Dependencies:
    - mysql.connector: Used for MySQL database connections.
    - pandas: Used for data manipulation and analysis.
    - psycopg2: PostgreSQL database adapter for Python.
    (Not actively used in the code)
    - pymysql: A MySQL database connector for Python.
    (Not actively used in the code)
    - misc_helper: Contains the `write_fillable_pdf` function used
    to create the PDFs.

Environment Configuration:
    Environment variables are loaded from a `.env` file located in the
    project directory, containing database access
    credentials such as database name, user, password, and host.

Functions:
    - pdf_fill(projectnumber, river_frontage_length, logger_1):
        The main function in this module. It retrieves project-related
        data from a MySQL database and fills various
        PDF templates with this data. The filled PDF forms are then
        saved to specified directories.

        Args:
            projectnumber (int): The ID of the project in the MySQL
            database.
            river_frontage_length (int): The length of the river
            frontage in feet.
            logger_1: Logger object for capturing debug information
            and errors during execution.

        Returns:
            None: The function saves the filled PDF files to disk and
            does not return any value.

Directory and File Configurations:
    - BASE_DIR, FORM_DIR, TEMPLATE_DIR: Configurations loaded from a
    separate config module, representing various
      directory paths used in the code.
    - Templates for PDF forms are expected to be present in specified
    directories, and the filled PDFs are saved in
      designated output directories.
"""
from dirs_configs.config import (
    BASE_DIR,
    FORM_DIR,
    TEMPLATE_DIR
    )
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(
    "/home/jpournelle/python_projects/" \
        + "plabz/river_division/main/main.env"
    )
import os
from datetime import date, datetime
import mysql.connector as connection
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import pymysql
from helpers.misc_helper import write_fillable_pdf
from PyPDF2 import PdfReader, PdfWriter


def pdf_fillable(projectnumber, river_frontage_length, logger_1):
    """
    Fills a PDF form with data from a MySQL database and saves the
    filled form as a new PDF file.

    Args:
        projectnumber (int): The ID of the project in the MySQL
        database.
        path (str): The path to the directory where the filled PDF
        form will be saved.
        river_frontage_length (int): The length of the river frontage
        in feet.

    Returns:
        None
    """
    try:
        logger = logger_1
        projectnumber2 = int(projectnumber)
        db_1 = os.getenv("DB_1")
        user_1 = os.getenv("USER_1")
        passwd_1 = os.getenv("PASSWD_1")
        host_1 = os.getenv("HOST_1")
        query_2 = (
            f"SELECT * FROM users_newclient WHERE id = {projectnumber2};"
        )
        engine = create_engine(
            f"mysql+mysqlconnector://{user_1}:{passwd_1}@{host_1}/{db_1}"
            )
        df = pd.read_sql(query_2, engine)
        df = df.loc[df["id"] == projectnumber2]
        logger.debug(projectnumber2)
        fname = df["fname"].to_string(index=False)
        logger.debug(fname)
        lname = df["lname"].to_string(index=False)
        logger.debug(lname)
        phone = df["phone"].to_string(index=False)
        logger.debug(phone)
        email = df["email"].to_string(index=False)
        logger.debug(email)
        parcelid = df["parcelid"].to_string(index=False)
        logger.debug(parcelid)
        phyaddr1 = df["phyaddr1"].to_string(index=False)
        logger.debug(phyaddr1)
        phycity = df["phycity"].to_string(index=False)
        logger.debug(phycity)
        phystate = "FL"
        logger.debug(phystate)
        phyzip = df["phyzip"].to_string(index=False)
        logger.debug(phyzip)
        oaddr1 = df["oaddr1"].to_string(index=False)
        logger.debug(oaddr1)
        ocity = df["ocity"].to_string(index=False)
        logger.debug(ocity)
        ostate = df["ostate"].to_string(index=False)
        logger.debug(ostate)
        ozipcd = df["ozipcd"].to_string(index=False)
        logger.debug(ozipcd)
        county = df["cntyname"].to_string(index=False)
        logger.debug(county)
        decklength = df["decklength"].to_string(index=False)
        logger.debug(decklength)
        deckwidth = df["deckwidth"].to_string(index=False)
        logger.debug(deckwidth)
        gangwaylength = df["gangwaylength"].to_string(index=False)
        logger.debug(gangwaylength)
        gangwaywidth = df["gangwaywidth"].to_string(index=False)
        logger.debug(gangwaywidth)
        docklength = df["docklength"].to_string(index=False)
        logger.debug(docklength)
        dockwidth = df["dockwidth"].to_string(index=False)
        logger.debug(dockwidth)
        if df["project"].to_string(index=False) == "floatingdock":
            floatingdock = "x"
            logger.debug(floatingdock)
        else:
            floatingdock = ""
            logger.debug(floatingdock)
        newpermit = "x"
        logger.debug(newpermit)
        modification = ""
        logger.debug(modification)
        riverfrontage = ""
        allowablearea = ""
        dockarea = ""
        gangwayarea = ""
        totalarea = ""
        actualarea = ""
        if docklength not in ["None", "Null", "null"]:
            try:
                dockarea = int(docklength) * int(dockwidth)
                logger.debug(dockarea)
                gangwayarea = int(gangwaylength) * int(gangwaywidth)
                logger.debug(gangwayarea)
                totalarea = int(dockarea) + int(gangwayarea)
                riverfrontage = int(river_frontage_length)
                logger.debug(riverfrontage)
                allowablearea = int(riverfrontage) * 10
                logger.debug(allowablearea)
                actualarea = int(allowablearea) - int(totalarea)
                logger.debug(actualarea)
            except ValueError as e:
                logger.debug(
                    f"Unable to convert '{docklength}'" \
                        + f"to an integer.{e}"
                )
                riverfrontage = "n/a"
                allowablearea = "n/a"
                actualarea = "n/a"
                dockarea = "n/a"
                totalarea = "n/a"
                gangwayarea = "n/a"
        else:
            logger.debug("no dock")
            try:
                current_date = date.today()
                logger.debug(current_date)
            except ValueError as e:
                logger.debug('ValueError occurred %s', e)
            except TypeError as e:
                logger.debug('TypeError occurred %s', e)
                current_date = ""
                logger.debug(current_date)
                logger.debug(f"{e}")
        fullname = fname + " " + lname
        logger.debug(fullname)
        citystatezip = ocity + " " + ostate + ", " + ozipcd
        logger.debug(citystatezip)
        phyaddress = phycity + " " + phystate + ", " + phyzip
        logger.debug(phyaddress)
        INPDF_TEMPLATE_PATH = (
            TEMPLATE_DIR / "ace_templates/Agent_Auth_Form.pdf"
            )
        OUTPDF_OUTPUT_PATH = (
            FORM_DIR / f"{projectnumber2}-Agent_Auth_Form.pdf"
        )
        ANNOT_KEY = "/Annots"
        ANNOT_FIELD_KEY = "/T"
        ANNOT_VAL_KEY = "/V"
        ANNOT_RECT_KEY = "/Rect"
        SUBTYPE_KEY = "/Subtype"
        WIDGET_SUBTYPE_KEY = "/Widget"
        data_dict = {
            "fname": f"{fname}",
            "lname": f"{lname}",
            "fullname": f"{fullname}",
            "phone": f"{phone}",
            "email": f"{email}",
            "parcelid": f"{parcelid}",
            "oaddr1": f"{oaddr1}",
            "ocity": f"{ocity}",
            "ostate": f"{ostate}",
            "ozipcd": f"{ozipcd}",
            "phyaddr1": f"{phyaddr1}",
            "phycity": f"{phycity}",
            "phystate": f"{phystate}",
            "phyzip": f"{phyzip}",
            "phyaddress": f"{phyaddress}",
            "citystatezip": f"{citystatezip}",
        }
        write_fillable_pdf(
            INPDF_TEMPLATE_PATH,
            OUTPDF_OUTPUT_PATH,
            data_dict
        )
        input_pdf = PdfReader(
            FORM_DIR / f"{projectnumber2}-Agent_Auth_Form.pdf"
            )
        fp_output = str(
            FORM_DIR / f"{projectnumber2}-Agent_Auth_Form_final.pdf"
            )
        output_pdf = PdfWriter()
        for page in input_pdf.pages:
            output_pdf.add_page(page)
        with open(fp_output, 'wb') as output_file:
            output_pdf.write(output_file)
        INPDF_TEMPLATE_PATH = (
            TEMPLATE_DIR / "ace_templates/WOD_App_Form.pdf"
        )
        OUTPDF_OUTPUT_PATH = (
            FORM_DIR / f"{projectnumber2}-WOD_App_Form.pdf"
        )
        ANNOT_KEY = "/Annots"
        ANNOT_FIELD_KEY = "/T"
        ANNOT_VAL_KEY = "/V"
        ANNOT_RECT_KEY = "/Rect"
        SUBTYPE_KEY = "/Subtype"
        WIDGET_SUBTYPE_KEY = "/Widget"
        data_dict = {
            "fname": f"{fname}",
            "lname": f"{lname}",
            "fullname": f"{fullname}",
            "projectname": f"{lname} Dock",
            "phone": f"{phone}",
            "email": f"{email}",
            "parcelid": f"{parcelid}",
            "oaddr1": f"{oaddr1}",
            "ocity": f"{ocity}",
            "ostate": f"{ostate}",
            "ozipcd": f"{ozipcd}",
            "phyaddr1": f"{phyaddr1}",
            "phycity": f"{phycity}",
            "phystate": f"{phystate}",
            "phyzip": f"{phyzip}",
            "phyaddress": f"{phyaddress}",
            "modification": f"{modification}",
            "floatingdock": f"{floatingdock}",
            "newpermit": f"{newpermit}",
            "county": f"{county}",
            "citystatezip": f"{citystatezip}",
        }
        write_fillable_pdf(
            INPDF_TEMPLATE_PATH,
            OUTPDF_OUTPUT_PATH,
            data_dict
        )
        input_pdf = PdfReader(
            FORM_DIR / f"{projectnumber2}-WOD_App_Form.pdf"
            )
        fp_output = str(
            FORM_DIR / f"{projectnumber2}-WOD_App_Form_final.pdf"
            )
        output_pdf = PdfWriter()
        for page in input_pdf.pages:
            output_pdf.add_page(page)
        with open(fp_output, 'wb') as output_file:
            output_pdf.write(output_file)
        logger.debug("Checkpoint: WOD App created")
        INPDF_TEMPLATE_PATH = TEMPLATE_DIR / \
            "ace_templates/XXXX-Dock_Plan_Template.pdf"
        OUTPDF_OUTPUT_PATH = FORM_DIR / \
            f"{projectnumber2}.Plan-SITE-DOCK_PLAN.pdf"
        ANNOT_KEY = "/Annots"
        ANNOT_FIELD_KEY = "/T"
        ANNOT_VAL_KEY = "/V"
        ANNOT_RECT_KEY = "/Rect"
        SUBTYPE_KEY = "/Subtype"
        WIDGET_SUBTYPE_KEY = "/Widget"
        data_dict = {
            "fname": f"{fname}",
            "lname": f"{lname}",
            "fullname": f"{fullname}",
            "projectname": f"{lname} Dock",
            "projectnumber": f"{projectnumber2}",
            "phone": f"{phone}",
            "email": f"{email}",
            "parcelid": f"{parcelid}",
            "oaddr1": f"{oaddr1}",
            "ocity": f"{ocity}",
            "ostate": f"{ostate}",
            "ozipcd": f"{ozipcd}",
            "phyaddr1": f"{phyaddr1}",
            "phycity": f"{phycity}",
            "phystate": f"{phystate}",
            "phyzip": f"{phyzip}",
            "phyaddress": f"{phyaddress}",
            "decklength": f"{decklength}'",
            "deckwidth": f"{deckwidth}'",
            "gangwaylength": f"{gangwaylength}'",
            "gangwaywidth": f"{gangwaywidth}'",
            "docklength": f"{docklength}'",
            "dockwidth": f"{dockwidth}'",
            "modification": f"{modification}",
            "floatingdock": f"{floatingdock}",
            "newpermit": f"{newpermit}",
            "riverfrontage": (
                f"RIVER FRONTAGE LENGTH = {riverfrontage} FT"
                ),
            "allowablearea": (
                f"ALLOWABLE PREEMPTIVE AREA = {allowablearea} SF"
                ),
            "actualarea": f"ACTUAL PREEMPTIVE AREA = {actualarea} SF",
            "date": date.today(),
            "citystatezip": f"{citystatezip}",
        }
        write_fillable_pdf(
            INPDF_TEMPLATE_PATH,
            OUTPDF_OUTPUT_PATH,
            data_dict
        )
        input_pdf = PdfReader(
            FORM_DIR / f"{projectnumber2}.Plan-SITE-DOCK_PLAN.pdf"
            )
        fp_output = str(
            FORM_DIR / f"{projectnumber2}.Plan-SITE-DOCK_PLAN_final.pdf"
            )
        output_pdf = PdfWriter()
        for page in input_pdf.pages:
            output_pdf.add_page(page)
        with open(fp_output, 'wb') as output_file:
            output_pdf.write(output_file)
        logger.debug("Dock Plan PDF Created")
        INPDF_TEMPLATE_PATH = TEMPLATE_DIR / \
            "ace_templates/XXXX-Dock_Section_View_Template.pdf"
        OUTPDF_OUTPUT_PATH = FORM_DIR / \
            f"{projectnumber2}.Plan-SITE-DOCK_SECTION_VIEW_.pdf"
        ANNOT_KEY = "/Annots"
        ANNOT_FIELD_KEY = "/T"
        ANNOT_VAL_KEY = "/V"
        ANNOT_RECT_KEY = "/Rect"
        SUBTYPE_KEY = "/Subtype"
        WIDGET_SUBTYPE_KEY = "/Widget"
        data_dict = {
            "fname": f"{fname}",
            "lname": f"{lname}",
            "projectname": f"{lname} Dock",
            "projectnumber": f"{projectnumber2}",
            "phone": f"{phone}",
            "email": f"{email}",
            "parcelid": f"{parcelid}",
            "oaddr1": f"{oaddr1}",
            "ocity": f"{ocity}",
            "ostate": f"{ostate}",
            "ozipcd": f"{ozipcd}",
            "phyaddr1": f"{phyaddr1}",
            "phycity": f"{phycity}",
            "phystate": f"{phystate}",
            "phyzip": f"{phyzip}",
            "county": f"{county}",
            "decklength": f"{decklength}",
            "deckwidth": f"{deckwidth}",
            "gangwaylength": f"{gangwaylength}",
            "gangwaywidth": f"{gangwaywidth}",
            "docklength": f"{docklength}",
            "dockwidth": f"{dockwidth}",
            "newpermit": f"{newpermit}",
            "modification": f"{modification}",
            "floatingdock": f"{floatingdock}",
            "riverfrontage": f"{riverfrontage}",
            "allowablearea": f"{allowablearea}",
            "actualarea": f"{actualarea}",
            "date": date.today(),
            "citystatezip": f"{citystatezip}",
            "fullname": f"{fullname}",
            "phyaddress": f"{phyaddress}",
        }
        write_fillable_pdf(
            INPDF_TEMPLATE_PATH,
            OUTPDF_OUTPUT_PATH,
            data_dict
        )
        input_pdf = PdfReader(
            TEMPLATE_DIR / \
                "ace_templates/XXXX-Dock_Section_View_Template.pdf")
        fp_output = str(TEMPLATE_DIR / \
            "ace_templates/XXXX-Dock_Section_View_Template_final.pdf")
        output_pdf = PdfWriter()
        for page in input_pdf.pages:
            output_pdf.add_page(page)
        with open(fp_output, 'wb') as output_file:
            output_pdf.write(output_file)
    except ValueError as e:
        logger.debug('ValueError occurred %s', e)
        logger.debug("get_pdf_fillable: failed")
    except TypeError as e:
        logger.debug('TypeError occurred %s', e)
        logger.debug("get_pdf_fillable: failed")
