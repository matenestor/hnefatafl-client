import argument_parser
import client_handler


def main():
    ip, port = argument_parser.parse_args()
    client_handler.init(ip, port)


if __name__ == '__main__':
    main()
