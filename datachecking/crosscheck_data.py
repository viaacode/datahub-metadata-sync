import sys
import os
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"USAGE: python {sys.argv[0]} <csv file to check>")
        sys.exit(1)

    csv_file = sys.argv[1]

    database = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        host=os.environ.get('DB_HOST')
    )

    cursor = database.cursor()

    with open(csv_file, newline='') as csvfile:
        csvdata = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in csvdata:
            # check_external_id(cursor, row)
            check_fragment(cursor, row)

    cursor.close()
    database.close()
