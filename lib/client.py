#coding=utf8
from lib.rpcservice import RpcService
from lib import proto as sproto

class Client(object):
    def __init__(self):
        self.service = None
        self.verbosity = 0

    def connect(self, host=None, port=None):
        self.host = host
        self.port = port
	timeout = 5
        self.service = RpcService(self.host, self.port, sproto.sproto_obj, timeout)
        assert self.service.start()

    def reconnect(self):
        self.connect(self.host, self.port)

    def close(self):
        self.service._stop()
        self.service = None

    def send(self, protoname, args=None):
        if self.verbosity > 0:
            print "send", protoname, str(args)
        return self.service.send(protoname, args)

    def is_conn(self):
        return self.service != None

    def call(self, protoname, args=None):
        if self.verbosity > 0:
            print "send", protoname, str(args)
        assert self.is_conn()
        ret = self.service.call(protoname, args)
        msg = ret["msg"]
        if self.verbosity > 0:
            print "recv", protoname, msg
        return msg

    def register_notify(self, protoname, cb):
        def _cb(msg):
            return cb(utils.to_dictobj(msg))

        self.service.register_notify(protoname, _cb if cb else None)
