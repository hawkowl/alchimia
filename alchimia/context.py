

class Transaction(object):
    """
    A database transaction.
    """
    def __init__(self, engine):
        self._engine = engine

    async def __aenter__(self):
        self.connection = await self._engine.connect()
        self._transaction = await self.connection.begin()
        return self.connection

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self._transaction.commit()
        else:
            await self._transaction.rollback()
