from collections import namedtuple
from collections import OrderedDict
from collections import UserDict
from collections import UserList


Any = None
Field = namedtuple("Field", "name required type")


class DictRestriction:
    def __init__(self, name, fields, options, repository):
        self.name = name
        self.fields = fields
        self.options = options
        self.repository = repository

    def access(self, k, data):
        return self.validate_member(k, data, skip_type_validation=True)

    def validate_dict(self, data, skip_member_validation=False):
        if not skip_member_validation:
            for k in data.keys():
                self.validate_member(k, data)

        # todo: performance
        keys_from_fields = set(v.name for v in self.fields.values() if v.required)
        keys_from_data = set(data.keys())
        diff = keys_from_fields.difference(keys_from_data)
        if diff:
            raise ValueError("{}: required fields {} are not found".format(self.name, diff))
        return data

    def validate_member(self, k, data, skip_type_validation=False):
        value = data[k]
        return self.validate_member_value(k, value, skip_type_validation=skip_type_validation)

    def validate_member_value(self, k, value, skip_type_validation):
        field = self.fields.get(k)
        if field is None:
            if not self.options["additional_properties"]:
                raise ValueError("{}: unsupported field {!r}, field members={}".format(self.name, k, list(self.fields.keys())))
            else:
                return value

        if skip_type_validation or field.type is Any:
            return value
        else:
            return field.type(value)

    def __call__(self, value):
        dict_class = self.repository[self.name]
        return dict_class(value)

    def __repr__(self):
        return "<{}Restriction at {}>".format(self.name, hex(id(self)))


class ListRestriction:
    def __init__(self, restriction, repository):
        self.restriction = restriction
        self.repository = repository

    def __call__(self, value):
        list_class = self.repository[self.restriction.name]
        return list_class(value)

    def validate_list(self, xs):
        return [self.restriction.validate_dict(x) for x in xs]

    def validate_item(self, x):
        if hasattr(x, "restriction") and x.restriction is self.restriction:
            return x
        return self.restriction.validate_dict(x)

    def access(self, i, xs):
        return xs[i]


class Repository:
    def __init__(self):
        self.pool = {}

    def __getitem__(self, k):
        return self.pool[k]

    def get(self, k):
        return self.pool.get(k)

    def register(self, name, restriction, force=False):
        if not force and name in self.pool:
            if restriction != self.pool[name].restriction:
                raise ValueError("conflicted. {} is already existed.".format(self.pool[name].restriction))
        self.pool[name] = self.create_container(name, restriction)


class RestrictedDictRepository(Repository):
    def create_container(self, name, restriction):
        cls = type("{}Dict".format(name), (RestrictedDict, ), {})
        cls.restriction = restriction
        return cls


class RestrictedListRepository(Repository):
    def create_container(self, name, restriction):
        cls = type("{}List".format(name), (RestrictedList, ), {})
        cls.restriction = restriction
        return cls


class Module:
    def __init__(self):
        self.dict_repository = RestrictedDictRepository()
        self.list_repository = RestrictedListRepository()

    def __getattr__(self, k):
        v = self.dict_repository.get(k) or self.list_repository.get(k)
        if v is None:
            raise AttributeError(k)
        return v


class RestrictionBuilder:
    default_options = {"additional_properties": False}

    def __init__(self, name=None, factory_name=None, options=None, restriction=None, parent=None, module=None):
        self.name = name
        self.factory_name = factory_name
        self.parent = parent
        self.options = options or self.__class__.default_options
        self.module = module or Module()
        self.restriction = restriction
        if restriction is None:
            self.restriction, _ = self.get_or_create_restriction(self.factory_name, self.options)

    @property
    def fields(self):
        return self.restriction.fields

    def get_or_create_restriction(self, factory_name, options):
        repository = self.module.dict_repository
        dict_class = repository.get(factory_name)
        if dict_class is not None:
            return dict_class.restriction, False

        restriction = DictRestriction(factory_name, OrderedDict(), options, repository=repository)
        return restriction, True

    def add_member(self, name, required=True, type=Any, force=False):
        if not force and name in self.fields:
            raise ValueError("conflicted. {} is already existed.".format(self.fields[name]))
        field = Field(name=name, required=required, type=type)
        self.fields[name] = field

    def define_dict(self, factory_name, required=True, restriction=None, options=None):
        options = options or self.options
        sub = self.__class__(factory_name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.dict_repository
        repository.register(factory_name, sub.restriction)
        return sub

    def add_dict(self, name, factory_name, required=True, restriction=None, options=None):
        options = options or self.options
        sub = self.__class__(name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.dict_repository
        repository.register(factory_name, sub.restriction)
        self.fields[name] = Field(name=name, required=required, type=sub.restriction)
        return sub

    def add_list(self, name, factory_name, required=True, restriction=None, options=None):
        options = options or self.options
        dict_restriction, created = self.get_or_create_restriction(factory_name, options)
        if created:
            self.module.dict_repository.register(factory_name, dict_restriction)
        restriction = ListRestriction(dict_restriction, repository=self.module.list_repository)
        sub = self.__class__(name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.list_repository
        repository.register(factory_name, sub.restriction)
        self.fields[name] = Field(name=name, required=required, type=sub.restriction)
        return sub

    def build(self):
        return self.module


class RestrictedDict(UserDict):
    restriction = None

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs
        self.restriction.validate_dict(data)
        super().__init__(data)

    def __getitem__(self, k):
        return self.restriction.access(k, self.data)

    def __setitem__(self, k, v):
        if hasattr(v, "restriction") and v.restriction is self.restriction.fields[k]:
            super().__setitem__(k, v)
        else:
            super().__setitem__(k, self.restriction.validate_member_value(k, v, skip_type_validation=False))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.restriction.validate_dict(self.data, skip_member_validation=True)


class RestrictedList(UserList):
    restriction = None

    def __init__(self, *args):
        if not args:
            super().__init__()
        else:
            super().__init__(self.restriction.validate_list(args[0]))

    def __getitem__(self, k):
        return self.restriction.access(k, self.data)

    def append(self, x):
        self.restriction.validate_item(x)
        return super().append(x)

    def extend(self, xs):
        return super().extend(self.restriction.validate_item(x) for x in xs)
