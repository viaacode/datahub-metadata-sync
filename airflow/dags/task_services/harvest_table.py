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
                datestamp timestamp with time zone,
                synchronized BOOL DEFAULT 'false',
                xml_converted BOOL DEFAULT 'false',
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
        cursor.execute("SELECT max(datestamp) FROM harvest_vkc")
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
            SELECT count(*)
            FROM harvest_vkc JOIN mapping_vkc ON
            (harvest_vkc.work_id = mapping_vkc.work_id)
            WHERE
            harvest_vkc.xml_converted=FALSE
            """
        )

    @staticmethod
    def batch_select_transform_records(server_cursor):
        # we do a join with our new mapping_vkc table instead:
        server_cursor.execute(
            """
            SELECT harvest_vkc.id, harvest_vkc.mam_xml, harvest_vkc.vkc_xml,
                harvest_vkc.work_id, harvest_vkc.datestamp,
                harvest_vkc.synchronized, harvest_vkc.xml_converted,
                mapping_vkc.fragment_id, mapping_vkc.cp_id, mapping_vkc.external_id
            FROM harvest_vkc JOIN mapping_vkc ON
            (harvest_vkc.work_id = mapping_vkc.work_id)
            WHERE
            harvest_vkc.xml_converted=FALSE
            ORDER BY work_id
            """
        )

    @staticmethod
    def publish_count(connection):
        return HarvestTable.count_qry(
            connection,
            """
            SELECT count(*)
            FROM harvest_vkc JOIN mapping_vkc ON
            (harvest_vkc.work_id = mapping_vkc.work_id)
            WHERE
            harvest_vkc.synchronized=FALSE AND harvest_vkc.xml_converted=TRUE
            """
        )

    @staticmethod
    def batch_select_publish_records(server_cursor):
        server_cursor.execute(
            """
            SELECT harvest_vkc.id, harvest_vkc.mam_xml, harvest_vkc.vkc_xml,
                harvest_vkc.work_id, harvest_vkc.datestamp,
                harvest_vkc.synchronized, harvest_vkc.xml_converted,
                mapping_vkc.fragment_id, mapping_vkc.cp_id, mapping_vkc.external_id
            FROM harvest_vkc JOIN mapping_vkc ON
            (harvest_vkc.work_id = mapping_vkc.work_id)
            WHERE
            harvest_vkc.synchronized=FALSE AND harvest_vkc.xml_converted=TRUE
            ORDER BY work_id
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
    def set_xml_converted(cursor, record, val):
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET xml_converted = %s,
                updated_at = now()
            WHERE id=%s
            """,
            (val, record['id'])
        )

    @staticmethod
    def update_mam_xml(cursor, record, mam_xml):
        cursor.execute(
            """
            UPDATE harvest_vkc
            SET mam_xml = %s,
                synchronized = FALSE,
                xml_converted = TRUE,
                updated_at = now()
            WHERE id=%s
            """,
            (mam_xml, record['id'])
        )
