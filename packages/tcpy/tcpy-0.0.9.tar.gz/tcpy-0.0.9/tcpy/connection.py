import logging
import msgpack as umsgpack
import socket
import time

from util import msgpk_decode_datetime, msgpk_encode_datetime
try:
    from tcpyconfig import DEBUG
except:
    from default import DEBUG

MAX_ATTEMPTS = 20
logging.basicConfig()
logger = logging.getLogger("tcpy.connection")
if DEBUG:
    logger.setLevel(logging.DEBUG)


def prefix_to_len(prefix):
    "Converts a 4 byte big-endian value, to native"
    return ord(prefix[0]) << 24 | \
        ord(prefix[1]) << 16 | \
        ord(prefix[2]) << 8  | \
        ord(prefix[3])


def len_to_prefix(length):
    "Converts length to a 4 byte big-endian value"
    parts = "".join([
        chr(length >> 24 & 0xff),
        chr(length >> 16 & 0xff),
        chr(length >> 8 & 0xff),
        chr(length & 0xff)])
    return parts


def recv_bytes(sock, bytes):
    "Receive at least bytes"
    buf = ""
    while len(buf) < bytes:
        diff = bytes - len(buf)
        more = sock.recv(diff)
        if not more:
            raise Exception("Socket closed!")
        buf += more
    return buf


class ClientConnection(object):

    """ Client Connection wrapper class for nice send/read interface """

    def __init__(self, host, port, sock=None):
        self.host = host
        self.port = port
        self.sock = sock
        self.attempts = 0
        self.connect()

    def connect(self):
        if not self.sock:
            logger.debug("Creating socket for client.")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug("Socket created successfully.")
        try:
            logger.debug("Trying to connect socket to %s:%s." % (self.host, self.port))
            self.sock.connect((self.host, self.port))
            logger.debug("Successfully connected.")
        except socket.error:
            logger.debug("Socket is already connected.")
            return

    def send(self, data):
        msg = umsgpack.packb(data, default=msgpk_encode_datetime)
        while self.attempts <= MAX_ATTEMPTS:
            try:
                logger.debug("Client sending bytes to server.")
                self.sock.sendall(len_to_prefix(len(msg)))
                self.sock.sendall(msg)
                logger.debug("Client sent %s bytes to server." % len(msg))
                self.attempts = 0
                break
            except socket.error:
                logger.debug("Failed to send data to server -- Retrying.")
                self.attempts += 1
                self.sock.close()
                self.sock = None
                if self.attempts >= MAX_ATTEMPTS:
                    raise Exception('Max number of retries reached!')
                self.connect()
            time.sleep(.01)

    def read(self):
        logger.debug("Client waiting for bytes from server.")
        msgprefix = self.sock.recv(4)
        msglen = prefix_to_len(msgprefix)
        response = recv_bytes(self.sock, msglen)
        logger.debug("Client received %s bytes from server." % msglen)
        return umsgpack.unpackb(response, object_hook=msgpk_decode_datetime)

    def finish(self):
        logger.debug("Closing socket.")
        self.sock.close()
        self.sock = None


class ServerConnection(object):

    """ Server Connection wrapper class for nice send/read interface.
    Different from the ClientConnection in that it will not retry to send.
    """

    def __init__(self, cl_host, cl_port, cl_sock):
        self.host = cl_host
        self.port = cl_port
        self.sock = cl_sock
        self.sock.setblocking(1)

    def send(self, data):
        msg = umsgpack.packb(data, default=msgpk_encode_datetime)
        try:
            logger.debug("Server sending bytes to client.")
            self.sock.sendall(len_to_prefix(len(msg)))
            self.sock.sendall(msg)
            logger.debug("Server sent %s bytes to client." % len(msg))
        except socket.error:
            self.finish()
            logger.exception('ServerConnection failed to send %s.' % data)

    def read(self):
        logger.debug("Server waiting for bytes from client.")
        msgprefix = self.sock.recv(4)
        msglen = prefix_to_len(msgprefix)
        response = recv_bytes(self.sock, msglen)
        logger.debug("Server received %s bytes from client." % msglen)
        return umsgpack.unpackb(response, object_hook=msgpk_decode_datetime)

    def finish(self):
        self.sock.close()
