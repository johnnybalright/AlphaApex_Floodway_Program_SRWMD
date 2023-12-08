"""
This module contains constants defining file paths and URLs necessary
for a GIS-related project.

Paths included refer to the location of shapefiles, TIFF files, and
text files used in the project:
- EB_LINE: Path to the eastbound line shapefile.
- WB_LINE: Path to the westbound line shapefile.
- IN_SHP_MAIN: Path to the main input shapefile.
- IN_SHP_MAIN_SUBSET: Path to a subset of the main input shapefile.
- IN_DEM_MAIN: Path to the main Digital Elevation Model (DEM) TIFF file.
- XML_LINKS: Path to a text file containing XML links.
- BOUND_COORDS: Path to a text file containing boundary coordinates.
- LASTOOLS_DIRECTORY: Directory path where LAStools binaries are
located.

URLs included refer to various metadata located on the USGS FTP server.
These URLs point to metadata
pertaining to elevation projects across various counties, such as
Suwannee, Columbia, Lafayette, and
others.

All paths and URLs are hardcoded and point to specific locations or
files necessary for the execution and completion of the GIS project.
"""
EB_LINE="./gis/suw_eb_line.shp"
WB_LINE="./gis/suw_wb_line.shp"
EFLDWY="./gis/efldwy_l.shp"
WFLDWY="./gis/wfldwy_l.shp"
SUW="./gis/suw_cut.shp"
SUW_XS="./gis/suw_xs.shp"
IN_SHP_MAIN="./gis/parcels20.shp"
IN_SHP_MAIN_SUBSET="./gis/subset_parcels20.shp"
IN_DEM_MAIN="/mnt/ubuntu-storage-2/dem2019.tiff"
SQLITE_PARCELS_20="./gis/parcels20.sqlite3"
XML_LINKS="./tmp/xml_links.txt"
BOUND_COORDS="./tmp/bound_coords.txt"
LASTOOLS_DIRECTORY="./tmp/LAStools/bin"
USGS_METADATA_FTP_SUWANNEE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Suwannee_2018/metadata/"
USGS_METADATA_FTP_COLUMBIA="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Columbia_2018/metadata/"
USGS_METADATA_FTP_LAFAYETTE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Lafayette_2018/metadata/"
USGS_METADATA_FTP_GILCHRIST="https://rockyweb.usgs.gov/vdelivery/Datasets" \
    + "/Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA" \
    + "/FL_Peninsular_FDEM_Gilchrist_2018/metadata/"
USGS_METADATA_FTP_DIXIE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Dixie_2018/metadata/"
USGS_METADATA_FTP_LEVY="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_2018_D18/" \
        + "FL_Peninsular_Levy_2018/metadata/"
USGS_METADATA_FTP_MADISON="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Madison_2018/metadata/"
USGS_METADATA_FTP_HAMILTON="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Hamilton_2018/metadata/"
FLOOD_REPORT_URL='https://www.srwmdfloodreport.com/'
SUWANNEE_PARCEL_URL='http://www.suwanneepa.com/gis/'
COLUMBIA_PARCEL_URL='http://g4.columbia.floridapa.com/gis/'
LAFAYETTE_PARCEL_URL="http://www.lafayettepa.com/gis/"
