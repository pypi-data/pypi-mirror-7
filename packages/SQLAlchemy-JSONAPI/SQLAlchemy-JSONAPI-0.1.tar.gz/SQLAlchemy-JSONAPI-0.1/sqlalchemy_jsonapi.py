"""
SQLAlchemy-JSONAPI
Colton J. Provias - cj@coltonprovias.com
http://github.com/coltonprovias/sqlalchemy-jsonapi
"""


from functools import wraps
from sqlalchemy.orm.base import MANYTOONE, ONETOMANY


def as_relationship(to_many=False, linked_key=None, link_key=None,
                    columns=[]):
    """
    Decorates methods to add on properties needed to make them act like
    relationships.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        if to_many:
            wrapped.direction = ONETOMANY
        else:
            wrapped.direction = MANYTOONE
        wrapped.key = link_key or wrapped.__name__
        wrapped.linked_key = linked_key or wrapped.key
        wrapped.local_columns = []
        return wrapped
    return wrapper


class JSONAPIMixin:
    """
    Add this mixin to the models that you want to be accessible via your API.
    """
    jsonapi_exclude_columns = []
    jsonapi_extra_columns = []
    jsonapi_column_data_overrides = {}

    jsonapi_exclude_relationships = []
    jsonapi_extra_relationships = []
    jsonapi_override_relationships = {}

    def id(self):
        """ JSON API recommends having an id for each resource """
        raise NotImplemented


class SkipType(object):
    """
    Just a quick thing to help skip conversions.  It's very useful for
    passwords.
    """
    pass


class JSONAPI:
    """
    The JSONAPI Serializer.  This class can be overridden as necessary.
    """
    converters = {}

    def __init__(self, model):
        """
        Let's get started!  The model must be a class of a SQLAlchemy model.
        """
        self.model = model

    def inflector(self, to_inflect):
        """
        Override this to inflect the keys in your API.  This is useful for
        example with ember-json-api, which prefers camelCase.
        """
        return to_inflect

    def convert(self, item, to_convert):
        """
        Converts from a provided type to something a little nicer for JSON
        serialization
        """
        if to_convert is None:
            return None
        if isinstance(to_convert, (str, int, float, bool)):
            return to_convert
        if callable(to_convert):
            return to_convert(item)
        if self.converters[type(to_convert)] is not None:
            converter = self.converters[type(to_convert).__name__]
            return converter(to_convert)
        return SkipType

    def dump_column_data(self, item):
        """
        Dumps the data from the columns/properties for a model instance.
        """
        obj = dict()
        columns = list(item.__table__.columns)
        column_data = dict()

        for column in columns:
            if column.name in item.jsonapi_exclude_columns:
                continue
            column_data[column.name] = getattr(item, column.name)

        for column in item.jsonapi_extra_columns:
            column_data[column] = getattr(item, column)

        column_data.update(item.jsonapi_column_data_overrides)

        for name, value in column_data.items():
            key = self.inflector(name)
            converted = self.convert(item, value)
            if converted != SkipType:
                obj[key] = converted
        return obj

    def dump_relationship_data(self, item, obj, depth):
        """
        Dumps all of the data related to relationships, modifying the dumped
        object as necessary.
        """
        relationships = dict(map((lambda x: (x.key, x)),
                                 item.__mapper__.relationships))

        for key in item.jsonapi_exclude_relationships:
            if key not in relationships.keys():
                continue
            del relationships[key]

        for key in item.jsonapi_extra_relationships:
            relationships[key] = getattr(item, key)

        for key, value in item.jsonapi_override_relationships:
            relationships[key] = getattr(item, value)

        obj['links'] = {}
        linked = {}
        for key, relationship in relationships.items():
            link_key = self.inflector(key)
            if hasattr(relationship, 'mapper'):
                mapper = relationship.mapper.class_
                linked_key = self.inflector(getattr(mapper, 'jsonapi_key',
                                                    mapper.__tablename__))
            else:
                linked_key = self.inflector(relationship.linked_key)

            if relationship.direction == MANYTOONE:
                for column in relationship.local_columns:
                    if isinstance(column, str):
                        col_name = self.inflector(column)
                    else:
                        col_name = self.inflector(column.name)
                    if col_name in obj.keys():
                        obj['links'][link_key] = str(obj[col_name])
                        del obj[col_name]

            if depth > 0:
                if callable(relationship):
                    related = relationship()
                else:
                    related = getattr(item, relationship.key)
                if relationship.direction == MANYTOONE:
                    if isinstance(related, JSONAPIMixin):
                        if linked_key not in linked.keys():
                            linked[linked_key] = {}
                        r_obj, r_lnk = self.dump_object(related, depth - 1)
                        linked.update(r_lnk)
                        linked[linked_key][str(r_obj['id'])] = r_obj
                else:
                    for item in list(related):
                        if not isinstance(item, JSONAPIMixin):
                            continue
                        if link_key not in obj['links'].keys():
                            obj['links'][link_key] = []
                        if linked_key not in linked.keys():
                            linked[linked_key] = {}
                        obj['links'][link_key].append(str(item.id))
                        r_obj, r_lnk = self.dump_object(item, depth - 1)
                        linked.update(r_lnk)
                        linked[linked_key][str(r_obj['id'])] = r_obj
        return obj, linked

    def dump_object(self, item, depth):
        """
        Just something to override if you want to change the way data is
        pre-processed prior to the dump.
        """
        obj = self.dump_column_data(item)
        return self.dump_relationship_data(item, obj, depth)

    def serialize(self, to_serialize, depth=1):
        """
        Call this to return a dict containing the dumped collection or object.
        """
        api_key = getattr(self.model, 'jsonapi_key', self.model.__tablename__)
        api_key = self.inflector(api_key)

        to_return = {api_key: [], 'linked': {}, 'meta': {}}
        linked = dict()

        is_single = isinstance(to_serialize, JSONAPIMixin)

        if is_single:
            to_serialize = [to_serialize]

        for item in to_serialize:
            dumped = self.dump_object(item, depth)
            if dumped is None:
                continue

            obj, new_linked = dumped
            to_return[api_key].append(obj)

            for key in new_linked.keys():
                if key not in linked.keys():
                    linked[key] = dict()
                linked[key].update(new_linked[key])

        for key in linked.keys():
            to_return['linked'][key] = list(linked[key].values())

        if is_single:
            to_return[api_key] = to_return[api_key][0]

        return to_return
