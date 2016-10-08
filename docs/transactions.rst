Transactions
============

Manually
--------

When using ``engine.connect()`` to get a connection, you can run the database queries and commands of that connection in a transaction.
Transactions give you the power to cancel previous changes if a later one in the same transaction fails, or would leave your database in an inconsistent state.

``connection.begin()`` will return a Deferred which fires with a ``TwistedTransaction`` when the transaction has begun, and ``TwistedTransaction.commit()`` or ``TwistedTransaction.rollback()`` will return a Deferred which fires when the transaction is committed or rolled back.

Context Manager
---------------

Alchimia provides an asynchronous context manager to provide transactions for Python 3.5+ users.
You wrap your code in an ``alchimia.context.Transaction`` using ``async with``, and use the provided connection to execute your database code.
If an exception occurs in the context manager, it will be rolled back.

Example:

.. code-block:: python3

    from alchimia import TWISTED_STRATEGY
    from alchimia.context import Transaction

    from sqlalchemy import create_engine, MetaData
    from sqlalchemy import Table, Column, Integer, String
    from sqlalchemy.schema import CreateTable

    from twisted.internet import reactor, defer
    from twisted.internet.task import react

    connectionString = "sqlite:///test.db"
    engine = create_engine(
        connectionString, reactor=reactor, strategy=TWISTED_STRATEGY)
    metadata = MetaData()

    cities = Table("cities", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("country", String),
        Column("comments", String)
    )

    async def main(reactor):
        cityData = [
            {
                "name": "Perth",
                "country": "Australia",
                "comments": "Capital of Western Australia"
            },
            {
                "name": "Paris",
                "country": "United States of America",
                "comments": "Not the French city"
            },
            {
                "name": "Paris",
                "country": "France",
                "comments": "Capital of France"
            }
        ]

        await engine.execute(CreateTable(cities), returnsData=False)

        async with Transaction(engine) as t:
            # This transaction will be committed
            await t.execute(cities.insert(), cityData)

        try:
            async with Transaction(engine) as t:
                # This one will not
                await t.execute(cities.insert(), [{
                    "name": "New York",
                    "country": "United States of America",
                    "comments": "In New York State"}])
                raise Exception("Whoops!")
        except:
            pass

        query = await engine.execute("SELECT * from cities")
        results = await query.fetchall()

        # Will not contain New York
        print(results)

    if __name__ == "__main__":
        react(lambda reactor: defer.ensureDeferred(main(reactor)), [])


Limitations
-----------

The ``sqlite`` module in Python 3.5 and below `contains a bug <http://bugs.python.org/issue10740>`_ that will autocommit certain statements, even if you are in a transaction.
