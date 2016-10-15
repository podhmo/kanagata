import unittest


class Tests(unittest.TestCase):
    def _makeModule(self):
        from kanagata import Builder
        import string
        from functools import reduce
        builder = Builder()
        alphabets = list(string.ascii_lowercase)
        y = reduce(lambda builder, c: builder.add_dict(c, c.upper()), alphabets[:-1], builder)
        y.add_member("z", required=True)
        return builder.build()

    def test_it(self):
        m = self._makeModule()
        data = m.A({"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {"j": {"k": {"l": {"m": {"n": {"o": {"p": {"q": {"r": {"s": {"t": {"u": {"v": {"w": {"x": {"y": {"z": "∅"}}}}}}}}}}}}}}}}}}}}}}}}})
        self.assertTrue(data)
