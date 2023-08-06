# What is MongoTor ?

(MONGOdb + TORnado) is an asynchronous toolkit for working with ``mongodb`` inside a ``tornado`` app. Mongotor has a pure implementation of python + tornado and only depends on tornado and bson (provided by pymongo)

[![Build Status](https://travis-ci.org/marcelnicolay/mongotor.svg?branch=master)](https://travis-ci.org/marcelnicolay/mongotor)

## Features

MongoTor is still an alpha project, but already implements the following features:

* Support for ``replica sets``
* Automatic ``reconnection``
* Connection ``pooling``
* Support for running database commands (``count``, ``sum``, ``mapreduce`` etc...)
* ``ORM`` like to map documents and fields
* ``Signals`` for pre_save, post_save, pre_remove, post_remove, pre_update and post_update
* 100% of code coverage by test

The next steps are provide support to:

* sharding
* authentication
* nearest preference in replica sets
* gridfs
* all python versions (2.5, 2.6, 2.7, 3.2 and PyPy), only python 2.7 is tested now

## Documentation

Visit our online [documentation](http://mongotor.readthedocs.org/) for more examples

## Why not pymongo ?

[PyMongo](http://api.mongodb.org/python/current/) is a recommended way to work with MongoDB in python, but isn't asynchronous and not run inside de tornado's ioloop. If you use pymongo you won't take the advantages of tornado.

## Why not motor ?

[Motor](http://emptysquare.net/motor/) wraps PyMongo and makes it async with greenlet. Is a great project, but it uses greenlet. If you can use greenlets why not use gevent instead of tornado? PyMongo already works with gevent and you dont need to thinking about write all of your code with callbacks. My point is, if you are using a very powerfull non-blocking web server with a pure python code, you'll probably want to work with a pure tornado driver for accessing mongo, obviously since this module has a full support to mongodb features like pymongo.

## Why not asyncmongo ?

[AsyncMongo](https://github.com/bitly/asyncmongo) is an asynchronous library for accessing mongodb with tornado.ioloop, but don't implement replica set and other mongodb features.

Besides, this project is not walking very well, or better, very fast. Exist a lot of issues and pull requests that aren't looked.

I am very thankful to asyncmongo, i worked with it in some projects and it's been served as inspiration, but now, I am very excited to write my own library, more flexible, fast, secure and that will walking faster.


## Installing

```bash
pip install mongotor
```

## Simple usage

```python
import tornado.web
from tornado import gen
from mongotor.database import Database
from bson import ObjectId

class Handler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = Database.init('localhost:27017', 'mongotor_test')

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        user = {'_id': ObjectId(), 'name': 'User Name'}
        yield gen.Task(self.db.user.insert, user)
        
        yield gen.Task(self.db.user.update, user['_id'], {"$set": {'name': 'New User Name'}})

        user_found = yield gen.Task(self.db.user.find_one, user['_id'])
        assert user_found['name'] == 'New User Name'

        yield gen.Task(self.db.user.remove, user['_id'])
```

## Support to ReplicaSet

```python
import tornado.web
from tornado import gen
from mongotor.database import Database
from mongotor.node import ReadPreference
from bson import ObjectId
import time


class Handler(tornado.web.RequestHandler):

    def initialize(self):
        # configuring an replica set
        self.db = db = Database.init(["localhost:27027", "localhost:27028"], dbname='mongotor_test',
            read_preference=ReadPreference.SECONDARY_PREFERRED)

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        user = {'_id': ObjectId()}
        
        # write on primary
        yield gen.Task(self.db.user.insert, user)
        
        # wait for replication
        time.sleep(2)

        # read from secondary
        user_found = yield gen.Task(self.db.user.find_one, user['_id'])
        assert user_found == user
```

## Using ORM

```python
from mongotor.orm import collection, field
from mongotor.database import Database

from datetime import datetime
import tornado.web
from tornado import gen

# A connection to the MongoDB database needs to be
# established before perform operations
Database.init(['localhost:27017','localhost:27018'], 'mongotor_test')

class User(collection.Collection):
    __collection__ = "user"

    _id = field.ObjectIdField()
    name = field.StringField()
    active = field.BooleanField()
    created = field.DateTimeField()

class Handler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        user = User()
        user.name = "User name"
        user.active = True
        user.created = datetime.now()

        yield gen.Task(user.save)

        # update date
        user.name = "New name"
        yield gen.Task(user.update)

        # find one object
        user_found = yield gen.Task(User.objects.find_one, user._id)

        # find many objects
        new_user = User()
        new_user.name = "new user name"
        new_user.user.active = True
        new_user.created = datetime.now()

        users_actives = yield gen.Task(User.objects.find, {'active': True})

        users_actives[0].active = False
        yield gen.Task(users_actives[0].save)

        # remove object
        yield gen.Task(user_found.remove)
```

## Contributing

Write tests for your new feature and send a pull request.

For run mongotor tests install mongodb and do:

```bash
# create a new virtualenv
mkvirtualenv mongotor

# install dev requirements
pip install -r requirements-dev.txt

# start mongo
make mongo-start

# configure replicaset
make mongo-config

# run tests
make test
```

## Issues

Please report any issues via [github issues](https://github.com/marcelnicolay/mongotor/issues)
