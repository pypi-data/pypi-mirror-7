# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import contextlib
import threading

from kazoo import exceptions as k_exceptions
from kazoo.recipe import watchers as k_watchers

from zake import fake_client
from zake import test


@contextlib.contextmanager
def start_close(client):
    client.start()
    try:
        yield client
    finally:
        client.close()


class TestClient(test.Test):
    def setUp(self):
        super(TestClient, self).setUp()
        self.client = fake_client.FakeClient()

    def test_connected(self):
        self.assertFalse(self.client.connected)
        with start_close(self.client) as c:
            self.assertTrue(c.connected)

    def test_command(self):
        with start_close(self.client) as c:
            self.assertTrue(c.connected)
            self.assertEqual("imok", c.command('ruok'))
            self.client.command('kill')
            self.assertFalse(c.connected)

    def test_root(self):
        with start_close(self.client) as c:
            self.assertTrue(c.exists("/"))

    def test_version(self):
        with start_close(self.client) as c:
            self.assertTrue(len(c.server_version()) > 0)
            self.assertEqual(fake_client.SERVER_VERSION,
                             c.server_version())

    def test_make_path(self):
        with start_close(self.client) as c:
            c.create("/a/b/c", makepath=True)
            self.assertTrue(c.exists("/a/b/c"))
            self.assertTrue(c.exists("/a/b"))
            self.assertTrue(c.exists("/a"))

    def test_no_make_path(self):
        with start_close(self.client) as c:
            self.assertRaises(k_exceptions.KazooException,
                              c.create, "/a/b/c")

    def test_sequence(self):
        with start_close(self.client) as c:
            path = c.create("/", sequence=True)
            self.assertEqual("/0000000000", path)
            path = c.create("/", sequence=True)
            self.assertEqual("/0000000001", path)
            children = c.get_children("/")
            self.assertEqual(2, len(children))
            seqs = c.storage.sequences
            self.assertEqual(1, len(seqs))
            self.assertEqual(2, seqs['/'])

    def test_command_no_connect(self):
        self.assertRaises(k_exceptions.KazooException, self.client.sync, '/')

    def test_create(self):
        with start_close(self.client) as c:
            c.ensure_path("/b")
            c.create('/b/c', b'abc')
            paths = c.storage.paths
            self.assertEqual(3, len(paths))
            self.assertEqual(1, len(c.storage.get_children("/b")))
            self.assertEqual(1, len(c.storage.get_parents("/b")))
            data, znode = c.get("/b/c")
            self.assertEqual(b'abc', data)
            self.assertEqual(0, znode.version)
            c.set("/b/c", b"efg")
            data, znode = c.get("/b/c")
            self.assertEqual(b"efg", data)
            self.assertEqual(1, znode.version)

    def test_delete(self):
        with start_close(self.client) as c:
            self.assertRaises(k_exceptions.NoNodeError, c.delete, "/b")
            c.ensure_path("/")
            c.create("/b", b'b')
            c.delete("/b")
            self.assertRaises(k_exceptions.NoNodeError, c.delete, "/b")
            self.assertFalse(c.exists("/b"))

    def test_get_children(self):
        with start_close(self.client) as c:
            c.ensure_path("/a/b")
            c.ensure_path("/a/c")
            c.ensure_path("/a/d")
            self.assertEqual(3, len(c.get_children("/a")))

    def test_exists(self):
        with start_close(self.client) as c:
            c.ensure_path("/a")
            self.assertTrue(c.exists("/"))
            self.assertTrue(c.exists("/a"))

    def test_sync(self):
        with start_close(self.client) as c:
            c.sync("/")

    def test_transaction(self):
        with start_close(self.client) as c:
            c.ensure_path("/b")
            with c.transaction() as txn:
                txn.create("/b/c")
                txn.set_data("/b/c", b'e')
            data, znode = c.get("/b/c")
            self.assertEqual(b'e', data)
            self.assertTrue(txn.committed)

    def test_data_watch(self):
        updates = collections.deque()
        ev = threading.Event()

        def notify_me(data, stat):
            updates.append((data, stat))
            ev.set()

        with start_close(self.client) as c:
            k_watchers.DataWatch(self.client, "/b", func=notify_me)
            ev.wait()
            ev.clear()
            c.ensure_path("/b")
            ev.wait()
            ev.clear()
            c.set("/b", b"1")
            ev.wait()
            ev.clear()
            c.set("/b", b"2")
            ev.wait()
            ev.clear()

        self.assertEqual(4, len(updates))

        ev.clear()
        with start_close(self.client) as c:
            c.delete("/b")
            ev.wait()

        self.assertEqual(5, len(updates))

    def test_recursive_delete(self):
        with start_close(self.client) as c:
            c.ensure_path("/b/c/d/e")
            c.ensure_path("/b/e/f/g")
            c.ensure_path("/b/123/abc")
            c.ensure_path("/a")
            c.delete("/b", recursive=True)
            self.assertTrue(c.get("/a"))
            self.assertEqual(2, len(c.storage.paths))

    def test_child_left_delete(self):
        with start_close(self.client) as c:
            c.ensure_path("/b/c/d/e")
            self.assertRaises(k_exceptions.NotEmptyError, c.delete,
                              "/b", recursive=False)

    def test_child_watch(self):
        updates = collections.deque()
        ev = threading.Event()

        def one_time_collector_func(children):
            updates.extend(children)
            if children:
                ev.set()
                return False

        with start_close(self.client) as c:
            k_watchers.ChildrenWatch(self.client, "/",
                                     func=one_time_collector_func)
            c.ensure_path("/b")
            ev.wait()

        self.assertEqual(['b'], list(updates))

    def test_child_child_watch(self):
        updates = collections.deque()
        ev = threading.Event()

        def one_time_collector_func(children):
            updates.extend(children)
            if children:
                ev.set()
                return False

        with start_close(self.client) as c:
            k_watchers.ChildrenWatch(self.client, "/b",
                                     func=one_time_collector_func)
            c.ensure_path("/b/c")
            ev.wait()

        self.assertEqual(['c'], list(updates))

    def test_create_async(self):
        with start_close(self.client) as c:
            r = c.create_async("/b")
            self.assertEqual("/b", r.get())
            self.assertTrue(r.successful())
            self.assertIsNone(r.exception)

    def test_create_async_linked(self):
        traces = collections.deque()
        ev = threading.Event()

        def add_trace(result):
            traces.append(result)
            ev.set()

        with start_close(self.client) as c:
            r = c.create_async("/b")
            r.rawlink(add_trace)
            self.assertEqual("/b", r.get())
            ev.wait()

        self.assertEqual(1, len(traces))
        self.assertEqual(r, traces[0])

    def test_create_async_exception(self):
        ev = threading.Event()

        def wait_for(result):
            ev.set()

        with start_close(self.client) as c:
            r = c.create_async("/b/c/d")
            r.rawlink(wait_for)
            ev.wait()
            self.assertFalse(r.successful())
            self.assertIsNotNone(r.exception)
