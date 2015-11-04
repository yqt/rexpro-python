__author__ = 'estefanortiz'
from unittest import TestCase
from nose.plugins.attrib import attr
import os
from nose.tools import nottest
from rexpro.connectors.reventlet import RexProEventletConnectionPool, RexProEventletConnection

@attr('pooling', 'eventlet')
@nottest  # these require manual testing of bringing down titan, not to be run with unit tests
class TestEventletConnectionPoolingDrops(TestCase):

    host = os.getenv('TITAN_HOST', 'localhost')
    port = int(os.getenv('TITAN_REXPRO_PORT', 8184))
    default_graphname = 'graph'
    default_graph_obj_name = 'g'
    username = 'rexster'
    password = 'rexster'
    timeout = 30

    NUM_ITER = 10
    SLOW_NETWORK_QUERY = """def test_slow_query(sleep_length, data) {
    sleep sleep_length
    return data
    }

    test_slow_query(sleep_length, data)
    """

    def get_pool(self, host=None, port=None, graphname=None, graph_obj_name=None, username=None, password=None,
                 timeout=None):
        return RexProEventletConnectionPool(
            host=host or self.host,
            port=port or self.port,
            graph_name=graphname or self.default_graphname,
            graph_obj_name=graph_obj_name or self.default_graph_obj_name,
            username=username or self.username,
            password=password or self.password,
            timeout=timeout or self.timeout
        )

    def test_bring_pool_down(self):
        print "Eventlet Lengthy Query"
        # Well use this and add time delays to kill the connection before the while loop and
        # within the while loop of the respective connection.py file to simulate the db going down
        # and coming back up.
        pool = self.get_pool()
        conn1 = pool.create_connection()
        print "Calling Lengthy Query"
        result1 = conn1.execute(script="""g.V('element_type','measurement')""")
