"""
"""
import logging
from functools import wraps

import pymongo
import pyconfig

from humbledb import _version
from humbledb.index import Index
from humbledb.mongo import Mongo
from humbledb.cursor import Cursor
from humbledb.maps import DictMap, NameMap, ListMap
from humbledb.errors import NoConnection, MissingConfig

COLLECTION_METHODS = set([_ for _ in dir(pymongo.collection.Collection) if not
    _.startswith('_') and callable(getattr(pymongo.collection.Collection, _))])
del _ # This is necessary since _ lingers in the module namespace otherwise


class Embed(unicode):
    """ This class is used to map attribute names on embedded subdocuments.

        Example usage::

            class MyDoc(Document):
                config_database = 'db'
                config_collection = 'example'

                embed = Embed('e')
                embed.val = 'v'
                embed.time = 't'

    """
    def as_name_map(self, base_name):
        """ Return this object mapped onto :class:`~humbledb.maps.NameMap`
        objects. """
        name_map = NameMap(base_name)

        for name, value in self.__dict__.items():
            # Skip most everything
            if not isinstance(value, basestring):
                continue
            # Skip private stuff
            if name.startswith('_'):
                continue

            # Concatonate names
            if base_name:
                cname = base_name + '.' + value

            # Recursively map
            if isinstance(value, Embed):
                value = value.as_name_map(cname)
                setattr(name_map, name, value)
            else:
                # Create a new subattribute
                setattr(name_map, name, NameMap(cname))

        return name_map

    def as_reverse_name_map(self, base_name):
        """ Return this object mapped onto reverse-lookup
        :class:`~humbledb.maps.NameMap` objects. """
        name_map = NameMap(base_name)

        for name, value in self.__dict__.items():
            # Skip most everything
            if not isinstance(value, basestring):
                continue
            # Skip private stuff
            if name.startswith('_'):
                continue

            # Recursively map
            if isinstance(value, Embed):
                reverse_value = value.as_reverse_name_map(name)
            else:
                # Create a new subattribute
                reverse_value = NameMap(name)

            setattr(name_map, value, reverse_value)

        return name_map


class CollectionAttribute(object):
    """ Acts as the collection attribute. Refuses to be read unless the
        the executing code is in a :class:`Mongo` context or has already called
        :meth:`Mongo.start`.
    """
    def __get__(self, instance, owner):
        self = instance or owner
        database = self.config_database
        collection = self.config_collection
        if not database or not collection:
            raise MissingConfig("Missing config_database or config_collection")
        # Only allow access to the collection in a Mongo context
        if Mongo.context:
            return Mongo.context.connection[database][collection]
        raise NoConnection("'collection' unavailable without connection "
                "context")


