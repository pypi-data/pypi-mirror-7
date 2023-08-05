# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-database.
#
# logilab-database is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-database is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-database. If not, see <http://www.gnu.org/licenses/>.
"""
unit tests for module logilab.common.db
"""
from __future__ import with_statement

import socket

from logilab.common.testlib import TestCase, unittest_main
from logilab.common.shellutils import getlogin
from logilab.database import *
from logilab.database import _PREFERED_DRIVERS as PREFERED_DRIVERS
from logilab.database.postgres import _PGAdvFuncHelper
from logilab.database.sqlite import _SqliteAdvFuncHelper
from logilab.database import mysql, sqlserver # trigger registration

# from logilab.common.adbh import (_GenericAdvFuncHelper, _SqliteAdvFuncHelper,
#                                  _PGAdvFuncHelper, _MyAdvFuncHelper,
#                                  FunctionDescr, get_adv_func_helper,
#                                  auto_register_function,
#                                  UnsupportedFunction)



class PreferedDriverTC(TestCase):
    def setUp(self):
        self.drivers = {"pg":[('foo', None), ('bar', None)]}
        self.drivers = {'pg' : ["foo", "bar"]}
        self.old_drivers = PREFERED_DRIVERS['postgres'][:]

    def tearDown(self):
        """Reset PREFERED_DRIVERS as it was"""
        PREFERED_DRIVERS['postgres'] = self.old_drivers

    def testNormal(self):
        set_prefered_driver('pg','bar', self.drivers)
        self.assertEqual('bar', self.drivers['pg'][0])

    def testFailuresDb(self):
        with self.assertRaises(UnknownDriver) as cm:
            set_prefered_driver('oracle','bar', self.drivers)
        self.assertEqual(str(cm.exception), 'Unknown driver oracle')

    def testFailuresDriver(self):
        with self.assertRaises(UnknownDriver) as cm:
            set_prefered_driver('pg','baz', self.drivers)
        self.assertEqual(str(cm.exception), 'Unknown module baz for pg')

    def testGlobalVar(self):
        # XXX: Is this test supposed to be useful ? Is it supposed to test
        #      set_prefered_driver ?
        old_drivers = PREFERED_DRIVERS['postgres'][:]
        expected = old_drivers[:]
        expected.insert(0, expected.pop(expected.index('pgdb')))
        set_prefered_driver('postgres', 'pgdb')
        self.assertEqual(PREFERED_DRIVERS['postgres'], expected)
        set_prefered_driver('postgres', 'psycopg')
        # self.assertEqual(PREFERED_DRIVERS['postgres'], old_drivers)
        expected.insert(0, expected.pop(expected.index('psycopg')))
        self.assertEqual(PREFERED_DRIVERS['postgres'], expected)


class GetCnxTC(TestCase):
    def setUp(self):
        try:
            socket.gethostbyname('centaurus')
        except:
            self.skipTest("those tests require specific DB configuration")
        self.host = 'centaurus'
        self.db = 'template1'
        self.user = getlogin()
        self.passwd = getlogin()
        self.old_drivers = PREFERED_DRIVERS['postgres'][:]

    def tearDown(self):
        """Reset PREFERED_DRIVERS as it was"""
        PREFERED_DRIVERS['postgres'] = self.old_drivers

    def testPsyco(self):
        PREFERED_DRIVERS['postgres'] = ['psycopg']
        try:
            cnx = get_connection('postgres',
                                 self.host, self.db, self.user, self.passwd,
                                 quiet=1)
        except ImportError:
            self.skipTest('python-psycopg is not installed')

    def testPgdb(self):
        PREFERED_DRIVERS['postgres'] = ['pgdb']
        try:
            cnx = get_connection('postgres',
                                 self.host, self.db, self.user, self.passwd,
                                 quiet=1)
        except ImportError:
            self.skipTest('python-pgsql is not installed')

    def testPgsql(self):
        PREFERED_DRIVERS['postgres'] = ['pyPgSQL.PgSQL']
        try:
            import pyPgSQL.PgSQL
        except ImportError:
            self.skipTest('python-pygresql is not installed')
        try:
            cnx = get_connection('postgres',
                                 self.host, self.db, self.user, self.passwd,
                                 quiet=1)
        except pyPgSQL.PgSQL.DatabaseError, ex:
            if str(ex).startswith('could not connect to server:'):
                    self.skipTest('pgsql test requires a specific configuration')
            raise

    def testMysql(self):
        PREFERED_DRIVERS['mysql'] = ['MySQLdb']
        try:
            import MySQLdb
        except ImportError:
            self.skipTest('python-mysqldb is not installed')
        try:
            cnx = get_connection('mysql', self.host, database='', user='root',
                                 quiet=1)
        except  MySQLdb.OperationalError, ex:
            if ex.args[0] == 1045: # find MysqlDb
                self.skipTest('mysql test requires a specific configuration')
            elif ex.args[0] != 2003:
                raise

    def test_connection_wrap(self):
        """Tests the connection wrapping"""
        try:
            import psycopg2
        except ImportError:
            self.skipTest('psycopg2 module not installed')
        try:
            cnx = get_connection('postgres',
                                 self.host, self.db, self.user, self.passwd,
                                 quiet=1)
        except psycopg2.OperationalError, ex:
            self.skipTest('pgsql test requires a specific configuration')
        self.failIf(isinstance(cnx, PyConnection),
                    'cnx should *not* be a PyConnection instance')
        cnx = get_connection('postgres',
                             self.host, self.db, self.user, self.passwd,
                             quiet=1, pywrap=True)
        self.failUnless(isinstance(cnx, PyConnection),
                        'cnx should be a PyConnection instance')


    def test_cursor_wrap(self):
        """Tests cursor wrapping"""
        try:
            import psycopg2
        except ImportError:
            self.skipTest('psycopg2 module not installed')
        try:
            cnx = get_connection('postgres',
                                 self.host, self.db, self.user, self.passwd,
                                 quiet=1, pywrap=True)
        except psycopg2.OperationalError, ex:
            self.skipTest('pgsql test requires a specific configuration')
        cursor = cnx.cursor()
        self.failUnless(isinstance(cursor, PyCursor),
                        'cnx should be a PyCursor instance')


