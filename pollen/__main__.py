"""
Basic CLI for human interaction.

Not suitable for automated or programmatic usage.
"""
import argparse
from enum import Enum, auto
from pathlib import Path

from pollen.disk_store import DiskStorage

parser = argparse.ArgumentParser()
parser.add_argument("--file", default=Path("data.db"), type=Path)
parser.add_argument("-r", "--repl", action="store_true", help="run multiple commands")


class CommandResult(Enum):
    OK = auto()
    EXIT = auto()
    ERROR = auto()


def _print_help():
    print("Available commands:")
    print("\tget <key>")
    print("\tset <key> <value>")
    print("\tdel <key>")
    print("\tlist")
    print("\texit")


def run_command(store: DiskStorage) -> CommandResult:
    try:
        inp = input("> ")
    except EOFError:
        return CommandResult.EXIT
    if not inp:
        return CommandResult.OK
    parts = inp.split()
    if parts[0] == "list":
        print(store.list())
        return CommandResult.OK
    if parts[0] == "exit":
        return CommandResult.EXIT
    if parts[0] == "get":
        if len(parts) != 2:
            _print_help()
            return CommandResult.ERROR
        print(store.get(parts[1]))
        return CommandResult.OK
    if parts[0] == "del":
        if len(parts) != 2:
            _print_help()
            return CommandResult.ERROR
        store.remove(parts[1])
        return CommandResult.OK
    if parts[0] == "set":
        if len(parts) != 3:
            _print_help()
            return CommandResult.ERROR
        store.set(parts[1], parts[2])
        return CommandResult.OK
    print("Unknown command")
    _print_help()
    return CommandResult.ERROR


def repl(store: DiskStorage):
    while True:
        status = run_command(store)
        if status == CommandResult.EXIT:
            return


if __name__ == "__main__":
    args = parser.parse_args()
    print("Welcome to PollenStore")
    _print_help()
    store = DiskStorage(args.file)
    if args.repl:
        repl(store)
    else:
        run_command(store)
