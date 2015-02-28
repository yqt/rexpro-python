from rexpro import RexProConnection

conn = RexProConnection('localhost', 8184, 'graph')

# Use the management system to define properties and build indexes
conn.execute("""
from com.tinkerpop.blueprints import Vertex
ms = g.management_system
name = ms.make_property_key('name')
age = ms.make_property_key('age', data_type=Integer)
ms.build_index('by-name', Vertex, keys=[name])
ms.build_index('by-name-and-age', Vertex, keys=[name, age])
ms.commit()
""", language='python')


# the management system can also be used as a context manager with an implied commit when exiting the context
# this might be desirable if you'd like to cut down on some typing or group different blocks of code in transactions
conn.execute("""
from com.tinkerpop.blueprints import Vertex
with g.management_system as ms:
    name = ms.make_property_key('name')
    age = ms.make_property_key('age', data_type=Integer)
    ms.build_index('by-name', Vertex, keys=[name])
    ms.build_index('by-name-and-age', Vertex, keys=[name, age])
""", language='python')

