import argparse
import asyncio
from .killer import Server, Client, kill_process


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    client = subparsers.add_parser("client")
    client.add_argument("uri", type=str, help="uri in format ws://host:port")
    client.add_argument("process", type=str, help="name of process to kill")
    client.add_argument(
        "-t",
        "--trigger",
        type=str,
        default="left windows + x",
        help="Keyboard shortcut specified in the format of the python `keyboard` module. Defaults to ctrl+r.",
    )

    server = subparsers.add_parser("server")
    server.add_argument("port", type=int, help="Local port to bind to.")

    return parser.parse_args()


def main():
    args = parse_args()

    loop = asyncio.get_event_loop()

    if "port" in args.__dict__:  # server
        server = Server(args.port)
        loop.run_until_complete(server.serve())
    else:  # client
        client = Client(
            args.uri,
            on_trigger=lambda: kill_process(args.process),
            trigger=args.trigger,
            loop=loop,
        )
        loop.run_until_complete(client.connect())


if __name__ == "__main__":
    main()
