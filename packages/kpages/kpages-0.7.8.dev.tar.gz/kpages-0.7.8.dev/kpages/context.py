# -*- coding:utf-8 -*-
"""
    author comger@gmail.com
    logic context for db, cache
    db is mongodb,cache is redis
"""
import os
import time
import asyncmongo
import tornado.gen as gen

from threading import local
from hashlib import sha1

from gridfs import GridFS
from redis import Redis, ConnectionPool
from pymongo import Connection, MongoClient
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
try:
    import motor
except:
    print 'can not import motor '

session_id = lambda: sha1('%s%s' % (os.urandom(16), time.time())).hexdigest()


class ContextHandler(object):
    """
    base handler for session
    """
    def _execute(self, transforms, *args, **kwargs):
        ''' select base handler for self '''
        with LogicContext():
            if isinstance(self, WebSocketHandler):
                WebSocketHandler._execute(self, transforms, *args, **kwargs)
            elif isinstance(self, RequestHandler):
                RequestHandler._execute(self, transforms, *args, **kwargs)

    def session(self, key, val=None):
        ''' session for handler '''
        _id = self.get_secure_cookie('session_id', None)
        if not _id:
            _id = session_id()
            self.set_secure_cookie('session_id', _id)
        if __conf__.REDIS_SESSION:
            return get_context().redis_session(_id, key, val)
        else:
            return get_context().session(_id, key, val)


class LogicContext(object):
    """
        logic context for mongodb and redis cache
    """
    _thread_local = local()

    def __init__(self, redis_host=None, mongo_host=None):
        self._redis_host = redis_host or __conf__.CACHE_HOST
        self._mongo_host = mongo_host or __conf__.DB_HOST
        self._db_conn = None
        self._sync_db = None
        self._motor_clt = None
        self._session = None

    def __enter__(self):
        if not hasattr(self._thread_local, "contexts"):
            self._thread_local.contexts = []
        self._thread_local.contexts.append(self)
        return self

    def __exit__(self, exc_type, exc_value, trackback):
        if self._session:
            self._session.update(dict(
                _id=self._session_id), {'$set': {'data': self._session_val}})

        self._thread_local.contexts.remove(self)
        if self._db_conn:
            self._db_conn.disconnect()

    def get_redis(self):
        ''' get redis from context '''
        host = self._redis_host
        h, p = host.split(":") if ":" in host else (host, 6379)
        cache = Redis(
            host=h, port=int(p), socket_timeout=__conf__.SOCK_TIMEOUT)
        return cache

    def get_gfs(self, name=None):
        ''' get gfs from context '''
        name = name or __conf__.GFS_NAME
        return GridFS(self.get_mongo(name))

    def get_mongo(self, name=None):
        '''
        get temp  mongodb by connection
        '''
        name = name or __conf__.DB_NAME
        if not self._db_conn:
            self._db_conn = Connection(host=__conf__.DB_HOST,
                                       network_timeout=__conf__.SOCK_TIMEOUT)

        return self._db_conn[name]
    

    def get_asyncmongo(self, name=None):
        name = name or __conf__.DB_NAME
        if not hasattr(self,'_async_db'):
            self._async_db = asyncmongo.Client(pool_id='kpages_db', host=__conf__.DB_HOST, port=27017,dbname=name)

        return self._async_db

    def get_async_mongo(self, name=None):
        """ get motor client"""
        name = name or __conf__.DB_NAME
        if not self._sync_db:
            self._sync_db = motor.MotorClient(
                host=__conf__.DB_HOST).open_sync()[name]

        return self._sync_db

    @gen.coroutine
    def get_motor(self, name=None):
        ''' yield  motor client '''
        name = name or __conf__.DB_NAME
        if not self._motor_clt:
            result, err = (yield gen.Task(
                motor.MotorClient(host=self._mongo_host).open, )).args
            if err:
                raise err
            self._motor_clt = result

        raise gen.Return(self._motor_clt[name])

    def session(self, _id, key, val=None, expire=None):
        ''' mongodb session for tornado'''
        if not self._session:
            self._session = self.get_mongoclient('session')['session']
            self._session_val = (
                self._session.find_one(dict(_id=_id)) or {}).get('data', {})
            self._session_id = _id

        if not val:
            return self._session_val.get(key)
        if not self._session_val:
            self._session.insert(dict(_id = _id, data = dict(key = val)))

        self._session_val[key] = val

    def redis_session(self, _id, key, val=None):
        '''
        redis session for tornado
        '''
        return self.get_redis().hget(_id, key) if val else self.get_redis().hset(_id, key, val)

    @classmethod
    def get_context(cls):
        return hasattr(cls._thread_local, "contexts") and cls._thread_local.contexts and \
            cls._thread_local.contexts[-1] or cls()

    @classmethod 
    def get_mongoclient(cls, name=None):
        """
        get mongoclient in application
        """
        name = name or __conf__.DB_NAME
        if not hasattr(cls,'__mongoclient__'):
            cls.__mongoclient__ = MongoClient(host = __conf__.DB_HOST,
                socketTimeoutMS = __conf__.SOCK_TIMEOUT_MS)
        
        return cls.__mongoclient__[name]
    
    @classmethod
    def get_redisclient(cls):
        """
        get redis clinet in application 
        """
        if not hasattr(cls,'__redisclient__'):
            host = __conf__.CACHE_HOST
            h, p = host.split(":") if ":" in host else (host, 6379)
            cp = ConnectionPool(host=h, port=int(p), socket_timeout=__conf__.SOCK_TIMEOUT)
            cls.__redisclient__ = Redis(connection_pool=cp)
        
        return cls.__redisclient__

    @classmethod
    def get_replicaset(cls, hosts=None, replicaSet=None):
        hosts = hosts or __conf__.ReplicaSetHost
        replicaSet = replicaSet or __conf__.replicaSet

        if not hasattr(cls, '__replicaset__'):
            cls.__replicaset__ = MongoReplicaSetClient(hosts, replicaSet=relicaSet)
            
        return cls.__replicaset__

get_context = LogicContext.get_context

__all__ = ["ContextHandler", "LogicContext", "get_context"]
