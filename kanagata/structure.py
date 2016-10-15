# -*- coding:utf-8 -*-
from collections import UserDict
from collections import UserList


class RestrictedDict(UserDict):
    restriction = None

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs
        super().__init__(self.restriction.validate_dict(data))

    def __getitem__(self, k):
        return self.restriction.access(k, self.data)

    def __setitem__(self, k, v):
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
