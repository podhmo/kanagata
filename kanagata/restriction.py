# -*- coding:utf-8 -*-
from collections import namedtuple


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
            if not hasattr(data, "keys"):
                raise ValueError("{}: required dict but {!r}. (members={})".format(self.name, data, list(self.fields.keys())))
            for k in data.keys():
                data[k] = self.validate_member(k, data)

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
                raise ValueError("{}: unsupported field {!r}, members={}".format(self.name, k, list(self.fields.keys())))
            else:
                return value

        if skip_type_validation or field.type is Any:
            return value
        else:
            return field.type(value)

    def __call__(self, value):
        if hasattr(value, "restriction") and value.restriction is self:
            return value
        dict_class = self.repository[self.name]
        return dict_class(value)

    def __repr__(self):
        return "<{}Restriction at {}>".format(self.name, hex(id(self)))


class ListRestriction:
    def __init__(self, restriction, repository):
        self.restriction = restriction
        self.repository = repository

    def __call__(self, value):
        if hasattr(value, "restriction") and value.restriction is self:
            return value
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