class DocumentMeta(type):
    """ Metaclass for Documents. """
    _ignore_attributes = set(['__test__'])
    _collection_methods = COLLECTION_METHODS
    _wrapped_methods = set(['find', 'find_one', 'find_and_modify'])
    _wrapped_doc_methods = set(['find_one', 'find_and_modify'])
    _update = None

    # Helping pylint with identifying class attributes
    collection = None

    def __new__(mcs, cls_name, bases, cls_dict):
        # Don't process Document superclass
        if cls_name == 'Document' and bases == (dict,):
            return type.__new__(mcs, cls_name, bases, cls_dict)

        # Attribute names that are configuration settings
        config_names = set(['config_database', 'config_collection',
            'config_indexes'])

        # Attribute names that conflict with the dict base class
        bad_names = mcs._collection_methods | set(['clear', 'collection',
            'copy', 'fromkeys', 'get', 'has_key', 'items', 'iteritems',
            'iterkeys', 'itervalues', 'keys', 'pop', 'popitem', 'setdefault',
            'update', 'values', 'viewitems', 'viewkeys', 'viewvalues'])

        # Merge inherited name_maps
        name_map = NameMap()
        reverse_name_map = NameMap()
        for base in reversed(bases):
            if issubclass(base, Document):
                name_map.merge(getattr(base, '_name_map', NameMap()))
                reverse_name_map.merge(getattr(base, '_reverse_name_map',
                    NameMap()))

        # Always have an _id attribute
        if '_id' not in cls_dict and '_id' not in name_map:
            cls_dict['_id'] = '_id'

        # Iterate over the names in `cls_dict` looking for attributes whose
        # values are string literals or `NameMap` subclasses. These attributes
        # will be mapped to document keys where the key is the value
        for name in cls_dict.keys():
            # Raise error on bad attribute names
            if name in bad_names:
                raise TypeError("'{}' bad attribute name".format(name))
            # Skip configuration
            if name in config_names:
                continue
            # Skip most everything
            if not isinstance(cls_dict[name], basestring):
                continue
            # Skip private stuff
            if name.startswith('_') and name != '_id':
                continue

            # Remove the defining attribute from the class namespace
            value = cls_dict.pop(name)
            reverse_value = name

            # Convert Embed objects to nested name map objects
            if isinstance(value, Embed):
                reverse_value = value.as_reverse_name_map(name)
                value = value.as_name_map(value)
            else:
                # Regular attributes are converted to name map objects as well
                reverse_value = NameMap(name)
                value = NameMap(value)

            name_map[name] = value
            reverse_name_map[value] = reverse_value

        # Create _*name_map attributes
        cls_dict['_name_map'] = name_map
        cls_dict['_reverse_name_map'] = reverse_name_map

        # Create collection attribute
        cls_dict['collection'] = CollectionAttribute()

        # Create the class
        cls = type.__new__(mcs, cls_name, bases, cls_dict)

        # Check all the indexes
        indexes = getattr(cls, 'config_indexes', None)
        if indexes is not None:
            if not isinstance(indexes, list):
                raise TypeError("'config_indexes' must be a list")
            for i in xrange(len(indexes)):
                index = indexes[i]
                if isinstance(index, basestring):
                    indexes[i] = Index(index)
                    continue
                elif isinstance(index, Index):
                    index._resolve_index(cls)

        # Return the class if everything worked out OK
        return cls

    def __getattr__(cls, name):
        # Some attributes need to raise an error properly
        if name in cls._ignore_attributes:
            return object.__getattribute__(cls, name)

        # See if we're looking for a collection method
        if name in cls._collection_methods:
            value = getattr(cls.collection, name, None)
            if name in cls._wrapped_methods:
                value = cls._wrap(value)
            return value

        # Check if we have a mapped attribute name
        name_map = object.__getattribute__(cls, '_name_map')
        if name in name_map:
            return name_map[name]

        # Otherwise, let's just error
        return object.__getattribute__(cls, name)

    def _wrap(cls, func):
        """ Wraps ``func`` to ensure that it has the as_class keyword
            argument set to ``cls``. Also guarantees indexes.

            :param function func: Function to wrap.

        """
        # We have to handle find_and_modify separately because it doesn't take
        # a convenient as_class keyword argument, which is really too bad.
        if func.__name__ in cls._wrapped_doc_methods:
            @wraps(func)
            def doc_wrapper(*args, **kwargs):
                """ Wrapper function to gurantee object typing and indexes. """
                cls._ensure_indexes()
                doc = func(*args, **kwargs)
                # If doc is not iterable (e.g. None), then this will error
                if doc:
                    doc = cls(doc)
                return doc
            return doc_wrapper

        # If we've made it this far, it's not find_and_modify, and we can do a
        # "normal" wrap.
        @wraps(func)
        def cursor_wrapper(*args, **kwargs):
            """ Wrapper function to guarantee indexes and object typing. """
            cls._ensure_indexes()
            # Get the cursor
            cursor = func(*args, **kwargs)
            if not isinstance(cursor, pymongo.cursor.Cursor):
                return cursor
            # Change the cursor's class... this is pretty fidgety
            cursor.__class__ = Cursor
            # Assign the document class so the new class knows how to roll
            cursor._doc_cls = cls
            return cursor

        return cursor_wrapper

    def _get_update(cls):
        """ Method to pass through the *dict*'s update method and instead use
            the collection method.

        """
        return cls._update or cls.collection.update

    def _set_update(cls, value):
        """ Allows setting the update attribute for testing with mocks. """
        cls._update = value

    def _del_update(cls):
        """ Allows deleting the update attribute for testing with mocks. """
        cls._update = None

    def mapped_keys(cls):
        """ Return a list of the mapped keys. """
        return cls._reverse_name_map.mapped()

    def mapped_attributes(cls):
        """ Return a list of the mapped attributes. """
        return cls._name_map.mapped()

    update = property(_get_update, _set_update, _del_update)


