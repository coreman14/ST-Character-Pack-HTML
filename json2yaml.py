"Script/function for converting JSON to YAML"
import argparse
import json
import os
from glob import glob

import yaml
from yaml import YAMLError


def json2yaml(args: argparse.Namespace = None, input_dir=""):
    """Traverse given directory and convert all json files to yaml files
    Takes a namespace object or a string as input to allow for main program to use it
    Returns a tuple of the number of files converted and the total number of json files found
    """
    input_dir = args.input_dir if args else input_dir
    files = glob(os.path.join(input_dir, "**", "*.json"), recursive=True)
    file_len = len(files)
    converted_files = 0
    for index, file_json in enumerate(files, start=1):
        print(f"File {file_json}, {index}/{file_len}")
        file_yaml = f"{os.path.splitext(file_json)[0]}.yml"
        try:
            with open(file_json, "r", encoding="utf8") as f:
                data = json.load(f)

            with open(file_yaml, "wb") as f:
                f.write(
                    yaml.dump(
                        data,
                        default_flow_style=False,
                        encoding="utf-8",
                        allow_unicode=True,
                    )
                )
            converted_files += 1
            os.remove(file_json)
        except (OSError, json.JSONDecodeError, YAMLError):
            print(f"Failed to parse : {file_json}")

    print("Completed YML conversion.")
    print(f"Converted {converted_files}/{file_len} of json files found.")


def main():
    "Function used when running the script from the command line"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        dest="input_dir",
        required=True,
        metavar="dir",
        help="(required) The directory containing the input data",
    )
    args = parser.parse_args()

    try:
        json2yaml(args)
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating...")


if __name__ == "__main__":
    main()
