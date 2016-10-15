# -*- coding:utf-8 -*-
from .structure import RestrictedDict
from .structure import RestrictedList


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

    def __iter__(self):
        yield from self.pool.items()


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
