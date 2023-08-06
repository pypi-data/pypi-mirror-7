# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2013 Yahoo! Inc. All Rights Reserved.
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

import contextlib
import os
import sys

import six

from zake import utils

from kazoo import exceptions as k_exceptions
from kazoo.protocol import states as k_states


# See: https://issues.apache.org/jira/browse/ZOOKEEPER-243
SEQ_ROLLOVER = 2147483647
SEQ_ROLLOVER_TO = -2147483647


def _split_path(path):
    return os.path.split(path)


class FakeStorage(object):
    """A place too place fake zookeeper paths + data."""

    def __init__(self, lock, paths=None, sequences=None):
        if paths:
            self._paths = dict(paths)
        else:
            self._paths = {}
        if sequences:
            self._sequences = sequences
        else:
            self._sequences = {}
        self.lock = lock
        # Ensure the root path *always* exists.
        if "/" not in self._paths:
            self._paths["/"] = {
                'created_on': 0,
                'updated_on': 0,
                'version': 0,
                # Not supported for now...
                'aversion': -1,
                'cversion': -1,
                'data': b"",
                'ephemeral': False,
            }

    def _make_znode(self, node, child_count):
        # Not exactly right, but good enough...
        translated = {
            'czxid': node['version'],
            'mzxid': node['version'],
            'pzxid': node['version'],
            'ctime': node['created_on'],
            'mtime': node['updated_on'],
            'version': node['version'],
            'aversion': node['aversion'],
            'cversion': node['cversion'],
            'dataLength': len(node['data']),
            'numChildren': int(child_count),
        }
        if node['ephemeral']:
            translated['ephemeralOwner'] = node['ephemeral_owner']
        else:
            translated['ephemeralOwner'] = 0
        return k_states.ZnodeStat(**translated)

    @property
    def paths(self):
        with self.lock:
            return dict(self._paths)

    @property
    def sequences(self):
        with self.lock:
            return dict(self._sequences)

    def __getitem__(self, path):
        with self.lock:
            return self._paths[path]

    def __setitem__(self, path, value):
        with self.lock:
            self._paths[path] = value

    def set(self, path, value, version=-1):
        with self.lock:
            if version != -1:
                stat = self.get(path)[1]
                if stat.version != version:
                    raise k_exceptions.BadVersionError("Version mismatch %s "
                                                       "!= %s" % (stat.version,
                                                                  version))
            else:
                self._paths[path]['data'] = value
                self._paths[path]['updated_on'] = utils.millitime()
                self._paths[path]['version'] += 1
            return self.get(path)[1]

    def purge(self, session_id):
        if not session_id:
            return 0
        with self.lock:
            removals = []
            for path, data in six.iteritems(self._paths):
                if data['ephemeral'] and data['ephemeral_owner'] == session_id:
                    removals.append(path)
            for path in removals:
                del self._paths[path]
            return len(removals)

    def create(self, path, value=b"", sequence=False,
               ephemeral=False, session_id=None):
        parent_path, _node_name = _split_path(path)
        with self.lock:
            if sequence:
                sequence_id = self._sequences.get(parent_path, 0)
                if sequence_id == SEQ_ROLLOVER:
                    self._sequences[parent_path] = SEQ_ROLLOVER_TO
                else:
                    self._sequences[parent_path] = sequence_id + 1
                path = path + '%010d' % (sequence_id)
            parents = sorted(six.iterkeys(self.get_parents(path)))
            if ephemeral and not session_id:
                raise k_exceptions.SystemZookeeperError("Ephemeral node %s can"
                                                        " not be created"
                                                        " without a session"
                                                        " id" % path)
            if parent_path not in self:
                raise k_exceptions.NoNodeError("Parent node %s does not exist"
                                               % (parent_path))
            if path in self:
                raise k_exceptions.NodeExistsError("Node %s already"
                                                   " exists" % (path))
            for parent_path in reversed(parents):
                if self._paths[parent_path]['ephemeral']:
                    raise k_exceptions.NoChildrenForEphemeralsError(
                        "Parent %s is ephemeral" % parent_path)
            path_data = {
                # Kazoo clients expect in milliseconds
                'created_on': utils.millitime(),
                'updated_on': utils.millitime(),
                'version': 0,
                # Not supported for now...
                'aversion': -1,
                'cversion': -1,
                'data': value,
            }
            if ephemeral:
                path_data['ephemeral_owner'] = session_id
                path_data['ephemeral'] = True
            else:
                path_data['ephemeral'] = False
            self._paths[path] = path_data
            return (True, parents, path)

    def pop(self, path):
        with self.lock:
            if path == "/":
                raise k_exceptions.BadArgumentsError("Can not delete '/'")
            self._paths.pop(path)

    def get(self, path):
        with self.lock:
            node = self._paths[path]
            children_count = len(self.get_children(path))
            return (node['data'], self._make_znode(node, children_count))

    def __contains__(self, path):
        with self.lock:
            return path in self._paths

    @contextlib.contextmanager
    def transaction(self):
        with self.lock:
            # Keep the before the transaction information and reset to that
            # data if the context manager fails (this makes it appear that the
            # operations done during the transaction either complete as a
            # group or do not complete).
            paths = self.paths
            sequences = self.sequences
            try:
                yield
            except Exception:
                cause = sys.exc_info()
                try:
                    self._paths = paths
                    self._sequences = sequences
                finally:
                    six.reraise(*cause)

    def get_children(self, path, only_direct=True):
        paths = {}
        with self.lock:
            for (k, v) in list(six.iteritems(self._paths)):
                if utils.is_child_path(path, k, only_direct=only_direct):
                    paths[k] = v
        return paths

    def get_parents(self, path):
        paths = {}
        with self.lock:
            for (k, v) in list(six.iteritems(self._paths)):
                if utils.is_child_path(k, path, only_direct=False):
                    paths[k] = v
        return paths
