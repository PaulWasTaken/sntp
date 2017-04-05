import argparse

from server import SNTPServer


def create_parser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("-d", "--delay", help="Set delay time.", dest="delay", default=0, type=int)
    _parser.add_argument("-s", "--server", help="Set SNTP server.", dest="server",
                         default='pool.ntp.org', type=str)
    _parser.add_argument("-p", "--port", help="Set SNTP port.", dest="port", default=123, type=int)
    _parser.add_argument("-D", "--debug", help="Enable debug mode.", dest="debug", action="store_true")
    return _parser

if __name__ == "__main__":
    parser = create_parser()
    settings = parser.parse_args()
    try:
        SNTPServer(settings.server, settings.port, settings.delay, settings.debug).invoke()
    except ValueError as e:
        print("Wrong address or port: " + str(e))
