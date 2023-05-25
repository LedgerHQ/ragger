#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from re import compile


REGEX = r"((?P<destination>test)-)?v(?P<version>(\d\.){2}\d)"


def parse_args() -> Namespace:
    description = """
Extracts version and other info from a string

Implemented to extract destination / version number from a tag.

Tags can be like:

- 1.2.3 -> simple tag, means the package is to be deployed on `pypi.org` with version 1.2.3
- test-2.34.5 -> composite tag, means the package is to be deployed on `test.pypi.org` with version 2.34.5
"""
    parser = ArgumentParser(description=description)
    parser.add_argument("string", type=str)
    parser.add_argument("--version", "-v", action='store_true', default=False, help="Extract the version from the string")
    parser.add_argument("--destination", "-d", action='store_true', default=False, help="Deduce the destination from the string, either `pypi.org` or `test.pypi.org`")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        results = compile(REGEX).match(args.string).groupdict()
    except AttributeError as e:
        raise ValueError(f"String '{args.string}' did not match regex '{REGEX}'") from e

    if results["destination"] is None:
        results["destination"] = "pypi.org"
    else:
        results["destination"] = "test.pypi.org"

    if args.version:
        print(results["version"])
    elif args.destination:
        print(results["destination"])
    else:
        print(results)

if __name__ == '__main__':
    main()
