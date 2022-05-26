import argparse
import os
import re
import sys

import yaml

import json2yaml
import path_functions


def get_args():
    parser = argparse.ArgumentParser(
        description="Makes an HTML file to browse a scenarios Characters"
    )
    parser.add_argument(
        "-i",
        dest="inputdir",
        help="Give input directory to make HTML File for. In directory, there should be scenario.yml and a characters folder.",
        type=path_functions.dir_path,
        default=os.path.abspath(os.path.dirname(__file__))
        if os.path.isdir(os.path.dirname(__file__))
        else os.path.abspath(os.path.dirname(os.sep.join(__file__.split(os.sep)[:-1]))),
    )
    argroup = parser.add_argument_group("Return measurements")
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
    parser.add_argument(
        "-t",
        dest="trim",
        help="Trim images while making html. This uses the same method as website/robotkyoko (if it's in the github)",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        dest="removeempty",
        help="This removes any off accessories that are blank. Off accessories do not need to be present if they don't add anything. Does not remove anything during -b/bounds check.",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        dest="json2yaml",
        help="Skip HTML and instead convert JSON files to yaml. Will walk through the whole directory and convert any found. Requires YAML for this program to work",
        action="store_true",
    )
    parser.add_argument(
        "-fn",
        dest="name",
        help="Change output file name. Default is 'index.html'",
        default="index.html",
    )

    argroup = parser.add_argument_group("CSS Options")
    argroup.add_argument(
        "-tp",
        dest="toppadding",
        help="Add top padding the character row on main page. Accepts a px value (Just the number).",
        default="",
    )
    argroup.add_argument(
        "-tc",
        dest="titlecolor",
        help="Change the color of the title on all pages. Accepts css color code or #RGB value. Default is black.",
        default="",
    )
    argroup.add_argument(
        "-cc",
        dest="charactercolor",
        help="Change the color behind the characters on the main page. Accepts css color code or #RGB value. Default is none.",
        default="",
    )
    argroup.add_argument(
        "-c1",
        dest="color1",
        help="Change the first color of the expressions sheet generator. Accepts css color code or #RGB value. Default is black",
        default="Black",
    )
    argroup.add_argument(
        "-c2",
        dest="color2",
        help="Change the second color of the expressions sheet generator. Accepts css color code or #RGB value. Default is #121212",
        default="#121212",
    )
    argroup.add_argument(
        "-tn",
        dest="titlename",
        help="Use given name as Title (On main page) instead of the one from scenario.yaml.",
    )
    argroup.add_argument(
        "-tran",
        dest="transparent",
        help="Sets both colors to #00000000 (The extra 2 zero mean no alpha) making the squares transparent. ",
        action="store_true",
    )
    argroup.add_argument(
        "-bgc",
        dest="backgroundcolor",
        help="Changed the background of the whole webpage. This applies for both the main and character pages. Accepts css color code or #RGB value. Default white.",
        default="white",
    )
    argroup.add_argument(
        "-bgim",
        dest="backgroundimage",
        help="Changed the background of the whole webpage to given image. This applies for both the main and character pages. This can be a link to a file on the internet, or a relative path into your scenario folder. This will show overtop of the bgcolor.",
    )
    argroup.add_argument(
        "-rbg",
        dest="rectbackgroundcolor",
        help="Changed the background of the rectangles that hold the face reference on the character page. Accepts css color code or #RGB value. Default white.",
        default="white",
    )
    argroup.add_argument(
        "-txt",
        dest="textcolor",
        help="Change the color of the text that says the face references on the character page. Accepts css color code or #RGB value. Default black.",
        default="black",
    )
    argroup.add_argument(
        "-mhm",
        dest="maxheightmultiplier",
        help="Change the max face height multiplier. The bigger the number the more it will show of the outfit. Default is 1.07",
        type=float,
        default=1.07,
    )

    return parser.parse_args()


def setup_args(args):
    if args.json2yaml:
        print("Attempting to convert all JSON to YAML.")
        json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        sys.exit()
    yml_data: dict = {}
    if (
        not os.path.exists(os.path.join(args.inputdir, "scenario.yml"))
        and not args.bounds
    ):
        print(f"Error: Scenario.yaml does not exist in '{args.inputdir}'.")
        response = input(
            "Would you like to convert all JSON files to YAML? (Y|y for yes, anything else to exit): "
        )
        if response.lower() in ["y"]:
            json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        else:
            sys.exit()
    if not args.bounds:
        # Try to read YAML:
        with open(
            os.path.join(args.inputdir, "scenario.yml"), "r", encoding="utf8"
        ) as f:
            try:
                yml_data: dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(
                    f"Error: Could not read YAML data from scenario.yaml.\nInfo:{exc}"
                )
                input("Press Enter to exit...")
                sys.exit()

        if "title" not in yml_data:
            print("Error: Title Not found in YAML file.")
            input("Press Enter to exit...")
            sys.exit()

        if args.titlename:
            yml_data["title"] = args.titlename

    if "characters" not in os.listdir(args.inputdir):
        print(f"Error: Could not find 'characters' folder in {args.inputdir}")
        input("Press Enter to exit...")
        sys.exit()
    if args.transparent:
        args.color1 = "#00000000"
        args.color2 = "#00000000"

    return yml_data
