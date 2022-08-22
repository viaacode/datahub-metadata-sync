# https://meemoo.atlassian.net/browse/OPS-1614
# to install packages
# cd ..
# make install
# source python_env/bin/activate
# cd beelden_inventaris_lijst
# python inventaris.py
#
import openpyxl

# this works and can write to an xlsx, but is really slow:
# dataframe = openpyxl.load_workbook("OPS1614_inventarisnrs_20220804_copyright.xlsx")
# dataframe1 = dataframe.active
# for row in range(0, dataframe1.max_row):
#     for col in dataframe1.iter_cols(1, dataframe1.max_column):
#         print(col[row].value, end=" ")
#     print()

# by switching to read-only speed is acceptable.
wb = openpyxl.load_workbook("OPS1614_inventarisnrs_20220804_copyright.xlsx", read_only=True)
for ws in wb:
    for row in ws.rows:
        # for cell in row:
        #     print(cell.value, end=" ")
        instelling = row[0].value
        inventaris_nr = row[1].value
        copyright = row[2].value
        vervaardiger1 = row[3].value
        vervaardiger2 = row[4].value
        vervaardiger3 = row[5].value
        vervaardiger4 = row[6].value
        vervaardiger5 = row[7].value
        vervaardiger6 = row[8].value
        vervaardiger7 = row[9].value

        print(f"Lookup inventaris nr: {inventaris_nr}")


# TODO:
# output to csv format instead of xlsx because of poor python performance
# when writing to xlsx files.

# Velden voor csv export:
# inventarisnummer
# mediaobject ID (of fragment ID)
# titel
# Dynamic.dc_source,
# Dynamic.dc_rights_credit,
# Dynamic.dc_identifier_localids.PersistenteURI_Werk,
# Dynamic.dc_identifier_localids.WorkPID,
# Dynamic.dc_identifier_localids.Inventarisnummer,
# Dynamic.dc_identifier_localids.Afbeelding,
# Dynamic.dc_identifier_localids.Objectnaam,
# Dynamic.dc_identifier_localids.PersistenteURI_Record,
# Dynamic.dc_creators.Maker,
# Dynamic.dc_title,
# Dynamic.dc_identifier_localid,
# Dynamic.PID,
# Dynamic.dc_titles.archief,
# Dynamic.dc_titles.deelarchief,
# Technical.FileSize,
# Technical.MimeType,
# Technical.Height,
# Technical.Width,
# Technical.ImageOrientation,
# Descriptive.CreationDate,
# Descriptive.Authors.Author,
# Descriptive.OriginalFilename,
# Descriptive.Title
# Creator en rechtenstatus (SABAM etc) mogen ook toegevoegd worden. 

