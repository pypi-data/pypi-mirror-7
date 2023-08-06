aiopg
=======

**aiopg** is a library for accessing a PostgreSQL_ database
from the asyncio_ (PEP-3156/tulip) framework. It wraps
asynchronous features of the Psycopg database driver.

Example
-------

::

   import asyncio
   from aiopg.pool import create_pool

   dsn = 'dbname=jetty user=nick password=1234 host=localhost port=5432'


   @asyncio.coroutine
   def test_select():
       pool = yield from create_pool(dsn)

       with (yield from pool) as conn:
           cur = yield from conn.cursor()
           yield from cur.execute('SELECT 1')
           ret = yield from cur.fetchone()
           assert ret == (1,), ret


   asyncio.get_event_loop().run_until_complete(test_select())


Example of SQLAlchemy optional integration
-------------------------------------------

::

   import asyncio
   from aiopg.sa import create_engine
   import sqlalchemy as sa


   metadata = sa.MetaData()

   tbl = sa.Table('tbl', metadata,
       sa.Column('id', sa.Integer, primary_key=True),
       sa.Column('val', sa.String(255)))


   @asyncio.coroutine
   def go():
       engine = yield from create_engine(user='aiopg',
                                         database='aiopg',
                                         host='127.0.0.1',
                                         password='passwd')

       with (yield from engine) as conn:
           yield from conn.execute(tbl.insert().values(val='abc'))

           res = yield from conn.execute(tbl.select())
           for row in res:
               print(row.id, row.val)


   asyncio.get_event_loop().run_until_complete(go())

.. _PostgreSQL: http://www.postgresql.org/
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html

Please use::

   $ python3 runtests.py

for executing project's unittests

CHANGES
-------

0.3.1 (2014-07-04)
^^^^^^^^^^^^^^^^^^

* Forward arguments to cursor constructor for pooled connections.

0.3.0 (2014-06-22)
^^^^^^^^^^^^^^^^^^

* Allow executing SQLAlchemy DDL statements.

* Fix bug with race conditions on acquiring/releasing connections from pool.

0.2.3 (2014-06-12)
^^^^^^^^^^^^^^^^^^

* Fix bug in connection pool.

0.2.2 (2014-06-07)
^^^^^^^^^^^^^^^^^^

* Fix bug with passing parameters into SAConnection.execute when
  executing raw SQL expression.

0.2.1 (2014-05-08)
^^^^^^^^^^^^^^^^^^

* Close connection with invalid transaction status on returning to pool.

0.2.0 (2014-05-04)
^^^^^^^^^^^^^^^^^^

* Implemented optional support for sqlalchemy functional sql layer.

0.1.0 (2014-04-06)
^^^^^^^^^^^^^^^^^^

* Implemented plain connections: connect, Connection, Cursor.

* Implemented database pools: create_pool and Pool.

