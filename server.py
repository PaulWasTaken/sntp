import logging
import socket
import struct
import time

import datetime
from concurrent.futures import ThreadPoolExecutor

import math

from SNTPPacket import SNTPPacket

_SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
_NTP_EPOCH = datetime.date(1900, 1, 1)
NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600


class SNTPServer:
    def __init__(self, server_address, port, delay, debug):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.sock.bind(("", port))
        self.delay = delay
        try:
            self.server_address = socket.getaddrinfo(
                server_address, port)[0][4]
        except socket.gaierror:
            raise ValueError(server_address, port)
        self.logging(debug)

    @staticmethod
    def logging(debug):
        if debug:
            logging.basicConfig(
                format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-2s '
                       u'[%(asctime)s]  %(message)s',
                level=logging.DEBUG, filename=u'log.log')
            logging.debug("---------The application was started---------\n")

    def invoke(self):
        print("Was started at: {} GMT+0".format(time.asctime(time.gmtime())))
        with ThreadPoolExecutor(max_workers=10) as executor:
            try:
                while 1:
                    try:
                        data, addr = self.sock.recvfrom(4096)
                        print("New client has connected. IP: {}, Port: {}"
                              .format(addr[0], addr[1]))
                    except struct.error:
                        print("Wrong SNTP format.")
                        continue
                    except socket.timeout:
                        continue
                    executor.submit(self.process_new_client, addr,
                                    data).result()
            except KeyboardInterrupt:
                print("Finishing...")
                logging.debug("---------The program was closed.---------")
                self.sock.close()
                executor.shutdown()

    @staticmethod
    def is_valid(data):
        inc_pack = SNTPPacket().get_basis_info(data[:1])
        logging.debug(
            "Received from a client: {}\n".format(data))
        if inc_pack.mode != "011":
            print(
                "Somebody who is not a client is "
                "trying to connect. Denied.")
            return False
        return True

    def process_new_client(self, addr, data):
        if not self.is_valid(data):
            return
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.settimeout(2)
                sock.sendto(self.form_query(), self.server_address)
                data, _ = sock.recvfrom(4096)
                logging.debug("Received from a SNTP server: {}\n".format(data))
                response = SNTPPacket().form_packet(data)
                sock.sendto(self.form_response(response), addr)
                logging.debug("Send to a client: {}\n".format(data))
            except socket.timeout:
                print("The delay is too high. Drop the task.")
            except struct.error:
                print("Probably incorrect server response. Try another one.")

    @staticmethod
    def form_query():
        leap = "00"
        version = "100"
        mode = "011"
        first = int(leap + version + mode, 2)
        return struct.pack("!bbbb 11I", first, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                           int(time.time()), 0)

    def form_response(self, response):
        first = int(response.leap + response.version + response.mode, 2)
        trunc_part, int_part = math.modf(time.time())
        trunc_part = int(str(trunc_part)[2:11])
        return struct.pack("!bbbb 11I", first,
                           response.stratum, response.poll,
                           response.precision, int(response.delay),
                           int(response.dispersion), response.ref_id,
                           response.ref_timestamp,
                           0,
                           response.tx_timestamp,
                           0,
                           self.insert_delay(time.time() + NTP_DELTA),
                           trunc_part,
                           self.insert_delay(time.time() + NTP_DELTA),
                           trunc_part
                           )

    def insert_delay(self, value):
        return int(value + self.delay)
