"""The fundamental package for controlling instruments in Python.

              ,▄▄▄█▄▄▄,
            ▄█▀▒▒▒╬▒▒▒▀▀█▄        ▄██▄
     ╔▄    █▀╢╣╢╣╢╢▒▀▒╣╬╢█▄,,,,,,  ▀█'   ,▄
    `▀█▀  ██╢╣▒▒▒██▄▄▄▄▄██▀▀▀▀▀▀▀       `▀█▀
  ,       █▌╢╢▒╢▒▒██
*▀█▀      ██╢╣▒▒╢╣██        █████████████████▄
           █▌╣╢▒▒▒▒█▌      ▐█╣█████████████▌█▌
    ▄█▌     ██▒╢▒▒▒▒▀█,    ▐█╣█▒███████▒█▒█▌█▌
   ███       ▀█▌╢╢▒▒▒▒██   ▐█╣██▓██▓██▌██▄█▒█▌
   █▌█▄  ,▄▄▄▄▄██▌╢▒▒▒▒▀█▄ ▐█╣██████▒█▒████▌█▌
   ██▒█▄██▒▒╣▒╢▒▒██╣╣▒▒▒▒█w █▓▓▓▓▓▓▓▓▒▓▓█▓▓▒█▌
    ▀█▒▒██▒▒▒▒▒▒▒▒█▌╢▒▒▒▒██  ▀▀▀▀▀▀███▌▀▀▀▀▀
    ╓██▀▀▀▀▀▀▀▀▀▀▀▀▒╢▒▒▒▒▓█  ▄██████████████▄
 ,▄▄█▌╢╢╢╢╢╢╢╢╢╢╢╢╢╣▒▒╣╢▒██▄██╢╣▒▒╫▄▒╢▒███▄╣█▌
██▒▒██▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄█▀▒▒▒▒╢╢╣▒▒█▌╢██▒▒█▌█▌
█▌╣╢╣▒▒▒▒▒▒▒▒▒▒▒╢╢▒▒▒▒▒▒╢╢╢╢╢╢╢╢╢╢▒▒╣╢▒▀▀▀▒╢█▌
"▀█████████████████████████████████████████▀▀
       ▄▄
       ▐▄ ▄ ▄▄▄   ▄▄▄▄  ▄▄ ▄▄▄   ▄    ▄
       ██ ██▀▀██ ██▄▄ ▀ ██▀  ▀█▌ ██  ▄█▀
       ██ ██  ██  ▀▀▀██ ██▄   ██  ████
       ▀▀ ▀▀  ▀▀ ▀▀██▀▀ ██▀██▀▀    ██
                        ██        █▀

  https://github.com/cambridgeconsultants/inspy
"""

import argparse
import io
import sys
from argparse import RawTextHelpFormatter
from importlib.metadata import version

from .utils import list_instruments


def main() -> None:
    """Execute inspy functions from the command line."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-v", "--version", action="version", version=version("cc-inspy")
    )
    parser.add_argument(
        "-l",
        "--list",
        help="list accessible instruments",
        action="store_true",
    )

    args = parser.parse_args()
    if args.list:
        list_instruments()
    else:
        parser.print_help()
        parser.exit()


if __name__ == "__main__":
    main()
