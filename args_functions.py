"Function relating to parsing the command line"
import argparse
import base64
import builtins
import os
import re
import sys
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import yaml
import classes

import json2yaml
import path_functions

INPUT_DIR = ""
STRICT_ERROR_PARSING = False


def get_args(args: list[str] = None) -> argparse.Namespace:
    "Create the parser used for the arguments. If args is given, will use those args instead"
    parser = argparse.ArgumentParser(description="Makes an HTML file to browse a scenarios Characters")
    parser.add_argument(
        "-cj",
        "--convertjson",
        dest="json2yaml",
        help="Skip HTML and instead convert JSON files to YML. Will walk through the whole directory and convert any found.",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--inputdir",
        help="Run the program in a different directory.",
        type=path_functions.dir_path,
        default=os.path.abspath(os.curdir),
    )
    parser.add_argument("-s", "--silent", help="Will not ask for input", action="store_true")
    parser.add_argument(
        "-hp",
        "--hashprogress",
        help=argparse.SUPPRESS,
        # Given a hash, will create a progress file for it in the format <hash>.<current_char_number>.<total>.
        # This also replaces the sys.exit() command with an exception raise instead.
        # This is used for the webserver which uses the file as a progress bar.
    )
    parser.add_argument(
        "-st",
        "--strict",
        help="Will throw more errors when characters are not configured correctly",
        action="store_true",
    )
    argroup = parser.add_argument_group(
        "Bounds functions",
        description='Output the "real size" (Image size after maximum crop). '
        + "It will highlight any file that has a different size than the most common, or all if the most_common is 1. "
        + "This can catch invisible pixels that may be left over from editing.",
    )
    argroup.add_argument(
        "-b",
        dest="bounds",
        help="Run the bounds function.",
        action="store_true",
    )
    argroup.add_argument(
        "-re",
        dest="regex",
        help="Filter search results by comparing character names to regex.",
        type=re.compile,
    )
    argroup.add_argument(
        "-ss",
        dest="skip_if_same",
        help="In bounds, skip output if all images have the same size.",
        action="store_true",
    )
    argdiff = argroup.add_mutually_exclusive_group()
    argdiff.add_argument(
        "-so",
        dest="skip_outfits",
        help="In bounds, skip output of outfits.",
        action="store_false",
    )
    argdiff.add_argument(
        "-sf",
        dest="skip_faces",
        help="In bounds, skip output of faces.",
        action="store_false",
    )
    # Output a JSON File instead of HTML
    argroup = parser.add_argument_group(
        "Separate files",
        description="These commands deal with creating the character data in a different file than the HTML."
        + " This aim of these commands are to allow for modifications to the "
        + "HTML file that wont need to be overwritten if a character changes.",
    )
    argdiff = argroup.add_mutually_exclusive_group()
    argdiff.add_argument(
        "-j",
        "--onlyjson",
        help="Instead of creating an HTML file, output the character data in a different file.",
        action="store_true",
    )
    argdiff.add_argument(
        "-sp",
        "--splitfiles",
        help="Creates an HTML and character data file instead of a single HTML file. "
        + "The HTML file will work the same way, but the character data will not be embedded.",
        action="store_true",
    )

    argroup.add_argument(
        "-jn",
        "--jsonname",
        help="Name for the character data file if created.",
        default="characters.js",
    )
    # Normal args
    argroup = parser.add_argument_group("Image functions")
    argroup.add_argument(
        "-t",
        "--trim",
        help="Trim images while making html. This uses the same method as ST Utils/robotkyoko",
        action="store_true",
    )
    argroup.add_argument(
        "-r",
        "--removeempty",
        help="This removes any off accessories that are blank. "
        + "Off accessories do not need to be present if they have no pixels. Does not remove anything during -b/bounds check.",
        action="store_true",
    )
    argroup.add_argument(
        "-op",
        "--outfitpriority",
        dest="outfitprio",
        help="Change the priority in which outfits are chosen. Outfits priority is decided by order from the command line. "
        + f"This switch will replace the default order. Current order, from left to right, is: {path_functions.OUTFIT_PRIORITY}",
        nargs="+",
    )

    argroup = parser.add_argument_group("General Functions")
    argroup.add_argument(
        "-fn",
        "--name",
        help="Change output file name. Default is 'index.html'",
        default="index.html",
    )

    argroup.add_argument(
        "-tn",
        "--titlename",
        help="Use the given text as the title on main page instead of the one from scenario.yml.",
    )
    argroup.add_argument(
        "-fi", "--favicon", help="Change the favicon to a given file. Recommend file size is 32x32 or smaller"
    )

    argroup.add_argument(
        "-mhm",
        "--maxheightmultiplier",
        help="Change the max face height multiplier. "
        + "The bigger the number, the more it will show of the outfit on the expression sheet. Default is 1.07",
        type=float,
        default=1.07,
    )
    argroup.add_argument(
        "-oh",
        "--outfitheight",
        help="Change the height of the outfits that are displayed on the main page and top of the character page. Default is 200px",
        type=int,
        default=200,
    )
    argroup.add_argument(
        "-ah",
        "--accessoryheight",
        help="Change the height of the accessory picker that is displayed on the character page. Default is 400px",
        type=int,
        default=400,
    )
    return parser.parse_args(args)


