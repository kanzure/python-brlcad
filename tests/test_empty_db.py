import os
import unittest
from brlcad.exceptions import BRLCADException
import brlcad._bindings.libwdb as libwdb


def ls(db_ip):
    for i in xrange(0, libwdb.RT_DBNHASH):
        dp = db_ip.contents.dbi_Head[i]
        while dp:
            crt_dir = dp.contents
            yield crt_dir
            dp = crt_dir.d_forw


class EmptyDBTestCase(unittest.TestCase):

    def check_empty_db(self, db_ip):
        # the _GLOBAL object should exist:
        lst = [x for x in ls(db_ip) if str(x.d_namep) == '_GLOBAL']
        self.assertEqual(1, len(lst))
        _global = lst[0]
        # the _GLOBAL object should be hidden:
        self.assertEqual(libwdb.RT_DIR_HIDDEN, libwdb.RT_DIR_HIDDEN & _global.d_flags)
        # the directory listing should be empty:
        lst = [x for x in ls(db_ip) if not (x.d_flags & libwdb.RT_DIR_HIDDEN)]
        self.assertEqual(0, len(lst))

    def test_direct_calls(self):
        db_name = "direct_empty_db.g"
        if os.path.isfile(db_name):
            os.remove(db_name)
        # first time the DB is created:
        db_fp = libwdb.wdb_fopen(db_name)
        if db_fp == libwdb.RT_WDB_NULL:
            raise BRLCADException("Failed creating new DB file: <{}>".format(db_name))
        db_ip = db_fp.contents.dbip
        self.check_empty_db(db_ip)
        libwdb.wdb_close(db_fp)
        # second time the DB exists and it is re-opened:
        db_ip = libwdb.db_open(db_name, "r+w")
        if db_ip == libwdb.DBI_NULL:
            raise BRLCADException("Can't open existing DB file: <{0}>".format(db_name))
        if libwdb.db_dirbuild(db_ip) < 0:
            raise BRLCADException("Failed loading directory of DB file: <{}>".format(db_name))
        self.db_fp = libwdb.wdb_dbopen(db_ip, libwdb.RT_WDB_TYPE_DB_DISK)
        if self.db_fp == libwdb.RT_WDB_NULL:
            raise BRLCADException("Failed read existing DB file: <{}>".format(db_name))
        self.check_empty_db(db_ip)


if __name__ == "__main__":
    unittest.main()
