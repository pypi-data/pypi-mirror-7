# coding: utf-8
# <mongotor - An asynchronous driver and toolkit for accessing MongoDB with Tornado>
# Copyright (C) <2012>  Marcel Nicolay <marcel.nicolay@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from bson.son import SON
from tornado import gen
from mongotor.database import Database
from mongotor.client import Client


class Manager(object):

    def __init__(self, collection):
        self.collection = collection

    @gen.engine
    def find_one(self, query, callback):
        client = Client(Database(), self.collection.__collection__)
        result, error = yield gen.Task(client.find_one, query)

        instance = None
        if result:
            instance = self.collection.create(result, cleaned=True)

        callback(instance)

    @gen.engine
    def find(self, query, callback, **kw):
        client = Client(Database(), self.collection.__collection__)
        result, error = yield gen.Task(client.find, query, **kw)

        items = []

        if result:
            for item in result:
                items.append(self.collection.create(item, cleaned=True))

        callback(items)

    def count(self, query=None, callback=None):
        client = Client(Database(), self.collection.__collection__)
        client.find(query).count(callback=callback)

    @gen.engine
    def distinct(self, key, callback, query=None):
        client = Client(Database(), self.collection.__collection__)
        client.find(query).distinct(key, callback=callback)

    @gen.engine
    def geo_near(self, near, max_distance=None, num=None, spherical=None,
        unique_docs=None, query=None, callback=None, **kw):

        command = SON({"geoNear": self.collection.__collection__})

        if near != None:
            command.update({'near': near})

        if query != None:
            command.update({'query': query})

        if num != None:
            command.update({'num': num})

        if max_distance != None:
            command.update({'maxDistance': max_distance})

        if unique_docs != None:
            command.update({'uniqueDocs': unique_docs})

        if spherical != None:
            command.update({'spherical': spherical})

        result, error = yield gen.Task(Database().command, command)
        items = []

        if result and result['ok']:
            for item in result['results']:
                items.append(self.collection.create(item['obj'], cleaned=True))

        callback(items)

    @gen.engine
    def map_reduce(self, map_, reduce_, callback, query=None, out=None):
        command = SON({'mapreduce': self.collection.__collection__})

        command.update({
            'map': map_,
            'reduce': reduce_,
        })

        if query is not None:
            command.update({'query': query})
        if out is None:
            command.update({'out': {'inline': 1}})

        result, error = yield gen.Task(Database().command, command)
        if not result or int(result['ok']) != 1:
            callback(None)
            return

        callback(result['results'])

    @gen.engine
    def truncate(self, callback=None):
        client = Client(Database(), self.collection.__collection__)
        yield gen.Task(client.remove, {})

        if callback:
            callback()