def setup_args(args: argparse.Namespace) -> dict:
    "After args are parsed, do any maintenance or make changes based on switches"
    if args.favicon is None:
        args.favicon = "data:image/png;base64,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"
    elif not os.path.exists(args.favicon):
        print(f"""ERROR: Given Favicon does not exist. Given file is {args.favicon}""")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        try:
            fav_icon = Image.open(args.favicon)
            new_fav_icon = BytesIO()
            fav_icon.save(new_fav_icon, format="png")
            img_str = base64.b64encode(new_fav_icon.getvalue())
            args.favicon = "data:image/png;base64," + img_str.decode()
        except UnidentifiedImageError:
            print("ERROR: Could not identify given image. Please specify an image or re-convert the image")

    if args.silent:
        builtins.input2 = builtins.input
        builtins.input = lambda x: ""
    if args.hashprogress:
        sys.exit2 = sys.exit

        # No exit should happen, raise exception instead
        def throw_error(*args, **kwargs):
            raise Exception()

        sys.exit = throw_error
    if args.json2yaml:
        print("Attempting to convert all JSON to YML.")
        json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        input("Press Enter to exit...")
        sys.exit(1)
    yml_data: dict = {}
    json_convert = False
    if not os.path.exists(os.path.join(args.inputdir, "scenario.yml")) and not args.bounds:
        json_convert = True
        print(f"Error: Scenario.yml does not exist in '{args.inputdir}'.")
        response = input(
            "Would you like to convert all JSON files to YAML? (y for yes, anything else to exit): ",
        )
        if response.lower() in ["y"]:
            json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        else:
            sys.exit(1)
    if not args.bounds:
        # Try to read YAML:
        with open(os.path.join(args.inputdir, "scenario.yml"), "r", encoding="utf8") as f:
            try:
                yml_data: dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(f"Error: Could not read YAML data from scenario.yaml.\nInfo:{exc}")
                input("Press Enter to exit...")
                sys.exit(1)

        if "title" not in yml_data:
            yml_data["title"] = ""

        if args.titlename:
            yml_data["title"] = args.titlename

        args.prefix = yml_data.get("prefix", "PRE")

    if args.outfitheight:
        classes.HEIGHT_OF_MAIN_PAGE = args.outfitheight

    if args.accessoryheight:
        classes.HEIGHT_OF_ACCESSORY_PAGE = args.accessoryheight

    if "characters" not in os.listdir(args.inputdir):
        print(f"Error: Could not find 'characters' folder in {args.inputdir}")
        input("Press Enter to exit...")
        sys.exit(1)
    global INPUT_DIR, STRICT_ERROR_PARSING
    INPUT_DIR = args.inputdir if not json_convert else ""
    STRICT_ERROR_PARSING = args.strict
    return yml_data
