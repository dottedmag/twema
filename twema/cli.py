#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import sys
import argparse

from . import config
import twema


def main():
    parser = argparse.ArgumentParser(description="Twitter to e-mail gateway")
    parser.add_argument(
        "command", metavar="(fetch|send)", help="the command to run"
    )
    parser.add_argument(
        "--verbose", help="enable verbose output", action="store_true"
    )
    parser.add_argument("--id", help="ID of tweet to render")
    args = parser.parse_args()

    c = config.load()

    if args.command == "fetch":
        twema.fetch(c)
    elif args.command == "send":
        twema.send(c)
    elif args.command == "render":  # debugging commands
        twema.render(c, args.id)
    elif args.command == "print":
        twema.cmd_print(c, args.id)
    elif args.command == "list":
        twema.list(c)
    else:
        print("Unknown command:", args.command)
        sys.exit(1)
