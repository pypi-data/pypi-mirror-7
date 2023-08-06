#! /usr/bin/env python
"""Binds the OData API to the Python DB API."""


import sqlite3
import time
import string
import sys
import traceback
import threading
import decimal
import math
import logging
import types
import warnings
import os.path
import hashlib
import io

import pyslet.iso8601 as iso
import pyslet.http.params as params
import pyslet.blockstore as blockstore
from pyslet.vfs import OSFilePath

import csdl as edm
import core
import metadata as edmx


# : the standard timeout while waiting for a database connection, in seconds
SQL_TIMEOUT = 90


class SQLError(Exception):

    """Base class for all module exceptions."""
    pass


class DatabaseBusy(SQLError):

    """Raised when a database connection times out."""
    pass

SQLOperatorPrecedence = {
    ',': 0,
    'OR': 1,
    'AND': 2,
    'NOT': 3,
    '=': 4,
    '<>': 4,
    '<': 4,
    '>': 4,
    '<=': 4,
    '>=': 4,
    'LIKE': 4,
    '+': 5,
    '-': 5,
    '*': 6,
    '/': 6
}
"""Look-up table for SQL operator precedence calculations.

The keys are strings representing the operator, the values are
integers that allow comparisons for operator precedence. For
example::

    SQLOperatorPrecedence['+']<SQLOperatorPrecedence['*']
    SQLOperatorPrecedence['<']==SQLOperatorPrecedence['>']"""


class UnparameterizedLiteral(core.LiteralExpression):

    """Class used as a flag that this literal is safe and does not need
    to be parameterized.

    This is used in the query converter to prevent things like this
    happening when the converter itself constructs a LIKE expression::

            "name" LIKE ?+?+? ; params=[u'%',u"Smith",u'%']"""
    pass


class SQLParams(object):

    """An abstract class used to build parameterized queries.

    Python's DB API support three different conventions for specifying
    parameters and each module indicates the convention in use.  The SQL
    construction methods in this module abstract away this variability
    for maximum portability using different implementations of the basic
    SQLParams class."""

    def __init__(self):
        # : an object suitable for passing to DB API's execute method
        self.params = None

    def add_param(self, value):
        """Adds a value to this set of parameters

        Returns the string to include in the query in place of this
        value.

        value:
                The native representation of the value in a format
                suitable for passing to the underlying DB API."""
        raise NotImplementedError


class QMarkParams(SQLParams):

    """A class for building parameter lists using '?' syntax."""

    def __init__(self):
        super(QMarkParams, self).__init__()
        self.params = []

    def add_param(self, value):
        self.params.append(value)
        return "?"


class NumericParams(SQLParams):

    """A class for building parameter lists using ':1', ':2',... syntax"""

    def __init__(self):
        super(QMarkParams, self).__init__()
        self.params = []

    def add_param(self, value):
        self.params.append(value)
        return ":%i" % len(self.params)


class NamedParams(SQLParams):

    """A class for building parameter lists using ':A', ':B",... syntax

    Although there is more freedom with named parameters, in order to
    support the ordered lists of the other formats we just invent
    parameter names using ':p1', ':p2', etc."""

    def __init__(self):
        super(QMarkParams, self).__init__()
        self.params = {}

    def add_param(self, value):
        name = "p%i" % len(self.params)
        self.params[name] = value
        return ":" + name


class SQLTransaction(object):

    """Class used to model a transaction.

    Python's DB API uses transactions by default, hiding the details from
    the caller.  Essentially, the first execute call on a connection issues
    a BEGIN statement and the transaction ends with either a commit or a
    rollback.  It is generally considered a bad idea to issue a SQL command
    and then leave the connection with an open transaction.

    The purpose of this class is to help us write methods that can
    operate either as a single transaction or as part of sequence of
    methods that form a single transaction.  It also manages cursor
    creation and closing and logging.

    Essentially, the class is used as follows::

            t=SQLTransaction(db_module,db_connection)
            try:
                    t.begin()
                    t.execute("UPDATE SOME_TABLE SET SOME_COL='2'")
                    t.commit()
            except Exception as e:
                    t.rollback(e)
            finally:
                    t.close(e)

    The transaction object can be passed to a sub-method between the
    begin and commit calls provided that method follows the same pattern
    as the above for the try, except and finally blocks.  The object
    keeps track of these 'nested' transactions and delays the commit or
    rollback until the outermost method invokes them."""

    def __init__(self, api, dbc):
        self.api = api          #: the database module
        self.dbc = dbc          #: the database connection
        #: the database cursor to use for executing commands
        self.cursor = None
        self.noCommit = 0           #: used to manage nested transactions
        self.queryCount = 0     #: records the number of successful commands

    def begin(self):
        """Begins a transaction

        If a transaction is already in progress a nested transaction is
        started which has no affect on the database connection itself."""
        if self.cursor is None:
            self.cursor = self.dbc.cursor()
        else:
            self.noCommit += 1

    def execute(self, sqlcmd, params):
        """Executes *sqlcmd* as part of this transaction.

        sqlcmd
                A string containing the query

        params
                A :py:class:`SQLParams` object containing any
                parameterized values."""
        self.cursor.execute(sqlcmd, params.params)
        self.queryCount += 1

    def commit(self):
        """Ends this transaction with a commit

        Nested transactions do nothing."""
        if self.noCommit:
            return
        self.dbc.commit()

    def rollback(self, err=None, swallow=False):
        """Calls the underlying database connection rollback method.

        Nested transactions do not rollback the connection, they do
        nothing except re-raise *err* (if required).

        If rollback is not supported the resulting error is absorbed.

        err
                The exception that triggered the rollback.  If not None then
                this is logged at INFO level when the rollback succeeds.

                If the transaction contains at least one successfully
                executed query and the rollback fails then *err* is logged
                at ERROR rather than INFO level indicating that the data may
                now be in violation of the model.

        swallow
                A flag (defaults to False) indicating that *err* should be
                swallowed, rather than re-raised."""
        if not self.noCommit:
            try:
                self.dbc.rollback()
                if err is not None:
                    logging.info(
                        "rollback invoked for transaction following error %s",
                        str(err))
            except self.api.NotSupportedError:
                if err is not None:
                    if self.queryCount:
                        logging.error(
                            "Data Integrity Error on TABLE %s: rollback "
                            "invoked on a connection that does not "
                            "support transactions after error %s",
                            self.table_name,
                            str(err))
                    else:
                        logging.info(
                            "Query failed following error %s", str(err))
                pass
        if err is not None and not swallow:
            logging.debug(
                string.join(
                    traceback.format_exception(
                        *
                        sys.exc_info(),
                        limit=6)))
            if isinstance(err, self.api.Error):
                raise SQLError(str(err))
            else:
                raise err

    def close(self):
        """Closes this transaction after a rollback or commit.

        Each call to :py:meth:`begin` MUST be balanced with one call to
        close."""
        if self.noCommit:
            self.noCommit = self.noCommit - 1
        elif self.cursor is not None:
            self.cursor.close()
            self.cursor = None
            self.queryCount = 0


