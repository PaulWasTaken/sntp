import struct
import time
import datetime

_SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
_NTP_EPOCH = datetime.date(1900, 1, 1)
NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600


class SNTPPacket:
    def __init__(self):
        self.leap = 0
        self.version = 0
        self.mode = 0
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.delay = 0
        self.dispersion = 0
        self.ref_id = 0
        self.ref_timestamp = 0
        self.orig_timestamp = 0
        self.recv_timestamp = 0
        self.tx_timestamp = 0

    def get_basis_info(self, data):
        unpacked = struct.unpack("!b", data)
        first = "{0:8b}".format(unpacked[0]).replace(" ", "0")
        self.leap = first[:2]
        self.version = first[2:5]
        self.mode = first[5:]
        return self

    def form_packet(self, data):
        unpacked = struct.unpack("!bbbb 11I", data)
        first = "{0:8b}".format(unpacked[0]).replace(" ", "0")
        self.leap = first[:2]
        self.version = first[2:5]
        self.mode = first[5:]
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.delay = unpacked[4]
        self.dispersion = unpacked[5]
        self.ref_id = unpacked[6]
        self.ref_timestamp = unpacked[7]
        self.orig_timestamp = unpacked[9] + NTP_DELTA
        self.recv_timestamp = unpacked[11]
        self.tx_timestamp = unpacked[13]
        return self
