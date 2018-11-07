#coding=utf8
import gevent
from gevent.server import StreamServer
import os, sys
from pysproto import SprotoRpc
with open("./example.spb", "rb") as f:
    sprotobin = f.read()
rpc = SprotoRpc(sprotobin, "BasePackage")

import sys
sys.path.append("../lib")
import netpack

def get_server_list(proto):
    if proto["platform"] == 1:
        l = [
                {"sid":1, "name":"server1"},
                {"sid":2, "name":"server3"},
                ]
    else:
        l = [
                {"sid":proto["platform"], "name":"no one"},
                ]
    return {"list": l}

proto_handlers = {}
proto_handlers["get_server_list"] = get_server_list

def loop(sock, addr):
    print("start loop")
    np = netpack.NetPack()
    while True:
        data = sock.recv(1024)
        if not data:
            break
        np.add(data)
        while True:
            pack = np.get_one()
            if not pack:
                break
            info = rpc.dispatch(pack)
            print(info)
            f = proto_handlers[info["proto"]]
            retmsg = f(info["msg"])
            if retmsg:
                retpack = info.get("response")(retmsg, None)
                sock.sendall(np.pack(retpack))


def handle(sock, addr):
    print("new connection", addr)
    loop(sock, addr)
    print("connection close", addr)

server = StreamServer(("127.0.0.1", 6000), handle)
server.serve_forever()