class DBAPIAdaptersTC(TestCase):
    """Tests DbApi adapters management"""

    def setUp(self):
        """Memorize original PREFERED_DRIVERS"""
        self.old_drivers = PREFERED_DRIVERS['postgres'][:]

    def tearDown(self):
        """Reset PREFERED_DRIVERS as it was"""
        PREFERED_DRIVERS['postgres'] = self.old_drivers

    def test_raise(self):
        self.assertRaises(UnknownDriver, get_dbapi_compliant_module, 'pougloup')

    def test_pgdb_types(self):
        """Tests that NUMBER really wraps all number types"""
        PREFERED_DRIVERS['postgres'] = ['pgdb']
        try:
            module = get_dbapi_compliant_module('postgres')
        except ImportError:
            self.skipTest('postgresql pgdb module not installed')
        number_types = ('int2', 'int4', 'serial',
                        'int8', 'float4', 'float8',
                        'numeric', 'bool', 'money', 'decimal')
        for num_type in number_types:
            yield self.assertEqual, num_type, module.NUMBER
        yield self.assertNotEqual, 'char', module.NUMBER

    def test_pypgsql_getattr(self):
        """Tests the getattr() delegation for pyPgSQL"""
        PREFERED_DRIVERS['postgres'] = ['pyPgSQL.PgSQL']
        try:
            module = get_dbapi_compliant_module('postgres')
        except ImportError:
            self.skipTest('postgresql dbapi module not installed')
        try:
            binary = module.BINARY
        except AttributeError, err:
            raise
            self.fail(str(err))

    def test_adv_func_helper(self):
        try:
            helper = get_db_helper('postgres')
        except ImportError:
            self.skipTest('postgresql dbapi module not installed')
        self.failUnless(isinstance(helper, _PGAdvFuncHelper))
        try:
            helper = get_db_helper('sqlite')
        except ImportError:
            self.skipTest('sqlite dbapi module not installed')
        self.failUnless(isinstance(helper, _SqliteAdvFuncHelper))


    def test_register_funcdef(self):
        class MYFUNC(FunctionDescr):
            supported_backends = ('postgres', 'sqlite',)
            name_mapping = {'postgres': 'MYFUNC',
                            'mysql': 'MYF',
                            'sqlite': 'SQLITE_MYFUNC'}
        register_function(MYFUNC)

        pghelper = get_db_helper('postgres')
        mshelper = get_db_helper('mysql')
        slhelper = get_db_helper('sqlite')
        self.assertRaises(UnsupportedFunction, mshelper.function_description, 'MYFUNC')
        try:
            pghelper.function_description('MYFUNC')
        except UnsupportedFunction:
            self.fail('MYFUNC should support "postgres"')
        try:
            slhelper.function_description('MYFUNC')
        except UnsupportedFunction:
            self.fail('MYFUNC should support "sqlite"')

    def test_funcname_with_different_backend_names(self):
        class MYFUNC(FunctionDescr):
            supported_backends = ('postgres', 'mysql', 'sqlite')
            name_mapping = {'postgres': 'MYFUNC',
                            'mysql': 'MYF',
                            'sqlite': 'SQLITE_MYFUNC'}
        register_function(MYFUNC)

        pghelper = get_db_helper('postgres')
        mshelper = get_db_helper('mysql')
        slhelper = get_db_helper('sqlite')
        self.assertEqual(slhelper.func_as_sql('MYFUNC', ()), 'SQLITE_MYFUNC()')
        self.assertEqual(pghelper.func_as_sql('MYFUNC', ('foo',)), 'MYFUNC(foo)')
        self.assertEqual(mshelper.func_as_sql('MYFUNC', ('foo', 'bar')), 'MYF(foo, bar)')

