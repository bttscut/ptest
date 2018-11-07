
import unittest
from lib import client
from lib import env

class TestLogin(unittest.TestCase):

    def test_login(self):
        print("start login")
        c = client.Client()
        c.connect(env.get("login", "server"), int(env.get("login", "port")))
        sl = c.call("get_server_list", {"platform":1})
        print(sl)