class SQLCollectionBase(core.EntityCollection):

    """A base class to provide core SQL functionality.

    Additional keyword arguments:

    container
            A :py:class:`SQLEntityContainer` instance.

    qualify_names
            An optional boolean (defaults to False) indicating whether or not
            the column names must be qualified in all queries.

    On construction a data connection is acquired from *container*, this
    may prevent other threads from using the database until the lock is
    released by the :py:meth:`close` method."""

    def __init__(self, container, qualify_names=False, **kwargs):
        super(SQLCollectionBase, self).__init__(**kwargs)
        self.container = container
        #: the parent container (database) for this collection
        self.table_name = self.container.mangled_names[(self.entity_set.name,)]
        self.auto_keys = False
        for k in self.entity_set.keys:
            source_path = (self.entity_set.name, k)
            if source_path in self.container.ro_names:
                self.auto_keys = True
        # the quoted table name containing this collection
        self.qualify_names = qualify_names
        # if True, field names in expressions are qualified with
        # :py:attr:`table_name`
        # force orderNames to be initialised
        self.set_orderby(None)
        self.dbc = None                 #: a connection to the database
        self._sqlLen = None
        self._sqlGen = None
        try:
            self.dbc = self.container.acquire_connection(SQL_TIMEOUT)
            if self.dbc is None:
                raise DatabaseBusy(
                    "Failed to acquire connection after %is" % SQL_TIMEOUT)
        except:
            self.close()
            raise

    def close(self):
        """Closes the cursor and database connection if they are open."""
        if self.dbc is not None:
            self.container.release_connection(self.dbc)
            self.dbc = None

    def __len__(self):
        if self._sqlLen is None:
            query = ["SELECT COUNT(*) FROM %s" % self.table_name]
            params = self.container.ParamsClass()
            query.append(self.join_clause())
            query.append(self.where_clause(None, params))
            query = string.join(query, '')
            self._sqlLen = (query, params)
        else:
            query, params = self._sqlLen
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            # get the result
            result = transaction.cursor.fetchone()[0]
            # we haven't changed the database, but we don't want to
            # leave the connection idle in transaction
            transaction.commit()
            return result
        except Exception as e:
            # we catch (almost) all exceptions and re-raise after rollback
            transaction.rollback(e)
        finally:
            transaction.close()

    def entity_generator(self):
        entity, values = None, None
        if self._sqlGen is None:
            entity = self.new_entity()
            query = ["SELECT "]
            params = self.container.ParamsClass()
            column_names, values = zip(*list(self.select_fields(entity)))
            # values is used later for the first result
            column_names = list(column_names)
            self.orderby_cols(column_names, params)
            query.append(string.join(column_names, ", "))
            query.append(' FROM ')
            query.append(self.table_name)
            query.append(self.join_clause())
            query.append(self.where_clause(None, params,
                                           use_filter=True, use_skip=False))
            query.append(self.orderby_clause())
            query = string.join(query, '')
            self._sqlGen = query, params
        else:
            query, params = self._sqlGen
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            while True:
                row = transaction.cursor.fetchone()
                if row is None:
                    break
                if entity is None:
                    entity = self.new_entity()
                    values = zip(*list(self.select_fields(entity)))[1]
                for value, new_value in zip(values, row):
                    self.container.read_sql_value(value, new_value)
                entity.exists = True
                yield entity
                entity, values = None, None
            # we haven't changed the database, but we don't want to
            # leave the connection idle in transaction
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def itervalues(self):
        return self.expand_entities(
            self.entity_generator())

    def set_page(self, top, skip=0, skiptoken=None):
        """Sets the values for paging.

        Our implementation uses a special format for *skiptoken*.  It is
        a comma-separated list of simple literal values corresponding to
        the values required by the ordering augmented with the key
        values to ensure uniqueness.

        For example, if $orderby=A,B on an entity set with key K then
        the skiptoken will typically have three values comprising the
        last values returned for A,B and K in that order.  In cases
        where the resulting skiptoken would be unreasonably large an
        additional integer (representing a further skip) may be appended
        and the whole token expressed relative to an earlier skip
        point."""
        self.top = top
        self.skip = skip
        if skiptoken is None:
            self.skiptoken = None
        else:
            # parse a sequence of literal values
            p = core.Parser(skiptoken)
            self.skiptoken = []
            while True:
                p.ParseWSP()
                self.skiptoken.append(
                    p.require_production(p.ParseURILiteral()))
                p.ParseWSP()
                if not p.Parse(','):
                    if p.MatchEnd():
                        break
                    else:
                        raise core.InvalidSystemQueryOption(
                            "Unrecognized $skiptoken: %s" % skiptoken)
            if self.orderby is None:
                order_len = 0
            else:
                order_len = len(self.orderby)
            if (len(self.skiptoken) ==
                    order_len + len(self.entity_set.keys) + 1):
                # the last value must be an integer we add to skip
                if isinstance(self.skiptoken[-1], edm.Int32Value):
                    self.skip += self.skiptoken[-1].value
                    self.skiptoken = self.skiptoken[:-1]
                else:
                    raise core.InvalidSystemQueryOption(
                        "skiptoken incompatible with ordering: %s" % skiptoken)
            elif len(self.skiptoken) != order_len + len(self.entity_set.keys):
                raise core.InvalidSystemQueryOption(
                    "skiptoken incompatible with ordering: %s" % skiptoken)
        self.nextSkiptoken = None

    def next_skiptoken(self):
        if self.nextSkiptoken:
            token = []
            for t in self.nextSkiptoken:
                token.append(core.ODataURI.FormatLiteral(t))
            return string.join(token, u",")
        else:
            return None

    def page_generator(self, set_next=False):
        if self.top == 0:
            # end of paging
            return
        entity = self.new_entity()
        query = ["SELECT "]
        params = self.container.ParamsClass()
        column_names, values = zip(*list(self.select_fields(entity)))
        column_names = list(column_names)
        self.orderby_cols(column_names, params, True)
        query.append(string.join(column_names, ", "))
        query.append(' FROM ')
        query.append(self.table_name)
        query.append(self.join_clause())
        query.append(
            self.where_clause(None, params, use_filter=True, use_skip=True))
        query.append(self.orderby_clause())
        query = string.join(query, '')
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            skip = self.skip
            top = self.top
            topmax = self.topmax
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            while True:
                row = transaction.cursor.fetchone()
                if row is None:
                    # no more pages
                    if set_next:
                        self.top = self.skip = 0
                        self.skipToken = None
                    break
                if skip:
                    skip = skip - 1
                    continue
                if entity is None:
                    entity = self.new_entity()
                    values = zip(*list(self.select_fields(entity)))[1]
                row_values = list(row)
                for value, new_value in zip(values, row_values):
                    self.container.read_sql_value(value, new_value)
                entity.exists = True
                yield entity
                if topmax is not None:
                    topmax = topmax - 1
                    if topmax < 1:
                        # this is the last entity, set the nextSkiptoken
                        order_values = row_values[-len(self.orderNames):]
                        self.nextSkiptoken = []
                        for v in order_values:
                            self.nextSkiptoken.append(
                                self.container.new_from_sql_value(v))
                        tokenlen = 0
                        for v in self.nextSkiptoken:
                            if v and isinstance(v, (edm.StringValue,
                                                    edm.BinaryValue)):
                                tokenlen += len(v.value)
                        # a really large skiptoken is no use to anyone
                        if tokenlen > 512:
                            # ditch this one, copy the previous one and add a
                            # skip
                            self.nextSkiptoken = list(self.skiptoken)
                            v = edm.Int32Value()
                            v.set_from_value(self.topmax)
                            self.nextSkiptoken.append(v)
                        if set_next:
                            self.skiptoken = self.nextSkiptoken
                            self.skip = 0
                        break
                if top is not None:
                    top = top - 1
                    if top < 1:
                        if set_next:
                            if self.skip is not None:
                                self.skip = self.skip + self.top
                            else:
                                self.skip = self.top
                        break
                entity = None
            # we haven't changed the database, but we don't want to
            # leave the connection idle in transaction
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def iterpage(self, set_next=False):
        return self.expand_entities(
            self.page_generator(set_next))

    def __getitem__(self, key):
        entity = self.new_entity()
        entity.set_key(key)
        params = self.container.ParamsClass()
        query = ["SELECT "]
        column_names, values = zip(*list(self.select_fields(entity)))
        query.append(string.join(column_names, ", "))
        query.append(' FROM ')
        query.append(self.table_name)
        query.append(self.join_clause())
        query.append(self.where_clause(entity, params))
        query = string.join(query, '')
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            rowcount = transaction.cursor.rowcount
            row = transaction.cursor.fetchone()
            if rowcount == 0 or row is None:
                raise KeyError
            elif rowcount > 1 or (rowcount == -1 and
                                  transaction.cursor.fetchone() is not None):
                # whoops, that was unexpected
                raise SQLError(
                    "Integrity check failure, non-unique key: %s" % repr(key))
            for value, new_value in zip(values, row):
                self.container.read_sql_value(value, new_value)
            entity.exists = True
            entity.Expand(self.expand, self.select)
            transaction.commit()
            return entity
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def read_stream(self, key, out=None):
        entity = self.new_entity()
        entity.set_key(key)
        svalue = self._get_streamid(key)
        sinfo = core.StreamInfo()
        if svalue:
            estream = self.container.streamstore.get_stream(svalue.value)
            sinfo.type = params.MediaType.from_str(estream['mimetype'].value)
            sinfo.created = estream['created'].value.WithZone(0)
            sinfo.modified = estream['modified'].value.WithZone(0)
            sinfo.size = estream['size'].value
            sinfo.md5 = estream['md5'].value
        else:
            estream = None
            sinfo.size = 0
            sinfo.md5 = hashlib.md5('').digest()
        if out is not None and svalue:
            with self.container.streamstore.open_stream(estream, 'r') as src:
                actual_size, actual_md5 = self._copy_src(src, out)
            if sinfo.size is not None and sinfo.size != actual_size:
                # unexpected size mismatch
                raise SQLError("stream size mismatch on read %s" %
                               entity.GetLocation())
            if sinfo.md5 is not None and sinfo.md5 != actual_md5:
                # md5 mismatch
                raise SQLError("stream checksum mismatch on read %s" %
                               entity.GetLocation())
        return sinfo

    def read_stream_close(self, key):
        entity = self.new_entity()
        entity.set_key(key)
        svalue = self._get_streamid(key)
        sinfo = core.StreamInfo()
        if svalue:
            estream = self.container.streamstore.get_stream(svalue.value)
            sinfo.type = params.MediaType.from_str(estream['mimetype'].value)
            sinfo.created = estream['created'].value.WithZone(0)
            sinfo.modified = estream['modified'].value.WithZone(0)
            sinfo.size = estream['size'].value
            sinfo.md5 = estream['md5'].value
            return sinfo, self._read_stream_gen(estream, sinfo)
        else:
            estream = None
            sinfo.size = 0
            sinfo.md5 = hashlib.md5('').digest()
            self.close()
            return sinfo, []

    def _read_stream_gen(self, estream, sinfo):
        try:
            with self.container.streamstore.open_stream(estream, 'r') as src:
                h = hashlib.md5()
                count = 0
                while True:
                    data = src.read(io.DEFAULT_BUFFER_SIZE)
                    if len(data):
                        count += len(data)
                        h.update(data)
                        yield data
                    else:
                        break
            if sinfo.size is not None and sinfo.size != count:
                # unexpected size mismatch
                raise SQLError("stream size mismatch on read [%i]" %
                               estream.key())
            if sinfo.md5 is not None and sinfo.md5 != h.digest():
                # md5 mismatch
                raise SQLError("stream checksum mismatch on read [%i]" %
                               estream.key())
        finally:
            self.close()

    def update_stream(self, src, key, sinfo=None):
        e = self.new_entity()
        e.set_key(key)
        if sinfo is None:
            sinfo = core.StreamInfo()
        etag = e.ETagValues()
        if len(etag) == 1 and isinstance(etag[0], edm.BinaryValue):
            h = hashlib.sha256()
            etag = etag[0]
        else:
            h = None
        c, v = self.stream_field(e)
        if self.container.streamstore:
            # spool the data into the store and store the stream key
            estream = self.container.streamstore.new_stream(sinfo.type,
                                                            sinfo.created)
            with self.container.streamstore.open_stream(estream, 'w') as dst:
                sinfo.size, sinfo.md5 = self._copy_src(src, dst, sinfo.size, h)
            if sinfo.modified is not None:
                # force modified date based on input
                estream['modified'].set_from_value(sinfo.modified.ShiftZone(0))
                estream.Update()
            v.set_from_value(estream.key())
        else:
            raise NotImplementedError
        if h is not None:
            etag.set_from_value(h.digest())
        oldvalue = self._get_streamid(key)
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            # store the new stream value for the entity
            query = ['UPDATE ', self.table_name, ' SET ']
            params = self.container.ParamsClass()
            query.append(
                "%s=%s" %
                (c, params.add_param(self.container.prepare_sql_value(v))))
            query.append(' WHERE ')
            for k, kv in e.KeyDict().items():
                query.append(
                    '%s=%s' %
                    (self.container.mangled_names[(self.entity_set.name, k)],
                     params.add_param(self.container.prepare_sql_value(kv))))
            query = string.join(query, '')
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
        except Exception as e:
            # we allow the stream store to re-use the same database but
            # this means we can't transact on both at once (from the
            # same thread) - settle for logging at the moment
            # self.container.streamstore.delete_stream(estream)
            logging.error("Orphan stream created %s[%i]",
                          estream.entity_set.name, estream.key())
            transaction.rollback(e)
        finally:
            transaction.close()
        # now remove the old stream
        if oldvalue:
            oldstream = self.container.streamstore.get_stream(oldvalue.value)
            self.container.streamstore.delete_stream(oldstream)

    def _get_streamid(self, key, transaction=None):
        entity = self.new_entity()
        entity.set_key(key)
        params = self.container.ParamsClass()
        query = ["SELECT "]
        sname, svalue = self.stream_field(entity)
        query.append(sname)
        query.append(' FROM ')
        query.append(self.table_name)
        query.append(self.where_clause(entity, params, use_filter=False))
        query = string.join(query, '')
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            rowcount = transaction.cursor.rowcount
            row = transaction.cursor.fetchone()
            if rowcount == 0 or row is None:
                raise KeyError
            elif rowcount > 1 or (rowcount == -1 and
                                  transaction.cursor.fetchone() is not None):
                # whoops, that was unexpected
                raise SQLError(
                    "Integrity check failure, non-unique key: %s" % repr(key))
            self.container.read_sql_value(svalue, row[0])
            entity.exists = True
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()
        return svalue

    def _copy_src(self, src, dst, max_bytes=None, xhash=None):
        md5 = hashlib.md5()
        rbytes = max_bytes
        count = 0
        while rbytes is None or rbytes > 0:
            if rbytes is None:
                data = src.read(io.DEFAULT_BUFFER_SIZE)
            else:
                data = src.read(min(rbytes, io.DEFAULT_BUFFER_SIZE))
                rbytes -= len(data)
            if not data:
                # we're done
                break
            # add the data to the hash
            md5.update(data)
            if xhash is not None:
                xhash.update(data)
            while data:
                wbytes = dst.write(data)
                if wbytes is None:
                    if not isinstance(dst, io.RawIOBase):
                        wbytes = len(data)
                    else:
                        wbytes = 0
                        time.sleep(0)   # yield to prevent hard loop
                if wbytes < len(data):
                    data = data[wbytes:]
                else:
                    data = None
                count += wbytes
        return count, md5.digest()

    def join_clause(self):
        """A utility method to return the JOIN clause.

        Defaults to an empty expression."""
        return ""

    def set_filter(self, filter):
        self.filter = filter
        self.set_page(None)
        self._sqlLen = None
        self._sqlGen = None

    def where_clause(
            self,
            entity,
            params,
            use_filter=True,
            use_skip=False,
            null_cols=()):
        """A utility method that generates the WHERE clause for a query

        entity
                An optional entity within this collection that is the focus
                of this query.  If not None the resulting WHERE clause will
                restrict the query to this entity only.

        params
                The :py:class:`SQLParams` object to add parameters to.

        use_filter
                Defaults to True, indicates if this collection's filter should
                be added to the WHERE clause.

        use_skip
                Defaults to False, indicates if the skiptoken should be used
                in the where clause.  If True then the query is limited to
                entities appearing after the skiptoken's value (see below).

        null_cols
                An iterable of mangled column names that must be NULL (defaults
                to an empty tuple).  This argument is used during updates to
                prevent the replacement of non-NULL foreign keys.

        The operation of the skiptoken deserves some explanation.  When in
        play the skiptoken contains the last value of the order expression
        returned.  The order expression always uses the keys to ensure
        unambiguous ordering.  The clause added is best served with an
        example.  If an entity has key K and an order expression such
        as "tolower(Name) desc" then the query will contain
        something like::

                SELECT K, Nname, DOB, LOWER(Name) AS o_1, K ....
                        WHERE (o_1 < ? OR (o_1 = ? AND K > ?))

        The values from the skiptoken will be passed as parameters."""
        where = []
        if entity is not None:
            self.where_entity_clause(where, entity, params)
        if self.filter is not None and use_filter:
            # use_filter option adds the current filter too
            where.append('(' + self.sql_expression(self.filter, params) + ')')
        if self.skiptoken is not None and use_skip:
            self.where_skiptoken_clause(where, params)
        for nullCol in null_cols:
            where.append('%s IS NULL' % nullCol)
        if where:
            return ' WHERE ' + string.join(where, ' AND ')
        else:
            return ''

    def where_entity_clause(self, where, entity, params):
        """Adds the entity constraint expression to a list of SQL expressions.

        where
                The list to append the entity expression to.

        entity
                An expression is added to restrict the query to this entity"""
        for k, v in entity.KeyDict().items():
            where.append(
                '%s=%s' %
                (self.container.mangled_names[
                    (self.entity_set.name, k)], params.add_param(
                    self.container.prepare_sql_value(v))))

    def where_skiptoken_clause(self, where, params):
        """Adds the entity constraint expression to a list of SQL expressions.

        where
                The list to append the skiptoken expression to."""
        skip_expression = []
        i = ket = 0
        while True:
            oname, dir = self.orderNames[i]
            v = self.skiptoken[i]
            op = ">" if dir > 0 else "<"
            skip_expression.append(
                "(%s %s %s" %
                (oname,
                 op,
                 params.add_param(
                     self.container.prepare_sql_value(v))))
            ket += 1
            i += 1
            if i < len(self.orderNames):
                # more to come
                skip_expression.append(
                    " OR (%s = %s AND " %
                    (oname, params.add_param(
                        self.container.prepare_sql_value(v))))
                ket += 1
                continue
            else:
                skip_expression.append(u")" * ket)
                break
        where.append(string.join(skip_expression, ''))

    def set_orderby(self, orderby):
        """Sets the orderby rules for this collection.

        We override the default implementation to calculate a list
        of field name aliases to use in ordered queries.  For example,
        if the orderby expression is "tolower(Name) desc" then each SELECT
        query will be generated with an additional expression, e.g.::

                SELECT ID, Name, DOB, LOWER(Name) AS o_1 ...
                    ORDER BY o_1 DESC, ID ASC

        The name "o_1" is obtained from the name mangler using the tuple::

                (entity_set.name,'o_1')

        Subsequent order expressions have names 'o_2', 'o_3', etc.

        Notice that regardless of the ordering expression supplied the
        keys are always added to ensure that, when an ordering is
        required, a defined order results even at the expense of some
        redundancy."""
        self.orderby = orderby
        self.set_page(None)
        self.orderNames = []
        if self.orderby is not None:
            oi = 0
            for expression, direction in self.orderby:
                oi = oi + 1
                oname = "o_%i" % oi
                oname = self.container.mangled_names.get(
                    (self.entity_set.name, oname), oname)
                self.orderNames.append((oname, direction))
        for key in self.entity_set.keys:
            mangled_name = self.container.mangled_names[
                (self.entity_set.name, key)]
            if self.qualify_names:
                mangled_name = "%s.%s" % (self.table_name, mangled_name)
            self.orderNames.append((mangled_name, 1))
        self._sqlGen = None

    def orderby_clause(self):
        """A utility method to return the orderby clause.

        params
                The :py:class:`SQLParams` object to add parameters to."""
        if self.orderNames:
            orderby = []
            for expression, direction in self.orderNames:
                orderby.append(
                    "%s %s" % (expression, "DESC" if direction < 0 else "ASC"))
            return ' ORDER BY ' + string.join(orderby, u", ")
        else:
            return ''

    def orderby_cols(self, column_names, params, force_order=False):
        """A utility to add the column names and aliases for the ordering.

        column_names
            A list of SQL column name/alias expressions

        params
            The :py:class:`SQLParams` object to add parameters to.

        force_order
            Forces the addition of an ordering by key if an orderby
            expression has not been set."""
        oname_index = 0
        if self.orderby is not None:
            for expression, direction in self.orderby:
                oname, odir = self.orderNames[oname_index]
                oname_index += 1
                sql_expression = self.sql_expression(expression, params)
                column_names.append("%s AS %s" % (sql_expression, oname))
        if self.orderby is not None or force_order:
            # add the remaining names (which are just the keys)
            while oname_index < len(self.orderNames):
                oname, odir = self.orderNames[oname_index]
                oname_index += 1
                column_names.append(oname)

    def _mangle_name(self, source_path):
        mangled_name = self.container.mangled_names[source_path]
        if self.qualify_names:
            mangled_name = "%s.%s" % (self.table_name, mangled_name)
        return mangled_name

    def insert_fields(self, entity):
        """A generator for inserting mangled property names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).

        Read only fields are never generated, even if they are keys.
        This allows automatically generated keys to be used and also
        covers the more esoteric use case where a foreign key constraint
        exists on the primary key (or part thereof) - in the latter case
        the relationship should be marked as required to prevent
        unexpected constraint violations.

        Otherwise, only selected fields are yielded so if you attempt to
        insert a value without selecting the key fields you can expect a
        constraint violation unless the key is read only."""
        for k, v in entity.data_items():
            source_path = (self.entity_set.name, k)
            if (source_path not in self.container.ro_names and
                    entity.Selected(k)):
                if isinstance(v, edm.SimpleValue):
                    yield self._mangle_name(source_path), v
                else:
                    for sub_path, fv in self._complex_field_generator(v):
                        source_path = tuple([self.entity_set.name, k] +
                                            sub_path)
                        yield self._mangle_name(source_path), fv

    def auto_fields(self, entity):
        """A generator for selecting auto mangled property names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).

        Only fields that are read only are yielded with the caveat that
        they must also be either selected or keys.  The purpose of this
        method is to assist with reading back automatically generated
        field values after an insert or update."""
        keys = entity.entity_set.keys
        for k, v in entity.data_items():
            source_path = (self.entity_set.name, k)
            if (source_path in self.container.ro_names and (
                    entity.Selected(k) or k in keys)):
                if isinstance(v, edm.SimpleValue):
                    yield self._mangle_name(source_path), v
                else:
                    for sub_path, fv in self._complex_field_generator(v):
                        source_path = tuple([self.entity_set.name, k] +
                                            sub_path)
                        yield self._mangle_name(source_path), fv

    def key_fields(self, entity):
        """A generator for selecting mangled key names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).
        Only the keys fields are yielded."""
        for k in entity.entity_set.keys:
            v = entity[k]
            source_path = (self.entity_set.name, k)
            yield self._mangle_name(source_path), v

    def select_fields(self, entity):
        """A generator for selecting mangled property names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).
        Only selected fields are yielded with the caveat that the keys
        are always selected."""
        keys = entity.entity_set.keys
        for k, v in entity.data_items():
            source_path = (self.entity_set.name, k)
            if (k in keys or entity.Selected(k)):
                if isinstance(v, edm.SimpleValue):
                    yield self._mangle_name(source_path), v
                else:
                    for sub_path, fv in self._complex_field_generator(v):
                        source_path = tuple([self.entity_set.name, k] +
                                            sub_path)
                        yield self._mangle_name(source_path), fv

    def update_fields(self, entity):
        """A generator for updating mangled property names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).

        Neither read only fields nor key are generated.  All other
        fields are yielded but unselected fields are set to NULL before
        being yielded. This implements OData's PUT semantics.  See
        :py:meth:`merge_fields` for an alternative."""
        keys = entity.entity_set.keys
        for k, v in entity.data_items():
            source_path = (self.entity_set.name, k)
            if k in keys or source_path in self.container.ro_names:
                continue
            if not entity.Selected(k):
                v.SetNull()
            if isinstance(v, edm.SimpleValue):
                yield self._mangle_name(source_path), v
            else:
                for sub_path, fv in self._complex_field_generator(v):
                    source_path = tuple([self.entity_set.name, k] +
                                        sub_path)
                    yield self._mangle_name(source_path), fv

    def merge_fields(self, entity):
        """A generator for merging mangled property names and values.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        The yielded values are tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance).

        Neither read only fields, keys nor unselected fields are
        generated. All other fields are yielded implementing OData's
        MERGE semantics.  See
        :py:meth:`update_fields` for an alternative."""
        keys = entity.entity_set.keys
        for k, v in entity.data_items():
            source_path = (self.entity_set.name, k)
            if (k in keys or
                    source_path in self.container.ro_names or
                    not entity.Selected(k)):
                continue
            if isinstance(v, edm.SimpleValue):
                yield self._mangle_name(source_path), v
            else:
                for sub_path, fv in self._complex_field_generator(v):
                    source_path = tuple([self.entity_set.name, k] +
                                        sub_path)
                    yield self._mangle_name(source_path), fv

    def _complex_field_generator(self, ct):
        for k, v in ct.iteritems():
            if isinstance(v, edm.SimpleValue):
                yield [k], v
            else:
                for source_path, fv in self._complex_field_generator(v):
                    yield [k] + source_path, fv

    def stream_field(self, entity):
        """Returns information for selecting the stream ID.

        entity
            Any instance of :py:class:`~pyslet.odata2.csdl.Entity`

        Returns a tuples of (mangled field name,
        :py:class:`~pyslet.odata2.csdl.SimpleValue` instance)."""
        source_path = (self.entity_set.name, '_value')
        return self._mangle_name(source_path), \
            edm.EDMValue.NewSimpleValue(edm.SimpleType.Int64)

    SQLBinaryExpressionMethod = {}
    SQLCallExpressionMethod = {}

    def sql_expression(self, expression, params, context="AND"):
        """Converts an expression into a SQL expression string.

        expression
                A :py:class:`pyslet.odata2.core.CommonExpression` instance.

        params
                A :py:class:`SQLParams` object of the appropriate type for
                this database connection.

        context
                A string containing the SQL operator that provides the
                context in which the expression is being converted, defaults
                to 'AND'. This is used to determine if the resulting
                expression must be bracketed or not.  See
                :py:meth:`sql_bracket` for a useful utility function to
                illustrate this.

        This method is basically a grand dispatcher that sends calls to
        other node-specific methods with similar signatures.  The effect
        is to traverse the entire tree rooted at *expression*.

        The result is a string containing the parameterized expression
        with appropriate values added to the *params* object *in the same
        sequence* that they appear in the returned SQL expression.

        When creating derived classes to implement database-specific
        behaviour you should override the individual evaluation methods
        rather than this method.  All related methods have the same
        signature.

        Where methods are documented as having no default implementation,
        NotImplementedError is raised."""
        if isinstance(expression, core.UnaryExpression):
            raise NotImplementedError
        elif isinstance(expression, core.BinaryExpression):
            return getattr(
                self,
                self.SQLBinaryExpressionMethod[
                    expression.operator])(
                expression,
                params,
                context)
        elif isinstance(expression, UnparameterizedLiteral):
            return unicode(expression.value)
        elif isinstance(expression, core.LiteralExpression):
            return params.add_param(
                self.container.prepare_sql_value(
                    expression.value))
        elif isinstance(expression, core.PropertyExpression):
            try:
                p = self.entity_set.entityType[expression.name]
                if isinstance(p, edm.Property):
                    if p.complexType is None:
                        field_name = self.container.mangled_names[
                            (self.entity_set.name, expression.name)]
                        if self.qualify_names:
                            return "%s.%s" % (self.table_name, field_name)
                        else:
                            return field_name
                    else:
                        raise core.EvaluationError(
                            "Unqualified property %s "
                            "must refer to a simple type" %
                            expression.name)
            except KeyError:
                raise core.EvaluationError(
                    "Property %s is not declared" % expression.name)
        elif isinstance(expression, core.CallExpression):
            return getattr(
                self,
                self.SQLCallExpressionMethod[
                    expression.method])(
                expression,
                params,
                context)

    def sql_bracket(self, query, context, operator):
        """A utility method for bracketing a SQL query.

        query
                The query string

        context
                A string representing the SQL operator that defines the
                context in which the query is to placed.  E.g., 'AND'

        operator
                The dominant operator in the query.

        This method is used by operator-specific conversion methods.
        The query is not parsed, it is merely passed in as a string to be
        bracketed (or not) depending on the values of *context* and
        *operator*.

        The implementation is very simple, it checks the precedence of
        *operator* in *context* and returns *query* bracketed if
        necessary::

                collection.sql_bracket("Age+3","*","+")=="(Age+3)"
                collection.sql_bracket("Age*3","+","*")=="Age*3" """
        if SQLOperatorPrecedence[context] > SQLOperatorPrecedence[operator]:
            return "(%s)" % query
        else:
            return query

    def sql_expression_member(self, expression, params, context):
        """Converts a member expression, e.g., Address/City

        This implementation does not support the use of navigation
        properties but does support references to complex properties.

        It outputs the mangled name of the property, qualified by the
        table name if :py:attr:`qualify_names` is True."""
        name_list = self._calculate_member_field_name(expression)
        context_def = self.entity_set.entityType
        for name in name_list:
            if context_def is None:
                raise core.EvaluationError("Property %s is not declared" %
                                           string.join(name_list, '/'))
            p = context_def[name]
            if isinstance(p, edm.Property):
                if p.complexType is not None:
                    context_def = p.complexType
                else:
                    context_def = None
            elif isinstance(p, edm.NavigationProperty):
                raise NotImplementedError("Use of navigation properties in "
                                          "expressions not supported")
        # the result must be a simple property, so context_def must not be None
        if context_def is not None:
            raise core.EvaluationError(
                "Property %s does not reference a primitive type" %
                string.join(
                    name_list,
                    '/'))
        field_name = self.container.mangled_names[
            tuple([self.entity_set.name] + name_list)]
        if self.qualify_names:
            return "%s.%s" % (self.table_name, field_name)
        else:
            return field_name

    def _calculate_member_field_name(self, expression):
        if isinstance(expression, core.PropertyExpression):
            return [expression.name]
        elif (isinstance(expression, core.BinaryExpression) and
                expression.operator == core.Operator.member):
            return (
                self._calculate_member_field_name(expression.operands[0]) +
                self._calculate_member_field_name(expression.operands[1]))
        else:
            raise core.EvaluationError("Unexpected use of member expression")

    def sql_expression_cast(self, expression, params, context):
        """Converts the cast expression: no default implementation"""
        raise NotImplementedError

    def sql_expression_generic_binary(
            self,
            expression,
            params,
            context,
            operator):
        """A utility method for implementing binary operator conversion.

        The signature of the basic :py:meth:`sql_expression` is extended
        to include an *operator* argument, a string representing the
        (binary) SQL operator corresponding to the expression object."""
        query = []
        query.append(
            self.sql_expression(expression.operands[0], params, operator))
        query.append(u' ')
        query.append(operator)
        query.append(u' ')
        query.append(
            self.sql_expression(expression.operands[1], params, operator))
        return self.sql_bracket(string.join(query, ''), context, operator)

    def sql_expression_mul(self, expression, params, context):
        """Converts the mul expression: maps to SQL "*" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '*')

    def sql_expression_div(self, expression, params, context):
        """Converts the div expression: maps to SQL "/" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '/')

    def sql_expression_mod(self, expression, params, context):
        """Converts the mod expression: no default implementation"""
        raise NotImplementedError

    def sql_expression_add(self, expression, params, context):
        """Converts the add expression: maps to SQL "+" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '+')

    def sql_expression_sub(self, expression, params, context):
        """Converts the sub expression: maps to SQL "-" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '-')

    def sql_expression_lt(self, expression, params, context):
        """Converts the lt expression: maps to SQL "<" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '<')

    def sql_expression_gt(self, expression, params, context):
        """Converts the gt expression: maps to SQL ">" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '>')

    def sql_expression_le(self, expression, params, context):
        """Converts the le expression: maps to SQL "<=" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '<=')

    def sql_expression_ge(self, expression, params, context):
        """Converts the ge expression: maps to SQL ">=" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '>=')

    def sql_expression_isof(self, expression, params, context):
        """Converts the isof expression: no default implementation"""
        raise NotImplementedError

    def sql_expression_eq(self, expression, params, context):
        """Converts the eq expression: maps to SQL "=" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '=')

    def sql_expression_ne(self, expression, params, context):
        """Converts the ne expression: maps to SQL "<>" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            '<>')

    def sql_expression_and(self, expression, params, context):
        """Converts the and expression: maps to SQL "AND" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            'AND')

    def sql_expression_or(self, expression, params, context):
        """Converts the or expression: maps to SQL "OR" """
        return self.sql_expression_generic_binary(
            expression,
            params,
            context,
            'OR')

    def sql_expression_endswith(self, expression, params, context):
        """Converts the endswith function: maps to "op[0] LIKE '%'+op[1]"

        This is implemented using the concatenation operator"""
        percent = edm.SimpleValue.NewSimpleValue(edm.SimpleType.String)
        percent.set_from_value(u"'%'")
        percent = UnparameterizedLiteral(percent)
        concat = core.CallExpression(core.Method.concat)
        concat.operands.append(percent)
        concat.operands.append(expression.operands[1])
        query = []
        query.append(
            self.sql_expression(expression.operands[0], params, 'LIKE'))
        query.append(" LIKE ")
        query.append(self.sql_expression(concat, params, 'LIKE'))
        return self.sql_bracket(string.join(query, ''), context, 'LIKE')

    def sql_expression_indexof(self, expression, params, context):
        """Converts the indexof method: maps to POSITION( op[0] IN op[1] )"""
        query = [u"POSITION("]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(u" IN ")
        query.append(self.sql_expression(expression.operands[1], params, ','))
        query.append(u")")
        return string.join(query, '')

    def sql_expression_replace(self, expression, params, context):
        """Converts the replace method: no default implementation"""
        raise NotImplementedError

    def sql_expression_startswith(self, expression, params, context):
        """Converts the startswith function: maps to "op[0] LIKE op[1]+'%'"

        This is implemented using the concatenation operator"""
        percent = edm.SimpleValue.NewSimpleValue(edm.SimpleType.String)
        percent.set_from_value(u"'%'")
        percent = UnparameterizedLiteral(percent)
        concat = core.CallExpression(core.Method.concat)
        concat.operands.append(expression.operands[1])
        concat.operands.append(percent)
        query = []
        query.append(
            self.sql_expression(expression.operands[0], params, 'LIKE'))
        query.append(" LIKE ")
        query.append(self.sql_expression(concat, params, 'LIKE'))
        return self.sql_bracket(string.join(query, ''), context, 'LIKE')

    def sql_expression_tolower(self, expression, params, context):
        """Converts the tolower method: maps to LOWER function"""
        return u"LOWER(%s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_toupper(self, expression, params, context):
        """Converts the toupper method: maps to UCASE function"""
        return u"UPPER(%s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_trim(self, expression, params, context):
        """Converts the trim method: maps to TRIM function"""
        return u"TRIM(%s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_substring(self, expression, params, context):
        """Converts the substring method

        maps to SUBSTRING( op[0] FROM op[1] [ FOR op[2] ]"""
        query = [u"SUBSTRING("]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(u" FROM ")
        query.append(self.sql_expression(expression.operands[1], params, ','))
        if len(expression.operands > 2):
            query.append(u" FOR ")
            query.append(
                self.sql_expression(expression.operands[2], params, ','))
        query.append(u")")
        return string.join(query, '')

    def sql_expression_substringof(self, expression, params, context):
        """Converts the substringof function

        maps to "op[1] LIKE '%'+op[0]+'%'"

        To do this we need to invoke the concatenation operator.

        This method has been poorly defined in OData with the parameters
        being switched between versions 2 and 3.  It is being withdrawn
        as a result and replaced with contains in OData version 4.  We
        follow the version 3 convention here of "first parameter in the
        second parameter" which fits better with the examples and with
        the intuitive meaning::

                substringof(A,B) == A in B"""
        percent = edm.SimpleValue.NewSimpleValue(edm.SimpleType.String)
        percent.set_from_value(u"'%'")
        percent = UnparameterizedLiteral(percent)
        rconcat = core.CallExpression(core.Method.concat)
        rconcat.operands.append(expression.operands[0])
        rconcat.operands.append(percent)
        lconcat = core.CallExpression(core.Method.concat)
        lconcat.operands.append(percent)
        lconcat.operands.append(rconcat)
        query = []
        query.append(
            self.sql_expression(expression.operands[1], params, 'LIKE'))
        query.append(" LIKE ")
        query.append(self.sql_expression(lconcat, params, 'LIKE'))
        return self.sql_bracket(string.join(query, ''), context, 'LIKE')

    def sql_expression_concat(self, expression, params, context):
        """Converts the concat method: maps to ||"""
        query = []
        query.append(self.sql_expression(expression.operands[0], params, '*'))
        query.append(u' || ')
        query.append(self.sql_expression(expression.operands[1], params, '*'))
        return self.sql_bracket(string.join(query, ''), context, '*')

    def sql_expression_length(self, expression, params, context):
        """Converts the length method: maps to CHAR_LENGTH( op[0] )"""
        return u"CHAR_LENGTH(%s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_year(self, expression, params, context):
        """Converts the year method: maps to EXTRACT(YEAR FROM op[0])"""
        return u"EXTRACT(YEAR FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_month(self, expression, params, context):
        """Converts the month method: maps to EXTRACT(MONTH FROM op[0])"""
        return u"EXTRACT(MONTH FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_day(self, expression, params, context):
        """Converts the day method: maps to EXTRACT(DAY FROM op[0])"""
        return u"EXTRACT(DAY FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_hour(self, expression, params, context):
        """Converts the hour method: maps to EXTRACT(HOUR FROM op[0])"""
        return u"EXTRACT(HOUR FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_minute(self, expression, params, context):
        """Converts the minute method: maps to EXTRACT(MINUTE FROM op[0])"""
        return u"EXTRACT(MINUTE FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_second(self, expression, params, context):
        """Converts the second method: maps to EXTRACT(SECOND FROM op[0])"""
        return u"EXTRACT(SECOND FROM %s)" % self.sql_expression(
            expression.operands[0],
            params,
            ',')

    def sql_expression_round(self, expression, params, context):
        """Converts the round method: no default implementation"""
        raise NotImplementedError

    def sql_expression_floor(self, expression, params, context):
        """Converts the floor method: no default implementation"""
        raise NotImplementedError

    def sql_expression_ceiling(self, expression, params, context):
        """Converts the ceiling method: no default implementation"""
        raise NotImplementedError


SQLCollectionBase.SQLCallExpressionMethod = {
    core.Method.endswith: 'sql_expression_endswith',
    core.Method.indexof: 'sql_expression_indexof',
    core.Method.replace: 'sql_expression_replace',
    core.Method.startswith: 'sql_expression_startswith',
    core.Method.tolower: 'sql_expression_tolower',
    core.Method.toupper: 'sql_expression_toupper',
    core.Method.trim: 'sql_expression_trim',
    core.Method.substring: 'sql_expression_substring',
    core.Method.substringof: 'sql_expression_substringof',
    core.Method.concat: 'sql_expression_concat',
    core.Method.length: 'sql_expression_length',
    core.Method.year: 'sql_expression_year',
    core.Method.month: 'sql_expression_month',
    core.Method.day: 'sql_expression_day',
    core.Method.hour: 'sql_expression_hour',
    core.Method.minute: 'sql_expression_minute',
    core.Method.second: 'sql_expression_second',
    core.Method.round: 'sql_expression_round',
    core.Method.floor: 'sql_expression_floor',
    core.Method.ceiling: 'sql_expression_ceiling'
}

SQLCollectionBase.SQLBinaryExpressionMethod = {
    core.Operator.member: 'sql_expression_member',
    core.Operator.cast: 'sql_expression_cast',
    core.Operator.mul: 'sql_expression_mul',
    core.Operator.div: 'sql_expression_div',
    core.Operator.mod: 'sql_expression_mod',
    core.Operator.add: 'sql_expression_add',
    core.Operator.sub: 'sql_expression_sub',
    core.Operator.lt: 'sql_expression_lt',
    core.Operator.gt: 'sql_expression_gt',
    core.Operator.le: 'sql_expression_le',
    core.Operator.ge: 'sql_expression_ge',
    core.Operator.isof: 'sql_expression_isof',
    core.Operator.eq: 'sql_expression_eq',
    core.Operator.ne: 'sql_expression_ne',
    core.Operator.boolAnd: 'sql_expression_and',
    core.Operator.boolOr: 'sql_expression_or'
}


class SQLEntityCollection(SQLCollectionBase):

    """Represents a collection of entities from an :py:class:`EntitySet`.

    This class is the heart of the SQL implementation of the API,
    constructing and executing queries to implement the core methods
    from :py:class:`pyslet.odata2.csdl.EntityCollection`."""

    def insert_entity(self, entity):
        """Inserts *entity* into the collection.

        We override this method, rerouting it to a SQL-specific
        implementation that takes additional arguments."""
        self.insert_entity_sql(entity)

    def new_stream(self, src, sinfo=None, key=None):
        e = self.new_entity()
        if key is None:
            e.auto_key()
        else:
            e.set_key(key)
        if sinfo is None:
            sinfo = core.StreamInfo()
        etag = e.ETagValues()
        if len(etag) == 1 and isinstance(etag[0], edm.BinaryValue):
            h = hashlib.sha256()
            etag = etag[0]
        else:
            h = None
        c, v = self.stream_field(e)
        if self.container.streamstore:
            # spool the data into the store and store the stream key
            estream = self.container.streamstore.new_stream(sinfo.type,
                                                            sinfo.created)
            with self.container.streamstore.open_stream(estream, 'w') as dst:
                sinfo.size, sinfo.md5 = self._copy_src(src, dst, sinfo.size, h)
            if sinfo.modified is not None:
                # force modified date based on input
                estream['modified'].set_from_value(sinfo.modified.ShiftZone(0))
                estream.Update()
            v.set_from_value(estream.key())
        else:
            raise NotImplementedError
        if h is not None:
            etag.set_from_value(h.digest())
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            # now try the insert and loop with random keys if required
            for i in xrange(100):
                try:
                    self.insert_entity_sql(e, transaction=transaction)
                    break
                except edm.ConstraintError:
                    # try a different key
                    e.auto_key()
            if not e.exists:
                # give up - we can't insert anything
                logging.error("Failed to find an unused key in %s "
                              "after 100 attempts", e.entity_set.name)
                raise edm.SQLError("Auto-key failure")
            # finally, store the stream value for the entity
            query = ['UPDATE ', self.table_name, ' SET ']
            params = self.container.ParamsClass()
            query.append(
                "%s=%s" %
                (c, params.add_param(self.container.prepare_sql_value(v))))
            query.append(' WHERE ')
            for k, kv in e.KeyDict().items():
                query.append(
                    '%s=%s' %
                    (self.container.mangled_names[(self.entity_set.name, k)],
                     params.add_param(self.container.prepare_sql_value(kv))))
            query = string.join(query, '')
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
        except Exception as e:
            # we allow the stream store to re-use the same database but
            # this means we can't transact on both at once (from the
            # same thread) - settle for logging at the moment
            # self.container.streamstore.delete_stream(estream)
            logging.error("Orphan stream created %s[%i]",
                          estream.entity_set.name, estream.key())
            transaction.rollback(e)
        finally:
            transaction.close()
        return e

    def insert_entity_sql(
            self,
            entity,
            from_end=None,
            fk_values=None,
            transaction=None):
        """Inserts *entity* into the collection.

        This method is not designed to be overridden by other
        implementations but it does extend the default functionality for
        a more efficient implementation and to enable better
        transactional processing. The additional parameters are
        documented here.

        from_end
                An optional :py:class:`pyslet.odata2.csdl.AssociationSetEnd`
                bound to this entity set.  If present, indicates that this
                entity is being inserted as part of a single transaction
                involving an insert or update to the other end of the
                association.

                This suppresses any check for a required link via this
                association (as it is assumed that the link is present, or
                will be, in the same transaction).

        fk_values
                If the association referred to by *from_end* is represented
                by a set of foreign keys stored in this entity set's table
                (see :py:class:`SQLReverseKeyCollection`) then fk_values is
                the list of (mangled column name, value) tuples that must be
                inserted in order to create the link.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted.

        The method functions in three phases.

        1.  Process all bindings for which we hold the foreign key.
            This includes inserting new entities where deep inserts are
            being used or calculating foreign key values where links to
            existing entities have been specified on creation.

            In addition, all required links are checked and raise errors
            if no binding is present.

        2.  A simple SQL INSERT statement is executed to add the record
            to the database along with any foreign keys generated in (1)
            or passed in *fk_values*.

        3.  Process all remaining bindings.  Although we could do this
            using the
            :py:meth:`~pyslet.odata2.csdl.DeferredValue.update_bindings`
            method of DeferredValue we handle this directly to retain
            transactional integrity (where supported).

            Links to existing entities are created using the insert_link
            method available on the SQL-specific
            :py:class:`SQLNavigationCollection`.

            Deep inserts are handled by a recursive call to this method.
            After step 1, the only bindings that remain are (a) those
            that are stored at the other end of the link and so can be
            created by passing values for *from_end* and *fk_values* in a
            recursive call or (b) those that are stored in a separate
            table which are created by combining a recursive call and a
            call to insert_link.

        Required links are always created in step 1 because the
        overarching mapping to SQL forces such links to be represented
        as foreign keys in the source table (i.e., this table) unless
        the relationship is 1-1, in which case the link is created in
        step 3 and our database is briefly in violation of the model. If
        the underlying database API does not support transactions then
        it is possible for this state to persist resulting in an orphan
        entity or entities, i.e., entities with missing required links.
        A failed :py:meth:`rollback` call will log this condition along
        with the error that caused it."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        if entity.exists:
            raise edm.EntityExists(str(entity.GetLocation()))
        # We must also go through each bound navigation property of our
        # own and add in the foreign keys for forward links.
        if fk_values is None:
            fk_values = []
        fk_mapping = self.container.fk_table[self.entity_set.name]
        try:
            transaction.begin()
            nav_done = set()
            for link_end, nav_name in self.entity_set.linkEnds.iteritems():
                if nav_name:
                    dv = entity[nav_name]
                if (link_end.otherEnd.associationEnd.multiplicity ==
                        edm.Multiplicity.One):
                    # a required association
                    if link_end == from_end:
                        continue
                    if nav_name is None:
                        # unbound principal; can only be created from this
                        # association
                        raise edm.NavigationError(
                            "Entities in %s can only be created "
                            "from their principal" % self.entity_set.name)
                    if not dv.bindings:
                        raise edm.NavigationError(
                            "Required navigation property %s of %s "
                            "is not bound" % (nav_name, self.entity_set.name))
                aset_name = link_end.parent.name
                # if link_end is in fk_mapping it means we are keeping a
                # foreign key for this property, it may even be required but
                # either way, let's deal with it now.  We're only interested
                # in associations that are bound to navigation properties.
                if link_end not in fk_mapping or nav_name is None:
                    continue
                nullable, unique = fk_mapping[link_end]
                target_set = link_end.otherEnd.entity_set
                if len(dv.bindings) == 0:
                    # we've already checked the case where nullable is False
                    # above
                    continue
                elif len(dv.bindings) > 1:
                    raise edm.NavigationError(
                        "Unexpected error: found multiple bindings "
                        "for foreign key constraint %s" % nav_name)
                binding = dv.bindings[0]
                if not isinstance(binding, edm.Entity):
                    # just a key, grab the entity
                    with target_set.OpenCollection() as targetCollection:
                        targetCollection.SelectKeys()
                        target_entity = targetCollection[binding]
                    dv.bindings[0] = target_entity
                else:
                    target_entity = binding
                    if not target_entity.exists:
                        # add this entity to it's base collection
                        with target_set.OpenCollection() as targetCollection:
                            targetCollection.insert_entity_sql(
                                target_entity,
                                link_end.otherEnd,
                                transaction=transaction)
                # Finally, we have a target entity, add the foreign key to
                # fk_values
                for key_name in target_set.keys:
                    fk_values.append(
                        (self.container.mangled_names[
                            (self.entity_set.name,
                             aset_name,
                             key_name)],
                            target_entity[key_name]))
                nav_done.add(nav_name)
            # Step 2
            try:
                entity.key()
            except KeyError:
                # missing key on insert, auto-generate if we can
                for i in xrange(100):
                    entity.auto_key()
                    if not self.test_key(entity, transaction):
                        break
            entity.SetConcurrencyTokens()
            query = ['INSERT INTO ', self.table_name, ' (']
            insert_values = list(self.insert_fields(entity))
            # watch out for exposed FK fields!
            for fkname, fkv in fk_values:
                i = 0
                while i < len(insert_values):
                    iname, iv = insert_values[i]
                    if fkname == iname:
                        # fk overrides - update the entity's value
                        iv.set_from_value(fkv.value)
                        # now drop it from the list to prevent
                        # double column names
                        del insert_values[i]
                    else:
                        i += 1
            column_names, values = zip(
                *(insert_values + fk_values))
            query.append(string.join(column_names, ", "))
            query.append(') VALUES (')
            params = self.container.ParamsClass()
            query.append(string.join(
                map(lambda x: params.add_param(
                    self.container.prepare_sql_value(x)), values), ", "))
            query.append(')')
            query = string.join(query, '')
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            # before we can say the entity exists we need to ensure
            # we have the key
            auto_fields = list(self.auto_fields(entity))
            if auto_fields:
                # refresh these fields in the entity
                self.get_auto(entity, auto_fields, transaction)
            entity.exists = True
            # Step 3
            for k, dv in entity.NavigationItems():
                link_end = self.entity_set.navigation[k]
                if not dv.bindings:
                    continue
                elif k in nav_done:
                    dv.bindings = []
                    continue
                aset_name = link_end.parent.name
                target_set = dv.Target()
                target_fk_mapping = self.container.fk_table[target_set.name]
                with dv.OpenCollection() as navCollection:
                    with target_set.OpenCollection() as targetCollection:
                        while dv.bindings:
                            binding = dv.bindings[0]
                            if not isinstance(binding, edm.Entity):
                                targetCollection.SelectKeys()
                                binding = targetCollection[binding]
                            if binding.exists:
                                navCollection.insert_link(binding, transaction)
                            else:
                                if link_end.otherEnd in target_fk_mapping:
                                    # target table has a foreign key
                                    target_fk_values = []
                                    for key_name in self.entity_set.keys:
                                        target_fk_values.append(
                                            (self.container.mangled_names[
                                                (target_set.name,
                                                 aset_name,
                                                 key_name)],
                                                entity[key_name]))
                                    targetCollection.insert_entity_sql(
                                        binding,
                                        link_end.otherEnd,
                                        target_fk_values,
                                        transaction=transaction)
                                else:
                                    # foreign keys are in an auxiliary table
                                    targetCollection.insert_entity_sql(
                                        binding,
                                        link_end.otherEnd,
                                        transaction=transaction)
                                    navCollection.insert_link(
                                        binding, transaction)
                            dv.bindings = dv.bindings[1:]
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            # we might need to distinguish between a failure due to
            # fk_values or a missing key
            transaction.rollback(e, swallow=True)
            # swallow the error as this should indicate a failure at the
            # point of INSERT, fk_values may have violated a unique
            # constraint but we can't make that distinction at the
            # moment.
            raise edm.ConstraintError(
                "insert_entity failed for %s : %s" %
                (str(
                    entity.GetLocation()),
                    str(e)))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def get_auto(self, entity, auto_fields, transaction):
        params = self.container.ParamsClass()
        query = ["SELECT "]
        column_names, values = zip(*auto_fields)
        query.append(string.join(column_names, ", "))
        query.append(' FROM ')
        query.append(self.table_name)
        # no join clause required
        if self.auto_keys:
            query.append(self.where_last(entity, params))
        else:
            query.append(self.where_clause(entity, params, use_filter=False))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            rowcount = transaction.cursor.rowcount
            row = transaction.cursor.fetchone()
            if rowcount == 0 or row is None:
                raise KeyError
            elif rowcount > 1 or (rowcount == -1 and
                                  transaction.cursor.fetchone() is not None):
                # whoops, that was unexpected
                raise SQLError(
                    "Integrity check failure, non-unique key after insert")
            for value, new_value in zip(values, row):
                self.container.read_sql_value(value, new_value)
            entity.Expand(self.expand, self.select)
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def test_key(self, entity, transaction):
        params = self.container.ParamsClass()
        query = ["SELECT "]
        column_names, values = zip(*list(self.key_fields(entity)))
        query.append(string.join(column_names, ", "))
        query.append(' FROM ')
        query.append(self.table_name)
        query.append(self.where_clause(entity, params, use_filter=False))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            rowcount = transaction.cursor.rowcount
            row = transaction.cursor.fetchone()
            if rowcount == 0 or row is None:
                result = False
            elif rowcount > 1 or (rowcount == -1 and
                                  transaction.cursor.fetchone() is not None):
                # whoops, that was unexpected
                raise SQLError(
                    "Integrity check failure, non-unique key: %s" %
                    repr(entity.key()))
            else:
                result = True
            transaction.commit()
            return result
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def where_last(self, entity, params):
        raise NotImplementedError("Automatic keys not supported")

    def update_entity(self, entity):
        """Updates *entity*

        This method follows a very similar pattern to :py:meth:`InsertMethod`,
        using a three-phase process.

        1.  Process all bindings for which we hold the foreign key.
                This includes inserting new entities where deep inserts are
                being used or calculating foreign key values where links to
                existing entities have been specified on update.

        2.  A simple SQL UPDATE statement is executed to update the
                record in the database along with any updated foreign keys
                generated in (1).

        3.  Process all remaining bindings while retaining transactional
                integrity (where supported).

                Links to existing entities are created using the insert_link
                or replace methods available on the SQL-specific
                :py:class:`SQLNavigationCollection`.  The replace method is
                used when a navigation property that links to a single
                entity has been bound.  Deep inserts are handled by calling
                insert_entity_sql before the link is created.

        The same transactional behaviour as :py:meth:`insert_entity_sql` is
        exhibited."""
        if not entity.exists:
            raise edm.NonExistentEntity(
                "Attempt to update non existent entity: " +
                str(entity.GetLocation()))
            fk_values = []
        fk_values = []
        fk_mapping = self.container.fk_table[self.entity_set.name]
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            nav_done = set()
            for k, dv in entity.NavigationItems():
                link_end = self.entity_set.navigation[k]
                if not dv.bindings:
                    continue
                aset_name = link_end.parent.name
                # if link_end is in fk_mapping it means we are keeping a
                # foreign key for this property, it may even be required but
                # either way, let's deal with it now.  This will insert or
                # update the link automatically, this navigation property
                # can never be a collection
                if link_end not in fk_mapping:
                    continue
                target_set = link_end.otherEnd.entity_set
                nullable, unique = fk_mapping[link_end]
                if len(dv.bindings) > 1:
                    raise edm.NavigationError(
                        "Unexpected error: found multiple bindings for "
                        "foreign key constraint %s" % k)
                binding = dv.bindings[0]
                if not isinstance(binding, edm.Entity):
                    # just a key, grab the entity
                    with target_set.OpenCollection() as targetCollection:
                        targetCollection.SelectKeys()
                        target_entity = targetCollection[binding]
                    dv.bindings[0] = target_entity
                else:
                    target_entity = binding
                    if not target_entity.exists:
                        # add this entity to it's base collection
                        with target_set.OpenCollection() as targetCollection:
                            targetCollection.insert_entity_sql(
                                target_entity, link_end.otherEnd, transaction)
                # Finally, we have a target entity, add the foreign key to
                # fk_values
                for key_name in target_set.keys:
                    fk_values.append(
                        (self.container.mangled_names[
                            (self.entity_set.name,
                             aset_name,
                             key_name)],
                            target_entity[key_name]))
                nav_done.add(k)
            # grab a list of sql-name,sql-value pairs representing the key
            # constraint
            concurrency_check = False
            constraints = []
            for k, v in entity.KeyDict().items():
                constraints.append(
                    (self.container.mangled_names[
                        (self.entity_set.name, k)],
                        self.container.prepare_sql_value(v)))
            cv_list = list(self.update_fields(entity))
            for cname, v in cv_list:
                # concurrency tokens get added as if they were part of the key
                if v.pDef.concurrencyMode == edm.ConcurrencyMode.Fixed:
                    concurrency_check = True
                    constraints.append(
                        (cname, self.container.prepare_sql_value(v)))
            # now update the entity to have the latest concurrency token
            entity.SetConcurrencyTokens()
            query = ['UPDATE ', self.table_name, ' SET ']
            params = self.container.ParamsClass()
            updates = []
            for cname, v in cv_list + fk_values:
                updates.append(
                    '%s=%s' %
                    (cname,
                     params.add_param(
                         self.container.prepare_sql_value(v))))
            query.append(string.join(updates, ', '))
            query.append(' WHERE ')
            where = []
            for cname, cValue in constraints:
                where.append('%s=%s' % (cname, params.add_param(cValue)))
            query.append(string.join(where, ' AND '))
            query = string.join(query, '')
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            if transaction.cursor.rowcount == 0:
                # no rows matched this constraint, probably a concurrency
                # failure
                if concurrency_check:
                    raise edm.ConcurrencyError
                else:
                    raise KeyError("Entity %s does not exist" %
                                   str(entity.GetLocation()))
            # We finish off the bindings in a similar way to
            # insert_entity_sql but this time we need to handle the case
            # where there is an existing link and the navigation
            # property is not a collection.
            for k, dv in entity.NavigationItems():
                link_end = self.entity_set.navigation[k]
                if not dv.bindings:
                    continue
                elif k in nav_done:
                    dv.bindings = []
                    continue
                aset_name = link_end.parent.name
                target_set = dv.Target()
                target_fk_mapping = self.container.fk_table[target_set.name]
                with dv.OpenCollection() as navCollection:
                    with target_set.OpenCollection() as targetCollection:
                        while dv.bindings:
                            binding = dv.bindings[0]
                            if not isinstance(binding, edm.Entity):
                                targetCollection.SelectKeys()
                                binding = targetCollection[binding]
                            if binding.exists:
                                if dv.isCollection:
                                    navCollection.insert_link(
                                        binding, transaction)
                                else:
                                    navCollection.replace_link(binding,
                                                               transaction)
                            else:
                                if link_end.otherEnd in target_fk_mapping:
                                    # target table has a foreign key
                                    target_fk_values = []
                                    for key_name in self.entity_set.keys:
                                        target_fk_values.append(
                                            (self.container.mangled_names[
                                                (target_set.name,
                                                 aset_name,
                                                 key_name)],
                                                entity[key_name]))
                                    if not dv.isCollection:
                                        navCollection.clear_links(transaction)
                                    targetCollection.insert_entity_sql(
                                        binding,
                                        link_end.otherEnd,
                                        target_fk_values,
                                        transaction)
                                else:
                                    # foreign keys are in an auxiliary table
                                    targetCollection.insert_entity_sql(
                                        binding, link_end.otherEnd)
                                    if dv.isCollection:
                                        navCollection.insert_link(
                                            binding, transaction)
                                    else:
                                        navCollection.replace_link(
                                            binding, transaction)
                            dv.bindings = dv.bindings[1:]
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            # we might need to distinguish between a failure due to
            # fk_values or a missing key
            transaction.rollback(e, swallow=True)
            raise edm.ConstraintError(
                "Update failed for %s : %s" %
                (str(
                    entity.GetLocation()),
                    str(e)))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def update_link(
            self,
            entity,
            link_end,
            target_entity,
            no_replace=False,
            transaction=None):
        """Updates a link when this table contains the foreign key

        entity
                The entity being linked from (must already exist)

        link_end
                The :py:class:`~pyslet.odata2.csdl.AssociationSetEnd` bound
                to this entity set that represents this entity set's end of
                the assocation being modified.

        target_entity
                The entity to link to or None if the link is to be removed.

        no_replace
                If True, existing links will not be replaced.  The affect is
                to force the underlying SQL query to include a constraint
                that the foreign key is currently NULL.  By default this
                argument is False and any existing link will be replaced.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        if not entity.exists:
            raise edm.NonExistentEntity(
                "Attempt to update non-existent entity: " +
                str(entity.GetLocation()))
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['UPDATE ', self.table_name, ' SET ']
        params = self.container.ParamsClass()
        updates = []
        null_cols = []
        target_set = link_end.otherEnd.entity_set
        aset_name = link_end.parent.name
        nullable, unique = \
            self.container.fk_table[self.entity_set.name][link_end]
        if not nullable and target_entity is None:
            raise edm.NavigationError("Can't remove a required link")
        if target_entity:
            for key_name in target_set.keys:
                v = target_entity[key_name]
                cname = self.container.mangled_names[
                    (self.entity_set.name, aset_name, key_name)]
                updates.append(
                    '%s=%s' %
                    (cname,
                     params.add_param(
                         self.container.prepare_sql_value(v))))
                if no_replace:
                    null_cols.append(cname)
        else:
            for key_name in target_set.keys:
                cname = self.container.mangled_names[
                    (self.entity_set.name, aset_name, key_name)]
                updates.append('%s=NULL' % cname)
        query.append(string.join(updates, ', '))
        # we don't do concurrency checks on links, and we suppress the filter
        # check too
        query.append(
            self.where_clause(entity, params, False, null_cols=null_cols))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            if transaction.cursor.rowcount == 0:
                if null_cols:
                    # raise a constraint failure, rather than a key failure -
                    # assume entity is good
                    raise edm.NavigationError(
                        "Entity %s is already linked through association %s" %
                        (entity.GetLocation(), aset_name))
                else:
                    # key failure - unexpected case as entity should be good
                    raise KeyError("Entity %s does not exist" %
                                   str(entity.GetLocation()))
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            transaction.rollback(e, swallow=True)
            raise KeyError("Linked entity %s does not exist" %
                           str(target_entity.GetLocation()))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def __delitem__(self, key):
        with self.entity_set.OpenCollection() as base:
            entity = base.new_entity()
            entity.set_key(key)
            entity.exists = True    # an assumption!
            # base.SelectKeys()
            # entity = base[key]
        self.delete_entity(entity)

    def delete_entity(self, entity, from_end=None, transaction=None):
        """Deletes an entity

        Called by the dictionary-like del operator, provided as a
        separate method to enable it to be called recursively when
        doing cascade deletes and to support transactions.

        from_end
                An optional
                :py:class:`~pyslet.odata2.csdl.AssociationSetEnd` bound to
                this entity set that represents the link from which we are
                being deleted during a cascade delete.

                The purpose of this parameter is prevent cascade deletes
                from doubling back on themselves and causing an infinite
                loop.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            fk_mapping = self.container.fk_table[self.entity_set.name]
            for link_end, nav_name in self.entity_set.linkEnds.iteritems():
                if link_end == from_end:
                    continue
                aset_name = link_end.parent.name
                if link_end in fk_mapping:
                    # if we are holding a foreign key then deleting us
                    # will delete the link too, so nothing to do here.
                    continue
                else:
                    if (link_end.associationEnd.multiplicity ==
                            edm.Multiplicity.One):
                        # we are required, so it must be a 1-? relationship
                        if nav_name is not None:
                            # and it is bound to a navigation property so we
                            # can cascade delete
                            target_entity_set = link_end.otherEnd.entity_set
                            with entity[nav_name].OpenCollection() as links:
                                with target_entity_set.OpenCollection() as \
                                        cascade:
                                    links.SelectKeys()
                                    for target_entity in links.values():
                                        links.delete_link(target_entity,
                                                          transaction)
                                        cascade.delete_entity(
                                            target_entity,
                                            link_end.otherEnd,
                                            transaction)
                        else:
                            raise edm.NavigationError(
                                "Can't cascade delete from an entity in %s as "
                                "the association set %s is not bound to a "
                                "navigation property" %
                                (self.entity_set.name, aset_name))
                    else:
                        # we are not required, so just drop the links
                        if nav_name is not None:
                            with entity[nav_name].OpenCollection() as links:
                                links.clear_links(transaction)
                        # otherwise annoying, we need to do something special
                        elif aset_name in self.container.aux_table:
                            # foreign keys are in an association table,
                            # hardest case as navigation may be unbound so
                            # we have to call a class method and pass the
                            # container and connection
                            SQLAssociationCollection.clear_links_unbound(
                                self.container, link_end, entity, transaction)
                        else:
                            # foreign keys are at the other end of the
                            # link, we have a method for that...
                            target_entity_set = link_end.otherEnd.entity_set
                            with target_entity_set.OpenCollection() as \
                                    keyCollection:
                                keyCollection.clear_links(
                                    link_end.otherEnd, entity, transaction)
            params = self.container.ParamsClass()
            query = ["DELETE FROM "]
            params = self.container.ParamsClass()
            query.append(self.table_name)
            # WHERE - ignore the filter
            query.append(self.where_clause(entity, params, use_filter=False))
            query = string.join(query, '')
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            rowcount = transaction.cursor.rowcount
            if rowcount == 0:
                raise KeyError
            elif rowcount > 1:
                # whoops, that was unexpected
                raise SQLError(
                    "Integrity check failure, non-unique key: %s" %
                    repr(entity.key()))
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def delete_link(self, entity, link_end, target_entity, transaction=None):
        """Deletes the link between *entity* and *target_entity*

        The foreign key for this link must be held in this entity set's
        table.

        entity
                The entity in this entity set that the link is from.

        link_end
                The :py:class:`~pyslet.odata2.csdl.AssociationSetEnd` bound
                to this entity set that represents this entity set's end of
                the assocation being modified.

        target_entity
                The target entity that defines the link to be removed.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        if not entity.exists:
            raise edm.NonExistentEntity(
                "Attempt to update non-existent entity: " +
                str(entity.GetLocation()))
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['UPDATE ', self.table_name, ' SET ']
        params = self.container.ParamsClass()
        updates = []
        aset_name = link_end.parent.name
        target_set = link_end.otherEnd.entity_set
        nullable, unique = \
            self.container.fk_table[self.entity_set.name][link_end]
        if not nullable:
            raise edm.NavigationError(
                "Can't remove a required link from association set %s" %
                aset_name)
        for key_name in target_set.keys:
            cname = self.container.mangled_names[
                (self.entity_set.name, aset_name, key_name)]
            updates.append('%s=NULL' % cname)
        query.append(string.join(updates, ', '))
        # custom where clause to ensure that the link really existed before we
        # delete it
        query.append(' WHERE ')
        where = []
        kd = entity.KeyDict()
        for k, v in kd.items():
            where.append(
                '%s=%s' %
                (self.container.mangled_names[
                    (self.entity_set.name, k)], params.add_param(
                    self.container.prepare_sql_value(v))))
        for key_name in target_set.keys:
            v = target_entity[key_name]
            cname = self.container.mangled_names[
                (self.entity_set.name, aset_name, key_name)]
            where.append(
                '%s=%s' %
                (cname,
                 params.add_param(
                     self.container.prepare_sql_value(v))))
        query.append(string.join(where, ' AND '))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            if transaction.cursor.rowcount == 0:
                # no rows matched this constraint, entity either doesn't exist
                # or wasn't linked to the target
                raise KeyError(
                    "Entity %s does not exist or is not linked to %s" % str(
                        entity.GetLocation(),
                        target_entity.GetLocation))
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def clear_links(self, link_end, target_entity, transaction=None):
        """Deletes all links to *target_entity*

        The foreign key for this link must be held in this entity set's
        table.

        link_end
                The :py:class:`~pyslet.odata2.csdl.AssociationSetEnd` bound
                to this entity set that represents this entity set's end of
                the assocation being modified.

        target_entity
                The target entity that defines the link(s) to be removed.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['UPDATE ', self.table_name, ' SET ']
        params = self.container.ParamsClass()
        updates = []
        aset_name = link_end.parent.name
        target_set = link_end.otherEnd.entity_set
        nullable, unique = \
            self.container.fk_table[self.entity_set.name][link_end]
        for key_name in target_set.keys:
            cname = self.container.mangled_names[
                (self.entity_set.name, aset_name, key_name)]
            updates.append('%s=NULL' % cname)
        # custom where clause
        query.append(string.join(updates, ', '))
        query.append(' WHERE ')
        where = []
        for key_name in target_set.keys:
            v = target_entity[key_name]
            cname = self.container.mangled_names[
                (self.entity_set.name, aset_name, key_name)]
            where.append(
                '%s=%s' %
                (cname,
                 params.add_param(
                     self.container.prepare_sql_value(v))))
        query.append(string.join(where, ' AND '))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            # catch the nullable violation here, makes it benign to
            # clear links to an unlinked target
            transaction.rollback(e, swallow=True)
            raise edm.NavigationError(
                "Can't remove required link from assocation set %s" %
                aset_name)
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def create_table_query(self):
        """Returns a SQL statement and params for creating the table."""
        entity = self.new_entity()
        query = ['CREATE TABLE ', self.table_name, ' (']
        params = self.container.ParamsClass()
        cols = []
        cnames = {}
        for c, v in self.select_fields(entity):
            if c in cnames:
                continue
            else:
                cnames[c] = True
                cols.append("%s %s" %
                            (c, self.container.prepare_sql_type(v, params)))
        # do we have a media stream?
        if self.entity_set.entityType.HasStream():
            v = edm.EDMValue.NewSimpleValue(edm.SimpleType.Int64)
            c = self.container.mangled_names[(self.entity_set.name, u'_value')]
            cnames[c] = True
            cols.append("%s %s" %
                        (c, self.container.prepare_sql_type(v, params)))
        keys = entity.KeyDict()
        constraints = []
        constraints.append(
            u'PRIMARY KEY (%s)' %
            string.join(
                map(
                    lambda x: self.container.mangled_names[
                        (self.entity_set.name, x)], keys.keys()), u', '))
        # Now generate the foreign keys
        fk_mapping = self.container.fk_table[self.entity_set.name]
        for link_end in fk_mapping:
            aset_name = link_end.parent.name
            target_set = link_end.otherEnd.entity_set
            nullable, unique = fk_mapping[link_end]
            fk_names = []
            k_names = []
            for key_name in target_set.keys:
                # create a dummy value to catch the unusual case where
                # there is a default
                v = target_set.entityType[key_name]()
                cname = self.container.mangled_names[
                    (self.entity_set.name, aset_name, key_name)]
                fk_names.append(cname)
                k_names.append(
                    self.container.mangled_names[(target_set.name, key_name)])
                if cname in cnames:
                    # if a fk is already declared, skip it
                    continue
                else:
                    cols.append(
                        "%s %s" %
                        (cname,
                         self.container.prepare_sql_type(
                             v,
                             params,
                             nullable)))
            constraints.append(
                "CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s(%s)" %
                (self.container.quote_identifier(aset_name), string.join(
                    fk_names, ', '), self.container.mangled_names[
                    (target_set.name,)], string.join(
                    k_names, ', ')))
        cols = cols + constraints
        query.append(string.join(cols, u", "))
        query.append(u')')
        return string.join(query, ''), params

    def create_table(self):
        """Executes the SQL statement :py:meth:`create_table_query`"""
        query, params = self.create_table_query()
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()


class SQLNavigationCollection(SQLCollectionBase, core.NavigationCollection):

    """Abstract class representing all navigation collections.

    Additional keyword arguments:

    aset_name
            The name of the association set that defines this relationship.
            This additional parameter is used by the name mangler to obtain
            the field name (or table name) used for the foreign keys."""

    def __init__(self, aset_name, **kwargs):
        super(SQLNavigationCollection, self).__init__(**kwargs)
        self.aset_name = aset_name

    def __setitem__(self, key, entity):
        # sanity check entity to check it can be inserted here
        if (not isinstance(entity, edm.Entity) or
                entity.entity_set is not self.entity_set):
            raise TypeError
        if key != entity.key():
            raise ValueError
        if not entity.exists:
            raise edm.NonExistentEntity(
                "Attempt to link to a non-existent entity: " +
                str(entity.GetLocation()))
        self.insert_link(entity)

    def insert_link(self, entity, transaction=None):
        """Inserts a link to *entity* into this collection.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        raise NotImplementedError

    def replace(self, entity):
        if (not isinstance(entity, edm.Entity) or
                entity.entity_set is not self.entity_set):
            raise TypeError
        if not entity.exists:
            raise edm.NonExistentEntity(
                "Attempt to link to a non-existent entity: " +
                str(entity.GetLocation()))
        self.replace_link(entity)

    def replace_link(self, entity, transaction=None):
        """Replaces all links with a single link to *entity*.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        raise NotImplementedError

    def delete_link(self, entity, transaction=None):
        """A utility method that deletes the link to *entity* in this collection.

        This method is called during cascaded deletes to force-remove a
        link prior to the deletion of the entity itself.

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        raise NotImplementedError


class SQLForeignKeyCollection(SQLNavigationCollection):

    """The collection of entities obtained by navigation via a foreign key

    This object is used when the foreign key is stored in the same table
    as *from_entity*.  This occurs when the relationship is one of::

            0..1 to 1
            Many to 1
            Many to 0..1

    The name mangler looks for the foreign key in the field obtained by
    mangling::

            (entity set name, association set name, key name)

    For example, suppose that a link exists from entity set Orders[*] to
    entity set Customers[0..1] and that the key field of Customer is
    "CustomerID".  If the association set that binds Orders to Customers
    with this link is called OrdersToCustomers then the foreign key would
    be obtained by looking up::

            ('Orders','OrdersToCustomers','CustomerID')

    By default this would result in the field name::

            'OrdersToCustomers_CustomerID'

    This field would be looked up in the 'Orders' table.  The operation
    of the name mangler can be customised by overriding the
    :py:meth:`SQLEntityContainer.mangle_name` method in the container."""

    def __init__(self, **kwargs):
        # absorb qualify_names just in case
        if not kwargs.pop('qualify_names', True):
            logging.warn("SQLForeignKeyCollection ignored qualify_names=False")
        super(SQLForeignKeyCollection, self).__init__(
            qualify_names=True, **kwargs)
        self.keyCollection = self.from_entity.entity_set.OpenCollection()
        nav_name = self.entity_set.linkEnds[self.from_end.otherEnd]
        if not nav_name:
            self.sourceName = self.container.mangled_names[
                (self.entity_set.name, self.from_end.name)]
        else:
            self.sourceName = self.container.mangled_names[
                (self.entity_set.name, nav_name)]

    def join_clause(self):
        """Overridden to provide a join to *from_entity*'s table.

        The join clause introduces an additional name that is looked up
        by the name mangler.  To avoid name clashes when the
        relationship is recursive the join clause introduces an alias
        for the table containing *from_entity*.  To continue the example
        above, if the link from Orders to Customers is bound to a
        navigation property in the reverse direction called, say,
        'AllOrders' *in the target entity set* then this alias is
        looked up using::

            ('Customers','AllOrders')

        By default this would just be the string 'AllOrders' (the
        name of the navigation property). The resulting join looks
        something like this::

            SELECT ... FROM Customers
            INNER JOIN Orders AS AllOrders ON
                Customers.CustomerID=AllOrders.OrdersToCustomers_CustomerID
            ...
            WHERE AllOrders.OrderID = ?;

        The value of the OrderID key property in from_entity is passed as
        a parameter when executing the expression.

        There is an awkward case when the reverse navigation property
        has not been bound, in this case the link's role name is used
        instead, this provides a best guess as to what the navigation
        property name would have been had it been bound; it must be
        unique within the context of *target* entity_set's type - a
        benign constraint on the model's metadata description."""
        join = []
        # we don't need to look up the details of the join again, as
        # self.entity_set must be the target
        for key_name in self.entity_set.keys:
            join.append(
                '%s.%s=%s.%s' %
                (self.table_name, self.container.mangled_names[
                    (self.entity_set.name, key_name)],
                    self.sourceName, self.container.mangled_names[
                        (self.from_entity.entity_set.name,
                         self.aset_name, key_name)]))
        return ' INNER JOIN %s AS %s ON ' % (
            self.container.mangled_names[(self.from_entity.entity_set.name,)],
            self.sourceName) + string.join(join, ', ')

    def where_clause(self, entity, params, use_filter=True, use_skip=False):
        """Adds the constraint for entities linked from *from_entity* only.

        We continue to use the alias set in the :py:meth:`join_clause`
        where an example WHERE clause is illustrated."""
        where = []
        for k, v in self.from_entity.KeyDict().items():
            where.append(
                u"%s.%s=%s" %
                (self.sourceName, self.container.mangled_names[
                    (self.from_entity.entity_set.name, k)], params.add_param(
                    self.container.prepare_sql_value(v))))
        if entity is not None:
            self.where_entity_clause(where, entity, params)
        if self.filter is not None and use_filter:
            # use_filter option adds the current filter too
            where.append('(' + self.sql_expression(self.filter, params) + ')')
        if self.skiptoken is not None and use_skip:
            self.where_skiptoken_clause(where, params)
        if where:
            return ' WHERE ' + string.join(where, ' AND ')
        else:
            return ''

    def insert_entity(self, entity):
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            # Because of the nature of the relationships we are used
            # for, *entity* can be inserted into the base collection
            # without a link back to us (the link is optional from
            # entity's point of view). We still force the insert to
            # take place without a commit as the insertion of the link
            # afterwards might still fail.
            transaction.begin()
            with self.entity_set.OpenCollection() as baseCollection:
                baseCollection.insert_entity_sql(
                    entity, self.from_end.otherEnd, transaction=transaction)
            self.keyCollection.update_link(
                self.from_entity,
                self.from_end,
                entity,
                no_replace=True,
                transaction=transaction)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            # we can't tell why the operation failed, could be a
            # KeyError, if we are trying to insert an existing entity or
            # could be a ConstraintError if we are already linked to a
            # different entity
            transaction.rollback(e, swallow=True)
            raise edm.NavigationError(str(e))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def insert_link(self, entity, transaction=None):
        return self.keyCollection.update_link(
            self.from_entity,
            self.from_end,
            entity,
            no_replace=True,
            transaction=transaction)

    def replace_link(self, entity, transaction=None):
        # Target multiplicity must be 0..1 or 1; treat it the same as setitem
        return self.keyCollection.update_link(
            self.from_entity,
            self.from_end,
            entity,
            transaction=transaction)

    def delete_link(self, entity, transaction=None):
        return self.keyCollection.delete_link(
            self.from_entity,
            self.from_end,
            entity,
            transaction=transaction)

    def __delitem__(self, key):
        #   Before we remove a link we need to know if this is ?-1
        #   relationship, if so, this deletion will result in a
        #   constraint violation.
        if self.toMultiplicity == edm.Multiplicity.One:
            raise edm.NavigationError("Can't remove a required link")
        #   Turn the key into an entity object as required by delete_link
        with self.entity_set.OpenCollection() as targetCollection:
            target_entity = targetCollection.new_entity()
            target_entity.set_key(key)
            # we open the base collection and call the update link method
            self.keyCollection.delete_link(
                self.from_entity, self.from_end, target_entity)

    def close(self):
        if self.keyCollection is not None:
            self.keyCollection.close()
        super(SQLForeignKeyCollection, self).close()


class SQLReverseKeyCollection(SQLNavigationCollection):

    """The collection of entities obtained by navigation to a foreign key

    This object is used when the foreign key is stored in the target
    table.  This occurs in the reverse of the cases where
    :py:class:`SQLReverseKeyCollection` is used, i.e:

            1 to 0..1
            1 to Many
            0..1 to Many

    The implementation is actually simpler in this direction as no JOIN
    clause is required."""

    def __init__(self, **kwargs):
        super(SQLReverseKeyCollection, self).__init__(**kwargs)
        self.keyCollection = self.entity_set.OpenCollection()

    def where_clause(self, entity, params, use_filter=True, use_skip=False):
        """Adds the constraint to entities linked from *from_entity* only."""
        where = []
        for k, v in self.from_entity.KeyDict().items():
            where.append(u"%s=%s" % (
                self.container.mangled_names[
                    (self.entity_set.name, self.aset_name, k)],
                params.add_param(self.container.prepare_sql_value(v))))
        if entity is not None:
            self.where_entity_clause(where, entity, params)
        if self.filter is not None and use_filter:
            # use_filter option adds the current filter too
            where.append('(' + self.sql_expression(self.filter, params) + ')')
        if self.skiptoken is not None and use_skip:
            self.where_skiptoken_clause(where, params)
        if where:
            return ' WHERE ' + string.join(where, ' AND ')
        else:
            return ''

    def insert_entity(self, entity):
        transaction = SQLTransaction(self.container.dbapi, self.dbc)
        fk_values = []
        for k, v in self.from_entity.KeyDict().items():
            fk_values.append(
                (self.container.mangled_names[
                    (self.entity_set.name, self.aset_name, k)], v))
        try:
            transaction.begin()
            self.keyCollection.insert_entity_sql(
                entity, self.from_end.otherEnd, fk_values, transaction)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            transaction.rollback(e, swallow=True)
            raise KeyError(str(entity.GetLocation()))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def insert_link(self, entity, transaction=None):
        return self.keyCollection.update_link(
            entity,
            self.from_end.otherEnd,
            self.from_entity,
            no_replace=True,
            transaction=transaction)
        # we use no_replace mode as the source multiplicity must be 1 or
        # 0..1 for this type of collection and if *entity* is already
        # linked it would be an error

    def replace_link(self, entity, transaction=None):
        if self.fromMultiplicity == edm.Multiplicity.One:
            # we are required, this must be an error
            raise edm.NavigationError(
                "Can't delete required link from association set %s" %
                self.aset_name)
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            self.keyCollection.clear_links(
                self.from_end.otherEnd, self.from_entity, transaction)
            self.insert_link(entity, transaction)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            transaction.rollback(e, swallow=True)
            raise edm.NavigationError(
                "Model integrity error when linking %s and %s" %
                (str(
                    self.from_entity.GetLocation()), str(
                    entity.GetLocation())))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def __delitem__(self, key):
        entity = self.keyCollection[key]
        if self.fromMultiplicity == edm.Multiplicity.One:
            # we are required, this must be an error
            raise edm.NavigationError(
                "Can't delete required link from association set %s" %
                self.aset_name)
        # fromMultiplicity is 0..1
        self.keyCollection.delete_link(
            entity, self.from_end.otherEnd, self.from_entity)

    def delete_link(self, entity, transaction=None):
        """Called during cascaded deletes.

        This is actually a no-operation as the foreign key for this
        association is in the entity's record itself and will be removed
        automatically when entity is deleted."""
        return 0

    def clear(self):
        self.keyCollection.clear_links(
            self.from_end.otherEnd,
            self.from_entity)

    def clear_links(self, transaction=None):
        """Deletes all links from this collection's *from_entity*

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        self.keyCollection.clear_links(
            self.from_end.otherEnd, self.from_entity, transaction)

    def close(self):
        self.keyCollection.close()
        super(SQLReverseKeyCollection, self).close()


class SQLAssociationCollection(SQLNavigationCollection):

    """The collection obtained by navigation using an auxiliary table

    This object is used when the relationship is described by two sets
    of foreign keys stored in an auxiliary table.  This occurs mainly
    when the link is Many to Many but it is also used for 1 to 1
    relationships.  This last use may seem odd but it is used to
    represent the symmetry of the relationship. In practice, a single
    set of foreign keys is likely to exist in one table or the other and
    so the relationship is best modelled by a 0..1 to 1 relationship
    even if the intention is that the records will always exist in
    pairs.

    The name of the auxiliary table is obtained from the name mangler
    using the association set's name.  The keys use a more complex
    mangled form to cover cases where there is a recursive Many to Many
    relation (such as a social network of friends between User
    entities).  The names of the keys are obtained by mangling::

            ( association set name, target entity set name,
                navigation property name, key name )

    An example should help.  Suppose we have entities representing
    sports Teams(TeamID) and sports Players(PlayerID) and that you can
    navigate from Player to Team using the "PlayedFor" navigation
    property and from Team to Player using the "Players" navigation
    property.  Both navigation properties are collections so the
    relationship is Many to Many.  If the association set that binds the
    two entity sets is called PlayersAndTeams then the the auxiliary
    table name will be mangled from::

            ('PlayersAndTeams')

    and the fields will be mangled from::

            ('PlayersAndTeams','Teams','PlayedFor','TeamID')
            ('PlayersAndTeams','Players','Players','PlayerID')

    By default this results in column names 'Teams_PlayedFor_TeamID' and
    'Players_Players_PlayerID'.  If you are modelling an existing
    database then 'TeamID' and 'PlayerID' on their own are more likely
    choices. You would need to override the
    :py:meth:`SQLEntityContainer.mangle_name` method in the container to
    catch these cases and return the shorter column names."""

    def __init__(self, **kwargs):
        if not kwargs.pop('qualify_names', True):
            logging.warn(
                'SQLAssociationCollection ignored qualify_names=False')
        super(SQLAssociationCollection, self).__init__(
            qualify_names=True, **kwargs)
        # The relation is actually stored in an extra table so we will
        # need a join for all operations.
        self.aset_name = self.from_end.parent.name
        self.atable_name = self.container.mangled_names[
            (self.aset_name,)]
        entitySetA, nameA, entitySetB, nameB, self.uniqueKeys = \
            self.container.aux_table[self.aset_name]
        if self.from_entity.entity_set is entitySetA and self.name == nameA:
            self.from_nav_name = nameA
            self.toNavName = nameB
        else:
            self.from_nav_name = nameB
            self.toNavName = nameA

    def join_clause(self):
        """Overridden to provide the JOIN to the auxiliary table.

        Unlike the foreign key JOIN clause there is no need to use an
        alias in this case as the auxiliary table is assumed to be
        distinct from the the table it is being joined to."""
        join = []
        # we don't need to look up the details of the join again, as
        # self.entity_set must be the target
        for key_name in self.entity_set.keys:
            join.append(
                '%s.%s=%s.%s' %
                (self.table_name,
                 self.container.mangled_names[
                     (self.entity_set.name,
                      key_name)],
                    self.atable_name,
                    self.container.mangled_names[
                     (self.aset_name,
                      self.entity_set.name,
                      self.toNavName,
                      key_name)]))
        return ' INNER JOIN %s ON ' % self.atable_name + \
            string.join(join, ', ')

    def where_clause(self, entity, params, use_filter=True, use_skip=False):
        """Provides the *from_entity* constraint in the auxiliary table."""
        where = []
        for k, v in self.from_entity.KeyDict().items():
            where.append(
                u"%s.%s=%s" %
                (self.atable_name,
                 self.container.mangled_names[
                     (self.aset_name,
                      self.from_entity.entity_set.name,
                      self.from_nav_name,
                      k)],
                    params.add_param(
                     self.container.prepare_sql_value(v))))
        if entity is not None:
            for k, v in entity.KeyDict().items():
                where.append(
                    u"%s.%s=%s" %
                    (self.atable_name,
                     self.container.mangled_names[
                         (self.aset_name,
                          entity.entity_set.name,
                          self.toNavName,
                          k)],
                        params.add_param(
                         self.container.prepare_sql_value(v))))
        if use_filter and self.filter is not None:
            where.append("(%s)" % self.sql_expression(self.filter, params))
        if self.skiptoken is not None and use_skip:
            self.where_skiptoken_clause(where, params)
        return ' WHERE ' + string.join(where, ' AND ')

    def insert_entity(self, entity):
        """Rerouted to a SQL-specific implementation"""
        self.insert_entity_sql(entity, transaction=None)

    def insert_entity_sql(self, entity, transaction=None):
        """Inserts *entity* into the base collection and creates the link.

        This is always done in two steps, bound together in a single
        transaction (where supported).  If this object represents a 1 to
        1 relationship then, briefly, we'll be in violation of the
        model. This will only be an issue in non-transactional
        systems."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        try:
            transaction.begin()
            with self.entity_set.OpenCollection() as baseCollection:
                # if this is a 1-1 relationship insert_entity_sql will
                # fail (with an unbound navigation property) so we need
                # to suppress the back-link.
                baseCollection.insert_entity_sql(
                    entity, self.from_end.otherEnd, transaction=transaction)
            self.insert_link(entity, transaction)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            transaction.rollback(e, swallow=True)
            raise edm.NavigationError(str(entity.GetLocation()))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def insert_link(self, entity, transaction=None):
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['INSERT INTO ', self.atable_name, ' (']
        params = self.container.ParamsClass()
        value_names = []
        values = []
        for k, v in self.from_entity.KeyDict().items():
            value_names.append(
                self.container.mangled_names[
                    (self.aset_name,
                     self.from_entity.entity_set.name,
                     self.from_nav_name,
                     k)])
            values.append(
                params.add_param(
                    self.container.prepare_sql_value(v)))
        for k, v in entity.KeyDict().items():
            value_names.append(
                self.container.mangled_names[
                    (self.aset_name,
                     self.entity_set.name,
                     self.toNavName,
                     k)])
            values.append(
                params.add_param(
                    self.container.prepare_sql_value(v)))
        query.append(string.join(value_names, ', '))
        query.append(') VALUES (')
        query.append(string.join(values, ', '))
        query.append(')')
        query = string.join(query, '')
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            transaction.commit()
        except self.container.dbapi.IntegrityError as e:
            transaction.rollback(e, swallow=True)
            raise edm.NavigationError(
                "Model integrity error when linking %s and %s" %
                (str(
                    self.from_entity.GetLocation()), str(
                    entity.GetLocation())))
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def replace_link(self, entity, transaction=None):
        if self.from_entity[self.from_nav_name].isCollection:
            if transaction is None:
                transaction = SQLTransaction(self.container.dbapi, self.dbc)
            try:
                transaction.begin()
                self.clear_links(transaction)
                self.insert_link(entity, transaction)
                transaction.commit()
            except self.container.dbapi.IntegrityError as e:
                transaction.rollback(e, swallow=True)
                raise edm.NavigationError(
                    "Model integrity error when linking %s and %s" %
                    (str(
                        self.from_entity.GetLocation()), str(
                        entity.GetLocation())))
            except Exception as e:
                transaction.rollback(e)
            finally:
                transaction.close()
        else:
            # We don't support symmetric associations of the 0..1 - 0..1
            # variety so this must be a 1..1 relationship.
            raise edm.NavigationError(
                "replace not allowed for 1-1 relationship "
                "(implicit delete not supported)")

    def __delitem__(self, key):
        #   Before we remove a link we need to know if this is 1-1
        #   relationship, if so, this deletion will result in a
        #   constraint violation.
        if self.uniqueKeys:
            raise edm.NavigationError("Can't remove a required link")
        with self.entity_set.OpenCollection() as targetCollection:
            entity = targetCollection.new_entity()
            entity.set_key(key)
            self.delete_link(entity)

    def delete_link(self, entity, transaction=None):
        """Called during cascaded deletes to force-remove a link prior
        to the deletion of the entity itself.

        This method is also re-used for simple deletion of the link in
        this case as the link is in the auxiliary table itself."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['DELETE FROM ', self.atable_name]
        params = self.container.ParamsClass()
        # we suppress the filter check on the where clause
        query.append(self.where_clause(entity, params, False))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            if transaction.cursor.rowcount == 0:
                # no rows matched this constraint must be a key failure at one
                # of the two ends
                raise KeyError(
                    "One of the entities %s or %s no longer exists" %
                    (str(
                        self.from_entity.GetLocation()), str(
                        entity.GetLocation())))
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    def clear_links(self, transaction=None):
        """Deletes all links from this collection's *from_entity*

        transaction
                An optional transaction.  If present, the connection is left
                uncommitted."""
        if transaction is None:
            transaction = SQLTransaction(self.container.dbapi, self.dbc)
        query = ['DELETE FROM ', self.atable_name]
        params = self.container.ParamsClass()
        # we suppress the filter check on the where clause
        query.append(self.where_clause(None, params, False))
        query = string.join(query, '')
        try:
            transaction.begin()
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()

    @classmethod
    def clear_links_unbound(
            cls,
            container,
            from_end,
            from_entity,
            transaction):
        """Special class method for deleting all the links from *from_entity*

        This is a class method because it has to work even if there is
        no navigation property bound to this end of the association.

        container
                The :py:class:`SQLEntityContainer` containing this
                association set.

        from_end
                The :py:class:`~pyslet.odata2.csdl.AssociationSetEnd`
                that represents the end of the association that
                *from_entity* is bound to.

        from_entity
                The entity to delete links from

        transaction
                The current transaction (required)

        This is a class method because it has to work even if there is
        no navigation property bound to this end of the association.  If
        there was a navigation property then an instance could be
        created and the simpler :py:meth:`clear_links` method used."""
        aset_name = from_end.parent.name
        atable_name = container.mangled_names[(aset_name,)]
        nav_name = from_entity.entity_set.linkEnds[from_end]
        if nav_name is None:
            # this is most likely the case, we're being called this way
            # because we can't instantiate a collection on an unbound
            # navigation property
            nav_name = u""
        entitySetA, nameA, entitySetB, nameB, uniqueKeys = container.aux_table[
            aset_name]
        if from_entity.entity_set is entitySetA and nav_name == nameA:
            from_nav_name = nameA
        else:
            from_nav_name = nameB
        query = ['DELETE FROM ', atable_name]
        params = container.ParamsClass()
        query.append(' WHERE ')
        where = []
        for k, v in from_entity.KeyDict().items():
            where.append(
                u"%s.%s=%s" %
                (atable_name,
                 container.mangled_names[
                     (aset_name,
                      from_entity.entity_set.name,
                      from_nav_name,
                      k)],
                    params.add_param(
                     container.prepare_sql_value(v))))
        query.append(string.join(where, ' AND '))
        query = string.join(query, '')
        logging.info("%s; %s", query, unicode(params.params))
        transaction.execute(query, params)

    @classmethod
    def create_table_query(cls, container, aset_name):
        """Returns a SQL statement and params to create the auxiliary table.

        This is a class method to enable the table to be created before
        any entities are created."""
        entitySetA, nameA, entitySetB, nameB, uniqueKeys = container.aux_table[
            aset_name]
        query = ['CREATE TABLE ', container.mangled_names[
            (aset_name,)], ' (']
        params = container.ParamsClass()
        cols = []
        constraints = []
        pk_names = []
        for es, prefix, ab in ((entitySetA, nameA, 'A'),
                               (entitySetB, nameB, 'B')):
            target_table = container.mangled_names[(es.name,)]
            fk_names = []
            k_names = []
            for key_name in es.keys:
                # create a dummy value to catch the unusual case where
                # there is a default
                v = es.entityType[key_name]()
                cname = container.mangled_names[
                    (aset_name, es.name, prefix, key_name)]
                fk_names.append(cname)
                pk_names.append(cname)
                k_names.append(container.mangled_names[(es.name, key_name)])
                cols.append("%s %s" %
                            (cname, container.prepare_sql_type(v, params)))
            constraints.append(
                "CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s(%s)" %
                (container.quote_identifier(
                    u"fk" +
                    ab),
                    string.join(
                    fk_names,
                    ', '),
                    target_table,
                    string.join(
                    k_names,
                    ', ')))
            if uniqueKeys:
                constraints.append("CONSTRAINT %s UNIQUE (%s)" % (
                    container.quote_identifier(u"u" + ab),
                    string.join(fk_names, ', ')))
        # Finally, add a unique constraint spanning all columns as we don't
        # want duplicate relations
        constraints.append("CONSTRAINT %s UNIQUE (%s)" % (
            container.quote_identifier(u"pk"),
            string.join(pk_names, ', ')))
        cols = cols + constraints
        query.append(string.join(cols, u", "))
        query.append(u')')
        return string.join(query, ''), params

    @classmethod
    def create_table(cls, container, aset_name):
        """Executes the SQL statement :py:meth:`create_table_query`"""
        dbc = container.acquire_connection(
            SQL_TIMEOUT)        #: a connection to the database
        if dbc is None:
            raise DatabaseBusy(
                "Failed to acquire connection after %is" % SQL_TIMEOUT)
        transaction = SQLTransaction(container.dbapi, dbc)
        try:
            transaction.begin()
            query, params = cls.create_table_query(container, aset_name)
            logging.info("%s; %s", query, unicode(params.params))
            transaction.execute(query, params)
            transaction.commit()
        except Exception as e:
            transaction.rollback(e)
        finally:
            transaction.close()
            if dbc is not None:
                container.release_connection(dbc)


class DummyLock(object):

    """An object to use in place of a real Lock, can always be acquired"""

    def acquire(self, blocking=None):
        return True

    def release(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class SQLConnectionLock(object):

    """An object used to wrap a lock object.

    lock_class
            An object to use as the lock."""

    def __init__(self, lock_class):
        self.thread = None
        self.thread_id = None
        self.lock = lock_class()
        self.locked = 0
        self.dbc = None


class SQLEntityContainer(object):

    """Object used to represent an Entity Container (aka Database).

    Keyword arguments on construction:

    container
        The :py:class:`~pyslet.odata2.csdl.EntityContainer` that defines
        this database.

    streamstore
        An optional :py:class:`~pyslet.blockstore.StreamStore` that will
        be used to store media resources in the container.  If absent,
        media resources actions will generate NotImplementedError.

    dbapi
        The DB API v2 compatible module to use to connect to the
        database.

        This implementation is compatible with modules regardless of
        their thread-safety level (provided they declare it
        correctly!).

    max_connections (optional)
        The maximum number of connections to open to the database.
        If your program attempts to open more than this number
        (defaults to 10) then it will block until a connection
        becomes free.  Connections are always shared within the same
        thread so this argument should be set to the expected
        maximum number of threads that will access the database.

        If using a module with thread-safety level 0 max_connections
        is ignored and is effectively 1, so use of the API is then
        best confined to single-threaded programs. Multi-threaded
        programs can still use the API but it will block when there
        is contention for access to the module and context switches
        will force the database connection to be closed and reopened.

    field_name_joiner (optional)
        The character used by the name mangler to join compound
        names, for example, to obtain the column name of a complex
        property like "Address/City".  The default is "_", resulting
        in names like "Address_City" but it can be changed here.
        Note: all names are quoted using :py:meth:`quote_identifier`
        before appearing in SQL statements.

    This class is designed to work with diamond inheritance and super.
    All derived classes must call __init__ through super and pass all
    unused keyword arguments.  For example::

        class MyDBContainer:
                def __init__(self,myDBConfig,**kwargs):
                        super(MyDBContainer,self).__init__(**kwargs)
                        # do something with myDBConfig...."""

    def __init__(
            self,
            container,
            dbapi,
            streamstore=None,
            max_connections=10,
            field_name_joiner=u"_",
            **kwargs):
        if kwargs:
            logging.debug(
                "Unabsorbed kwargs in SQLEntityContainer constructor")
        self.container = container
        #: the :py:class:`~pyslet.odata2.csdl.EntityContainer`
        self.streamstore = streamstore
        #: the optional :py:class:`~pyslet.blockstore.StreamStore`
        self.dbapi = dbapi
        #: the DB API compatible module
        self.module_lock = None
        if self.dbapi.threadsafety == 0:
            # we can't even share the module, so just use one connection will
            # do
            self.module_lock = threading.RLock()
            self.clocker = DummyLock
            self.cpool_max = 1
        else:
            # Level 1 and above we can share the module
            self.module_lock = DummyLock()
            self.clocker = threading.RLock
            self.cpool_max = max_connections
        self.cpool_lock = threading.Condition()
        self.cpool_closing = False
        self.cpool_locked = {}
        self.cpool_unlocked = {}
        self.cpool_dead = []
        # set up the parameter style
        if self.dbapi.paramstyle == "qmark":
            self.ParamsClass = QMarkParams
        elif self.dbapi.paramstyle == "numeric":
            self.ParamsClass = NumericParams
        elif self.dbapi.paramstyle == "named":
            self.ParamsClass = NamedParams
        else:
            # will fail later when we try and add parameters
            self.ParamsClass = SQLParams
        self.fk_table = {}
        """A mapping from an entity set name to a FK mapping of the form::

            {<association set end>: (<nullable flag>, <unique keys flag>),...}

        The outer mapping has one entry for each entity set (even if the
        corresponding foreign key mapping is empty).

        Each foreign key mapping has one entry for each foreign key
        reference that must appear in that entity set's table.  The key
        is an :py:class:`AssociationSetEnd` that is bound to the entity
        set (the other end will be bound to the target entity set).
        This allows us to distinguish between the two ends of a
        recursive association."""
        self.aux_table = {}
        """A mapping from the names of symmetric association sets to::

            (<entity set A>, <name prefix A>, <entity set B>,
             <name prefix B>, <unique keys>)
        """
        self.mangled_names = {}
        """A mapping from source path tuples to mangled and quoted names
        to use in SQL queries.  For example::

            (u'Customer'):u'"Customer"'
            (u'Customer', u'Address', u'City') : u"Address_City"
            (u'Customer', u'Orders') : u"Customer_Orders"

        Note that the first element of the tuple is the entity set name
        but the default implementation does not use this in the mangled
        name for primitive fields as they are qualified in contexts
        where a name clash is possible.  However, mangled navigation
        property names do include the table name prefix as they used as
        pseudo-table names."""
        self.field_name_joiner = field_name_joiner
        """Default string used to join complex field names in SQL
        queries, e.g. Address_City"""
        self.ro_names = set()
        """The set of names that should be considered read only by the
        SQL insert and update generation code.  The items in the set are
        source paths, as per :py:attr:`mangled_names`.  The set is
        populated on construction using the :py:meth:`ro_name` method."""
        # for each entity set in this container, bind a SQLEntityCollection
        # object
        for es in self.container.EntitySet:
            self.fk_table[es.name] = {}
            for source_path in self.source_path_generator(es):
                self.mangled_names[source_path] = self.mangle_name(source_path)
                if self.ro_name(source_path):
                    self.ro_names.add(source_path)
            self.bind_entity_set(es)
        for es in self.container.EntitySet:
            for np in es.entityType.NavigationProperty:
                self.bind_navigation_property(es, np.name)
        # once the navigation properties have been bound, fk_table will
        # have been populated with any foreign keys we need to add field
        # name mappings for
        for esName, fk_mapping in self.fk_table.iteritems():
            for link_end, details in fk_mapping.iteritems():
                aset_name = link_end.parent.name
                target_set = link_end.otherEnd.entity_set
                for key_name in target_set.keys:
                    """Foreign keys are given fake source paths starting
                    with the association set name::

                            ( u"Orders_Customers", u"CustomerID" )"""
                    source_path = (esName, aset_name, key_name)
                    self.mangled_names[source_path] = \
                        self.mangle_name(source_path)
        # and aux_table will have been populated with additional tables to
        # hold symmetric associations...
        for aSet in self.container.AssociationSet:
            if aSet.name not in self.aux_table:
                continue
            self.mangled_names[(aSet.name,)] = self.mangle_name((aSet.name,))
            """Foreign keys in Tables that model association sets are
            given fake source paths that combine the entity set name and
            the name of the navigation property endpoint.

            This ensures the special case where the two entity sets are
            the same is taken care of (as the navigation property
            endpoints must still be unique). For one-way associations,
            prefixB will be an empty string."""
            esA, prefixA, esB, prefixB, unique = self.aux_table[aSet.name]
            for key_name in esA.keys:
                source_path = (aSet.name, esA.name, prefixA, key_name)
                self.mangled_names[source_path] = self.mangle_name(source_path)
            for key_name in esB.keys:
                source_path = (aSet.name, esB.name, prefixB, key_name)
                self.mangled_names[source_path] = self.mangle_name(source_path)

    def mangle_name(self, source_path):
        """Mangles a source path into a quoted SQL name

        This is a key extension point to use when you are wrapping an existing
        database with the API.  It allows you to control the names used for
        entity sets (tables) and properties (columns) in SQL queries.

        source_path
            A tuple or list of strings describing the path to a property
            in the metadata model.

            For entity sets, this is a tuple with a single entry in it,
            the entity set name.

            For data properties this is a tuple containing the path,
            including the entity set name e.g.,
            ("Customers","Address","City") for the City property in a
            complex property 'Address' in entity set "Customers".

            For navigation properties the tuple is the navigation
            property name prefixed with the entity set name, e.g.,
            ("Customers","Orders"). This name is only used as a SQL
            alias for the target table, to remove ambiguity from certain
            queries that include a join across the navigation property.
            The mangled name must be distinct from the entity set name
            itself. from other such aliases and from other column names
            in this table.

            Foreign key properties contain paths starting with both the
            entity set and the association set names (see
            :py:class:`SQLForeignKeyCollection` for details) unless the
            association is symmetric, in which case they also contain
            the navigation property name (see
            :py:class:`SQLAssociationCollection` for details of these
            more complex cases).

        The default implementation strips the entity set name away and
        uses the default joining character to create a compound name
        before calling
        :py:meth:`quote_identifier` to obtain the SQL string. All names
        are mangled once, on construction, and from then on looked up in
        the dictionary of mangled names.

        If you need to override this method to modify the names used in
        your database you should ensure all other names (including any
        unrecognized by your program) are passed to the default
        implementation for mangling."""
        if len(source_path) > 1:
            source_path = list(source_path)[1:]
        return self.quote_identifier(
            string.join(
                source_path,
                self.field_name_joiner))

    def ro_name(self, source_path):
        """Test if a source_path identifies a read-only property

        This is a an additional extension point to use when you are
        wrapping an existing database with the API.  It allows you to
        manage situations where an entity property has an implied
        value and should be treated read only.

        There are two key use cases, auto-generated primary keys (such
        as auto-increment integer keys) and foreign keys which are
        exposed explicitly as foreign keys and should only be updated
        through an associated navigation property.

        source_path
            A tuple or list of strings describing the path to a property
            in the metadata model.  See :py:meth:`mangle_name` for more
            information.

        The default implementation returns False.

        If you override this method you must ensure all other names
        (including any unrecognized by your program) are passed to the
        default implementation using super."""
        return False

    def source_path_generator(self, entity_set):
        """Utility generator for source path *tuples* for *entity_set*"""
        yield (entity_set.name,)
        for source_path in self.type_name_generator(entity_set.entityType):
            yield tuple([entity_set.name] + source_path)
        if entity_set.entityType.HasStream():
            yield (entity_set.name, u'_value')
        for link_end, nav_name in entity_set.linkEnds.iteritems():
            if not nav_name:
                # use the role name of the other end of the link instead
                # this makes sense because if entity_set is 'Orders' and
                # is linked to 'Customers' but lacks a navigation
                # property then the role name for link_end is likely to
                # be something like 'Order' and the other end is likely
                # to be something like 'Customer' - which provides a
                # reasonable guess at what the navigation property might
                # have been called and, furthermore, is under the
                # control of the model designer without directly
                # affecting the entities themselves.
                yield (entity_set.name, link_end.otherEnd.name)
            else:
                yield (entity_set.name, nav_name)

    def type_name_generator(self, type_def):
        for p in type_def.Property:
            if p.complexType is not None:
                for subPath in self.type_name_generator(p.complexType):
                    yield [p.name] + subPath
            else:
                yield [p.name]

    def bind_entity_set(self, entity_set):
        entity_set.bind(self.get_collection_class(), container=self)

    def bind_navigation_property(self, entity_set, name):
        # Start by making a tuple of the end multiplicities.
        from_as_end = entity_set.navigation[name]
        to_as_end = from_as_end.otherEnd
        # extract the name of the association set
        aset_name = from_as_end.parent.name
        target_set = to_as_end.entity_set
        multiplicity = (
            from_as_end.associationEnd.multiplicity,
            to_as_end.associationEnd.multiplicity)
        # now we can work on a case-by-case basis, note that fk_table may
        # be filled in twice for the same association (if navigation
        # properties are defined in both directions) but this is benign
        # because the definition should be identical.
        if multiplicity in (
                (edm.Multiplicity.One, edm.Multiplicity.One),
                (edm.Multiplicity.ZeroToOne, edm.Multiplicity.ZeroToOne)):
            entity_set.BindNavigation(
                name,
                self.get_symmetric_navigation_class(),
                container=self,
                aset_name=aset_name)
            if aset_name in self.aux_table:
                # This is the navigation property going back the other
                # way, set the navigation name only
                self.aux_table[aset_name][3] = name
            else:
                self.aux_table[aset_name] = [
                    entity_set, name, target_set, "", True]
        elif multiplicity == (edm.Multiplicity.Many, edm.Multiplicity.Many):
            entity_set.BindNavigation(
                name,
                self.get_symmetric_navigation_class(),
                container=self,
                aset_name=aset_name)
            if aset_name in self.aux_table:
                self.aux_table[aset_name][3] = name
            else:
                self.aux_table[aset_name] = [
                    entity_set, name, target_set, "", False]
        elif (multiplicity ==
                (edm.Multiplicity.One, edm.Multiplicity.ZeroToOne)):
            entity_set.BindNavigation(name,
                                      self.get_rk_class(),
                                      container=self, aset_name=aset_name)
            self.fk_table[target_set.name][to_as_end] = (False, True)
        elif multiplicity == (edm.Multiplicity.One, edm.Multiplicity.Many):
            entity_set.BindNavigation(name,
                                      self.get_rk_class(),
                                      container=self, aset_name=aset_name)
            self.fk_table[target_set.name][to_as_end] = (False, False)
        elif (multiplicity ==
                (edm.Multiplicity.ZeroToOne, edm.Multiplicity.Many)):
            entity_set.BindNavigation(
                name,
                self.get_rk_class(),
                container=self,
                aset_name=aset_name)
            self.fk_table[target_set.name][to_as_end] = (True, False)
        elif (multiplicity ==
                (edm.Multiplicity.ZeroToOne, edm.Multiplicity.One)):
            entity_set.BindNavigation(
                name,
                self.get_fk_class(),
                container=self,
                aset_name=aset_name)
            self.fk_table[entity_set.name][from_as_end] = (False, True)
        elif multiplicity == (edm.Multiplicity.Many, edm.Multiplicity.One):
            entity_set.BindNavigation(
                name,
                self.get_fk_class(),
                container=self,
                aset_name=aset_name)
            self.fk_table[entity_set.name][from_as_end] = (False, False)
        else:
            #           (edm.Multiplicity.Many,edm.Multiplicity.ZeroToOne)
            entity_set.BindNavigation(name, self.get_fk_class(
            ), container=self, aset_name=aset_name)
            self.fk_table[entity_set.name][from_as_end] = (True, False)

    def get_collection_class(self):
        """Returns the collection class used to represent a generic entity set.

        Override this method to provide a class derived from
        :py:class:`SQLEntityCollection` when you are customising this
        implementation for a specific database engine."""
        return SQLEntityCollection

    def get_symmetric_navigation_class(self):
        """Returns the collection class used to represent a symmetric relation.

        Override this method to provide a class derived from
        :py:class:`SQLAssociationCollection` when you are customising this
        implementation for a specific database engine."""
        return SQLAssociationCollection

    def get_fk_class(self):
        """Returns the class used when the FK is in the source table.

        Override this method to provide a class derived from
        :py:class:`SQLForeignKeyCollection` when you are customising this
        implementation for a specific database engine."""
        return SQLForeignKeyCollection

    def get_rk_class(self):
        """Returns the class used when the FK is in the target table.

        Override this method to provide a class derived from
        :py:class:`SQLReverseKeyCollection` when you are customising this
        implementation for a specific database engine."""
        return SQLReverseKeyCollection

    def create_all_tables(self):
        """Creates all tables in this container.

        Tables are created in a sensible order to ensure that foreign
        key constraints do not fail but this method is not compatible
        with databases that contain circular references though, e.g.,
        Table A -> Table B with a foreign key and Table B -> Table A
        with a foreign key.  Such databases will have to be created by
        hand. You can use the create_table_query methods to act as a
        starting point for your script."""
        visited = set()
        for es in self.container.EntitySet:
            if es.name not in visited:
                self.create_table(es, visited)
        # we now need to go through the aux_table and create them
        for aset_name in self.aux_table:
            self.get_symmetric_navigation_class().create_table(
                self, aset_name)

    def CreateAllTables(self):      # noqa
        warnings.warn("SQLEntityContainer.CreateAllTables is deprecated, "
                      "use create_all_tables",
                      DeprecationWarning,
                      stacklevel=3)
        return self.create_all_tables()

    def create_table(self, es, visited):
        # before we create this table, we need to check to see if it
        # references another table
        visited.add(es.name)
        fk_mapping = self.fk_table[es.name]
        for link_end, details in fk_mapping.iteritems():
            target_set = link_end.otherEnd.entity_set
            if target_set.name in visited:
                # prevent recursion
                continue
            self.create_table(target_set, visited)
        # now we are free to create the table
        with es.OpenCollection() as collection:
            collection.create_table()

    def acquire_connection(self, timeout=None):
        # block on the module for threadsafety==0 case
        thread_id = threading.current_thread().ident
        now = start = time.time()
        with self.cpool_lock:
            if self.cpool_closing:
                # don't open connections when we are trying to close them
                return None
            while not self.module_lock.acquire(False):
                self.cpool_lock.wait(timeout)
                now = time.time()
                if timeout is not None and now > start + timeout:
                    logging.warn(
                        "Thread[%i] timed out waiting for the the database "
                        "module lock", thread_id)
                    return None
            # we have the module lock
            if thread_id in self.cpool_locked:
                # our thread_id is in the locked table
                cpool_lock = self.cpool_locked[thread_id]
                if cpool_lock.lock.acquire(False):
                    cpool_lock.locked += 1
                    return cpool_lock.dbc
                else:
                    logging.warn(
                        "Thread[%i] moved a database connection to the "
                        "dead pool", thread_id)
                    self.cpool_dead.append(cpool_lock)
                    del self.cpool_locked[thread_id]
            while True:
                if thread_id in self.cpool_unlocked:
                    # take the connection that last belonged to us
                    cpool_lock = self.cpool_unlocked[thread_id]
                    del self.cpool_unlocked[thread_id]
                elif (len(self.cpool_unlocked) + len(self.cpool_locked) <
                      self.cpool_max):
                    # Add a new connection
                    cpool_lock = SQLConnectionLock(self.clocker)
                    cpool_lock.dbc = self.open()
                elif self.cpool_unlocked:
                    # take a connection that doesn't belong to us, popped at
                    # random
                    oldThreadId, cpool_lock = self.cpool_unlocked.popitem()
                    if self.dbapi.threadsafety > 1:
                        logging.debug(
                            "Thread[%i] recycled database connection from "
                            "Thread[%i]", thread_id, oldThreadId)
                    else:
                        logging.debug(
                            "Thread[%i] closed an unused database connection "
                            "(max connections reached)", oldThreadId)
                        # is it ok to close a connection from a different
                        # thread?
                        cpool_lock.dbc.close()
                        cpool_lock.dbc = self.open()
                else:
                    now = time.time()
                    if timeout is not None and now > start + timeout:
                        logging.warn(
                            "Thread[%i] timed out waiting for a database "
                            "connection", thread_id)
                        break
                    logging.debug(
                        "Thread[%i] forced to wait for a database connection",
                        thread_id)
                    self.cpool_lock.wait(timeout)
                    logging.debug(
                        "Thread[%i] resuming search for database connection",
                        thread_id)
                    continue
                cpool_lock.lock.acquire()
                cpool_lock.locked += 1
                cpool_lock.thread = threading.current_thread()
                cpool_lock.thread_id = thread_id
                self.cpool_locked[thread_id] = cpool_lock
                return cpool_lock.dbc
        # we are defeated, no database connection for the caller
        # release lock on the module as there is no connection to release
        self.module_lock.release()
        return None

    def release_connection(self, c):
        thread_id = threading.current_thread().ident
        with self.cpool_lock:
            # we have exclusive use of the cPool members
            if thread_id in self.cpool_locked:
                cpool_lock = self.cpool_locked[thread_id]
                if cpool_lock.dbc is c:
                    cpool_lock.lock.release()
                    self.module_lock.release()
                    cpool_lock.locked -= 1
                    if not cpool_lock.locked:
                        del self.cpool_locked[thread_id]
                        self.cpool_unlocked[thread_id] = cpool_lock
                        self.cpool_lock.notify()
                    return
            logging.error(
                "Thread[%i] attempting to release a database connection "
                "it didn't acquire", thread_id)
            # it seems likely that some other thread is going to leave a
            # locked connection now, let's try and find it to correct
            # the situation
            bad_thread, bad_lock = None, None
            for tid, cpool_lock in self.cpool_locked.iteritems():
                if cpool_lock.dbc is c:
                    bad_thread = tid
                    bad_lock = cpool_lock
                    break
            if bad_lock is not None:
                bad_lock.lock.release()
                self.module_lock.release()
                bad_lock.locked -= 1
                if not bad_lock.locked:
                    del self.cpool_locked[bad_thread]
                    self.cpool_unlocked[bad_lock.thread_id] = bad_lock
                    self.cpool_lock.notify()
                    logging.warn(
                        "Thread[%i] released database connection acquired by "
                        "Thread[%i]", thread_id, bad_thread)
                return
            # this is getting frustrating, exactly which connection does
            # this thread think it is trying to release?
            # Check the dead pool just in case
            idead = None
            for i in xrange(len(self.cpool_dead)):
                cpool_lock = self.cpool_dead[i]
                if cpool_lock.dbc is c:
                    idead = i
                    break
            if idead is not None:
                bad_lock = self.cpool_dead[idead]
                bad_lock.lock.release()
                self.module_lock.release()
                bad_lock.locked -= 1
                logging.warn(
                    "Thread[%i] successfully released a database connection "
                    "from the dead pool", thread_id)
                if not bad_lock.locked:
                    # no need to notify other threads as we close this
                    # connection for safety
                    bad_lock.dbc.close()
                    del self.cpool_dead[idead]
                    logging.warn(
                        "Thread[%i] removed a database connection from the "
                        "dead pool", thread_id)
                return
            # ok, this really is an error!
            logging.error(
                "Thread[%i] attempted to unlock un unknown database "
                "connection: %s", thread_id, repr(c))

    def open(self):
        """Creates and returns a new connection object.

        Must be overridden by database specific implementations because
        the underlying DB ABI does not provide a standard method of
        connecting."""
        raise NotImplementedError

    def break_connection(self, connection):
        """Called when closing or cleaning up locked connections.

        This method is called when the connection is locked (by a
        different thread) and the caller wants to force that thread to
        relinquish control.

        The assumption is that the database is stuck in some lengthy
        transaction and that break_connection can be used to terminate
        the transaction and force an exception in the thread that
        initiated it - resulting in a subsequent call to
        :py:meth:`release_connection` and a state which enables this
        thread to acquire the connection's lock so that it can close it.

        The default implementation does nothing, which might cause the
        close method to stall until the other thread relinquishes
        control normally."""
        pass

    def close(self, timeout=5):
        """Closes this database.

        This method goes through each open connection and attempts to
        acquire it and then close it.  The object is put into a mode
        that disables :py:meth:`acquire_connection` (it returns None
        from now on).

        timeout
            Defaults to 5 seconds.  If connections are locked by other
            *running* threads we wait for those threads to release them,
            calling :py:meth:`break_connection` to speed up termination
            if possible.

            If None (not recommended!) this method will block
            indefinitely until all threads properly call
            :py:meth:`release_connection`.

        Any locks we fail to acquire in the timeout are ignored and
        the connections are left open for the python garbage
        collector to dispose of."""
        with self.cpool_lock:
            self.cpool_closing = True
            while self.cpool_unlocked:
                thread_id, cpool_lock = self.cpool_unlocked.popitem()
                # we don't bother to acquire the lock
                cpool_lock.dbc.close()
            while self.cpool_locked:
                # trickier, these are in use
                thread_id, cpool_lock = self.cpool_locked.popitem()
                no_wait = False
                while True:
                    if cpool_lock.lock.acquire(False):
                        cpool_lock.dbc.close()
                        break
                    elif cpool_lock.thread.isAlive():
                        if no_wait:
                            break
                        else:
                            self.break_connection(cpool_lock.dbc)
                            logging.warn(
                                "Waiting to break database connection "
                                "acquired by Thread[%i]", thread_id)
                            self.cpool_lock.wait(timeout)
                            no_wait = True
                    else:
                        # This connection will never be released properly
                        cpool_lock.dbc.close()
            while self.cpool_dead:
                cpool_lock = self.cpool_dead.pop()
                no_wait = False
                while True:
                    if cpool_lock.lock.acquire(False):
                        cpool_lock.dbc.close()
                        break
                    elif cpool_lock.thread.isAlive():
                        if no_wait:
                            break
                        else:
                            self.break_connection(cpool_lock.dbc)
                            logging.warn(
                                "Waiting to break a database connection from "
                                "the dead pool")
                            self.cpool_lock.wait(timeout)
                            no_wait = True
                    else:
                        # This connection will never be released properly
                        cpool_lock.dbc.close()

    def __del__(self):
        self.close()

    def quote_identifier(self, identifier):
        """Given an *identifier* returns a safely quoted form of it.

        By default we strip double quote and then use them to enclose
        it.  E.g., if the string u'Employee_Name' is passed then the
        string u'"Employee_Name"' is returned."""
        return u'"%s"' % identifier.replace('"', '')

    def prepare_sql_type(self, simple_value, params, nullable=None):
        """Given a simple value, returns a SQL-formatted name of its type.

        Used to construct CREATE TABLE queries.

        simple_value
            A :py:class:`pyslet.odata2.csdl.SimpleValue` instance which
            should have been created from a suitable
            :py:class:`pyslet.odata2.csdl.Property` definition.

        params
            A :py:class:`SQLParams` object.  If simple_value is non-NULL, a
            DEFAULT value is added as part of the type definition.

        nullable
            Optional Boolean that can be used to override the nullable status
            of the associated property definition.

        For example, if the value was created from an Int32 non-nullable
        property and has value 0 then this might return the string
        u'INTEGER NOT NULL DEFAULT ?' with 0 being added to *params*

        You should override this implementation if your database
        platform requires special handling of certain datatypes.  The
        default mappings are given below.

        ==================  =============================================
           EDM Type         SQL Equivalent
        ------------------  ---------------------------------------------
        Edm.Binary          BINARY(MaxLength) if FixedLength specified
        Edm.Binary          VARBINARY(MaxLength) if no FixedLength
        Edm.Boolean         BOOLEAN
        Edm.Byte            SMALLINT
        Edm.DateTime        TIMESTAMP
        Edm.DateTimeOffset  CHARACTER(20), ISO 8601 string
                            representation is used
        Edm.Decimal         DECIMAL(Precision,Scale), defaults 10,0
        Edm.Double          FLOAT
        Edm.Guid            BINARY(16)
        Edm.Int16           SMALLINT
        Edm.Int32           INTEGER
        Edm.Int64           BIGINT
        Edm.SByte           SMALLINT
        Edm.Single          REAL
        Edm.String          CHAR(MaxLength) or VARCHAR(MaxLength)
        Edm.String          NCHAR(MaxLength) or NVARCHAR(MaxLength) if
                            Unicode="true"
        Edm.Time            TIME
        ==================  =============================================

        Parameterized CREATE TABLE queries are unreliable in my
        experience so the current implementation of the native
        create_table methods ignore default values when calling this
        method."""
        p = simple_value.pDef
        column_def = []
        if isinstance(simple_value, edm.BinaryValue):
            if p is None:
                raise NotImplementedError(
                    "SQL binding for Edm.Binary of unbounded length: %s" %
                    p.name)
            elif p.fixedLength:
                if p.maxLength:
                    column_def.append(u"BINARY(%i)" % p.maxLength)
                else:
                    raise edm.ModelConstraintError(
                        "Edm.Binary of fixed length missing max: %s" % p.name)
            elif p.maxLength:
                column_def.append(u"VARBINARY(%i)" % p.maxLength)
            else:
                raise NotImplementedError(
                    "SQL binding for Edm.Binary of unbounded length: %s" %
                    p.name)
        elif isinstance(simple_value, edm.BooleanValue):
            column_def.append(u"BOOLEAN")
        elif isinstance(simple_value, edm.ByteValue):
            column_def.append(u"SMALLINT")
        elif isinstance(simple_value, edm.DateTimeValue):
            column_def.append("TIMESTAMP")
        elif isinstance(simple_value, edm.DateTimeOffsetValue):
            # stored as string and parsed e.g. 20131209T100159+0100
            column_def.append("CHARACTER(20)")
        elif isinstance(simple_value, edm.DecimalValue):
            if p.precision is None:
                precision = 10  # chosen to allow 32-bit integer precision
            else:
                precision = p.precision
            if p.scale is None:
                scale = 0       # from the CSDL model specification
            else:
                scale = p.scale
            column_def.append(u"DECIMAL(%i,%i)" % (precision, scale))
        elif isinstance(simple_value, edm.DoubleValue):
            column_def.append("FLOAT")
        elif isinstance(simple_value, edm.GuidValue):
            column_def.append("BINARY(16)")
        elif isinstance(simple_value, edm.Int16Value):
            column_def.append(u"SMALLINT")
        elif isinstance(simple_value, edm.Int32Value):
            column_def.append(u"INTEGER")
        elif isinstance(simple_value, edm.Int64Value):
            column_def.append(u"BIGINT")
        elif isinstance(simple_value, edm.SByteValue):
            column_def.append(u"SMALLINT")
        elif isinstance(simple_value, edm.SingleValue):
            column_def.append(u"REAL")
        elif isinstance(simple_value, edm.StringValue):
            if p.unicode is None or p.unicode:
                n = "N"
            else:
                n = ""
            if p.fixedLength:
                if p.maxLength:
                    column_def.append(u"%sCHAR(%i)" % (n, p.maxLength))
                else:
                    raise edm.ModelConstraintError(
                        "Edm.String of fixed length missing max: %s" % p.name)
            elif p.maxLength:
                column_def.append(u"%sVARCHAR(%i)" % (n, p.maxLength))
            else:
                raise NotImplementedError(
                    "SQL binding for Edm.String of unbounded length: %s" %
                    p.name)
        elif isinstance(simple_value, edm.TimeValue):
            column_def.append(u"TIME")
        else:
            raise NotImplementedError("SQL type for %s" % p.type)
        if ((nullable is not None and not nullable) or
                (nullable is None and not p.nullable)):
            column_def.append(u' NOT NULL')
        if simple_value:
            # Format the default
            column_def.append(u' DEFAULT ')
            column_def.append(
                params.add_param(self.prepare_sql_value(simple_value)))
        return string.join(column_def, '')

    def prepare_sql_value(self, simple_value):
        """Returns a python object suitable for passing as a parameter

        simple_value
                A :py:class:`pyslet.odata2.csdl.SimpleValue` instance.

        You should override this method if your database requires
        special handling of parameter values.  The default
        implementation performs the following conversions

        ==================  =======================================
           EDM Type         Python value added as parameter
        ------------------  ---------------------------------------
        NULL                None
        Edm.Binary          (byte) string
        Edm.Boolean         True or False
        Edm.Byte            int
        Edm.DateTime        Timestamp instance from DB API module
        Edm.DateTimeOffset  string (ISO 8601 basic format)
        Edm.Decimal         Decimal instance
        Edm.Double          float
        Edm.Guid            (byte) string
        Edm.Int16           int
        Edm.Int32           int
        Edm.Int64           long
        Edm.SByte           int
        Edm.Single          float
        Edm.String          (unicode) string
        Edm.Time            Time instance from DB API module
        ==================  =======================================
        """
        if not simple_value:
            return None
        elif isinstance(simple_value, (
                edm.BooleanValue,
                edm.BinaryValue,
                edm.ByteValue,
                edm.DecimalValue,
                edm.DoubleValue,
                edm.Int16Value,
                edm.Int32Value,
                edm.Int64Value,
                edm.SByteValue,
                edm.SingleValue,
                edm.StringValue
        )):
            return simple_value.value
        elif isinstance(simple_value, edm.DateTimeValue):
            microseconds, seconds = math.modf(simple_value.value.time.second)
            return self.dbapi.Timestamp(
                simple_value.value.date.century *
                100 + simple_value.value.date.year,
                simple_value.value.date.month,
                simple_value.value.date.day,
                simple_value.value.time.hour,
                simple_value.value.time.minute,
                int(seconds), int(1000000.0 * microseconds + 0.5))
        elif isinstance(simple_value, edm.DateTimeOffsetValue):
            return simple_value.value.GetCalendarString(
                basic=True,
                ndp=6,
                dp=".").ljust(
                27,
                ' ')
        elif isinstance(simple_value, edm.GuidValue):
            return simple_value.value.bytes
        elif isinstance(simple_value, edm.TimeValue):
            return self.dbapi.Time(
                simple_value.value.hour,
                simple_value.value.minute,
                simple_value.value.second)
        else:
            raise NotImplementedError(
                "SQL type for " + simple_value.__class__.__name__)

    def read_sql_value(self, simple_value, new_value):
        """Updates *simple_value* from *new_value*.

        simple_value
                A :py:class:`pyslet.odata2.csdl.SimpleValue` instance.

        new_value
                A value returned by the underlying DB API, e.g., from a cursor
                fetch  operation

        This method performs the reverse transformation to
        :py:meth:`prepare_sql_value` and may need to be overridden to
        convert *new_value* into a form suitable for passing to the
        underlying
        :py:meth:`~pyslet.odata2.csdl.SimpleValue.set_from_value`
        method."""
        simple_value.set_from_value(new_value)

    def new_from_sql_value(self, sql_value):
        """Returns a new simple value with value *sql_value*

        The return value is a :py:class:`pyslet.odata2.csdl.SimpleValue`
        instance.

        sql_value
            A value returned by the underlying DB API, e.g., from a
            cursor fetch  operation

        This method creates a new instance, selecting the most
        appropriate type to represent sql_value.  By default
        :py:meth:`pyslet.odata2.csdl.EDMValue.NewSimpleValueFromValue`
        is used.

        You may need to override this method to identify the appropriate
        value type."""
        return edm.EDMValue.NewSimpleValueFromValue(sql_value)


class SQLiteEntityContainer(SQLEntityContainer):

    """Creates a container that represents a SQLite database.

    Additional keyword arguments:

    file_path
            The path to the SQLite database file.

    sqlite_options
        A dictionary of additional options to pass as named arguments to
        the connect method.  It defaults to an empty dictionary, you
        won't normally need to pass additional options and you shouldn't
        change the isolation_level as the collection classes have been
        designed to work in the default mode.

        For more information see sqlite3_

    ..  _sqlite3:   https://docs.python.org/2/library/sqlite3.html

    All other keyword arguments required to initialise the base class
    must be passed on construction except *dbapi* which is automatically
    set to the Python sqlite3 module."""

    def __init__(self, file_path, sqlite_options={}, **kwargs):
        super(SQLiteEntityContainer, self).__init__(dbapi=sqlite3, **kwargs)
        if (not isinstance(file_path, OSFilePath) and
                not type(file_path) in types.StringTypes):
            raise TypeError("SQLiteDB requires an OS file path")
        self.file_path = file_path
        self.sqlite_options = sqlite_options

    def get_collection_class(self):
        """Overridden to return :py:class:`SQLiteEntityCollection`"""
        return SQLiteEntityCollection

    def get_symmetric_navigation_class(self):
        """Overridden to return :py:class:`SQLiteAssociationCollection`"""
        return SQLiteAssociationCollection

    def get_fk_class(self):
        """Overridden to return :py:class:`SQLiteForeignKeyCollection`"""
        return SQLiteForeignKeyCollection

    def get_rk_class(self):
        """Overridden to return :py:class:`SQLiteReverseKeyCollection`"""
        return SQLiteReverseKeyCollection

    def open(self):
        """Calls the underlying connect method.

        Passes the file_path used to construct the container as the only
        parameter.  You can pass the string ':memory:' to create an
        in-memory database.

        Other connection arguments are not currently supported, you can
        derive a more complex implementation by overriding this method
        and (optionally) the __init__ method to pass in values for ."""
        dbc = self.dbapi.connect(str(self.file_path), **self.sqlite_options)
        c = dbc.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.close()
        return dbc

    def break_connection(self, connection):
        """Calls the underlying interrupt method."""
        connection.interrupt()

    def prepare_sql_type(self, simple_value, params, nullable=None):
        """Performs SQLite custom mappings

        We inherit most of the type mappings but the following types use
        custom mappings:

        ==================  ===================================
           EDM Type         SQLite Equivalent
        ------------------  -----------------------------------
        Edm.Decimal         TEXT
        Edm.Guid            BLOB
        Edm.Time            REAL
        Edm.Int64           INTEGER
        ==================  ==================================="""
        p = simple_value.pDef
        column_def = []
        if isinstance(simple_value, (edm.StringValue, edm.DecimalValue)):
            column_def.append(u"TEXT")
        elif isinstance(simple_value, (edm.BinaryValue, edm.GuidValue)):
            column_def.append(u"BLOB")
        elif isinstance(simple_value, edm.TimeValue):
            column_def.append(u"REAL")
        elif isinstance(simple_value, edm.Int64Value):
            column_def.append(u"INTEGER")
        else:
            return super(
                SQLiteEntityContainer,
                self).prepare_sql_type(
                simple_value,
                params,
                nullable)
        if ((nullable is not None and not nullable) or
                (nullable is None and p is not None and not p.nullable)):
            column_def.append(u' NOT NULL')
        if simple_value:
            # Format the default
            column_def.append(u' DEFAULT ')
            column_def.append(
                params.add_param(self.prepare_sql_value(simple_value)))
        return string.join(column_def, '')

    def prepare_sql_value(self, simple_value):
        """Returns a python value suitable for passing as a parameter.

        We inherit most of the value mappings but the following types
        have custom mappings.

        ==================  ==============================================
           EDM Type         Python value added as parameter
        ------------------  ----------------------------------------------
        Edm.Binary          buffer object
        Edm.Decimal         string representation obtained with str()
        Edm.Guid            buffer object containing bytes representation
        Edm.Time            value of
                            :py:meth:`pyslet.iso8601.Time.GetTotalSeconds`
        ==================  ==============================================

        Our use of buffer type is not ideal as it generates warning when
        Python is run with the -3 flag (to check for Python 3
        compatibility) but it seems unavoidable at the current time."""
        if not simple_value:
            return None
        elif isinstance(simple_value, edm.BinaryValue):
            return buffer(simple_value.value)
        elif isinstance(simple_value, edm.DecimalValue):
            return str(simple_value.value)
        elif isinstance(simple_value, edm.GuidValue):
            return buffer(simple_value.value.bytes)
        elif isinstance(simple_value, edm.TimeValue):
            return simple_value.value.GetTotalSeconds()
        else:
            return super(
                SQLiteEntityContainer,
                self).prepare_sql_value(simple_value)

    def read_sql_value(self, simple_value, new_value):
        """Reverses the transformation performed by prepare_sql_value"""
        if new_value is None:
            simple_value.SetNull()
        elif isinstance(new_value, types.BufferType):
            new_value = str(new_value)
            simple_value.set_from_value(new_value)
        elif isinstance(simple_value,
                        (edm.DateTimeValue, edm.DateTimeOffsetValue)):
            # SQLite stores these as strings
            simple_value.set_from_value(
                iso.TimePoint.from_str(new_value, tDesignators="T "))
        elif isinstance(simple_value, edm.TimeValue):
            simple_value.value = iso.Time(totalSeconds=new_value)
        elif isinstance(simple_value, edm.DecimalValue):
            simple_value.value = decimal.Decimal(new_value)
        else:
            simple_value.set_from_value(new_value)

    def new_from_sql_value(self, sql_value):
        """Returns a new simple value instance initialised from *sql_value*

        Overridden to ensure that buffer objects returned by the
        underlying DB API are converted to strings.  Otherwise
        *sql_value* is passed directly to the parent."""
        if isinstance(sql_value, types.BufferType):
            result = edm.BinaryValue()
            result.set_from_value(str(sql_value))
            return result
        else:
            return super(SQLiteEntityContainer, self).new_from_sql_value(
                sql_value)


class SQLiteEntityCollectionBase(SQLCollectionBase):

    """Base class for SQLite SQL custom mappings.

    This class provides some SQLite specific mappings for certain
    functions to improve compatibility with the OData expression
    language."""

    def sql_expression_length(self, expression, params, context):
        """Converts the length method: maps to length( op[0] )"""
        query = ["length("]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(")")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_year(self, expression, params, context):
        """Converts the year method

        maps to CAST(strftime('%Y',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%Y',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_month(self, expression, params, context):
        """Converts the month method

        maps to  CAST(strftime('%m',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%m',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_day(self, expression, params, context):
        """Converts the day method

        maps to  CAST(strftime('%d',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%d',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_hour(self, expression, params, context):
        """Converts the hour method

        maps to  CAST(strftime('%H',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%H',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_minute(self, expression, params, context):
        """Converts the minute method

        maps to  CAST(strftime('%M',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%M',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_second(self, expression, params, context):
        """Converts the second method

        maps to  CAST(strftime('%S',op[0]) AS INTEGER)"""
        query = ["CAST(strftime('%S',"]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(") AS INTEGER)")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_tolower(self, expression, params, context):
        """Converts the tolower method

        maps to lower(op[0])"""
        query = ["lower("]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(")")
        return string.join(query, '')  # don't bother with brackets!

    def sql_expression_toupper(self, expression, params, context):
        """Converts the toupper method

        maps to upper(op[0])"""
        query = ["upper("]
        query.append(self.sql_expression(expression.operands[0], params, ','))
        query.append(")")
        return string.join(query, '')  # don't bother with brackets!


class SQLiteEntityCollection(SQLiteEntityCollectionBase, SQLEntityCollection):

    """SQLite-specific collection for entity sets"""

    def where_last(self, entity, params):
        """In SQLite all tables have a ROWID concept"""
        return ' WHERE ROWID = last_insert_rowid()'


class SQLiteAssociationCollection(
        SQLiteEntityCollectionBase,
        SQLAssociationCollection):

    """SQLite-specific collection for symmetric association sets"""
    pass


class SQLiteForeignKeyCollection(
        SQLiteEntityCollectionBase,
        SQLForeignKeyCollection):

    """SQLite-specific collection for navigation from a foreign key"""
    pass


class SQLiteReverseKeyCollection(
        SQLiteEntityCollectionBase,
        SQLReverseKeyCollection):

    """SQLite-specific collection for navigation to a foreign key"""
    pass


class SQLiteStreamStore(blockstore.StreamStore):

    """A stream store backed by a SQLite database.

    file_path
        The path to the SQLite database file.

    dpath
        The optional directory path to the file system to use for
        storing the blocks of data. If dpath is None then the blocks are
        stored in the SQLite database itself."""

    def load_container(self):
        """Loads and returns a default entity container

        The return value is a
        :py:class:`pyslet.odata2.csdl.EntityContainer` instance with
        an EntitySets called 'Blocks', 'Locks' and 'Streams' that are
        suitable for passing to the constructors of
        :py:class:`pyslet.blockstore.BlockStore`,
        :py:class:`pyslet.blockstore.LockStore` and
        :py:class:`pyslet.blockstore.StreamStore`
        respectively."""
        doc = edmx.Document()
        with file(os.path.join(os.path.dirname(__file__),
                               'streamstore.xml'), 'r') as f:
            doc.Read(f)
        return doc.root.DataServices['StreamStoreSchema.Container']

    def __init__(self, file_path, dpath=None):
        self.container_def = self.load_container()
        if isinstance(file_path, OSFilePath):
            file_path = str(file_path)
        create = not os.path.exists(file_path)
        self.container = SQLiteEntityContainer(file_path=file_path,
                                               container=self.container_def)
        if create:
            self.container.create_all_tables()
        if dpath is None:
            bs = blockstore.FileBlockStore(dpath)
        else:
            bs = blockstore.EDMBlockStore(
                entity_set=self.container_def['Blocks'])
        ls = blockstore.LockStore(entity_set=self.container_def['Locks'])
        blockstore.StreamStore.__init__(
            self, bs, ls, self.container_def['Streams'])