class BaseSqlServer(TestCase):
    def tearDown(self):
        cursor = self.cnx.cursor()
        cursor.execute('drop table TestBlob')
        cursor.execute('drop table TestLargeString')
        self.cnx.commit()
        cursor.close()
        self.cnx.close()

    def blob(self):
        cursor = self.cnx.cursor()
        data_length = xrange(400*1024-10, 400*1024+10)
        for length in data_length:
            data = buffer('\x00'*length)
            print "inserting string of length", len(data)
            cursor.execute('insert into TestBlob(id, data) VALUES(%(id)s, %(data)s)',
                           {'id': length, 'data': data})
            self.cnx.commit()
        cursor.execute('select count(*) from TestBlob')
        print '%d rows in table' % (cursor.fetchone()[0])
        cursor.close()

    def large_string(self):
        cursor = self.cnx.cursor()
        data_length = xrange(400*1024-10, 400*1024+10)
        for length in data_length:
            data = '1'*length
            print "inserting string of length", len(data)
            cursor.execute('insert into TestLargeString(id, data) VALUES(%(id)s, %(data)s)',
                           {'id': length, 'data': data})
            self.cnx.commit()
        cursor.execute('select count(*) from TestLargeString')
        print '%d rows in table' % (cursor.fetchone()[0])
        cursor.close()

    def varbinary_none(self):
        cursor = self.cnx.cursor()
        cursor.execute('insert into TestBlob (id) values (42)')
        self.cnx.commit()
        cursor.execute('select * from TestBlob where id=42')
        print cursor.fetchall()
        cursor.execute('update TestBlob set id=43, data=NULL where id=42')
        self.cnx.commit()
        cursor.execute('select * from TestBlob where id=43')
        print cursor.fetchall()
        cursor.execute('update TestBlob set id = %(id)s, data=%(data)s where id=%(old_id)s', {'data': None, 'id': 42, 'old_id': 43})
        self.cnx.commit()
        cursor.execute('select * from TestBlob where id=42')
        print cursor.fetchall()
        cursor.close()


try:
    import pyodbc
except ImportError:
    print "pyodbc tests skipped"
else:
    class pyodbcTC(BaseSqlServer):
        def setUp(self):
            try:
                self.cnx = get_connection(driver='sqlserver2005', database='alf',
                                      host='localhost', extra_args='Trusted_Connection')
            except pyodbc.Error, exc:
                self.skipTest(str(exc))
            cursor = self.cnx.cursor()
            try:
                cursor.execute('create table TestLargeString (id int, data varchar(max))')
                cursor.execute('create table TestBlob (id int, data varbinary(max))')
            except Exception, exc:
                print exc
            cursor.close()

        def test_blob(self):
            self.blob()

        def test_large_string(self):
            self.large_string()

        def test_varbinary_none(self):
            self.varbinary_none()

try:
    import adodbapi as adb
except ImportError:
    print "adodbapi tests skipped"
else:
    class adodbapiTC(BaseSqlServer):
        def setUp(self):
            try:
                self.cnx = get_connection(driver='sqlserver2005', database='alf',
                                      host='localhost', extra_args='Trusted_Connection')
            except adb.Error, exc:
                self.skipTest(str(exc))
            cursor = self.cnx.cursor()
            try:

                cursor.execute('create table TestLargeString (id int, data varchar(max))')
                cursor.execute('create table TestBlob (id int, data varbinary(max))')
            except Exception, exc:
                print exc
            cursor.close()

        def test_blob(self):
            self.blob()

        def test_large_string(self):
            self.large_string()

        def test_varbinary_none(self):
            self.varbinary_none()


if __name__ == '__main__':
    unittest_main()
