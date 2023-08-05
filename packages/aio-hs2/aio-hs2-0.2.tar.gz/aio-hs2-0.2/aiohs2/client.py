import asyncio

from thrift.protocol.TBinaryProtocol import TBinaryProtocolAcceleratedFactory

from .sasl_transport import TSaslAsyncioTransport
from .lowlevel.TCLIService.ttypes import TOpenSessionReq
from .lowlevel.TCLIService.TCLIService import Client as ThriftClient
from .cursor import Cursor


class Client(object):

    def __init__(self, host, port, **auth):
        self.host = host
        self.port = port
        if not auth:
            auth = {
                'mechanism': 'PLAIN',
                'username': 'anonymous',
                'password': 'anonymous',
                }
        self.auth = auth
        self._svc = None

    @asyncio.coroutine
    def connect(self):
        trans = yield from TSaslAsyncioTransport.connect(
            self.host, self.port, **self.auth)
        svc = ThriftClient(trans, TBinaryProtocolAcceleratedFactory())
        info = yield from svc.OpenSession(TOpenSessionReq(client_protocol=0))
        self._svc = svc
        self._hsession = info.sessionHandle

    @asyncio.coroutine
    def cursor(self):
        if self._svc:
            tsk = self._svc._task
            if tsk.cancelled() or tsk.done():
                self._svc = None
        if not self._svc:
            yield from self.connect()
        return Cursor(self._svc, self._hsession)
