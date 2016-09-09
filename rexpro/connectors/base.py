from contextlib import contextmanager
from socket import SHUT_RDWR

from rexpro import exceptions, messages
from rexpro.exceptions import RexProConnectionException
from rexpro.messages import ErrorResponse


class RexProBaseConnectionPool(object):
    """ Base RexProConnectionPool Framework

    Start from here if you want to build additional support or modify the core structure
    """

    QUEUE_CLASS = None
    CONN_CLASS = None

    def __init__(self, host, port, graph_name, graph_obj_name='g', username='', password='', timeout=None,
                 pool_size=10, with_session=False, session_less=False):
        """
        Connection constructor

        :param host: the server to connect to
        :type host: str (ip address)
        :param port: the server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :param pool_size: the initial connection pool size
        :type pool_size: int
        :param with_session: share session with connections
        :type with_session: bool
        :param session_less: sending msg without creating session
        :type session_less: bool
        """

        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.graph_obj_name = graph_obj_name
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session_less = session_less

        self.pool_size = pool_size
        self.pool = self.QUEUE_CLASS()
        self.size = 0
        self.session_key = None

        if with_session and session_less is False:
            with self.connection() as conn:
                self.session_key = conn._session_key
                conn.pool_session = self.session_key

    def get(self, *args, **kwargs):
        """ Retrieve a rexpro connection from the pool

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        pool = self.pool
        if self.size >= self.pool_size or pool.qsize():
            return pool.get()
        else:
            self.size += 1
            try:
                new_item = self._create_connection(*args, **kwargs)
            except:
                self.size -= 1
                raise
            return new_item

    def put(self, conn):
        """ Restore a connection to the pool

        :param conn: A rexpro connection to restore to the pool
        :type conn: RexProSyncConnection | RexProGeventConnection | RexProEventletConnection | RexProConnection
        """
        self.pool.put(conn)

    def close_all(self, force_commit=False):
        """ Close all pool connections for a clean shutdown """
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                if force_commit:
                    conn.execute(
                        script='g.stopTransaction(SUCCESS)',
                        isolate=False,
                        transaction=False,
                    )
                conn.close()
            except Exception:
                pass

    @contextmanager
    def connection(self, transaction=True, *args, **kwargs):
        """ Context manager that conveniently grabs a connection from the pool and provides it with the context
        cleanly closes up the connection and restores it to the pool afterwards

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        """
        conn = self.create_connection(*args, **kwargs)
        if not conn:
            raise RexProConnectionException("Cannot commit because connection was closed: %r" % (conn, ))

        try:
            if transaction:
                with conn.transaction():
                    yield conn
            else:
                yield conn
        finally:
            self.close_connection(conn, soft=True)

    def _create_connection(self, host=None, port=None, graph_name=None, graph_obj_name=None, username=None,
                           password=None, timeout=None, session_key=None, session_less=None):
        """ Create a RexProSyncConnection using the provided parameters, defaults to Pool defaults

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        return self.CONN_CLASS(host=host or self.host,
                               port=port or self.port,
                               graph_name=graph_name or self.graph_name,
                               graph_obj_name=graph_obj_name or self.graph_obj_name,
                               username=username or self.username,
                               password=password or self.password,
                               timeout=timeout or self.timeout,
                               session_key=session_key or self.session_key,
                               pool_session=self.session_key,
                               session_less=self.session_less if session_less is None else session_less)

    def create_connection(self, *args, **kwargs):
        """ Get a connection from the pool if available, otherwise return a new connection if the pool isn't full

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        :rtype: RexProConnection
        """
        conn = self.get(*args, **kwargs)
        conn.open(soft=conn._opened)  # if opened, soft open, else hard open
        return conn

    def close_connection(self, conn, soft=False):
        """ Close a connection and restore it to the pool

        :param conn: a rexpro connection that was pull from the Pool
        :type conn: RexProConnection
        :param soft: define whether to soft-close the connection or hard-close the socket
        :type soft: bool
        """
        if conn._opened:
            conn.close(soft=soft)
        self.put(conn)


