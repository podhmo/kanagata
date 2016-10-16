# -*- coding:utf-8 -*-
import sys
from collections import OrderedDict
from .restriction import Field, Any, NOTSET
from .restriction import ListRestriction
from .restriction import DictRestriction
from .repository import RestrictedDictRepository
from .repository import RestrictedListRepository


class Module:
    def __init__(self):
        self.dict_repository = RestrictedDictRepository()
        self.list_repository = RestrictedListRepository()

    def __getattr__(self, k):
        v = self.dict_repository.get(k) or self.list_repository.get(k)
        if v is None:
            raise AttributeError(k)
        return v

    def expose(self, d):
        for name, dict_class in self.dict_repository:
            d[name] = dict_class


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

    def add_member(self, name, required=True, type=Any, force=False, default=NOTSET):
        if not force and name in self.fields:
            raise ValueError("conflicted. {} is already existed.".format(self.fields[name]))
        field = Field(name=name, required=required, type=type, default=default)
        self.fields[name] = field

    def define_dict(self, factory_name, required=True, restriction=None, options=None):
        options = options or self.options
        sub = self.__class__(factory_name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.dict_repository
        repository.register(factory_name, sub.restriction)
        return sub

    def add_dict(self, name, factory_name, required=True, restriction=None, options=None, default=NOTSET):
        options = options or self.options
        sub = self.__class__(name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.dict_repository
        repository.register(factory_name, sub.restriction)
        self.fields[name] = Field(name=name, required=required, type=sub.restriction, default=default)
        return sub

    def add_list(self, name, factory_name, required=True, restriction=None, options=None, default=NOTSET):
        options = options or self.options
        dict_restriction, created = self.get_or_create_restriction(factory_name, options)
        if created:
            self.module.dict_repository.register(factory_name, dict_restriction)
        restriction = ListRestriction(dict_restriction, repository=self.module.list_repository)
        sub = self.__class__(name, factory_name, restriction=restriction, options=options, parent=self, module=self.module)
        repository = self.module.list_repository
        repository.register(factory_name, sub.restriction)
        self.fields[name] = Field(name=name, required=required, type=sub.restriction, default=default)
        return sub

    def build(self):
        return self.module

    def __enter__(self):
        return self

    _depth = 1

    @property
    def is_root_builder(self):
        return self.name is None and self.factory_name is None

    def __exit__(self, type, value, traceback):
        if self.is_root_builder:
            frame = sys._getframe(self._depth)
            self.build().expose(frame.f_globals)
