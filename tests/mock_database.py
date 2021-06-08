class MockCursor:
    def __init__(self):
        self.queries = []
        self.create_params = []
        self.fixture_data = []

    def create(self, cursor_factory):
        print(f"cursor create factory={cursor_factory}", flush=True)
        self.create_params.append(cursor_factory)

    def execute(self, qry, params=None):
        if params:
            self.queries.append(qry % params)
        else:
            self.queries.append(qry)

        print(f"execute called queries=={self.queries}", flush=True)

    def fetchone(self):
        for entry in self.fixture_data:
            if entry['qry'] in self._last_qry():
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
    def __init__(self, fixture_data=[]):
        self.mock_cursor = MockCursor()
        self.mock_cursor._store_fixture_data(fixture_data)

    def reset_counters(self):
        self.commit_count = 0
        self.close_count = 0

    def set_fixtures(self, fixture_data):
        self.mock_cursor._store_fixture_data(fixture_data)
        self.reset_counters()

    def qry_history(self):
        return self.mock_cursor.queries

    def cursor(self, cursor_factory=None):
        self.mock_cursor.create(cursor_factory)
        return self.mock_cursor

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.close_count += 1

