import asyncio
from aiopg import connect, sa, Cursor

import unittest

from sqlalchemy import MetaData, Table, Column, Integer, String

meta = MetaData()
tbl = Table('sa_tbl', meta,
            Column('id', Integer, nullable=False,
                   primary_key=True),
            Column('name', String(255)))


class TestSAConnection(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    @asyncio.coroutine
    def connect(self, **kwargs):
        conn = yield from connect(database='aiopg',
                                  user='aiopg',
                                  password='passwd',
                                  host='127.0.0.1',
                                  loop=self.loop,
                                  **kwargs)
        cur = yield from conn.cursor()
        yield from cur.execute("DROP TABLE IF EXISTS sa_tbl")
        yield from cur.execute("CREATE TABLE sa_tbl "
                               "(id serial, name varchar(255))")
        yield from cur.execute("INSERT INTO sa_tbl (name)"
                               "VALUES ('first')")
        cur.close()
        return sa.SAConnection(conn, sa.dialect)

    def test_execute_text_select(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute("SELECT * FROM sa_tbl;")
            self.assertIsInstance(res.cursor, Cursor)
            self.assertEqual(('id', 'name'), res.keys())
            rows = [r for r in res]
            self.assertTrue(res.closed)
            self.assertIsNone(res.cursor)
            self.assertEqual(1, len(rows))
            row = rows[0]
            self.assertEqual(1, row[0])
            self.assertEqual(1, row['id'])
            self.assertEqual(1, row.id)
            self.assertEqual('first', row[1])
            self.assertEqual('first', row['name'])
            self.assertEqual('first', row.name)

        self.loop.run_until_complete(go())

    def test_execute_sa_select(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.select())
            self.assertIsInstance(res.cursor, Cursor)
            self.assertEqual(('id', 'name'), res.keys())
            rows = [r for r in res]
            self.assertTrue(res.closed)
            self.assertIsNone(res.cursor)
            self.assertTrue(res.returns_rows)

            self.assertEqual(1, len(rows))
            row = rows[0]
            self.assertEqual(1, row[0])
            self.assertEqual(1, row['id'])
            self.assertEqual(1, row.id)
            self.assertEqual('first', row[1])
            self.assertEqual('first', row['name'])
            self.assertEqual('first', row.name)

        self.loop.run_until_complete(go())

    def test_scalar(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.scalar(tbl.count())
            self.assertEqual(1, res)

        self.loop.run_until_complete(go())

    def test_scalar_None(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.delete())
            res = yield from conn.scalar(tbl.select())
            self.assertIsNone(res)

        self.loop.run_until_complete(go())

    def test_row_proxy(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.select())
            rows = [r for r in res]
            row = rows[0]
            row2 = yield from (yield from conn.execute(tbl.select())).first()
            self.assertEqual(2, len(row))
            self.assertEqual(['id', 'name'], list(row))
            self.assertIn('id', row)
            self.assertNotIn('unknown', row)
            self.assertEqual('first', row.name)
            self.assertEqual('first', row[tbl.c.name])
            with self.assertRaises(AttributeError):
                row.unknown
            self.assertEqual("(1, 'first')", repr(row))
            self.assertEqual((1, 'first'), row.as_tuple())
            self.assertNotEqual((555, 'other'), row.as_tuple())
            self.assertEqual(row2, row)
            self.assertFalse(row2 != row)
            self.assertNotEqual(5, row)

        self.loop.run_until_complete(go())

    def test_insert(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.insert().values(name='second'))
            self.assertEqual(('id',), res.keys())
            self.assertEqual(1, res.rowcount)
            self.assertTrue(res.returns_rows)

            rows = [r for r in res]
            self.assertEqual(1, len(rows))
            self.assertEqual(2, rows[0].id)

        self.loop.run_until_complete(go())

    def test_delete(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.delete().where(tbl.c.id == 1))
            self.assertEqual((), res.keys())
            self.assertEqual(1, res.rowcount)
            self.assertFalse(res.returns_rows)
            self.assertTrue(res.closed)
            self.assertIsNone(res.cursor)

        self.loop.run_until_complete(go())

    def test_double_close(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute("SELECT 1")
            res.close()
            self.assertTrue(res.closed)
            self.assertIsNone(res.cursor)
            res.close()
            self.assertTrue(res.closed)
            self.assertIsNone(res.cursor)

        self.loop.run_until_complete(go())

    def test_weakrefs(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            self.assertEqual(0, len(conn._weak_results))
            res = yield from conn.execute("SELECT 1")
            self.assertEqual(1, len(conn._weak_results))
            cur = res.cursor
            self.assertFalse(cur.closed)
            del res
            self.assertTrue(cur.closed)
            self.assertEqual(0, len(conn._weak_results))

        self.loop.run_until_complete(go())

    def test_fetchall(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            rows = yield from res.fetchall()
            self.assertEqual(2, len(rows))
            self.assertTrue(res.closed)
            self.assertTrue(res.returns_rows)
            self.assertEqual([(1, 'first'), (2, 'second')], rows)

        self.loop.run_until_complete(go())

    def test_fetchall_closed(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            res.close()
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchall()

        self.loop.run_until_complete(go())

    def test_fetchall_not_returns_rows(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.delete())
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchall()

        self.loop.run_until_complete(go())

    def test_fetchone_closed(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            res.close()
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchone()

        self.loop.run_until_complete(go())

    def test_first_not_returns_rows(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.delete())
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.first()

        self.loop.run_until_complete(go())

    def test_fetchmany(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            rows = yield from res.fetchmany()
            self.assertEqual(1, len(rows))
            self.assertFalse(res.closed)
            self.assertTrue(res.returns_rows)
            self.assertEqual([(1, 'first')], rows)

        self.loop.run_until_complete(go())

    def test_fetchmany_with_size(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            rows = yield from res.fetchmany(100)
            self.assertEqual(2, len(rows))
            self.assertFalse(res.closed)
            self.assertTrue(res.returns_rows)
            self.assertEqual([(1, 'first'), (2, 'second')], rows)

        self.loop.run_until_complete(go())

    def test_fetchmany_closed(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            res.close()
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchmany()

        self.loop.run_until_complete(go())

    def test_fetchmany_with_size_closed(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            yield from conn.execute(tbl.insert().values(name='second'))

            res = yield from conn.execute(tbl.select())
            res.close()
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchmany(5555)

        self.loop.run_until_complete(go())

    def test_fetchmany_not_returns_rows(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()
            res = yield from conn.execute(tbl.delete())
            with self.assertRaises(sa.ResourceClosedError):
                yield from res.fetchmany()

        self.loop.run_until_complete(go())

    def test_fetchmany_close_after_last_read(self):
        @asyncio.coroutine
        def go():
            conn = yield from self.connect()

            res = yield from conn.execute(tbl.select())
            rows = yield from res.fetchmany()
            self.assertEqual(1, len(rows))
            self.assertFalse(res.closed)
            self.assertTrue(res.returns_rows)
            self.assertEqual([(1, 'first')], rows)
            rows2 = yield from res.fetchmany()
            self.assertEqual(0, len(rows2))
            self.assertTrue(res.closed)

        self.loop.run_until_complete(go())
