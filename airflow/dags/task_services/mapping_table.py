#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   airflow/dags/task_services/mapping_table.py
#
#   MappingTable keeps track of the mediahaven work_ids.
#   it replaces the hashmap we first used and allows for multiple matches
#   for a single work_id (it might have multiple fragment_id's due to different
#   versions of the same artwork that is stored in mediahaven).
from psycopg2.extras import DictCursor


class MappingTable:

    @staticmethod
    def create_sql():
        return """
            CREATE TABLE IF NOT EXISTS mapping_vkc(
                id SERIAL PRIMARY KEY,
                work_id VARCHAR,
                work_id_alternate VARCHAR,
                fragment_id VARCHAR,
                external_id VARCHAR,
                cp_id VARCHAR,
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );
            """

    @staticmethod
    def truncate(connection):
        print("Clearing mapping_vkc table")
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE mapping_vkc")
        connection.commit()
        cursor.close()
        # connection.close() connection is not closed here we use it later on.

    @staticmethod
    def insert(connection, record):
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO mapping_vkc
            (work_id, work_id_alternate, fragment_id, external_id, cp_id)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (
                record['work_id'],
                record['work_id_alternate'],
                record['fragment_id'],
                record['external_id'],
                record['cp_id'],
            )
        )

        connection.commit()
        cursor.close()

    # not used yet, might be useful for some kind of delta later on

    @staticmethod
    def get_max_datestamp(cursor):
        cursor.execute("""
            SELECT max(updated_at) FROM mapping_vkc
        """)
        result = cursor.fetchone()
        if len(result) == 1:
            return result[0]
        else:
            return None

    # NOT USED YET for performance we'll do a join with harvest table instead

    @staticmethod
    def find_work_id(cursor, work_id):
        # TODO: also add underscore variants here?
        # work_id_esc = work_id.replace(".", "_")
        cursor.execute(
            """
            SELECT * FROM mapping_vkc WHERE
            work_id=%s OR work_id_alternate=%s
            """,
            (work_id, work_id)
        )
        result = cursor.fetchall()
        return result

    # TODO: make a join qry in harvest_table...
    # this will avoid n+1 qry issue here.
