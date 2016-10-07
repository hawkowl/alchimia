from .test_engine import create_engine

from twisted.trial import unittest
from twisted.internet.defer import ensureDeferred
from alchimia.context import Transaction

from alchimia.engine import (
    TwistedConnection
)


class TransactionTestCases(unittest.TestCase):

    def test_run(self):
        engine = create_engine()

        async def run():
            async with Transaction(engine) as t:
                self.assertIsInstance(t, TwistedConnection)
                await engine.execute("CREATE TABLE mytable (id int)")

            return await engine.table_names()

        d = ensureDeferred(run())
        assert self.successResultOf(d) == ['mytable']
