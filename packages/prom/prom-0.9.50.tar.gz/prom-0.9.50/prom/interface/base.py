import sys
import os
import datetime
import logging
from contextlib import contextmanager

# first party
from ..query import Query
from ..exception import InterfaceError

logger = logging.getLogger(__name__)


class Interface(object):

    connected = False
    """true if a connection has been established, false otherwise"""

    connection = None
    """hold the actual raw connection to the db"""

    connection_config = None
    """a config.Connection() instance"""

    transaction_count = 0
    """
    counting semaphore, greater than 0 if in a transaction, 0 if no current current transaction.

    This will be incremented everytime transaction_start() is called, and decremented
    everytime transaction_stop() is called.

    transaction_fail will set this back to 0 and rollback the transaction
    """

    def __init__(self, connection_config=None):
        self.connection_config = connection_config

    def connect(self, connection_config=None, *args, **kwargs):
        """
        connect to the interface

        this will set the raw db connection to self.connection

        *args -- anything you want that will help the db connect
        **kwargs -- anything you want that the backend db connection will need to actually connect
        """

        if self.connected: return self.connected

        if connection_config: self.connection_config = connection_config

        self.connected = False
        self._connect(self.connection_config)
        if self.connection:
            self.connected = True
            self.transaction_count = 0
        else:
            raise ValueError("the ._connect() method did not set .connection attribute")

        self.log("Connected {}", self.connection_config.interface_name)
        return self.connected

    def _connect(self, connection_config):
        """this *MUST* set the self.connection attribute"""
        raise NotImplementedError("this needs to be implemented in a child class")

    def close(self):
        """
        close an open connection
        """
        if not self.connected: return True

        self.connection.close()
        self.connection = None
        self.connected = False
        self.transaction_count = 0
        self.log("Closed Connection {}", self.connection_config.interface_name)
        return True

    def assure(self, schema=None):
        """handle any things that need to be done before a query can be performed"""
        self.connect()

    def query(self, query_str, *query_args, **query_options):
        """
        run a raw query on the db

        query_str -- string -- the query to run
        *query_args -- if the query_str is a formatting string, pass the values in this
        **query_options -- any query options can be passed in by using key=val syntax
        """
        self.assure()
        return self._query(query_str, query_args, **query_options)

    def _query(self, query_str, query_args=None, query_options=None):
        raise NotImplementedError("this needs to be implemented in a child class")

    @contextmanager
    def transaction(self):
        """
        a simple context manager useful for when you want to wrap a bunch of db calls in a transaction

        This is useful for making sure the db is connected before starting a transaction

        http://docs.python.org/2/library/contextlib.html
        http://docs.python.org/release/2.5/whatsnew/pep-343.html

        example --
            with self.transaction()
                # do a bunch of calls
            # those db calls will be committed by this line
        """
        self.assure()
        self.transaction_start()
        try:
            yield self
            self.transaction_stop()
        except Exception, e:
            self.transaction_fail(e)

    def in_transaction(self):
        """return true if currently in a transaction"""
        return self.transaction_count > 0

    def transaction_start(self):
        """
        start a transaction

        this will increment transaction semaphore and pass it to _transaction_start()
        """
        self.transaction_count += 1
        if self.transaction_count == 1:
            self.log("Transaction started")
        else:
            self.log("Transaction incremented {}", self.transaction_count)

        self._transaction_start(self.transaction_count)
        return self.transaction_count

    def _transaction_start(self, count):
        """count = 1 is the first call, count = 2 is the second transaction call"""
        pass

    def transaction_stop(self):
        """stop/commit a transaction if ready"""
        if self.transaction_count > 0:
            if self.transaction_count == 1:
                self.log("Transaction stopped")
            else:
                self.log("Transaction decremented {}", self.transaction_count)

            self._transaction_stop(self.transaction_count)
            self.transaction_count -= 1

        return self.transaction_count

    def _transaction_stop(self, count):
        """count = 1 is the last time this will be called for current set of transactions"""
        pass

    def transaction_fail(self, e=None):
        """
        rollback a transaction if currently in one

        e -- Exception() -- if passed in, bubble up the exception by re-raising it
        """
        if self.in_transaction():
            self.log("Transaction fail")
            self._transaction_fail(self.transaction_count, e)
            self.transaction_count -= 1

        if not e:
            return True
        else:
            exc_info = sys.exc_info()
            e = InterfaceError(e, exc_info)
            raise e.__class__, e, exc_info[2]

    def _transaction_fail(self, count, e=None):
        pass

    def set_table(self, schema):
        """
        add the table to the db

        schema -- Schema() -- contains all the information about the table
        """
        self.assure(schema)
        if self.has_table(schema.table): return True

        try:
            self.transaction_start()

            self._set_table(schema)

            for index_name, index_d in schema.indexes.iteritems():
                self.set_index(schema, **index_d)

            self.transaction_stop()

        except Exception, e:
            self.transaction_fail(e)

    def _set_table(self, schema):
        raise NotImplementedError("this needs to be implemented in a child class")

    def has_table(self, table_name):
        """
        check to see if a table is in the db

        table_name -- string -- the table to check
        return -- boolean -- True if the table exists, false otherwise
        """
        self.assure()
        tables = self.get_tables(table_name)
        return len(tables) > 0

    def get_tables(self, table_name=""):
        """
        get all the tables of the currently connected db

        table_name -- string -- if you would like to filter the tables list to only include matches with this name
        return -- list -- a list of table names
        """
        self.assure()
        return self._get_tables(table_name)

    def _get_tables(self, table_name):
        raise NotImplementedError("this needs to be implemented in a child class")

    def delete_table(self, schema):
        """
        remove a table matching schema from the db

        schema -- Schema()
        """
        self.assure(schema)
        if not self.has_table(schema.table): return True

        try:
            self.transaction_start()
            self._delete_table(schema)
            self.transaction_stop()
        except Exception, e:
            self.transaction_fail(e)

        return True

    def _delete_table(self, schema):
        raise NotImplementedError("this needs to be implemented in a child class")

    def delete_tables(self, **kwargs):
        """
        removes all the tables from the db

        this is, obviously, very bad if you didn't mean to call this, because of that, you
        have to pass in disable_protection=True, if it doesn't get that passed in, it won't
        run this method
        """
        if not kwargs.get('disable_protection', False):
            raise ValueError('In order to delete all the tables, pass in disable_protection=True')

        self._delete_tables(**kwargs)

    def _delete_tables(self, **kwargs):
        raise NotImplementedError("this needs to be implemented in a child class")

    def get_indexes(self, schema):
        """
        get all the indexes

        schema -- Schema()

        return -- dict -- the indexes in {indexname: fields} format
        """
        self.assure(schema)

        return self._get_indexes(schema)

    def _get_indexes(self, schema):
        raise NotImplementedError("this needs to be implemented in a child class")

    def set_index(self, schema, name, fields, **index_options):
        """
        add an index to the table

        schema -- Schema()
        name -- string -- the name of the index
        fields -- array -- the fields the index should be on
        **index_options -- dict -- any index options that might be useful to create the index
        """
        self.assure()
        try:
            self.transaction_start()
            self._set_index(schema, name, fields, **index_options)
            self.transaction_stop()
        except Exception, e:
            self.transaction_fail(e)

        return True
    
    def _set_index(self, schema, name, fields, **index_options):
        raise NotImplementedError("this needs to be implemented in a child class")

    def prepare_dict(self, schema, d, is_insert):
        """
        prepare the dict for insert/update

        is_insert -- boolean -- True if insert, False if update
        return -- dict -- the same dict, but now prepared
        """
        # update the times
        now = datetime.datetime.utcnow()
        field_created = schema._created
        field_updated = schema._updated
        if is_insert:
            if field_created not in d:
                d[field_created] = now

        if field_updated not in d:
            d[field_updated] = now

        return d

    def insert(self, schema, d):
        """
        Persist d into the db

        schema -- Schema()
        d -- dict -- the values to persist

        return -- dict -- the dict that was inserted into the db
        """
        self.assure(schema)
        d = self.prepare_dict(schema, d, is_insert=True)

        try:
            self.transaction_start()
            r = self._insert(schema, d)
            d[schema._id] = r
            self.transaction_stop()

        except Exception, e:
            self.transaction_fail(e)

        return d

    def _insert(self, schema, d):
        """
        return -- id -- the _id value
        """
        raise NotImplementedError("this needs to be implemented in a child class")

    def update(self, schema, query):
        """
        Persist the query.fields into the db that match query.fields_where

        schema -- Schema()
        query -- Query() -- will be used to create the where clause

        return -- dict -- the dict that was inserted into the db
        """
        self.assure(schema)
        d = query.fields
        d = self.prepare_dict(schema, d, is_insert=False)

        try:
            self.transaction_start()
            r = self._update(schema, query, d)
            self.transaction_stop()

        except Exception, e:
            self.transaction_fail(e)

        return d

    def _update(self, schema, query, d):
        raise NotImplementedError("this needs to be implemented in a child class")

    def set(self, schema, query):
        """
        set d into the db, this is just a convenience method that will call either insert
        or update depending on if query has a where clause

        schema -- Schema()
        query -- Query() -- set a where clause to perform an update, insert otherwise
        return -- dict -- the dict inserted into the db
        """
        try:
            if query.fields_where:
                d = self.update(schema, query)

            else:
                # insert
                d = query.fields
                d = self.insert(schema, d)

        except Exception, e:
            if self.handle_error(schema, e):
                d = self.set(schema, query)
            else:
                exc_info = sys.exc_info()
                e = InterfaceError(e, exc_info)
                raise e.__class__, e, exc_info[2]

        return d

    def _get_query(self, callback, schema, query=None, *args, **kwargs):
        """
        this is just a common wrapper around all the get queries since they are
        all really similar in how they execute
        """
        if not query: query = Query()

        self.assure(schema)
        ret = None

        try:
            # we wrap SELECT queries in a transaction if we are in a transaction because
            # it could cause data loss if it failed by causing the db to discard
            # anything in the current transaction if the query isn't wrapped
            if self.in_transaction():
                self.transaction_start()

            ret = callback(schema, query, *args, **kwargs)

            if self.in_transaction():
                self.transaction_stop()

        except Exception, e:
            if self.in_transaction():
                self.transaction_fail()

            if self.handle_error(schema, e):
                ret = callback(schema, query, *args, **kwargs)

            else:
                exc_info = sys.exc_info()
                e = InterfaceError(e, exc_info)
                raise e.__class__, e, exc_info[2]

        return ret

    def get_one(self, schema, query=None):
        """
        get one row from the db matching filters set in query

        schema -- Schema()
        query -- Query()

        return -- dict -- the matching row
        """
        ret = self._get_query(self._get_one, schema, query)
        if not ret: ret = {}
        return ret

    def _get_one(self, schema, query):
        raise NotImplementedError("this needs to be implemented in a child class")

    def get(self, schema, query=None):
        """
        get matching rows from the db matching filters set in query

        schema -- Schema()
        query -- Query()

        return -- list -- a list of matching dicts
        """
        ret = self._get_query(self._get, schema, query)
        if not ret: ret = []
        return ret

    def _get(self, schema, query):
        raise NotImplementedError("this needs to be implemented in a child class")

    def count(self, schema, query=None):
        ret = self._get_query(self._count, schema, query)
        return int(ret)

    def _count(self, schema, query):
        raise NotImplementedError("this needs to be implemented in a child class")

    def delete(self, schema, query):
        if not query or not query.fields_where:
            raise ValueError('aborting delete because there is no where clause')

        try:
            self.transaction_start()
            ret = self._get_query(self._delete, schema, query)
            self.transaction_stop()

        except Exception, e:
            self.transaction_fail(e)

        return ret

    def _delete(self, schema, query):
        raise NotImplementedError("this needs to be implemented in a child class")

    def handle_error(self, schema, e):
        """
        try and handle the error, return False if the error can't be handled

        TODO -- this method is really general, maybe change this so there are a couple other methods
        like isTableError() and isFieldError() that the child needs to flesh out, maybe someday

        return -- boolean -- True if the error was handled, False if it wasn't
        """
        return False

    def log(self, format_str, *format_args, **log_options):
        """
        wrapper around the module's logger

        format_str -- string -- the message to log
        *format_args -- list -- if format_str is a string containing {}, then format_str.format(*format_args) is ran
        **log_options -- 
            level -- something like logging.DEBUG
        """
        if isinstance(format_str, Exception):
            logger.exception(format_str, *format_args)
        else:
            log_level = log_options.get('level', logging.DEBUG)
            if logger.isEnabledFor(log_level):
                if format_args:
                    logger.log(log_level, format_str.format(*format_args))
                else:
                    logger.log(log_level, format_str)


