''' Simple EVE Static Data Export SQLite database wrapper '''
import json
import sqlite3


class SDEError(Exception):
    ''' StaticDataExport exception '''
    pass


class StaticDataExport(object):
    '''
    Simple EVE Static Datat Export SQLite database wrapper

    Initialize
        >> sde = StaticDataExport('/path/to/sde.sqlite')
    Connect to DB and load tables (no-op if already done)
        >> sde()
    Show list of tables (if loaded)
        >> repr(sde)
    Select a table by its name (returns SDETable instance)
        >> sde().invTypes
    Get all rows from table (None if 0, SDERow instance if 1,
    list of SDERow instances otherwise). Also loads table columns.
        >> sde().invTypes()
    Get only rows with matching attributes
        >> sde().invTypes(typeName='Tritanium', typeID=34)
    Get value of row[column]
        >> sde().invTypes(typeID=34).typeName
    Show table info (name, columns) -- must be loaded first
        >> repr(sde().invTypes)
    '''
    def __init__(self, dbpath):
        ''' Open an SDE SQLite dump file '''
        self._conn = sqlite3.connect(dbpath)
        self._cur = None
        self._tables = None

    def __call__(self):
        ''' Connect to DB and load list of tables '''
        if not self._tables:
            self._conn.text_factory = str
            self._cur = self._conn.cursor()
            tables = self._cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")
            self._tables = [SDETable(self._conn, table[0])
                            for table in tables]
        return self

    def __getattr__(self, tablename):
        ''' Select a table from DB '''
        if not self._tables:
            raise SDEError('Database schema not loaded!')

        matches = [getattr(tbl, '_name') == tablename
                   for tbl in self._tables]
        try:
            index = matches.index(True)
            return self._tables[index]
        except IndexError:
            raise SDEError('Table `%s` does not exist' % tablename)

    def __repr__(self):
        ''' String representation of loaded DB state '''
        if self._tables:
            return str([table for table in self._tables])
        return 'DB not loaded.'


class SDETable(object):
    ''' Stores SDE table data '''
    def __init__(self, dbConn, tableName):
        ''' (internal use only) '''
        self._conn = dbConn
        self._name = tableName
        self._cur = self._conn.cursor()
        self._cols = None

    def __repr__(self):
        ''' String representation of loaded table state '''
        return json.dumps(
            {"name": self._name,
             "columns": [c for c in self._cols] if self._cols else None}
        )

    def __call__(self, **kwargs):
        '''
        Load table columns if not already done and select either:
            * all rows in table (no kwargs supplied)
            * only rows matching kwargs filter(s)

        Return type if one of:
            * None if query returned zero rows
            * instance of SDERow if only a single row was returned
            * list of SDERow instances otherwise
        '''
        if not self._cols:
            cols = self._cur.execute("PRAGMA table_info(%s)"
                                            % (self._name,))
            self._cols = [col[1] for col in cols]

        query = "SELECT * FROM %s" % (self._name,)
        params = tuple()

        first = True
        for column, value in kwargs.items():
            if column not in self._cols:
                raise SDEError('Non-existent column name: %s' % column)

            if first:
                query += " WHERE"
            else:
                query += " AND"

            query += " %s=?" % (column,)
            params += (value,)

        self._cur.execute(query, params)
        res = self._cur.fetchall()

        if not res:
            return None
        elif len(res) == 1:
            return SDERow(self._cols, res[0])
        else:
            return [SDERow(self._cols, row) for row in res]


class SDERow(object):
    ''' Stores SDE row data '''
    def __init__(self, cols, row):
        ''' (internal use only) '''
        self._data = dict(zip(cols, row))

    def __repr__(self):
        ''' String representation of row '''
        return json.dumps(self._data)

    def __getattr__(self, col):
        ''' Returns column value of row '''
        if col not in self._data:
            raise SDEError('Non-existent column: %s' % col)
        return self._data[col]


__all__ = ['SDEError', 'StaticDataExport']
