import doctest
import unittest


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocFileSuite("test_archetype.md"))
    tests.addTests(doctest.DocFileSuite("test_entity.md"))
    tests.addTests(doctest.DocFileSuite("test_query.md"))
    tests.addTests(doctest.DocFileSuite("test_world.md"))
    return tests


if __name__ == "__main__":
    unittest.main()

