import unittest


class DictNestedTests(unittest.TestCase):
    def _makeModule(self):
        # group: name, users
        # user: name, age, Option[skills], Option[school]
        # skill: name
        # school: name, groups
        from kanagata import RestrictionBuilder
        b = RestrictionBuilder()
        group = b.define_dict("Group")
        group.add_member("name", required=True)
        gusers = group.add_list("users", "User", required=True)

        user = b.define_dict("User")
        self.assertEqual(gusers.restriction.restriction, user.restriction)
        user.add_member("name", required=True)
        user.add_member("age", required=True)
        user.add_dict("school", "School", required=False)
        user.add_list("skills", "Skill", required=False)

        skill = b.define_dict("Skill")
        skill.add_member("name", required=True)

        school = b.define_dict("School")
        school.add_member("name")
        school.add_list("groups", "Group", required=True)
        return b.build()

    def test_dict__missing_arguments(self):
        m = self._makeModule()
        with self.assertRaises(ValueError):
            m.Group(name="g")

    def test_child_list(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[{"name": "foo", "age": 10}])
        self.assertEqual(len(group["users"]), 1)

    def test_child_list__missing_arguments(self):
        m = self._makeModule()
        with self.assertRaises(ValueError):
            m.Group(name="g", users=[{"name": "foo"}])

    def test_child_list__append(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        group["users"].append({"name": "foo", "age": 20})
        self.assertEqual(1, len(group["users"]))

    def test_child_list__append__typed_item(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        group["users"].append(m.User({"name": "foo", "age": 20}))
        self.assertEqual(1, len(group["users"]))

    def test_child_list__append__with__missing_arguments(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        with self.assertRaises(ValueError):
            group["users"].append({"name": "foo"})

    def test_child_list__extend(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        group["users"].extend([{"name": "foo", "age": 20}])
        self.assertEqual(1, len(group["users"]))

    def test_child_list__extend__typed_item(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        group["users"].extend([m.User({"name": "foo", "age": 20})])
        self.assertEqual(1, len(group["users"]))

    def test_child_list__extend__with__missing_arguments(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        with self.assertRaises(ValueError):
            group["users"].extend([{"name": "foo"}])

    def test_child_list__extend__typed_list(self):
        m = self._makeModule()
        group = m.Group(name="g", users=[])
        UserList = m.list_repository["User"]
        group["users"].extend(UserList([m.User({"name": "foo", "age": 20})]))
        self.assertEqual(1, len(group["users"]))

    def test_child_dict(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})  # default: groups=[]
        self.assertEqual(user["school"]["name"], "ABC")
        self.assertEqual(list(sorted(user["school"].keys())), ["groups", "name"])

    def test_child_dict__missing_arguments(self):
        m = self._makeModule()
        with self.assertRaises(ValueError):
            m.User(name="foo", age=10, school={})

    def test_child_dict__setitem(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        user["school"] = {"name": "XYZ", "groups": []}
        self.assertEqual(user["school"]["name"], "XYZ")

    def test_child_dict__setitem__typed_item(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        user["school"] = m.School({"name": "XYZ", "groups": []})
        self.assertEqual(user["school"]["name"], "XYZ")

    def test_child_dict__setitem__with__missing_arguments(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        with self.assertRaises(ValueError):
            user["school"] = {"name": "XYZ"}

    def test_child_dict__setitem__with__extra_arguments(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        with self.assertRaises(ValueError):
            user["school"]["xxxx"] = "zzzz"

    def test_child_dict__update(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        user["school"].update({"name": "XYZ", "groups": []})
        self.assertEqual(user["school"]["name"], "XYZ")

    def test_child_dict__update__typed_item(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        user["school"].update(m.School({"name": "XYZ", "groups": []}))
        self.assertEqual(user["school"]["name"], "XYZ")

    def test_child_dict__update__with__missing_arguments(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        user["school"].update({"name": "XYZ"})
        self.assertEqual(user["school"]["name"], "XYZ")

    def test_child_dict__update__with__extra_arguments(self):
        m = self._makeModule()
        user = m.User(name="foo", age=10, school={"name": "ABC", "groups": []})
        with self.assertRaises(ValueError):
            user["school"].update({"name": "XYZ", "xxx": "zzz"})
