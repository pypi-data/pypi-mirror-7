TOREDIS
=======

This is minimalistic, but feature rich redis client for Tornado built on top of `hiredis <https://github.com/pietern/hiredis-py>`_ protocol parser.

Supports all redis commands, which are auto-generated from the redis `JSON documentation file <https://github.com/antirez/redis-doc/blob/master/commands.json>`_.

Key design points:

1. While toredis attempts to add some syntactical sugar to the API, all responses are returned "as is". For example, if command returns
   list of items and developer requested only one key, list with one entry will be returned. For example::

    def handle(self, result):
        print(len(result))

    conn.hkeys('test1', handle)


2. Most redis commands accept one or more keys. Toredis adds a bit of logic to handle single key or array of keys. Due to python
   limitations, it is not possible to use ``*args`` with named ``callback`` argument, so you will have to pass array of key names::

    # This will work
    conn.blpop('test', callback=callback)
    conn.blpop(['test', 'test2'], callback=callback)

    # This won't work
    conn.blpop('test', 'test2', callback=callback)


3. If redis connection will be dropped while waiting for response, callback will be triggered with `None` as a value.

4. Toredis does not provide reconnection feature, but you can override :meth:`~toredis.Client.on_disconnect` method and implement your reconnection logic.

You can find command `documentation here <https://github.com/mrjoes/toredis/blob/master/toredis/commands.py>`_ (will be moved to rtd later).

Pipelining is also supported::

    # For more than one pipeline for connection create it with Pipeline(conn)
    pipeline = conn.pipeline()
    pipeline.set('foo', 'bar')
    pipeline.get('foo')
    pipeline.send(callback=callback)

For more examples please refer to tests.
More on `redis pipelining <http://redis.io/topics/pipelining>`_.

Things missing:

* Backport pure-python redis protocol parser (for PyPy support)
* Connection pools
