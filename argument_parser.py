import re
import sys


def pr_help():
    print("""
Game client of Hnefatafl is runned by thy commands, which follows:
  Usage: python3 main.py [options]
  Options:
    -a    IPv4 address                   default: 0.0.0.0
    -p    Port                           default: 4567
                                           range: <1024;49151>
Created by matenestor for KIV/UPS. Skål!""")


def parse_args():

    def parse_ip(arg):
        try:
            return re.fullmatch(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?!$)|$)){4}$", arg).string
        except (TypeError, ValueError, AttributeError):
            print("Invalid ip address [{}]. Run script with '-h' for help.".format(arg))
            exit(-1)

    def parse_port(arg):
        try:
            _port = int(arg)
            assert 1024 <= _port <= 49151, "Not valid port [{}]. Run script with '-h' for help.".format(_port)
            return _port
        except (TypeError, ValueError, AttributeError):
            print("Invalid port [{}]. Run script with '-h' for help.".format(arg))
            exit(-1)

    ip = None
    port = None

    for i in range(1, len(sys.argv), 2):
        # print help
        if sys.argv[i] == "-h":
            pr_help()
            exit(0)

        # parse ip address
        elif sys.argv[i] == "-a":
            if i+1 < len(sys.argv):
                ip = parse_ip(sys.argv[i+1])
            else:
                print("Missing value for flag '-a'. Run script with '-h' for help.")
                exit(-1)

        # parse port
        elif sys.argv[i] == "-p":
            if i+1 < len(sys.argv):
                port = parse_port(sys.argv[i+1])
            else:
                print("Missing value for flag '-p'. Run script with '-h' for help.")
                exit(-1)

        # unknown flag
        else:
            print("Unknown flag [{}]. Run script with '-h' for help.".format(sys.argv[i]))
            exit(-1)

    return ip, port
