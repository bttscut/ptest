#coding=utf-8
import gevent
from gevent import socket
from gevent.queue import Queue
from gevent.event import AsyncResult
from .netpack import NetPack

import time, struct


def showhex(s):
    ret = []
    for i in s:
        ret.append(ord(i))
    print ret 

class RpcService(object):
    def __init__(self, host, port, proto, timeout=5):
        self.addr = (host, port)
        self.sock = None
        self.is_conn = False
        self.proto = proto

        self.netpack = NetPack()
        self.write_queue = Queue()
        self.write_tr    = None
        self.read_queue  = Queue()
        self.read_tr     = None
        self.dispatch_tr = None
        self.timeout = timeout
        self.handlers = {}

        self._sessions = {}
	self.session_id = 1

    def start(self):
        if self.sock:
            return True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.addr)
        except socket.error, e:
            print("Err: connect to server %s failed, %s"%(self.addr, str(e)))
            return False

        self.sock        = sock
        self.read_tr     = gevent.spawn(self._read)
        self.write_tr    = gevent.spawn(self._write)
        self.dispatch_tr = gevent.spawn(self._dispatch)
        return True

    def set_timeout(self, timeout):
        self.timeout = timeout

    def stop(self):
        gevent.spawn(self._stop)

    def _stop(self):
        while True:
            if not self.is_conn:
                break
        
            if not self.write_queue.empty() or not self.read_queue.empty():
                gevent.sleep(0.1)
                continue
        
            self.write_tr.kill()
            self.read_tr.kill()
            self.dispatch_tr.kill()
            self.sock.close()
            self.is_conn = False
            break
        
    def _write(self):
        while True:
            data = self.write_queue.get()
            try:
                self.sock.sendall(data)
            except socket.error, e:
                print("Err: write socket failed:%s" % str(e))
                break
            
    def _read(self):
        left = ""
        while True:
            try:
                buf = self.sock.recv(4*1024)
                if not buf:
                    #print("client disconnected, %s:%s" % self.addr)
                    self.stop()
                    break
            except socket.error, e:
                print("Err: read socket failed:%s" % str(e))
                break
            self.netpack.add(buf)
            while True:
                data = self.netpack.get_one()
                if not data:
                    break
                self.read_queue.put(data)

    def _dispatch(self):
        while True:
            data = self.read_queue.get()
            p = self.proto.dispatch(data)
            # c2s response
            if p["type"] == "RESPONSE":
                self._dispatch_response(p)
            # s2c notify
            else:
                self._dispatch_request(p)

    def _dispatch_response(self, p):
        session   = p["session"]
        ev = self._sessions[session]
        del self._sessions[session]
        ev.set(p)

    def _dispatch_request(self, p):
        session   = p["session"]
        msg    =    p["msg"]
        protoname = p["proto"]
        try:
            cb = self.handlers[protoname]
        except KeyError:
            # print "no handler for proto:", protoname
            return

        def request_callback(cb, msg):
            resp = cb(msg)
            if session:
                pack = self.proto.response(protoname, resp, session)
                self._send(pack)

        gevent.spawn(request_callback, cb, msg)

    def _get_session(self):
        if self.session_id > 100000000:
            self.session_id = 1
        self.session_id += 1
        return self.session_id

    def _send(self, data):
        data = self.netpack.pack(data)
        self.write_queue.put(data)
        gevent.sleep(0)

    def send(self, protoname, msg):
        pack = self.proto.request(protoname, msg)
        self._send(pack)

    def call(self, protoname, msg, timeout=0):
        session = self._get_session()
        pack = self.proto.request(protoname, msg, session)
        ev = AsyncResult()
        self._sessions[session] = ev
        self._send(pack)
        ret = ev.get(timeout=self.timeout)
        return ret

    def register_notify(self, protoname, cb):
        if cb == None:
            assert(self.handlers.has_key(protoname))
            del self.handlers[protoname]
            return
        assert(not self.handlers.has_key(protoname))
        self.handlers[protoname] = cb
