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
                mh_checked BOOL DEFAULT 'false',
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );
            """

    @staticmethod
    def truncate(connection):
        print("Clearing harvest_vkc table")
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE harvest_vkc")
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def get_max_datestamp(cursor):
        cursor.execute("""
            SELECT max(datestamp) FROM harvest_vkc WHERE
                synchronized=TRUE AND
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
    def count_qry(connection, qry):
        cursor = connection.cursor()
        cursor.execute(qry)
        result = cursor.fetchone()
        cursor.close()

        if len(result) == 1:
            return result[0]
        else:
            return 0

    @staticmethod
    def transform_count(connection):
        return HarvestTable.count_qry(
            connection,
            """
            SELECT count(*) FROM harvest_vkc WHERE
            synchronized=FALSE AND mh_checked=FALSE
            """
        )

    @staticmethod
    def batch_select_transform_records(server_cursor):
        server_cursor.execute(
            """
            SELECT * FROM harvest_vkc WHERE
            synchronized=FALSE AND mh_checked=FALSE
            """
        )

    @staticmethod
    def publish_count(connection):
        return HarvestTable.count_qry(
            connection,
            """
            SELECT count(*) FROM harvest_vkc WHERE
            synchronized=FALSE AND
            fragment_id IS NOT NULL
            """
        )

    @staticmethod
    def batch_select_publish_records(server_cursor):
        server_cursor.execute(
            """
            SELECT * FROM harvest_vkc WHERE
            synchronized=FALSE AND
            fragment_id IS NOT NULL
            """
        )

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
    def set_mh_checked(cursor, record, val):
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET mh_checked = %s,
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
                synchronized = FALSE,
                mh_checked = TRUE,
                updated_at = now()
            WHERE id=%s
            """,
            (converted_record, fragment_id, cp_id, record['id'])
        )
