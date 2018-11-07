import struct

HEADER_LEN = 4
HEADER_FLAG = "!L"

class NetPack(object):
    def __init__(self):
        self.buf = ""
        self.c2s_encrypt = None
        self.s2c_encrypt = None

    def init_rc4(self, s):
        rc4_key = gen_rc4key(s)
        self.c2s_encrypt = RC4(rc4_key).crypt
        self.s2c_encrypt = RC4(rc4_key).crypt

    def add(self, buf):
        if self.s2c_encrypt:
            buf = self.s2c_encrypt(buf)
        self.buf = self.buf + buf

    def get_one(self):
        if len(self.buf) < HEADER_LEN:
            return None

        plen, = struct.unpack(HEADER_FLAG, self.buf[:HEADER_LEN])
        if len(self.buf) < plen + HEADER_LEN:
            return None

        data = self.buf[HEADER_LEN:plen+HEADER_LEN]
        self.buf = self.buf[plen+HEADER_LEN:]
        return data

    def pack(self, data):
        data = struct.pack(HEADER_FLAG, len(data)) + data
        if self.c2s_encrypt:
            data = self.c2s_encrypt(data)
        return data
