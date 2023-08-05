# stdlib
import inspect
import sys
import datetime

# first party
from .query import Query
from . import decorators
from .interface import get_interface
from .utils import get_objects


class Orm(object):
    """
    this is the parent class of any model Orm class you want to create that can access the db

    NOTE -- you must set the schema class as a class property (not an instance property)

    example -- create a user class

        import prom

        class User(prom.Orm):

            schema = prom.Schema(
                "user_table_name",
                username=(str, True),
                password=(str, True)
                email=(str, True)
                unique_user=('username') # set a unique index on user
                index_email=('email') # set a normal index on email
            )

        # create a user
        u = User(username='foo', password='awesome_and_secure_pw_hash', email='foo@bar.com')
        u.set()

        # query for our new user
        u = User.query.is_username('foo').get_one()
        print u.username # foo
    """

    connection_name = ""
    """the name of the connection to use to retrieve the interface"""

    schema = None
    """the Schema() instance that this class will derive all its db info from"""

    @decorators.cachedclassproperty
    def interface(cls):
        """
        return an Interface instance that can be used to access the db

        this will do the work required to find the interface instance, and then set this
        property to that interface instance, so all subsequent calls to this property
        will return the Interface() directly without running this method again

        return -- Interface() -- the interface instance this Orm will use
        """
        i = get_interface(cls.connection_name)
        return i

    @decorators.cachedclassproperty
    def query_class(cls):
        """
        return the Query class this class will use to create Query instances to actually query the db

        To be as magical and helpful as possible, this will start at the child class and look
        for a ChildClassNameQuery defined in the same module, it will then move down through
        each parent class looking for a matching <ParentClassName>Query class defined in the 
        same module as the parent class. If you want to short circuit the auto-finding, you 
        can just set the query_class in the child class

        example -- set the Query class manually

            class Foo(Orm):
                query_class = module.Query

        like .interface, this is cached

        return -- Query -- the query class, not an instance, but the actaul class object, Query if
            a custom one isn't found
        """
        query_class = Query
        parents = inspect.getmro(cls)
        for parent in parents:
            parent_module_name = parent.__module__
            parent_class_name = '{}Query'.format(parent.__name__)
            if parent_module_name in sys.modules:
                parent_class = getattr(sys.modules[parent_module_name], parent_class_name, None)
                if parent_class:
                    query_class = parent_class
                    break

        return query_class

    @decorators.classproperty
    def query(cls):
        """
        return a new Query instance ready to make a db call using the child class

        example -- fluid interface

            results = Orm.query.is_foo('value').desc_bar().get()

        return -- Query() -- every time this is called a new query instance is created using cls.query_class
        """
        query_class = cls.query_class
        return query_class(orm=cls)

    @classmethod
    def query_ref(cls, orm_classpath, cls_pk=None):
        """
        like the query property, but takes a classpath to allow query-ing from another
        Orm class

        the reason why it takes string paths is to avoid infinite recursion import 
        problems because an orm class from module A might have a ref from module B
        and sometimes it is handy to have module B be able to get the objects from
        module A that correspond to the object in module B, but you can't import
        module A into module B because module B already imports module A.

        orm_classpath -- string -- a full python class path (eg, foo.bar.Che)
        cls_pk -- mixed -- automatically set the where field to this value if present
        return -- Query()
        """
        # split orm from module path
        orm_module, orm_class = get_objects(orm_classpath)
        q = orm_class.query
        if cls_pk:
            ref_s = orm_class.schema
            for fn, f in ref_s.fields.iteritems():
                cls_ref_s = f.get('ref', f.get('weak_ref', None))
                if cls_ref_s and cls.schema == cls_ref_s:
                        q.is_field(fn, cls_pk)
                        break

        return q

    @property
    def pk(self):
        """wrapper method to return the primary key, None if the primary key is not set"""
        return getattr(self, self.schema.pk, None)

    @property
    def created(self):
        """wrapper property method to return the created timestamp"""
        return getattr(self, self.schema._created, None)

    @property
    def updated(self):
        """wrapper property method to return the updated timestamp"""
        return getattr(self, self.schema._updated, None)

    @property
    def fields(self):
        """
        return all the fields and their raw values for this Orm instance. This
        property returns a dict with the field names and their current values

        if you want to control the values for outputting to an api, use .jsonable()
        """
        return {k:getattr(self, k, None) for k in self.schema.fields}

    def __init__(self, fields=None, **fields_kwargs):
        fields = self._normalize_dict(fields, fields_kwargs)
        self.reset_modified()
        self.modify(fields)

    @classmethod
    def normalize(cls, fields=None, **fields_kwargs):
        """
        return only the fields in the fields dict that are also in schema

        you can override this method to do some sanity checking of the fields

        fields -- dict -- a dict of field/values
        return -- dict -- the field/values that are in cls.schema
        """
        rd = {}
        fields = cls._normalize_dict(fields, fields_kwargs)
        s = cls.schema
        for field_name, field_val in fields.iteritems():
            if field_name in s.fields:
                rd[field_name] = field_val

        for field_name, field in cls.schema.required_fields.iteritems():
            if field_name not in rd:
                raise KeyError("Missing required field {}".format(field_name))

        return rd

    @classmethod
    def create(cls, fields=None, **fields_kwargs):
        """
        create an instance of cls with the passed in fields and set it into the db

        fields -- dict -- field_name keys, with their respective values
        **fields_kwargs -- dict -- if you would rather pass in fields as name=val, that works also
        """
        fields = cls._normalize_dict(fields, fields_kwargs)
        instance = cls(**cls.normalize(fields))
        instance.set()
        return instance

    @classmethod
    def populate(cls, fields=None, **fields_kwargs):
        """
        create an instance of cls with the passed in fields but don't set it into the db or mark the passed
        in fields as modified, this is used by the Query class to hydrate objects

        fields -- dict -- field_name keys, with their respective values
        **fields_kwargs -- dict -- if you would rather pass in fields as name=val, that works also
        """
        fields = cls._normalize_dict(fields, fields_kwargs)
        instance = cls(**fields)
        instance.reset_modified()
        return instance

    def __setattr__(self, field_name, field_val):
        s = self.schema
        if field_name in s.fields:
            self.modified_fields.add(field_name)

        self.__dict__[field_name] = field_val

    def __int__(self):
        return int(self.pk)

    def insert(self):
        """persist the field values of this orm"""
        fields = self.get_modified()
        q = self.query
        q.set_fields(fields)
        fields = q.set()
        self.modify(fields)
        self.reset_modified()
        return True

    def update(self):
        """re-persist the updated field values of this orm that has a primary key"""
        fields = self.get_modified()

        q = self.query
        _id_name = self.schema.pk
        _id = self.pk
        if _id:
            q.is_field(_id_name, _id)

        q.set_fields(fields)
        fields = q.set()
        self.modify(fields)
        self.reset_modified()
        return True

    def set(self):
        """
        persist the fields in this object into the db, this will update if _id is set, otherwise
        it will insert

        see also -- .insert(), .update()
        """
        ret = False

        _id_name = self.schema.pk
        # we will only use the primary key if it hasn't been modified
        _id = None
        if _id_name not in self.modified_fields:
            _id = self.pk

        if _id:
            ret = self.update()
        else:
            ret = self.insert()

        return ret

    def delete(self):
        """delete the object from the db if _id is set"""
        ret = False
        q = self.query
        _id = self.pk
        _id_name = self.schema.pk
        if _id:
            self.query.is_field(_id_name, _id).delete()
            # get rid of _id
            delattr(self, _id_name)

            # mark all the fields that still exist as modified
            self.reset_modified()
            for field_name in self.schema.fields:
                if hasattr(self, field_name):
                    self.modified_fields.add(field_name)

            ret = True

        return ret

    def get_modified(self):
        """return the modified fields and their new values"""
        fields = {}
        for field_name in self.modified_fields:
            fields[field_name] = getattr(self, field_name)

        return fields

    def modify(self, fields=None, **fields_kwargs):
        """update the fields of this instance with the values in dict fields"""
        fields = self._normalize_dict(fields, fields_kwargs)
        for field_name in self.schema.fields:
            if field_name.startswith('_'):
                if field_name in fields:
                    setattr(self, field_name, fields[field_name])

            else:
                if field_name in fields:
                    setattr(self, field_name, fields[field_name])
                else:
                    if not hasattr(self, field_name):
                        setattr(self, field_name, None)
                        self.modified_fields.discard(field_name)

