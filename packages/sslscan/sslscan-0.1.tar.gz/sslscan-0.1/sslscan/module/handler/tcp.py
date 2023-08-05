from socket import socket

from OpenSSL import SSL, _util

from sslscan import modules
from sslscan.module.handler import BaseHandler


class TCP(BaseHandler):
    name="tcp"

    def __init__(self, **kwargs):
        self.port = 443
        BaseHandler.__init__(self, **kwargs)

    def connect(self):
        conn = socket()
        conn.connect((self.host, self.port))

        return conn


modules.register(TCP)
