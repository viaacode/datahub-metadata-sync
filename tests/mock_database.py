#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/mock_database.py
#
#   MockDatabase and MockCursor classes that fake out the
#   database connection used in our tasks.
#   By supplying a fixture_data it matches the query requested
#   and returns a fixed/static response from the fixture data.
#   This makes it possible for our dag tasks to run isolated without
#   an actual postgres database. See test_harvest_vkc_job and other
#   tests for usage.
#
#   a useful way to create fixtures is to just run the test code
#   and pass -s that will print the query history here:
#   python -m pytest tests/test_harvest_vkc_job.py -s

class MockCursor:
    def __init__(self):
        self.queries = []
        self.create_params = []
        self.fetchmany_history = {}
        self.fixture_data = {
            'fetchmany': [],    # entries used with cursor.fetchmany
            'fetchone': []      # entries used with cursor.fetchone
        }
        self.name = 'default'

    def create(self, name='default', cursor_factory=None):
        print(
            f"cursor create name={name}, cursor_factory={cursor_factory}", flush=True)
        self.create_params.append(cursor_factory)
        self.name = name

    def execute(self, qry, params=None):
        if params:
            self.queries.append(qry % params)
        else:
            self.queries.append(qry)

        print(f"execute called qry={qry}", flush=True)

    def fetchone(self):
        print(f'fetchone called qry={self._last_qry()}', flush=True)
        for entry in self.fixture_data['fetchone']:
            if entry['qry'] in self._last_qry():
                return entry.get('rows', [])

        return None

    def fetchmany(self, size=1):
        last_qry = self._last_qry()
        print(f'fetchmany called qry={last_qry}', flush=True)
        for entry in self.fixture_data['fetchmany']:
            if entry['qry'] in last_qry:
                # avoid infinite loops, if a fetchmany has returned
                # data, second time make it return None
                if self.fetchmany_history.get(last_qry, 0) > 0:
                    return None
                else:
                    self.fetchmany_history[last_qry] = 1
                    return entry.get('rows', [])

        return None

    def close(self):
        print("cursor close called", flush=True)

    def _last_qry(self):
        if len(self.queries) > 0:
            return self.queries[-1]

        return ''

    def _store_fixture_data(self, data):
        self.fixture_data = data


class MockDatabase:
    def __init__(self, fixture_data=None):
        if fixture_data is None:
            fixture_data = {
                'fetchmany': [],
                'fetchone': []
            }
        self.mock_cursor = MockCursor()
        self.mock_cursor._store_fixture_data(fixture_data)
        self._init_counters()

    def _set_fixtures(self, fixture_data):
        self.mock_cursor._store_fixture_data(fixture_data)
        self._init_counters()

    def _init_counters(self):
        self.commit_count = 0
        self.close_count = 0

    def qry_history(self):
        return self.mock_cursor.queries

    def cursor(self, name='default', cursor_factory=None):
        self.mock_cursor.create(name, cursor_factory)
        return self.mock_cursor

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.close_count += 1