class SQLInterface(Interface):
    """Generic base class for all SQL derived interfaces"""
    @property
    def val_placeholder(self):
        raise NotImplemented("this property should be set in any children class")

    def _delete_tables(self, **kwargs):
        for table_name in self.get_tables():
            self.transaction_start()
            self._delete_table(table_name)
            self.transaction_stop()

        return True

    def _delete(self, schema, query):
        where_query_str, query_args = self.get_SQL(schema, query, only_where_clause=True)
        query_str = []
        query_str.append('DELETE FROM')
        query_str.append('  {}'.format(schema))
        query_str.append(where_query_str)
        query_str = os.linesep.join(query_str)
        ret = self._query(query_str, query_args, ignore_result=True)

    def _query(self, query_str, query_args=None, **query_options):
        """
        **query_options -- dict
            ignore_result -- boolean -- true to not attempt to fetch results
            fetchone -- boolean -- true to only fetch one result
        """
        ret = True
        # http://stackoverflow.com/questions/6739355/dictcursor-doesnt-seem-to-work-under-psycopg2
        cur = self.connection.cursor()
        ignore_result = query_options.get('ignore_result', False)
        one_result = query_options.get('fetchone', False)
        cur_result = query_options.get('cursor_result', False)

        try:
            if not query_args:
                self.log(query_str)
                cur.execute(query_str)

            else:
                self.log("{}{}{}", query_str, os.linesep, query_args)
                cur.execute(query_str, query_args)

            if cur_result:
                ret = cur

            elif not ignore_result:
                    if one_result:
                        ret = cur.fetchone()
                    else:
                        ret = cur.fetchall()

        except Exception, e:
            self.log(e)
            raise

        return ret

    def _transaction_start(self, count):
        if count == 1:
            self._query("BEGIN", ignore_result=True)
        else:
            # http://www.postgresql.org/docs/9.2/static/sql-savepoint.html
            self._query("SAVEPOINT prom", ignore_result=True)

    def _transaction_stop(self, count):
        """
        http://initd.org/psycopg/docs/usage.html#transactions-control
        https://news.ycombinator.com/item?id=4269241
        """
        if count == 1:
            #self.connection.commit()
            self._query("COMMIT", ignore_result=True)

    def _transaction_fail(self, count, e=None):
        if count == 1:
            #self.connection.rollback()
            self._query("ROLLBACK", ignore_result=True)
        else:
            # http://www.postgresql.org/docs/9.2/static/sql-rollback-to.html
            self._query("ROLLBACK TO SAVEPOINT prom", ignore_result=True)

    def _normalize_date_SQL(self, field_name, field_kwargs):
        raise NotImplemented()

    def _normalize_field_SQL(self, schema, field_name):
        return field_name, self.val_placeholder

    def _normalize_list_SQL(self, schema, symbol_map, field_name, field_vals, field_kwargs=None):

        format_str = ''
        format_args = []
        symbol = symbol_map['symbol']

        if field_kwargs:
            f = schema.fields[field_name]
            if issubclass(f['type'], (datetime.datetime, datetime.date)):
                format_strs = self._normalize_date_SQL(field_name, field_kwargs)
                for fname, fvstr, fargs in format_strs:
                    if format_str:
                        format_str += ' AND '

                    format_str += '{} {} ({})'.format(fname, symbol, ', '.join([fvstr] * len(fargs)))
                    format_args.extend(fargs)

            else:
                raise ValueError('Field {} does not support extended kwarg values'.format(field_name))

        else:
            field_name, format_val_str = self._normalize_field_SQL(schema, field_name)
            format_str = '{} {} ({})'.format(field_name, symbol, ', '.join([format_val_str] * len(field_vals)))
            format_args.extend(field_vals)

        return format_str, format_args

    def _normalize_val_SQL(self, schema, symbol_map, field_name, field_val, field_kwargs=None):

        format_str = ''
        format_args = []

        if field_kwargs:
            symbol = symbol_map['symbol']
            # kwargs take precedence because None is a perfectly valid field_val
            f = schema.fields[field_name]
            if issubclass(f['type'], (datetime.datetime, datetime.date)):
                format_strs = self._normalize_date_SQL(field_name, field_kwargs)
                for fname, fvstr, farg in format_strs:
                    if format_str:
                        format_str += ' AND '

                    format_str += '{} {} {}'.format(fname, symbol, fvstr)
                    format_args.append(farg)

            else:
                raise ValueError('Field {} does not support extended kwarg values'.format(field_name))

        else:
            # special handling for NULL
            symbol = symbol_map['none_symbol'] if field_val is None else symbol_map['symbol']
            field_name, format_val_str = self._normalize_field_SQL(schema, field_name)
            format_str = '{} {} {}'.format(field_name, symbol, format_val_str)
            format_args.append(field_val)

        return format_str, format_args

    def _normalize_sort_SQL(self, field_name, field_vals, sort_dir_str):
        """normalize the sort string

        return -- tuple -- field_sort_str, field_sort_args"""
        raise NotImplemented()

    def get_SQL(self, schema, query, **sql_options):
        """
        convert the query instance into SQL

        this is the glue method that translates the generic Query() instance to the postgres
        specific SQL query, this is where the magic happens

        **sql_options -- dict
            count_query -- boolean -- true if this is a count query SELECT
            only_where_clause -- boolean -- true to only return after WHERE ...
        """
        only_where_clause = sql_options.get('only_where_clause', False)
        symbol_map = {
            'in': {'args': self._normalize_list_SQL, 'symbol': 'IN'},
            'nin': {'args': self._normalize_list_SQL, 'symbol': 'NOT IN'},
            'is': {'arg': self._normalize_val_SQL, 'symbol': '=', 'none_symbol': 'IS'},
            'not': {'arg': self._normalize_val_SQL, 'symbol': '!=', 'none_symbol': 'IS NOT'},
            'gt': {'arg': self._normalize_val_SQL, 'symbol': '>'},
            'gte': {'arg': self._normalize_val_SQL, 'symbol': '>='},
            'lt': {'arg': self._normalize_val_SQL, 'symbol': '<'},
            'lte': {'arg': self._normalize_val_SQL, 'symbol': '<='},
        }

        query_args = []
        query_str = []

        if not only_where_clause:
            query_str.append('SELECT')

            if sql_options.get('count_query', False):
                query_str.append('  count(*) as ct')
            else:
                select_fields = query.fields_select
                if select_fields:
                    query_str.append('  ' + ',{}'.format(os.linesep).join(select_fields))
                else:
                    query_str.append('  *')

            query_str.append('FROM')
            query_str.append('  {}'.format(schema))

        if query.fields_where:
            query_str.append('WHERE')

            for i, field in enumerate(query.fields_where):
                if i > 0: query_str.append('AND')

                field_str = ''
                field_args = []
                sd = symbol_map[field[0]]

                # field[0], field[1], field[2], field[3]
                _, field_name, field_val, field_kwargs = field

                if 'args' in sd:
                    field_str, field_args = sd['args'](schema, sd, field_name, field_val, field_kwargs)

                elif 'arg' in sd:
                    field_str, field_args = sd['arg'](schema, sd, field_name, field_val, field_kwargs)

                query_str.append('  {}'.format(field_str))
                query_args.extend(field_args)

        if query.fields_sort:
            query_sort_str = []
            query_str.append('ORDER BY')
            for field in query.fields_sort:
                sort_dir_str = 'ASC' if field[0] > 0 else 'DESC'
                if field[2]:
                    field_sort_str, field_sort_args = self._normalize_sort_SQL(field[1], field[2], sort_dir_str)
                    query_sort_str.append(field_sort_str)
                    query_args.extend(field_sort_args)

                else:
                    query_sort_str.append('  {} {}'.format(field[1], sort_dir_str))

            query_str.append(',{}'.format(os.linesep).join(query_sort_str))

        if query.bounds:
            limit, offset, _ = query.get_bounds()
            if limit > 0:
                query_str.append('LIMIT {} OFFSET {}'.format(limit, offset))

        query_str = os.linesep.join(query_str)
        return query_str, query_args

    def handle_error(self, schema, e):
        if not self.connection: return False

        ret = False
        if self.connection.closed == 0:
            self.transaction_stop()
            if isinstance(e, InterfaceError):
                ret = self._handle_error(schema, e.e)

            else:
                ret = self._handle_error(schema, e)

        else:
            self.close()
            ret = self.connect()

        return ret

    def _handle_error(self, schema, e):
        raise NotImplemented()

    def _set_all_tables(self, schema):
        """
        You can run into a problem when you are trying to set a table and it has a 
        foreign key to a table that doesn't exist, so this method will go through 
        all fk refs and make sure the tables exist
        """
        self.transaction_start()
        # go through and make sure all foreign key referenced tables exist
        for field_name, field_val in schema.fields.iteritems():
            for fn in ['ref', 'weak_ref']:
                if fn in field_val:
                    self._set_all_tables(field_val[fn])

        # now that we know all fk tables exist, create this table
        self.set_table(schema)
        self.transaction_stop()
        return True

    def _update(self, schema, query, d):
        where_query_str, where_query_args = self.get_SQL(schema, query, only_where_clause=True)
        pk_name = schema.pk

        query_str = 'UPDATE {} SET {} {}'
        query_args = []

        field_str = []
        for field_name, field_val in d.iteritems():
            field_str.append('{} = {}'.format(field_name, self.val_placeholder))
            query_args.append(field_val)

        query_str = query_str.format(
            schema.table,
            ',{}'.format(os.linesep).join(field_str),
            where_query_str
        )
        query_args.extend(where_query_args)

        return self._query(query_str, query_args, ignore_result=True)

    def _get_one(self, schema, query):
        # compensate for getting one with an offset
        if query.has_bounds() and not query.has_limit():
            query.set_limit(1)
        query_str, query_args = self.get_SQL(schema, query)
        return self._query(query_str, query_args, fetchone=True)

    def _get(self, schema, query):
        query_str, query_args = self.get_SQL(schema, query)
        return self._query(query_str, query_args)

    def _count(self, schema, query):
        query_str, query_args = self.get_SQL(schema, query, count_query=True)
        ret = self._query(query_str, query_args)
        if ret:
            ret = int(ret[0]['ct'])
        else:
            ret = 0

        return ret

    def _set_all_fields(self, schema):
        """
        this will add fields that don't exist in the table if they can be set to NULL,
        the reason they have to be NULL is adding fields to Postgres that can be NULL
        is really light, but if they have a default value, then it can be costly
        """
        current_fields = self._get_fields(schema)
        for field_name, field_options in schema.fields.iteritems():
            if field_name not in current_fields:
                if field_options.get('required', False):
                    raise ValueError('Cannot safely add {} on the fly because it is required'.format(field_name))

                else:
                    query_str = []
                    query_str.append('ALTER TABLE')
                    query_str.append('  {}'.format(schema))
                    query_str.append('ADD COLUMN')
                    query_str.append('  {}'.format(self.get_field_SQL(field_name, field_options)))
                    query_str = os.linesep.join(query_str)
                    self._query(query_str, [], ignore_result=True)

        return True

