import sys
from twisted.trial import unittest

if sys.version_info >= (3, 5, 0):
    from ._transaction import TransactionTestCases
else:
    class TransactionTestCases(unittest.TestCase):
        def test_skip(self):
            raise unittest.SkipTest("Not on < 3.5")


__all__ = ["TransactionTestCases"]
