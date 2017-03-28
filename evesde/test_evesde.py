# pylint: skip-file
import pytest

from .evesde import SDEError, StaticDataExport


@pytest.fixture
def sde():
    sde = StaticDataExport(':memory:')
    cur = sde._conn.cursor()
    cur.execute("""
        CREATE TABLE "invTypes" (
          "typeID" integer NOT NULL,
          "groupID" integer DEFAULT NULL,
          "typeName" varchar(100) DEFAULT NULL,
          "description" varchar(3000) DEFAULT NULL,
          "mass" double DEFAULT NULL,
          "volume" double DEFAULT NULL,
          "capacity" double DEFAULT NULL,
          "portionSize" integer DEFAULT NULL,
          "raceID" integer  DEFAULT NULL,
          "basePrice" decimal(19,4) DEFAULT NULL,
          "published" integer DEFAULT NULL,
          "marketGroupID" integer DEFAULT NULL,
          "chanceOfDuplicating" double DEFAULT NULL,
          PRIMARY KEY ("typeID")
        )""")
    cur.close()
    sde._conn.commit()
    cur = sde._conn.cursor()

    cur.execute('SELECT * FROM invTypes')
    assert cur.fetchall() == []

    items = [(0, 1, 'item0', 'foo', 0,   0,   0,   4, None, 7, 10, 13, 0),
             (1, 2, 'item1', 'bar', 0.1, 0.2, 0.3, 5, None, 8, 11, 14, 0.4),
             (2, 3, 'item2', 'baz', 1,   2,   3,   6, None, 9, 12, 15, 4)]

    for item in items:
        cur.execute('INSERT INTO invTypes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    item)

    cur.close()
    sde._conn.commit()
    return sde


def test_nonloadedrepr(sde):
    assert repr(sde) == 'DB not loaded.'


def test_nonloadedaccess(sde):
    with pytest.raises(SDEError):
        sde.invTypes()


def test_tableload(sde):
    sde()


def test_norows(sde):
    assert type(sde().invTypes(typeID=3)) == type(None)


def test_singlerow(sde):
    assert type(sde().invTypes(typeID=1)).__name__ == 'SDERow'


def test_multiplerows(sde):
    assert type(sde().invTypes()) == list
    assert len(sde().invTypes()) == 3


def test_loadedrepr(sde):
    assert repr(sde()) != 'DB not loaded.'


def test_singlerowattr(sde):
    assert type(sde().invTypes(typeID=1).typeName) == str
    assert sde().invTypes(typeID=1).typeName == 'item1'


def test_nxrowattr(sde):
    with pytest.raises(SDEError):
        sde().invTypes(typeID=2).nonExistentCol
