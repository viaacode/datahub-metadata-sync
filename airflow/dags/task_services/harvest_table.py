#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   airflow/dags/task_services/harvest_table.py
#
#   HarvestTable handles creation, truncating and updating
#   records in the harvest_vkc table


class HarvestTable:

    @staticmethod
    def create_sql():
        return """
            CREATE TABLE IF NOT EXISTS harvest_vkc(
                id SERIAL PRIMARY KEY,
                vkc_xml VARCHAR,
                mam_xml VARCHAR,
                work_id VARCHAR,
                fragment_id VARCHAR,
                cp_id VARCHAR,
                datestamp timestamp with time zone,
                synchronized BOOL DEFAULT 'false',
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );
            """

    @staticmethod
    def truncate(cursor):
        print("Clearing harvest_vkc table")
        cursor.execute("TRUNCATE TABLE harvest_vkc")

    @staticmethod
    def get_max_datestamp(cursor):
        cursor.execute("""
            SELECT max(datestamp) FROM harvest_vkc WHERE 
                synchronized=true AND
                mam_xml IS NOT NULL
        """)
        result = cursor.fetchone()
        if len(result) == 1:
            return result[0]
        else:
            return None

    @staticmethod
    def insert(cursor, record):
        cursor.execute(
            """
            INSERT INTO harvest_vkc (work_id, vkc_xml, mam_xml, datestamp)
            VALUES(%s, %s, NULL, %s)
            """,
            (record['work_id'], record['xml'], record['datestamp'])
        )

    @staticmethod
    def batch_select_records(server_cursor):
        server_cursor.execute(
            'select * from harvest_vkc where synchronized=false')

    @staticmethod
    def batch_select_updateable_records(server_cursor):
        server_cursor.execute(
            'select * from harvest_vkc where synchronized=false and fragment_id IS NOT NULL')

    @staticmethod
    def set_synchronized(cursor, record, val):
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET synchronized = %s,
                updated_at = now()
            WHERE id=%s
            """,
            (val, record['id'])
        )

    @staticmethod
    def update_mam_xml(cursor, record, converted_record, fragment_id=None, cp_id=None):
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET mam_xml = %s,
                fragment_id = %s,
                cp_id = %s,
                synchronized = 'false',
                updated_at = now()
            WHERE id=%s
            """,
            (converted_record, fragment_id, cp_id, record['id'])
        )
