import csv
import psycopg2


def check_external_id(cursor, row): 
    external_id = row[0]
    cursor.execute(
        "SELECT * from mapping_vkc where external_id=%s", 
        (external_id,)
    )

    result = cursor.fetchone()
    if result and len(result) >= 1:
        print(f"{external_id} MATCHED")
    else:
        print(f"{external_id} NOT FOUND: row={row}")


def check_fragment(cursor, row):
    fragment_id = row[1]
    cursor.execute(
        "SELECT * from mapping_vkc where fragment_id=%s", 
        (fragment_id,)
    )

    result = cursor.fetchone()
    if result and len(result) >= 1:
        print(f"{fragment_id} MATCHED")
    else:
        print(f"{fragment_id} NOT FOUND: row={row}")


database = psycopg2.connect(
    dbname="airflow_development",
    user="postgres",
    password="postgres",
    host="127.0.0.1"

)
cursor = database.cursor()

# with open('AIF_QAS_20210512.csv', newline='') as csvfile:
with open('aif_production.csv', newline='') as csvfile:
    csvdata = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in csvdata:
        check_fragment(cursor, row)


cursor.close()
database.close()

