import sys
import os
import csv
import psycopg2


def check_alternate(cursor, row):
    field_value = row[3]
    cursor.execute(
        "SELECT * from mapping_vkc where work_id_alternate=%s",
        (field_value,)
    )

    result = cursor.fetchone()
    if result and len(result) >= 1:
        print(f"{field_value} MATCHED : row={row}")
    else:
        print(f"{field_value} NOT FOUND")


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
            check_alternate(cursor, row)

    cursor.close()
    database.close()
