"""Gdbm database engine."""

try:
    import gdbm
except ImportError:
    gdbm = None

import sys
import time
import logging
import datetime
import threading

from pyzor.engines.common import *

class GdbmDBHandle(object):
    absolute_source = True
    sync_period = 60
    reorganize_period = 3600 * 24  # 1 day
    _dt_decode = lambda x: None if x == 'None' else datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    fields = (
        'r_count', 'r_entered', 'r_updated',
        'wl_count', 'wl_entered', 'wl_updated',
        )
    _fields = [('r_count', int),
                ('r_entered', _dt_decode),
                ('r_updated', _dt_decode),
                ('wl_count', int),
                ('wl_entered', _dt_decode),
                ('wl_updated', _dt_decode)]
    this_version = '1'
    log = logging.getLogger("pyzord")

    def __init__(self, fn, mode, max_age=None):
        self.max_age = max_age
        self.db = gdbm.open(fn, mode)
        self.start_reorganizing()
        self.start_syncing()

    def apply_method(self, method, varargs=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        return apply(method, varargs, kwargs)

    def __getitem__(self, key):
        return self.apply_method(self._really_getitem, (key,))

    def _really_getitem(self, key):
        return GdbmDBHandle.decode_record(self.db[key])

    def __setitem__(self, key, value):
        self.apply_method(self._really_setitem, (key, value))

    def _really_setitem(self, key, value):
        self.db[key] = GdbmDBHandle.encode_record(value)

    def __delitem__(self, key):
        self.apply_method(self._really_delitem, (key,))

    def _really_delitem(self, key):
        del self.db[key]

    def start_syncing(self):
        if self.db:
            self.apply_method(self._really_sync)
        self.sync_timer = threading.Timer(self.sync_period,
                                          self.start_syncing)
        self.sync_timer.setDaemon(True)
        self.sync_timer.start()

    def _really_sync(self):
        self.db.sync()

    def start_reorganizing(self):
        if not self.max_age:
            return
        if self.db:
            self.apply_method(self._really_reorganize)
        self.reorganize_timer = threading.Timer(self.reorganize_period,
                                                self.start_reorganizing)
        self.reorganize_timer.setDaemon(True)
        self.reorganize_timer.start()

    def _really_reorganize(self):
        self.log.debug("reorganizing the database")
        key = self.db.firstkey()
        breakpoint = time.time() - self.max_age
        while key is not None:
            rec = self._really_getitem(key)
            delkey = None
            if int(time.mktime(rec.r_updated.timetuple())) < breakpoint:
                self.log.debug("deleting key %s", key)
                delkey = key
            key = self.db.nextkey(key)
            if delkey:
                self._really_delitem(delkey)
        self.db.reorganize()

    @classmethod
    def encode_record(cls, value):
        values = [cls.this_version]
        values.extend(["%s" % getattr(value, x) for x in cls.fields])
        return ",".join(values)

    @classmethod
    def decode_record(cls, s):
        try:
            s = s.decode("utf8")
        except UnicodeError:
            raise StandardError("don't know how to handle db value %s" %
                                repr(s))
        parts = s.split(',')
        dispatch = None
        version = parts[0]
        if len(parts) == 3:
            dispatch = cls.decode_record_0
        elif version == '1':
            dispatch = cls.decode_record_1
        else:
            raise StandardError("don't know how to handle db value %s" %
                                repr(s))
        return dispatch(s)

    @staticmethod
    def decode_record_0(s):
        r = Record()
        parts = s.split(',')
        fields = ('r_count', 'r_entered', 'r_updated')
        assert len(parts) == len(fields)
        for i in range(len(parts)):
            setattr(r, fields[i], int(parts[i]))
        return r

    @classmethod
    def decode_record_1(cls, s):
        r = Record()
        parts = s.split(',')[1:]
        assert len(parts) == len(cls.fields)
        for part, field in zip(parts, cls._fields):
            f, decode = field
            setattr(r, f, decode(part))
        return r

class ThreadedGdbmDBHandle(GdbmDBHandle):
    """Like GdbmDBHandle, but handles multi-threaded access."""

    def __init__(self, fn, mode, max_age=None, bound=None):
        self.db_lock = threading.Lock()
        GdbmDBHandle.__init__(self, fn, mode, max_age=max_age)

    def apply_method(self, method, varargs=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        with self.db_lock:
            return GdbmDBHandle.apply_method(self, method, varargs=varargs,
                                             kwargs=kwargs)
# This won't work because the gdbm object needs to be in shared memory of the
# spawned processes.
# class ProcessGdbmDBHandle(ThreadedGdbmDBHandle):
#     def __init__(self, fn, mode, max_age=None, bound=None):
#         ThreadedGdbmDBHandle.__init__(self, fn, mode, max_age=max_age,
#                                       bound=bound)
#         self.db_lock = multiprocessing.Lock()

if sys.version_info[0] != 3 and gdbm is None:
    handle = DBHandle(single_threaded=None,
                      multi_threaded=None,
                      multi_processing=None)
else:
    handle = DBHandle(single_threaded=GdbmDBHandle,
                      multi_threaded=ThreadedGdbmDBHandle,
                      multi_processing=None)


