"Script/function for converting JSON to YAML"
import argparse
import json
import os
from glob import glob

import yaml
from yaml import YAMLError
from colorama import just_fix_windows_console, Fore

just_fix_windows_console()


def json2yaml(input_dir: str = ""):
    """Traverse given directory and convert all json files to yaml files
    Takes a namespace object or a string as input to allow for main program to use it
    Returns a tuple of the number of files converted and the total number of json files found
    """
    files = glob(os.path.join(input_dir, "**", "*.json"), recursive=True)
    file_len = len(files)
    converted_files = 0
    for index, file_json in enumerate(files, start=1):
        file_print = file_json.replace(input_dir, "")[1:]
        print(f"File {file_print}, {index}/{file_len}")
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
            print(f"{Fore.RED}Failed to parse : {file_print}{Fore.RESET}")

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
        json2yaml(args.input_dir)
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating...")


if __name__ == "__main__":
    main()
