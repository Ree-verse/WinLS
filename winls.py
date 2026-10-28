"""
WinLS - Recode of 'ls' for Windows/Linux in Python

Author: Ree-verse (GitHub username)
License: MIT - See LICENSE file for details
"""

__all__ = []
__version__ = '0.0.1'
__author__ = 'Ree-verse'
__license__ = 'MIT'
__doc__ = "WinLS - Recode of 'ls' for Windows/Linux in Python"

import argparse
import os
from typing import Optional

from colorama import Fore, Style

if os.name == "nt":
    import ctypes

    from colorama import just_fix_windows_console

    just_fix_windows_console()


def colorize(text: str, color: str) -> str:
    """Returns the given text with the specified color."""
    return f"{color}{text}{Style.RESET_ALL}"


def is_hidden(filepath: str) -> bool:
    """Checks if a file or folder is hidden using Windows API."""
    if os.name == "nt":  # Windows: checks if hidden attribute is set
        FILE_ATTRIBUTE_HIDDEN = 0x2

        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
        return attrs != -1 and bool(attrs & FILE_ATTRIBUTE_HIDDEN)

    else:  # Unix: checks if filename starts with "."
        return os.path.basename(filepath).startswith(".")


def list_dir(path: Optional[str] = None, show_all: bool = False) -> None:
    """Lists files and directories in the given path, with optional hidden files display."""
    if path is None:
        path = os.getcwd()

    # Checks if the path exists and is accessible before proceeding
    try:
        with os.scandir(path) as entries:  # Tries opening the directory with scandir

            for entry in entries:
                full_path = entry.path

                try:  # Handles hidden files only if the user doesn't want them
                    if not show_all and is_hidden(full_path):
                        continue
                except Exception as e:  # Shouldn't happen (path already handled earlier), but catch just in case
                    print(colorize(f"Failed to get file attributes for '{full_path}': {e}", Fore.YELLOW))
                    continue

                if entry.is_dir():  # Prints directories with cyan color
                    name = entry.name
                    if " " in entry.name:
                        name = f"'{entry.name}'"
                    display_name = colorize(name, Fore.CYAN)
                    print(f"{display_name}/")
                else:
                    print(entry.name)  # Prints files

    except FileNotFoundError:
        print(colorize(f"Path not found: {path}", Fore.RED))
        return
    except PermissionError:
        print(colorize(f"Permission denied: {path}", Fore.RED))
        return


def arg_parser() -> argparse.ArgumentParser:
    """Builds and configures the command-line argument parser for WinLS."""
    parser = argparse.ArgumentParser(
        prog="winls",
        description="WinLS - Recode of 'ls' for Windows/Linux in Python"
    )

    options = [
        (["-a", "--all"], {"action": "store_true", "help": "show hidden files"}),
        # (["-l"], {"action": "store_true", "help": "show detailed file info (long listing format)"}),
        # (["-R", "--recursive"], {"action": "store_true", "help": "list subdirectories recursively"}),
        (["--path"], {"type": str, "default": None, "help": "specify directory to list (default is current)"}),
        (["-v", "--version"], {"action": "version", "version": f"%(prog)s v{__version__}", "help": "output version information and exit"})
    ]

    for flags, kwargs in options:
        parser.add_argument(*flags, **kwargs)

    return parser


args = arg_parser().parse_args()
list_dir(path=args.path, show_all=args.all)
