# coding: utf-8
import os
import threading
import pymysql
from queue import Queue
from functools import wraps

from .setting import MYSQL


def _parse_execute_sql(sql):
  sql = sql.lstrip()
  cmd = sql.split(' ', 1)[0].lower()
  return cmd


class NestedTransactionError(Exception):
  pass


class NeedTransactionError(Exception):
  pass


class UnExpectTransactionError(Exception):
  pass


class AbstractSQLStore(object):

  def __init__(self, host, user, passwd, db, port, debug=False):
    self.host = host
    self.user = user
    self.passwd = passwd
    self.db = db
    self.port = port
    self.thread_local = threading.local()
    self.debug = debug

  def __str__(self):
    return "%s:%s:%s" % (type(self).__name__, self.host, self.user)

  def __repr__(self):
    return self.__str__()

  def get_connection(self):
    raise NotImplementedError

  def begin(self):
    if self.transaction:
      raise NestedTransactionError
    self.transaction = self.get_connection()
    self.transaction.begin()

  def commit(self):
    self.transaction.commit()
    conn = self.transaction
    self.transaction = None
    self.finish(conn)

  def rollback(self):
    self.transaction.rollback()
    conn = self.transaction
    self.transaction = None
    self.finish(conn)

  def finish(self, conn):
    pass

  @property
  def transaction(self):
    return getattr(self.thread_local, 'transaction', None)

  @transaction.setter
  def transaction(self, value):
    self.thread_local.transaction = value

  def execute(self, sql, *args, batch=False, debug=False):
    cmd = _parse_execute_sql(sql)
    conn = self.transaction or self.get_connection()
    cursor = conn.cursor()
    try:
      if self.debug or debug:
        print('DebugSQL:', cursor.mogrify(sql, args))
      result = cursor.execute(sql, args)
      if cmd in ['select', 'show']:
        return cursor.fetchall()
      elif cmd == 'insert':
        if batch:
          return range(cursor.lastrowid, cursor.lastrowid + cursor.rowcount)
        return cursor.lastrowid
      return result
    finally:
      self.finish(conn)

  def executemany(self, sql, *args):
    cmd = _parse_execute_sql(sql)
    conn = self.transaction or self.get_connection()
    cursor = conn.cursor()
    try:
      result = cursor.executemany(sql, args)
      if cmd in ['select', 'show']:
        return cursor.fetchall()
      elif cmd == 'insert':
        return cursor.lastrowid
      return result
    finally:
      self.finish(conn)

  def with_transaction(self, f):

    @wraps(f)
    def _(*args, **kwargs):
      try:
        self.begin()
        result = f(*args, **kwargs)
      except Exception as e:
        self.rollback()
        raise e
      else:
        self.commit()
        return result

    return _

  def need_transaction(self, f):

    @wraps(f)
    def _(*args, **kwargs):
      if not self.transaction:
        raise NeedTransactionError
      return f(*args, **kwargs)

    return _

  def no_transaction(self, f):

    @wraps(f)
    def _(*args, **kwargs):
      if self.transaction:
        raise UnExpectTransactionError
      return f(*args, **kwargs)

    return _


class SQLStore(AbstractSQLStore):

  def get_connection(self):
    conn = getattr(self.thread_local, 'connection', None)
    if not conn:
      conn = pymysql.connect(
        host=self.host,
        user=self.user,
        passwd=self.passwd,
        db=self.db,
        port=int(self.port),
        charset='utf8mb4',
        autocommit=True)
      self.thread_local.connection = conn
    conn.ping(True)
    return conn


class PoolSQLStore(AbstractSQLStore):

  def __init__(self, host, user, passwd, db, port, pool_size=10, debug=False):
    super(PoolSQLStore, self).__init__(host, user, passwd, db, port, debug)
    self.pool = Queue(maxsize=pool_size)
    for i in range(pool_size):
      _conn = pymysql.connect(
        host=self.host,
        user=self.user,
        passwd=self.passwd,
        db=self.db,
        port=self.port,
        charset='utf8mb4',
        autocommit=True)
      self.pool.put(_conn)

  def get_connection(self):
    conn = self.pool.get()
    conn.ping(True)
    return conn

  def finish(self, conn):
    if self.transaction is conn:
      return
    self.pool.put(conn)


def _get_pool_size():
  pool_size = os.environ.get('MYSQL_POOL_SIZE', None)
  if pool_size and pool_size.isdigit():
    return int(pool_size)
  else:
    return 20


pool_size = _get_pool_size()
if not pool_size:
  store = SQLStore(MYSQL['host'], MYSQL['user'], MYSQL['password'], MYSQL['db'],
                   MYSQL['port'], debug=False)
else:
  store = PoolSQLStore(
    MYSQL['host'],
    MYSQL['user'],
    MYSQL['password'],
    MYSQL['db'],
    MYSQL['port'],
    debug=False,
    pool_size=pool_size)
