#!/usr/bin/env python

import unittest
import psycopg2
from unittest import mock


def select_user(user_id):
    with psycopg2.connect("") as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            return cursor.fetchall()


class TestPatchConn(unittest.TestCase):
    def setUp(self):
        self.user_id = 16

    @mock.patch('psycopg2.connect')
    def test_with_context(self, mock_connect):
        mock_connect().__enter__().cursor().__enter__().fetchall.return_value = ['Walter']
        response = select_user(self.user_id)
        mock_connect().__enter__().cursor().__enter__().execute.assert_called_with('SELECT name FROM users WHERE id = %s', (self.user_id, ))
        assert response == ['Walter']



if __name__ == '__main__':
    unittest.main()



