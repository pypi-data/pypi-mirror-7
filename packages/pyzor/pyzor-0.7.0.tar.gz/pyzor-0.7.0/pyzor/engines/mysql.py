"""MySQLdb database engine."""

import time
import Queue
import logging
import datetime
import threading

try:
    import MySQLdb
except ImportError:
    # The SQL database backend will not work.
    MySQLdb = None

from pyzor.engines.common import *


class MySQLDBHandle(object):
    absolute_source = False
    # The table must already exist, and have this schema:
    #   CREATE TABLE `public` (
    #   `digest` char(40) default NULL,
    #   `r_count` int(11) default NULL,
    #   `wl_count` int(11) default NULL,
    #   `r_entered` datetime default NULL,
    #   `wl_entered` datetime default NULL,
    #   `r_updated` datetime default NULL,
    #   `wl_updated` datetime default NULL,
    #   PRIMARY KEY  (`digest`)
    #   )
    # XXX Re-organising might be faster with a r_updated index.  However,
    # XXX the re-organisation time isn't that important, and that would
    # XXX (slightly) slow down all inserts, so we leave it for now.
    reorganize_period = 3600 * 24  # 1 day
    reconnect_period = 60  # seconds
    log = logging.getLogger("pyzord")

    def __init__(self, fn, mode, max_age=None):
        self.max_age = max_age
        self.db = None
        # The 'fn' is host,user,password,db,table.  We ignore mode.
        # We store the authentication details so that we can reconnect if
        # necessary.
        self.host, self.user, self.passwd, self.db_name, \
            self.table_name = fn.split(",")
        self.last_connect_attempt = 0  # We have never connected.
        self.reconnect()
        self.start_reorganizing()

    def _get_new_connection(self):
        """Returns a new db connection."""
        db = MySQLdb.connect(host=self.host, user=self.user,
                               db=self.db_name, passwd=self.passwd)
        db.autocommit(True)
        return db

    def _check_reconnect_time(self):
        if time.time() - self.last_connect_attempt < self.reconnect_period:
            # Too soon to reconnect.
            self.log.debug("Can't reconnect until %s",
                           (time.ctime(self.last_connect_attempt +
                                       self.reconnect_period)))
            return False
        return True

    def reconnect(self):
        if not self._check_reconnect_time():
            return
        if self.db:
            try:
                self.db.close()
            except MySQLdb.Error:
                pass
        try:
            self.db = self._get_new_connection()
        except MySQLdb.Error, e:
            self.log.error("Unable to connect to database: %s", e)
            self.db = None
        # Keep track of when we connected, so that we don't retry too often.
        self.last_connect_attempt = time.time()

    def __del__(self):
        """Close the database when the object is no longer needed."""
        try:
            if self.db:
                self.db.close()
        except MySQLdb.Error:
            pass

    def _safe_call(self, name, method, args):
        try:
            return method(*args, db=self.db)
        except (MySQLdb.Error, AttributeError), e:
            self.log.error("%s failed: %s", name, e)
            self.reconnect()
            # Retrying just complicates the logic - we don't really care if
            # a single query fails (and it's possible that it would fail)
            # on the second attempt anyway.  Any exceptions are caught by
            # the server, and a 'nice' message provided to the caller.
            raise DatabaseError("Database temporarily unavailable.")

    def __getitem__(self, key):
        return self._safe_call("getitem", self._really__getitem__, (key,))

    def __setitem__(self, key, value):
        return self._safe_call("setitem", self._really__setitem__,
                               (key, value))

    def __delitem__(self, key):
        return self._safe_call("delitem", self._really__delitem__, (key,))

    def _really__getitem__(self, key, db=None):
        """__getitem__ without the exception handling."""
        c = db.cursor()
        # The order here must match the order of the arguments to the
        # Record constructor.
        c.execute("SELECT r_count, wl_count, r_entered, r_updated, "
                  "wl_entered, wl_updated FROM %s WHERE digest=%%s" %
                  self.table_name, (key,))
        try:
            try:
                return Record(*c.fetchone())
            except TypeError:
                # fetchone() returned None, i.e. there is no such record
                raise KeyError()
        finally:
            c.close()

    def _really__setitem__(self, key, value, db=None):
        """__setitem__ without the exception handling."""
        c = db.cursor()
        try:
            c.execute("INSERT INTO %s (digest, r_count, wl_count, "
                      "r_entered, r_updated, wl_entered, wl_updated) "
                      "VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s) ON "
                      "DUPLICATE KEY UPDATE r_count=%%s, wl_count=%%s, "
                      "r_entered=%%s, r_updated=%%s, wl_entered=%%s, "
                      "wl_updated=%%s" % self.table_name,
                      (key, value.r_count, value.wl_count, value.r_entered,
                       value.r_updated, value.wl_entered, value.wl_updated,
                       value.r_count, value.wl_count, value.r_entered,
                       value.r_updated, value.wl_entered, value.wl_updated))
        finally:
            c.close()

    def _really__delitem__(self, key, db=None):
        """__delitem__ without the exception handling."""
        c = db.cursor()
        try:
            c.execute("DELETE FROM %s WHERE digest=%%s" % self.table_name,
                      (key,))
        finally:
            c.close()

    def start_reorganizing(self):
        if not self.max_age:
            return
        self.log.debug("reorganizing the database")
        breakpoint = (datetime.datetime.now() -
                      datetime.timedelta(seconds=self.max_age))
        db = self._get_new_connection()
        c = db.cursor()
        try:
            c.execute("DELETE FROM %s WHERE r_updated<%%s" %
                      self.table_name, (breakpoint,))
        except (MySQLdb.Error, AttributeError), e:
            self.log.warn("Unable to reorganise: %s", e)
        finally:
            c.close()
            db.close()
        self.reorganize_timer = threading.Timer(self.reorganize_period,
                                                self.start_reorganizing)
        self.reorganize_timer.setDaemon(True)
        self.reorganize_timer.start()

