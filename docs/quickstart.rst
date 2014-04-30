.. _quickstart:

Quick Start
===========

Usage
-----

.. note:: This section provides a quick summary of rexpro features.
           A more detailed listing is available in the full documentations.


.. _quickstart_setup_connection:

Setup Connection
----------------

You'll need to setup the connection to the graph database.

.. code-block:: python

   from rexpro import RexProConnection

   # Without Authentication
   conn = RexProConnection('localhost', 8184, 'graph')
   # With authentication
   #conn = RexProConnection('localhost', 8184, 'graph', username='rexster', password='rexster')


.. _quickstart_define_models:

Basic Query
-----------

We will run a simple query using a groovy script with the supplied params

.. code-block:: python

   #create and return some elements
   #execute takes a script, and optionally, parameter bindings
   #for parameterized queries
   elements = conn.execute(
       """
       def v1 = g.addVertex([prop:bound_param1])
       def v2 = g.addVertex([prop:bound_param2])
       def e = g.addEdge(v1, v2, 'connects', [prop:bound_param3])
       return [v1, v2, e]
       """,
       {'bound_param1':'b1', 'bound_param2':'b2', 'bound_param3':'b3'}
   )

   #the contents of elements will be:
   ({'_id': '0', '_properties': {'prop': 'b1'}, '_type': 'vertex'},
    {'_id': '1', '_properties': {'prop': 'b2'}, '_type': 'vertex'},
    {'_id': '2',
     '_inV': '1',
     '_label': 'connects',
     '_outV': '0',
     '_properties': {'prop': 'b3'},
     '_type': 'edge'})


.. _quickstart_using_models:

Transactional Query
-------------------

If you're using this with a transactional graph you can do requests in the context of the transaction one of two ways

Explicit
""""""""

.. code-block:: python

   conn.test_connection()  # We test the connection here and attempt to re-connect if necessary
   conn.open_transaction()
   conn.execute("//do some stuff")
   conn.close_transaction()


Context Manager
"""""""""""""""

.. code-block:: python

   with conn.transaction():
       conn.execute("//do some other stuff")



Query Scoping & Global Variables
--------------------------------

A RexPro connection is basically a connection to a gremlin REPL. Queries executed with the RexProConnection's
``execute`` method are automatically wrapped in a closure before being executed to avoid cluttering the global
namespace with variables defined in previous queries. A globally available ``g`` graph object is is automatically
defined at the beginning of a RexPro session.

If you would like to define additional global variables, don't define variables with a ``def`` statement. For example:

.. code-block:: python

   #number will become a global variable for this session
   conn.execute("number = 5")

   #another_number is only available for this query
   conn.execute("def another_number = 6")