# -*- coding: utf-8 -*-

import gsocketpool.pool
import time
import uuid
import gevent

from mock import Mock, patch
from nose.tools import *

from bkyototycoon.client import KyotoTycoonConnection, KyotoTycoonPoolConnection


class TestKyotoTycoonConnection(object):
    def test_constructor_lazy_connection(self):
        connection = KyotoTycoonConnection(lazy=True)

        ok_(not connection.is_connected())
        connection.open()
        ok_(connection.is_connected())

    def test_open_and_close(self):
        connection = KyotoTycoonConnection()

        ok_(connection.is_connected())
        connection.close()
        ok_(not connection.is_connected())

    @patch('socket.create_connection')
    def test_open_socket_timeout(self, mock_create_connection):
        mock_socket_ins = Mock()
        mock_create_connection.return_value = mock_socket_ins
        KyotoTycoonConnection(timeout=5.0)

        mock_socket_ins.settimeout.assert_called_once_with(5.0)

    def test_get_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_({}, connection.get_bulk(data.keys()))

        connection.set_bulk(data)

        eq_(data, connection.get_bulk(data.keys()))
        eq_(data, connection.get_bulk(data.keys() + ['dummy_key']))

    def test_set_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_(3, connection.set_bulk(data))
        eq_(data, connection.get_bulk(data.keys()))

    def test_set_bulk_async(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        eq_(None, connection.set_bulk(data, async=True))

        time.sleep(0.3)
        eq_(data, connection.get_bulk(data.keys()))

    def test_set_bulk_lifetime(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        eq_(1, connection.set_bulk(data, lifetime=0.1))

        time.sleep(1)
        eq_({}, connection.get_bulk(data.keys()))

    def test_remove_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_(3, connection.set_bulk(data))
        eq_(data, connection.get_bulk(data.keys()))

        connection.remove_bulk(data.keys()[1:])
        eq_(data.items()[0:1], connection.get_bulk(data.keys()).items())

    def test_remove_bulk_async(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        connection.set_bulk(data)
        eq_(data, connection.get_bulk(data.keys()))

        eq_(None, connection.remove_bulk(data.keys(), async=True))

        time.sleep(1)
        eq_({}, connection.get_bulk(data.keys()))

    def test_query_with_db_index(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        connection.set_bulk(data, db_index=1)

        eq_(data, connection.get_bulk(data.keys(), db_index=1))
        connection.remove_bulk(data.keys(), db_index=1)

        eq_({}, connection.get_bulk(data.keys(), db_index=1))


class TestKyotoTycoonPoolConnection(object):
    def setUp(self):
        self._pool = gsocketpool.pool.Pool(KyotoTycoonPoolConnection)

    def test_with_statement(self):
        with self._pool.connection() as client:
            ok_(isinstance(client, KyotoTycoonConnection))
            ok_(client.is_connected())

    def test_get_bulk(self):
        data = {uuid.uuid1().hex: 1}

        with self._pool.connection() as client:
            client.set_bulk(data)

            eq_(data, client.get_bulk(data.keys()))

    def test_set_bulk(self):
        data = {uuid.uuid1().hex: 1}

        with self._pool.connection() as client:
            eq_(1, client.set_bulk(data))
            eq_(data, client.get_bulk(data.keys()))

    def test_remove_bulk(self):
        data = {uuid.uuid1().hex: 1}

        with self._pool.connection() as client:
            client.set_bulk(data)
            eq_(1, client.remove_bulk(data.keys()))
            eq_({}, client.get_bulk(data.keys()))

    def test_query_with_db_index(self):
        data = {uuid.uuid1().hex: 1}

        with self._pool.connection() as client:
            client.set_bulk(data, db_index=1)

            eq_(data, client.get_bulk(data.keys(), db_index=1))
            client.remove_bulk(data.keys(), db_index=1)

            eq_({}, client.get_bulk(data.keys(), db_index=1))

    def test_is_expired(self):
        def _test_is_expired():
            t = time.time()
            c = KyotoTycoonPoolConnection(lifetime=1)
            eq_(c._lifetime, 1)
            ok_(t <= c._created <= t + 1)
            ok_(not c.is_expired())
            gevent.sleep(1.1)
            ok_(c.is_expired())

            t2 = time.time()
            c2 = KyotoTycoonPoolConnection()
            ok_(c2._lifetime is None)
            ok_(t2 <= c2._created <= t2 + 1)

        gthread = gevent.spawn(_test_is_expired)
        gthread.join()
