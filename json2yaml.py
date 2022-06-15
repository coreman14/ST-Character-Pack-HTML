import argparse
import json
import os
from glob import glob

import yaml
from yaml import YAMLError


def json2yaml(args):
    files = glob(os.path.join(args.input_dir, "**", "*.json"), recursive=True)
    file_len = len(files)
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
        except (OSError, json.JSONDecodeError, YAMLError):
            print(f"Failed to parse : {file_json}")

        os.remove(file_json)


def main():
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