class ThreadedMySQLDBHandle(MySQLDBHandle):

    def __init__(self, fn, mode, max_age=None, bound=None):
        self.bound = bound
        if self.bound:
            self.db_queue = Queue.Queue()
        MySQLDBHandle.__init__(self, fn, mode, max_age=max_age)

    def _get_connection(self):
        if self.bound:
            return self.db_queue.get()
        else:
            return self._get_new_connection()

    def _release_connection(self, db):
        if self.bound:
            self.db_queue.put(db)
        else:
            db.close()

    def _safe_call(self, name, method, args):
        db = self._get_connection()
        try:
            return method(*args, db=db)
        except (MySQLdb.Error, AttributeError) as e:
            self.log.error("%s failed: %s", name, e)
            if not self.bound:
                raise DatabaseError("Database temporarily unavailable.")
            try:
                # Connection might be timeout, ping and retry
                db.ping(True)
                return method(*args, db=db)
            except (MySQLdb.Error, AttributeError) as e:
                # attempt a new connection, if we can retry
                db = self._reconnect(db)
                raise DatabaseError("Database temporarily unavailable.")
        finally:
            self._release_connection(db)

    def reconnect(self):
        if not self.bound:
            return
        for _ in xrange(self.bound):
            self.db_queue.put(self._get_new_connection())

    def _reconnect(self, db):
        if not self._check_reconnect_time():
            return db
        else:
            self.last_connect_attempt = time.time()
            return self._get_new_connection()

    def __del__(self):
        if not self.bound:
            return
        for db in iter(self.db_queue.get_nowait):
            try:
                db.close()
            except MySQLdb.Error:
                continue
            except Queue.Empty:
                break

class ProcessMySQLDBHandle(MySQLDBHandle):
    def __init__(self, fn, mode, max_age=None):
        MySQLDBHandle.__init__(self, fn, mode, max_age=max_age)

    def reconnect(self):
        pass

    def __del__(self):
        pass

    def _safe_call(self, name, method, args):
        db = None
        try:
            db = self._get_new_connection()
            return method(*args, db=db)
        except (MySQLdb.Error, AttributeError) as e:
            self.log.error("%s failed: %s", name, e)
            raise DatabaseError("Database temporarily unavailable.")
        finally:
            if db is not None:
                db.close()

if MySQLdb is None:
    handle = DBHandle(single_threaded=None,
                      multi_threaded=None,
                      multi_processing=None)
else:
    handle = DBHandle(single_threaded=MySQLDBHandle,
                      multi_threaded=ThreadedMySQLDBHandle,
                      multi_processing=ProcessMySQLDBHandle)
