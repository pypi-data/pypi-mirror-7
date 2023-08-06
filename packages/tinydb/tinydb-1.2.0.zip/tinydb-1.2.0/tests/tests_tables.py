from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

from nose.tools import *

#: :type: TinyDB
db = None


def setup():
    global db
    db = TinyDB(storage=MemoryStorage)


def test_one_table():
    db.purge_tables()

    table1 = db.table('table1')

    table1.insert({'int': 1, 'char': 'a'})
    table1.insert({'int': 1, 'char': 'b'})
    table1.insert({'int': 1, 'char': 'c'})

    assert_equal(table1.get(where('int') == 1)['char'], 'a')
    assert_equal(table1.get(where('char') == 'b')['char'], 'b')


def test_multiple_tables():
    db.purge_tables()

    table1 = db.table('table1')
    table2 = db.table('table2')
    table3 = db.table('table3')

    table1.insert({'int': 1, 'char': 'a'})
    table2.insert({'int': 1, 'char': 'b'})
    table3.insert({'int': 1, 'char': 'c'})

    assert_equal(len(table1.search(where('int') == 1)), 1)
    assert_equal(len(table2.search(where('int') == 1)), 1)
    assert_equal(len(table3.search(where('int') == 1)), 1)


def test_caching():
    db.purge_tables()

    table1 = db.table('table1')
    table2 = db.table('table1')

    table1.insert({'int': 1, 'char': 'a'})
    table2.insert({'int': 1, 'char': 'b'})

    assert_equal(len(table1.search(where('int') == 1)), 2)
    assert_equal(len(table2.search(where('int') == 1)), 2)
