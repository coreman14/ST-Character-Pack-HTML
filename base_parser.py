"Contains the base class for a parser object. This class holds methods that all types of parsers may need"
import json2yaml
import args_functions
import os
import sys
import yaml


YML_FAILS = []
JSON_CONVERT_ASK = False


class ParserBase:
    "Contains methods that a parser may need"

    def get_yaml(self, input_dir: str, name: str) -> dict:
        "Get the YAML file for the character"
        try:
            with open(
                os.path.join(input_dir, "characters", name, "character.yml"),
                "r",
                encoding="utf8",
            ) as char_file:
                return yaml.safe_load(char_file) or {}
        except FileNotFoundError:
            global JSON_CONVERT_ASK
            json_ask_finish = "anything else to skip"
            if args_functions.STRICT_ERROR_PARSING:
                json_ask_finish = "anything else to exit"
            if (
                os.path.exists(os.path.join(input_dir, "characters", name, "character.json"))
                and args_functions.INPUT_DIR != ""
                and name not in YML_FAILS
            ):
                if not JSON_CONVERT_ASK:
                    print(f"ERROR: Could not find character YML for {name}, but found a json file.")
                    response = input(
                        f"Would you like to convert all JSON files to YAML? (y for yes, {json_ask_finish}): ",
                    )
                    JSON_CONVERT_ASK = True
                else:
                    response = ""
                if response.lower() in ["y"]:
                    json2yaml.json2yaml(args_functions.INPUT_DIR)
                    return self.get_yaml(input_dir, name)
                elif not args_functions.STRICT_ERROR_PARSING:
                    pass
                else:
                    sys.exit(1)
            elif not args_functions.STRICT_ERROR_PARSING:
                pass
            else:
                print(f"ERROR: Could not find character YML for {name}")
                input("Press Enter to exit...")
                sys.exit(1)
            if name not in YML_FAILS:
                print(
                    f"Could not find config info for {name}. "
                    + "Using blank configuration. To disable this feature, use enable strict mode using --strict",
                )
                YML_FAILS.append(name)
            return {}
        except yaml.YAMLError as error:
            print(f"ERROR: Character YML for {name}, could not be read.\nInfo: {error}")

            input("Press Enter to exit...")
            sys.exit(1)
