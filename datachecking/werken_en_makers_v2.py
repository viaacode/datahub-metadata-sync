#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Walter Schreppers
# lightweight version for quicker debugging of our queries and xpath traversal

import sys
import os
import csv
import psycopg2
from psycopg2.extras import DictCursor
# import lxml.etree as etree
# from vkc_api import VkcApi


# simple version to fetch some xml data to work on:
def select_matches(cursor, offset, page_size):
    cursor.execute(
        """
            SELECT * FROM harvest_vkc WHERE xml_converted=TRUE
            ORDER BY id LIMIT %s OFFSET %s
        """,
        (page_size, offset)
    )
    return cursor.fetchall()


def count_records(cursor):
    cursor.execute(
        """
        SELECT count(*) FROM harvest_vkc where xml_converted=TRUE;
        """
    )
    result = cursor.fetchone()
    return result[0]


def main():
    if len(sys.argv) < 2:
        print(f"USAGE: python {sys.argv[0]} <output csv file>")
        sys.exit(1)

    output_file = sys.argv[1]

    print("Connecting to database...")
    database = psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'airflow_development'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        host=os.environ.get('DB_HOST'),
        sslmode='require',
        port=os.environ.get("DB_PORT")

    )
    cursor = database.cursor(cursor_factory=DictCursor)
    matched_count = count_records(cursor)
    print(f"Matched count = {matched_count}")

    print(f"Opening {output_file} for writing csv data...")

    csvfile = open(output_file, 'w')
    writer = csv.writer(csvfile, delimiter=';', quotechar='"')
    row = ['first_name', 'last_name', 'mail', 'apps', 'organizational_status']
    writer.writerow(row)

    offset = 0
    page_size = 500
    csv_entries = 0

    # use for debug session
    # vkc_api = VkcApi()

    while offset < matched_count:
        print("Saving {} records to {}, progress: {}%".format(
            page_size,
            output_file,
            round((offset/matched_count)*100, 2)
        )
        )
        vkc_records = select_matches(cursor, offset, page_size)
        for r in vkc_records:
            # use this for debug session:
            # aanbieder = r['aanbieder']
            # created_at = r['created_at']
            # datestamp = r['datestamp']
            # mam_xml = r['mam_xml']
            # vkc_xml = r['vkc_xml']
            # max_breedte_cm = r['max_breedte_cm']
            # min_breedte_cm = r['min_breedte_cm']
            # synchronized = r['synchronized']
            # updated_at = r['updated_at']
            # work_id = r['work_id']
            # result = vkc_api.process_xml_record(vkc_xml)
            # __import__('pdb').set_trace()

            writer.writerow(row)
            csv_entries += 1

        offset += page_size

    print("all done.")
    print(f"Saved {csv_entries} records to {output_file}")

    csvfile.close()
    cursor.close()
    database.close()


if __name__ == '__main__':
    main()