class RexProBaseConnection(object):
    """ Base RexProConnection Framework

    Start from here if you want to build additional support or modify the core structure
    """

    SOCKET_CLASS = None

    def __init__(self, host, port, graph_name, graph_obj_name='g', username='', password='', timeout=None,
                 session_key=None, pool_session=None, session_less=None):
        """
        Connection constructor

        :param host: the rexpro server to connect to
        :type host: str (ip address)
        :param port: the rexpro server port to connect to
        :type port: int
        :param graph_name: the graph to connect to
        :type graph_name: str
        :param graph_obj_name: The graph object to use
        :type graph_obj_name: str
        :param username: the username to use for authentication (optional)
        :type username: str
        :param password: the password to use for authentication (optional)
        :type password: str
        """
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.graph_obj_name = graph_obj_name
        self.username = username
        self.password = password
        self.timeout = timeout
        self._session_key = session_key
        self.pool_session = pool_session
        self.session_less = session_less

        self._conn = None
        self._in_transaction = False
        self._opened = False

        self.open()

    def _select(self, rlist, wlist, xlist, timeout=None):
        raise NotImplementedError

    def _open_session(self):
        """ Creates a session with rexster and creates the graph object """
        self._conn.send_message(
            messages.SessionRequest(
                username=self.username,
                password=self.password,
                graph_name=self.graph_name
            )
        )
        response = self._conn.get_response()
        if isinstance(response, ErrorResponse):
            response.raise_exception()
        self._session_key = response.session_key

    def open_transaction(self):
        """ opens a transaction """
        if self._in_transaction:
            raise exceptions.RexProScriptException("transaction is already open")
        self.execute(
            script='g.stopTransaction(FAILURE)',
            isolate=False,
            transaction=False,
        )
        self._in_transaction = True

    def close_transaction(self, success=True):
        """
        closes an open transaction

        :param success: indicates which status to close the transaction with, True will commit the changes,
                         False will roll them back
        :type success: bool
        """
        if not self._in_transaction:
            raise exceptions.RexProScriptException("transaction is not open")
        self.execute(
            script='g.stopTransaction({})'.format('SUCCESS' if success else 'FAILURE'),
            isolate=False,
            transaction=False
        )
        self._in_transaction = False

    def close(self, soft=False):
        """ Close a connection

        :param soft: Softly close the connection - do not actually close the socket (default: False)
        :type soft: bool
        """
        # close the session, unless it is associated with a pool
        if not self.pool_session and self.session_less is False:
            self._conn.send_message(
                messages.SessionRequest(
                    session_key=self._session_key,
                    graph_name=self.graph_name,
                    kill_session=True
                )
            )
            response = self._conn.get_response()
            self._session_key = None

            if isinstance(response, ErrorResponse):
                response.raise_exception()

        if not soft:
            self._opened = False

        self._in_transaction = False

    def open(self, soft=False):
        """ open the connection to the database

        :param soft: Attempt to re-use the connection, if False (default), create a new socket
        :type soft: bool
        """
        if not soft or not self._opened:
            # connect to server
            self._conn = self.SOCKET_CLASS()
            self._conn.settimeout(self.timeout)
            try:
                self._conn.connect((self.host, self.port))
            except Exception as e:
                raise RexProConnectionException("Could not connect to database: %s" % e)

        # indicate that we're not yet in a transaction
        self._in_transaction = False

        # get a new session key if there isn't one already
        self._opened = True
        if not self._session_key and self.session_less is False:
            self._open_session()

    def test_connection(self):
        """ Test the socket, if it's errored or closed out, try to reconnect. Otherwise raise and Exception """
        readable, writeable, in_error = self._select([self._conn], [self._conn], [], 1)
        if not readable and not writeable:
            for timeout in [2, 4, 8]:
                try:
                    self._conn.shutdown(SHUT_RDWR)
                    self._conn.close()
                    self._conn.connect((self.host, self.port))
                    readable, writeable, _ = self._select([self._conn], [self._conn], [], timeout)
                    if not readable and not writeable:
                        pass
                    else:
                        # We have reconnected
                        self._conn.settimeout(self.timeout)
                        # indicates that we're in a transaction
                        self._in_transaction = False

                        # set the session key to the pool default
                        if self.pool_session:
                            self._session_key = self.pool_session
                        elif self.session_less is False:
                            self._session_key = None
                            self._open_session()
                        return None
                except Exception as e:
                    # Ignore this at let the outer handler handle iterations
                    pass

            raise RexProConnectionException("Could not reconnect to database %s:%s" % (self.host, self.port))

    @contextmanager
    def transaction(self):
        """
        Context manager that opens a transaction and closes it at the end of it's code block, use with the 'with'
        statement

        Example::

            conn = RexproSyncConnection(host, port, graph_name)
            with conn.transaction():
                results = conn.execute(script, params)

        """
        self.test_connection()
        self.open_transaction()
        try:
            yield
        except:
            self.close_transaction(False)
            raise
        else:
            self.close_transaction(True)

    def execute(self, script, params=None, isolate=True, transaction=True,
                language=messages.ScriptRequest.Language.GROOVY):
        """
        executes the given gremlin script with the provided parameters

        :param script: the gremlin script to isolate
        :type script: str
        :param params: the parameters to execute the script with
        :type params: dictionary
        :param isolate: wraps the script in a closure so any variables set aren't persisted for the next execute call
        :type isolate: bool
        :param transaction: query will be wrapped in a transaction if set to True (default)
        :type transaction: bool
        :param language: the script language that should be used (defaults to groovy)
        :type language: str

        :rtype: list
        """
        if self._in_transaction:
            transaction = False

        self._conn.send_message(
            messages.ScriptRequest(
                script=script,
                params=params or {},
                in_session=False if self.session_less else True,
                session_key=None if self.session_less else self._session_key,
                isolate=isolate,
                in_transaction=transaction,
                language=language,
                graph_name=self.graph_name if self.session_less else None,
                graph_obj_name=self.graph_obj_name if self.session_less else None
            )
        )
        response = self._conn.get_response()

        if isinstance(response, messages.ErrorResponse):
            response.raise_exception()

        return response.results