#        for field_name in self.schema.normal_fields:
#            field_val = fields.get(field_name, None)
#            setattr(self, field_name, field_val)
#            if field_name not in fields:
#                self.modified_fields.discard(field_name)
#
#        for field_name in self.schema.magic_fields:
#            if field_name in fields:
#                setattr(self, field_name, fields[field_name])

    def is_modified(self):
        """true if a field has been changed from its original value, false otherwise"""
        return len(self.modified_fields) > 0

    def reset_modified(self):
        """
        reset field modification tracking

        this is handy for when you are loading a new Orm with the results from a query and
        you don't want set() to do anything, you can Orm(**fields) and then orm.reset_modified() to
        clear all the passed in fields from the modified list
        """
        self.modified_fields = set()

    def jsonable(self, *args, **options):
        """
        return a public version of this instance that can be jsonified

        Note that this does not return _id, _created, _updated, the reason why is
        because lots of times you have a different name for _id (like if it is a 
        user object, then you might want to call it user_id instead of _id) and I
        didn't want to make assumptions

        note 2, I'm not crazy about the name, but I didn't like to_dict() and pretty
        much any time I need to convert the object to a dict is for json, I kind of
        like dictify() though, but I've already used this method in so many places
        """
        d = {}
        def default_field_type(field_type):
            r = ''
            if issubclass(field_type, int):
                r = 0
            elif issubclass(field_type, bool):
                r = False
            elif issubclass(field_type, float):
                r = 0.0

            return r

        for field_name, field_info in self.schema.normal_fields.iteritems():
            try:
                d[field_name] = getattr(self, field_name, None)
                if d[field_name]:
                    if isinstance(d[field_name], datetime.date):
                        d[field_name] = str(d[field_name])
                    elif isinstance(d[field_name], datetime.datetime):
                        d[field_name] = str(d[field_name])

                else:
                    d[field_name] = default_field_type(field_info['type'])

            except AttributeError:
                d[field_name] = default_field_type(field_info['type'])

        return d

    @classmethod
    def _normalize_dict(cls, fields, fields_kwargs):
        """lot's of methods take a dict or kwargs, this combines those"""
        if not fields:
            fields = {}

        if fields_kwargs:
            fields.update(fields_kwargs)

        return fields

    @classmethod
    def install(cls):
        """install the Orm's table using the Orm's schema"""
        return cls.interface.set_table(cls.schema)

