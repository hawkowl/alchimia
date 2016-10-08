from .test_engine import create_engine

from twisted.trial import unittest
from twisted.internet.defer import ensureDeferred
from alchimia.context import Transaction

from alchimia.engine import (
    TwistedConnection
)


class TransactionTestCases(unittest.TestCase):

    def test_successful_run(self):
        engine = create_engine()

        async def run():
            await engine.execute("CREATE TABLE mytable (id int)")

            async with Transaction(engine) as t:
                self.assertIsInstance(t, TwistedConnection)
                await t.execute("INSERT INTO mytable (id) VALUES (1)")

            ex = await engine.execute("SELECT id FROM mytable")
            return await ex.fetchall()

        d = ensureDeferred(run())
        self.assertEqual(self.successResultOf(d), [(1,)])

    def test_rollback_run(self):
        engine = create_engine()

        async def run():
            await engine.execute("CREATE TABLE mytable (id int)")

            try:
                async with Transaction(engine) as t:
                    self.assertIsInstance(t, TwistedConnection)
                    await t.execute("INSERT INTO mytable (id) VALUES (1)")
                    raise Exception("nope")
            except Exception:
                exp = True

            self.assertTrue(exp)
            ex = await engine.execute("SELECT id FROM mytable")
            return await ex.fetchall()

        d = ensureDeferred(run())
        assert self.successResultOf(d) == []
