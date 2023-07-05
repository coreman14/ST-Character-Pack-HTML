import argparse
import ast
import builtins
import os
import re
import sys

import configargparse
import yaml
import classes

import json2yaml
import path_functions


def get_args():
    parser = configargparse.ArgumentParser(description="Makes an HTML file to browse a scenarios Characters")
    parser.add_argument("-c", "--my-config", is_config_file=True, help="config file path")
    parser.add_argument(
        "-i",
        dest="inputdir",
        help="Give input directory to make HTML File for. In directory, there should be scenario.yml and a characters folder.",
        type=path_functions.dir_path,
        default=os.path.abspath(os.curdir),
    )
    parser.add_argument("-s", "--silent", help="Will not ask for input", action="store_true")
    argroup = parser.add_argument_group("Bounds functions")
    argroup.add_argument(
        "-b",
        dest="bounds",
        help='Don\'t make html File. Outbox "real size" (Image size after maximum crop). It will highlight any file that has a different size than the most common, or all if the most_common is 1.',
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
    argroup = parser.add_argument_group("Separate files")
    argroup.add_argument(
        "--explained",
        help='This command is just explaination text. It does not change anything. These commands produce a JS file that stores the data. It has to be a JS file or it wont load correctly. The JS file is a json file but with "var data =" added',
    )
    argdiff = argroup.add_mutually_exclusive_group()
    argdiff.add_argument(
        "-j",
        "--json",
        dest="onlyjson",
        help="Instead of creating an HTML file, output the JS that the HTML uses to display. This is useful if you have made modifications to the HTML code and dont want to remake the HTML file.",
        action="store_true",
    )
    argdiff.add_argument(
        "-sp",
        "--splitfiles",
        help="Creates an HTML and JS file instead of a single HTML file. The HTML file will work the same way, but the JSON will not be embedded.",
        action="store_true",
    )

    argroup.add_argument(
        "-jn",
        "--jsname",
        help="Name for the JSON file created if ",
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
        help="This removes any off accessories that are blank. Off accessories do not need to be present if they have no pixels. Does not remove anything during -b/bounds check.",
        action="store_true",
    )
    argroup.add_argument(
        "-cj",
        "--convertjson",
        dest="json2yaml",
        help="Skip HTML and instead convert JSON files to yaml. Will walk through the whole directory and convert any found. Requires YAML for this program to work",
        action="store_true",
    )
    argroup.add_argument(
        "-op",
        "--outfitpriority",
        dest="outfitprio",
        help=f"Change the priority in which outfits are chosen. Accepts a python list made of strings and tuples. A tuple means both are wayed the same, but first one found will chosen for it. Current order, from left to right, is: {path_functions.OUTFIT_PRIO}",
        type=ast.literal_eval,
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
        help="Use given name as Title (On main page) instead of the one from scenario.yaml.",
    )
    argroup.add_argument(
        "-mhm",
        "--maxheightmultiplier",
        help="Change the max face height multiplier. The bigger the number the more it will show of the outfit. Default is 1.07",
        type=float,
        default=1.07,
    )
    argroup.add_argument(
        "-oh",
        "--outfitheight",
        help="Change the height of the outfits that are displayed on the main page and top of the character page. Default is 200",
        type=int,
        default=200,
    )
    argroup.add_argument(
        "-ah",
        "--accessoryheight",
        help="Change the height of the accessory picker that is . Default is 400",
        type=int,
        default=400,
    )
    return parser.parse_args()


def setup_args(args):
    if args.outfitprio and not isinstance(args.outfitprio, list):
        print('''ERROR: outfitprio arg must be in a list. Example: "['a', ('b', 'c'), 'd']"''')
        sys.exit()

    if args.silent:
        builtins.input2 = builtins.input
        builtins.input = lambda x: ""
    if args.json2yaml:
        print("Attempting to convert all JSON to YAML.")
        json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        sys.exit()
    yml_data: dict = {}
    if not os.path.exists(os.path.join(args.inputdir, "scenario.yml")) and not args.bounds:
        print(f"Error: Scenario.yaml does not exist in '{args.inputdir}'.")
        response = input(
            "Would you like to convert all JSON files to YAML? (Y|y for yes, anything else to exit): ",
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
            print("Error: Title Not found in YAML file.")
            input("Press Enter to exit...")
            sys.exit(1)

        if args.titlename:
            yml_data["title"] = args.titlename

    if args.outfitheight:
        classes.HEIGHT_OF_MAIN_PAGE = args.outfitheight

    if args.accessoryheight:
        classes.HEIGHT_OF_ACCESSORY_PAGE = args.accessoryheight

    if "characters" not in os.listdir(args.inputdir):
        print(f"Error: Could not find 'characters' folder in {args.inputdir}")
        input("Press Enter to exit...")
        sys.exit(1)

    return yml_data
