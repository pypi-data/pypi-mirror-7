Transactions
============

All database operations must use a transaction. Transactions are created
automatically when you perform a SQL operation, but you must provide a way to
commit a transaction. There are two ways to manage transaction: automatically
for each request using pyramid_tm, or manually.

Using pyramid_tm
----------------

The easiest way to handle transactions is to use the `pyramid_tm
<https://pypi.python.org/pypi/zope.sqlalchemy>`_ package.

.. code-block:: python
   :linenos:

   def main():
       config = Configurator()
       config.include('pyramid_tm')
       config.include('pyramid_sqlalchemy')

pyramid_tm will automatically commit the transaction when processing of a
request has finished. If an exception is raised during request processing the
transaction will be aborted. Note that raising HTTP exceptions such as
HTTPFound will also abort the transaction. This is the main difference in
Pyramid between raising a HTTP exception and returning it.


Managing transactions manually
------------------------------

You can also manage transactions manually. To do this you will need to use the
API provided by the `transaction <https://pypi.python.org/pypi/transaction>`_
package. The easiest way to do this is to use its context manager.

.. code-block:: python
   :linenos:

   import transaction
   from pyramid_sqlalchemy import Session
   from .model import MyModel

   def my_func():
       with transaction.manager:
           Session.query(MyModel).update({'active': False})


The transaction manager will automatically commit the transaction, unless an
exception is raised, in which case it will abort the transaction. You can also
abort the transaction manually by calling ``abort()`` on the transaction.

.. code-block:: python
   :linenos:

   import transaction
   from pyramid_sqlalchemy import Session
   from .model import MyModel

   def my_func():
       with transaction.manager as tx:
           Session.query(MyModel).update({'active': False})
           if something_bad_happened:
               tx.abort()

If you prefer not to use the context manager you can also use the underlying
transaction API directly. The methods you can use are:

* ``transaction.abort()`` aborts the current transaction.
* ``transaction.commit()`` commits the current transaction.

.. code-block:: python
   :linenos:

   import transaction
   from pyramid_sqlalchemy import Session
   from .model import MyModel

   def my_func():
       Session.query(MyModel).update({'active': False})
       if something_bad_happened:
           tx.abort()
       else:
           tx.commit()


Non-ORM modifications
---------------------

zope.sqlalchemy, which is used to handle the integration of SQLAlchemy and
the transaction system, can only detect changes made through the ORM. Sometimes
you may need to bypass the ORM and execute SQL statements directly using SQLAlchemy's
core API.

.. code-block:: python
   :linenos:

   from pyramid_sqlalchemy import Session
   from myapp.models import MyModel

   # Execute an UPDATE query directly, without using the ORM
   Session.query(MyModel).update({'active': False})

If you do this zope.sqlalchemy will not detect that you made any changes and
will not correctly commit the transaction. To handle this you must call
``mark_changed()`` with the current session.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,7

   from pyramid_sqlalchemy import Session
   from zope.sqlalchemy import mark_changed
   from myapp.models import MyModel

   session = Session()
   session.query(MyModel).update({'active': False})
   mark_changed(session)