class Document(dict):
    """ This is the base class for a HumbleDB document. It should not be used
        directly, but rather configured via subclassing.

        Example subclass::

            class BlogPost(Document):
                config_database = 'db'
                config_collection = 'example'

                meta = Embed('m')
                meta.tags = 't'
                meta.slug = 's'
                meta.published = 'p'

                author = 'a'
                title = 't'
                body = 'b'

    """
    __metaclass__ = DocumentMeta

    collection = None
    """ :class:`pymongo.collection.Collection` instance for this document. """

    config_database = None
    """ Database name for this document. """
    config_collection = None
    """ Collection name for this document. """
    config_indexes = None
    """ Indexes for this document. """

    def __repr__(self):
        return "{}({})".format(
                self.__class__.__name__,
                super(Document, self).__repr__())

    def for_json(self):
        """ Return this document as a dictionary, with short key names mapped
            to long names. This method is used by :meth:`pytools.json.as_json`.
        """
        # Get the reverse mapped keys
        reverse_name_map = object.__getattribute__(self, '_reverse_name_map')

        def mapper(doc, submap):
            """ Maps `doc` keys with the given `submap` substitution map. """
            copy = {}
            for key, value in doc.items():
                if key in submap:
                    mapped = submap[key]
                    if isinstance(value, dict):
                        # Recursively map items in a dictionary
                        copy[mapped] = mapper(value, mapped)
                    elif isinstance(value, list):
                        # Map items iteratively in a list
                        copy[mapped] = map_list(value, mapped)
                    else:
                        # Just map regular items
                        copy[mapped] = value
                else:
                    copy[key] = value

            return copy

        def map_list(values, submap):
            """ Maps `values` against `submap`. """
            values = values[:]
            for i in xrange(len(values)):
                value = values[i]
                if isinstance(value, dict):
                    # Recursively map items in a dictionary
                    values[i] = mapper(value, submap)
                elif isinstance(value, list):
                    values[i] = map_list(value, submap)

            return values

        return mapper(self, reverse_name_map)

    def __getattr__(self, name):
        # Get the mapped attributes
        name_map = object.__getattribute__(self, '_name_map')
        reverse_name_map = object.__getattribute__(self, '_reverse_name_map')
        # If the attribute is mapped, map it!
        if name in name_map:
            # name_map is a dict key and potentially a NameMap too here
            name_map = name_map[name]
            key = str(name_map)
            reverse_name_map = reverse_name_map[key]
            # Check if we actually have a key for that value
            if key in self:
                value = self[key]
                # If it's a dict, we need to keep mapping subkeys
                if isinstance(value, dict):
                    value = DictMap(value, name_map, self, key,
                            reverse_name_map)
                elif isinstance(value, list):
                    value = ListMap(value, name_map, self, key,
                            reverse_name_map)
                return value
            elif isinstance(name_map, NameMap):
                # Return an empty dict map to allow sub-key assignment
                return DictMap({}, name_map, self, key, reverse_name_map)
            else:
                # Return if a mapped attribute is missing
                # XXX: This should never happen
                return None  # pragma: no cover

        # TODO: Decide whether to allow non-mapped keys via attribute access
        object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        # Get the mapped attributes
        name_map = object.__getattribute__(self, '_name_map')
        # If it's mapped, let's map it!
        if name in name_map:
            key = name_map[name]
            if isinstance(key, NameMap):
                key = key.key
            # Assign the mapped key
            self[key] = value
            return

        # TODO: Decide whether to allow non-mapped keys via attribute access
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        # Get the mapped attributes
        name_map = object.__getattribute__(self, '_name_map')
        # If we have the key, we delete it
        if name in name_map:
            key = name_map[name]
            if isinstance(key, NameMap):
                key = key.key
            del self[key]
            return

        object.__delattr__(self, name)

    @classmethod
    def _ensure_indexes(cls):
        """ Guarantees indexes are created once per connection instance. """
        ensured = getattr(cls, '_ensured', None)
        if ensured:
            return

        if cls.config_indexes:
            for index in cls.config_indexes:
                logging.getLogger(__name__).info("Ensuring index: {}"
                        .format(index))
                if isinstance(index, Index):
                    index.ensure(cls)
                else:  # pragma: no cover
                    # This code is no longer reachable with the new Indexes,
                    # but I don't want to remove it yet
                    caching_key = 'cache_for' if _version._gte('2.3') else 'ttl'
                    kwargs = {caching_key: (60 * 60 * 24)}
                    cls.collection.ensure_index(getattr(cls, index),
                            background=True, **kwargs)

        logging.getLogger(__name__).info("Indexing ensured.")
        cls._ensured = True

        # Create a reload hook for the first time we run
        if ensured is None:
            @pyconfig.reload_hook
            def _reload():
                """ Allow index recreation if configuration settings change via
                    pyconfig.
                """
                cls._ensured = False

