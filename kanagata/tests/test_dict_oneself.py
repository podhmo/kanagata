import unittest


class DictTests(unittest.TestCase):
    def _makeModule(self, *args, **kwargs):
        # person: name, age, Option[gender]
        from kanagata import RestrictionBuilder
        builder = RestrictionBuilder()
        person = builder.define_dict("Person", *args, **kwargs)
        person.add_member("name", required=True)
        person.add_member("age", required=True)
        person.add_member("gender", required=False)
        return builder.build()

    def test_it__from_dict(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20})
        self.assertEqual(data["name"], "foo")
        self.assertEqual(data["age"], 20)

    def test_it__from_dict__with_optional(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20, "gender": "F"})
        self.assertEqual(data["gender"], "F")

    def test_it__from_dict__with_no_member_argments(self):
        m = self._makeModule()
        with self.assertRaises(ValueError):
            m.Person({"name": "foo", "age": 20, "xxxx": "yay!"})

    def test_it__from_dict__with_no_member_argments__with_adtional_properties(self):
        m = self._makeModule(options={"additional_properties": True})
        data = m.Person({"name": "foo", "age": 20, "xxxx": "yay!"})
        self.assertEqual(data["xxxx"], "yay!")

    def test_it__from_dict__keyerror(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20})
        with self.assertRaises(KeyError):
            # support default value?
            self.assertEqual(data["gender"], "F")

    def test_missing_fields(self):
        m = self._makeModule()
        with self.assertRaises(ValueError):
            m.Person(name="foo")

    def test_update(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20})
        data2 = m.Person({"name": "bar", "age": 21, "gender": "M"})
        data.update(data2)
        self.assertEqual(data["name"], "bar")
        self.assertEqual(data["age"], 21)
        self.assertEqual(data["gender"], "M")

    def test_update__with_nomember_argument(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20})
        with self.assertRaises(ValueError):
            data.update(xxx="yay!")

    def test_setitem__with_nomember_argument(self):
        m = self._makeModule()
        data = m.Person({"name": "foo", "age": 20})
        with self.assertRaises(ValueError):
            data["xxx"] = "yay!"
