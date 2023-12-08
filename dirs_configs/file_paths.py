"""
This module is used for defining output file templates related to
geographic data.

It sets up paths for saving output files such as:
- A Digital Elevation Model (DEM) clipped TIFF file,
- A shapefile representing parcel boundaries,
- A shapefile representing scaled parcel boundaries.

Each output filename is generated dynamically based on the project
number.

Attributes:
    OUT_DEM_TEMPLATE (Path): Template for the output path of the DEM
    clipped TIFF files.
    OUT_SHP_TEMPLATE (Path): Template for the output path of the parcel
    boundary shapefiles.
    OUT_SHP_SCALED_TEMPLATE (Path): Template for the output path of the
    scaled parcel boundary shapefiles.

Imported from:
    config : Contains configuration constants such as OUTPUT_DIR.

Author:
    Your Name (your.email@example.com)

Usage:
    from this_module import OUT_DEM_TEMPLATE, OUT_SHP_TEMPLATE,
    OUT_SHP_SCALED_TEMPLATE
"""
from .config import (OUTPUT_DIR,
                                 OUTPUT_DIRx,
                                 BASE_DIR,
                                 LOG_DIR
                                 )

OUT_DEM_TEMPLATE = str(
    OUTPUT_DIR / "{projectnumber}-dem_clipped.tiff"
    )
OUT_SHP_TEMPLATE = str(
    OUTPUT_DIR / "{projectnumber}-parcel_boundary.shp"
    )
OUT_SHP_SCALED_TEMPLATE = str(
    OUTPUT_DIR / "{projectnumber}-parcel_boundary_scaled.shp"
    )
OUT_SHP_HXLINE = str(
    OUTPUT_DIR / "hecras_line.shp"
    )
HX_CADD_TEMPLATE = str(
    OUTPUT_DIRx / "{projectnumber}-hecras_line.shp"
    )
OUT_SHP_BUFFER = str(
    OUTPUT_DIR / "hecras_line_buffer.shp"
    )
OUT_DEM_BUFFER = str(
    OUTPUT_DIR / "hecras_dem_clipped.tiff"
    )
HX_LINE_ADDED_PTS = str(
    OUTPUT_DIR / "hecras_line_added_pts.shp"
    )
HX_LINE_Z = str(
    OUTPUT_DIR / "hecras_line_z.shp"
    )
HX_LINE_Z_SMOOTHED = str(
    OUTPUT_DIR / "hecras_line_z_smoothed.shp"
    )
CSV_HX_ARR = str(
    OUTPUT_DIR / "hecras_arr.csv"
    )
XL_XS_EX = str(
    OUTPUT_DIR / "hecras_existing_xs.xlsx"
    )
CSV_PATH = str(
    OUTPUT_DIR / "xs_data.csv"
    )
XL_XS_DATA = str(
    BASE_DIR / "HECRAS" / "CrossSectionData.xlsx"
    )
OUT_SHP_CENTER = str(
            OUTPUT_DIR / "center_line.shp"
            )
OUT_SHP_CENTER_SCALED = str(
            OUTPUT_DIR / "center_line_scaled.shp"
            )
OUT_SHP_CENTER_LINE_BUFFER = str(
    OUTPUT_DIR / "/center_line_buffer.shp"
    )
OUT_DEM_CENTER_LINE_BUFFER = str(
    OUTPUT_DIR / "center_line_buffer_dem.tif"
    )
CENTER_XS_LINE_ADDED_PTS = str(
    OUTPUT_DIR / "center_line_added_pts.shp"
    )
CENTER_XS_LINE_Z = str(
    OUTPUT_DIR / "center_line_z.shp"
    )
CENTER_XS_LINE_Z_SMOOTHED = str(
    OUTPUT_DIR / "center_line_z_smoothed.shp"
    )
EOW_PT_1 = str(
    OUTPUT_DIR / "eow_pt_1.shp"
    )
TOB_PT_1 = str(
    OUTPUT_DIR / "tob_pt_1.shp"
    )
EOW_PT_2 = str(
    OUTPUT_DIR / "eow_pt_2.shp"
    )
TOB_PT_2 = str(
    OUTPUT_DIR / "tob_pt_2.shp"
    )
CONTOUR_EOW_TEMPLATE = str(
    OUTPUT_DIR / "{projectnumber}-eow_contour.shp"
    )
CONTOUR_EOW_TEMPLATE_1 = str(
    OUTPUT_DIR / "{projectnumber}-eow_contour_1.shp"
    )
CONTOUR_TOB_TEMPLATE = str(
    OUTPUT_DIR / "{projectnumber}-tob_contour.shp"
    )
CONTOUR_TOB_TEMPLATE_1 = str(
    OUTPUT_DIR / "{projectnumber}-tob_contour_1.shp"
    )
CONTOUR_EOW_TEMPLATE_2 = str(
    OUTPUT_DIR / "{projectnumber}-eow_contour_2.shp"
    )
CONTOUR_TOB_TEMPLATE_2 = str(
    OUTPUT_DIR / "{projectnumber}-tob_contour_2.shp"
    )
IN_SHP_CONTOURS = str(
    OUTPUT_DIR / "contours_2.shp"
    )
SETBACK75 = str(
    OUTPUT_DIR / "75ft_setback.shp"
    )
IN_SHP = str(
    OUTPUT_DIR / "parcel_boundary.shp"
    )
PARCEL_BOUNDARY_SURFACE = str(
    OUTPUT_DIR / "parcel_boundary_surface.shp"
    )
PARCEL_BOUNDARY_SITE = str(
    OUTPUT_DIR / "parcel_boundary_siteplan.shp"
    )
PARCEL_CONTOURS = str(
    OUTPUT_DIR / "countours_parcel.shp"
    )
TOB_CONTOUR_PARCEL = str(
    OUTPUT_DIR / "tob_countour_parcel.shp"
    )
EOW_CONTOUR_PARCEL = str(
    OUTPUT_DIR / "eow_countour_parcel.shp"
    )
YR100_CONTOUR = str(
    OUTPUT_DIR / "100yr_elev_contour.shp"
    )
YR50_CONTOUR = str(
    OUTPUT_DIR / "50yr_elev_contour.shp"
    )
YR10_CONTOUR = str(
    OUTPUT_DIR / "10yr_elev_contour.shp"
    )
WATER_LEVEL_SECTION_LINE = str(
    OUTPUT_DIR / "waterlevel_sectionline.shp"
    )
YR100_SECTION_LINE = str(
    OUTPUT_DIR / "100yr_sectionline.shp"
    )
HX_LINE_PARCEL_INTERSECTION_PTS = str(
    OUTPUT_DIR / "hxline_parcel_intersection_pts.shp"
    )
HX_LINE_PARCEL_INTERSECTION_PTS_2 = str(
    OUTPUT_DIR / "hxline_parcel_intersection_pts_2.shp"
    )
XL_POST = str(
    OUTPUT_DIR / "hecras_proposed_xs.xlsx"
    )
FRONTAGE_LINE = str(
    OUTPUT_DIR / "frontage_line.shp"
    )
WORKER_1_LOG_PATH = str(
    LOG_DIR / "worker1.log"
    )
WORKER_2_LOG_PATH = str(
    LOG_DIR / "worker2.log"
    )
WORKER_3_LOG_PATH = str(
    LOG_DIR / "worker3.log"
    )
WORKER_4_LOG_PATH = str(
    LOG_DIR / "worker4.log"
    )
MAIN_LOG_PATH = str(
    LOG_DIR / "main_py.log"
    )
