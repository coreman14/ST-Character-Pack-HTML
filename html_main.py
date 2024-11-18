"""
Main runner for the HTML process
"""

from argparse import Namespace
import os
import sys

from colorama import init
from bounds_parser import BoundsParser
from character_parser import CharacterParser

import args_functions
import classes
import create_html_js

init(convert=True)


def main_loop(args: Namespace):
    """Main Method"""
    chars: list[classes.Character] = []
    paths = [
        path
        for path in os.listdir(os.path.join(args.inputdir, "characters"))
        if os.path.isdir(os.path.join(args.inputdir, "characters", path))
    ]

    total_characters = len(paths)
    character_parser = (
        BoundsParser(args.inputdir, args.strict, args.regex, args.skip_if_same, args.skip_faces, args.skip_outfits)
        if args.bounds
        else CharacterParser(
            args.inputdir,
            args.strict,
            args.outfitpriority,
            args.maxheightmultiplier,
            args.trim,
            args.removeempty,
            args.removeemptypixels,
        )
    )
    if args.hashprogress:
        # Set hashprogress as the path
        args.hashprogress = args.inputdir + f"/progress.{args.hashprogress}.0.{len(paths)}"
        with open(args.hashprogress, "w", encoding="utf8"):
            pass
    for count, character_name in enumerate(
        sorted(paths),
        start=1,
    ):
        if not args.bounds:
            print(f"Character {count}/{total_characters}: {character_name}")
            if args.hashprogress:
                new_name = args.hashprogress.replace(f".{count - 1}.", f".{count}.")
                os.rename(args.hashprogress, new_name)
                args.hashprogress = new_name
        chars.append(character_parser.parse(character_name))
    if args.bounds:
        sys.exit(0)

    if not chars:
        print("No suitable characters found. Exiting...")
        input("Press enter to exit...")
        sys.exit(1)
    chars = list(filter(lambda x: x is not None, chars))
    print("Creating Html...")

    if args.onlyjson:
        create_html_js.create_js(
            args,
            chars,
        )
    elif args.splitfiles:
        create_html_js.create_html_file(
            args,
            chars,
            split_files=True,
        )
        create_html_js.create_js(
            args,
            chars,
        )

    else:
        create_html_js.create_html_file(
            args,
            chars,
        )


def main(args: list[str] = None):
    "Main method"
    args = args_functions.get_args(args)
    args_functions.setup_args(args)
    main_loop(args)


if __name__ == "__main__":
    main()
