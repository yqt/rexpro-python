from rexpro import RexProConnection

conn = RexProConnection('localhost', 8184, 'graph')

conn.execute("""
from com.thinkaurelius.titan.example import GraphOfTheGodsFactory
from com.thinkaurelius.titan.core import SchemaViolationException

try:
    #Try to load up the graph of the gods if it's not already loaded
    GraphOfTheGodsFactory.load(g.graph)
except SchemaViolationException:
    pass
""", language='python')

# Run some examples based on https://github.com/thinkaurelius/titan/wiki/Getting-Started
# `as` and `in` have trailing underscores to avoid clashing with python keywords
# whenever possible, naming conventions are the same as other gremlin language implementations
saturn_grandchild = conn.execute("""
g.V.has('name', 'saturn').in_('father').in_('father').name
""", language='python')

assert saturn_grandchild == ['hercules']

saturn_grandchild = conn.execute("""
g.V.has('name', 'saturn').as_('x').in_('father').loop('x', lambda it: it.loops < 3).name
""", language='python')

assert saturn_grandchild == ['hercules']

hercules_parent_names = conn.execute("""
g.V.has('name', 'saturn').in_('father').in_('father').out('father','mother').name
""", language='python')

assert set(hercules_parent_names) == {'jupiter', 'alcmene'}

# find hercules' parents and return a list of their information as dictionaries
hercules_parents = conn.execute("""
list(g.V.has('name', 'saturn').in_('father').in_('father').out('father','mother').map())
""", language='python')

assert hercules_parents == [{'age': 5000, 'name': 'jupiter'}, {'age': 45, 'name': 'alcmene'}]
