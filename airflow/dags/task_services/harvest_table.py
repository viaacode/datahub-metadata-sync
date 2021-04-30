#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class HarvestTable:
    """ HarvestTable handles creation, truncating and updating records in the harvest_vkc table """

    @staticmethod
    def create_sql():
        return """
            CREATE TABLE IF NOT EXISTS harvest_vkc(
                id SERIAL PRIMARY KEY,
                vkc_xml VARCHAR,
                mam_xml VARCHAR,
                work_id VARCHAR,
                datestamp timestamp with time zone,
                synchronized BOOL DEFAULT 'false',
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );
            """

    @staticmethod
    def truncate(conn):
        print("Clearing harvest_vkc table")
        cursor = conn.cursor()
        cursor.execute( "TRUNCATE TABLE harvest_vkc" )
        conn.commit()
        cursor.close()
        conn.close()

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
        server_cursor.execute('select * from harvest_vkc where synchronized=false')

    @staticmethod
    def set_synchronized(cursor, record, val):
        record_id = record[0]
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET synchronized = %s, 
                updated_at = now()
            WHERE id=%s
            """,
            (val, record_id)
        )

    @staticmethod
    def update_mam_xml(cursor, record, converted_record):
        record_id = record[0]
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET mam_xml = %s,
                synchronized = 'false',
                updated_at = now()
            WHERE id=%s
            """,
            (converted_record, record_id)
        )


