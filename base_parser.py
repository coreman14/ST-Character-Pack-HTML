"Contains the base class for a parser object. This class holds methods that all types of parsers may need"
from dataclasses import dataclass
from typing import ClassVar, Tuple
import os
import sys
from glob import glob
import itertools
import yaml
import json2yaml


@dataclass()
class ParserBase:
    "Contains methods that a parser may need"
    input_path: str
    strict_mode: bool
    accepted_extensions: ClassVar[list[str]] = [".webp", ".png"]
    # To make sure the warning about a blank config is not said more than once per character, we track the characters we said
    failed_yml_converts: ClassVar[list[str]] = []
    asked_for_json_convert: ClassVar[bool] = False

    def is_character_invalid(self, path_to_pose: str) -> str:
        """Check if character is invalid.
        To be a invalid character, It must be missing all faces or all outfits or both.
        If invalid, returns the reason it's invalid.
        Else returns an empty string"""
        face_found = False
        outfit_found = False
        for ext in self.accepted_extensions:
            # Check for any outfits/faces
            outfit_found = (
                outfit_found
                or bool([x for x in glob(os.path.join(path_to_pose, "outfits", f"*{ext}"))])
                or bool([x for x in glob(os.path.join(path_to_pose, "outfits", "*", f"*{ext}"))])
            )
            face_found = face_found or bool(glob(os.path.join(path_to_pose, "faces", "face", f"*{ext}")))
            if face_found and outfit_found:
                return ""
        if not face_found and not outfit_found:
            return "No faces or outfits exists"
        if not face_found:
            return "No faces exists"
        if not outfit_found:
            return "No outfits exists"
        return "This should never be returned"

    def get_yaml(self, name: str) -> dict:
        "Get the YAML file for the character"
        try:
            with open(
                os.path.join(self.input_path, "characters", name, "character.yml"),
                "r",
                encoding="utf8",
            ) as char_file:
                return yaml.safe_load(char_file) or {}
        except FileNotFoundError:
            json_ask_finish = "anything else to skip"
            if self.strict_mode:
                json_ask_finish = "anything else to exit"
            if (
                os.path.exists(os.path.join(self.input_path, "characters", name, "character.json"))
                and not self.asked_for_json_convert
            ):
                self.asked_for_json_convert = True
                print(f"ERROR: Could not find character YML for {name}, but found a json file.")
                response = input(
                    f"Would you like to convert all JSON files to YAML? (y for yes, {json_ask_finish}): ",
                )
                if response.lower() in ["y"]:
                    json2yaml.json2yaml(self.input_path)
                    return self.get_yaml(name)
                self.failed_yml_converts.append(name)
                if self.strict_mode:
                    sys.exit(1)
            elif self.strict_mode:
                print(f"ERROR: Could not find character YML for {name}")
                input("Press Enter to exit...")
                sys.exit(1)

            elif name not in self.failed_yml_converts:
                print(
                    f"Could not find config info for {name}. "
                    + "Using blank configuration. To disable this feature, use enable strict mode using --strict",
                )
                self.failed_yml_converts.append(name)
            return {}
        except yaml.YAMLError as error:
            print(f"ERROR: Character YML for {name}, could not be read.\nInfo: {error}")

            input("Press Enter to exit...")
            sys.exit(1)

    def find_access(
        self, out_path: str, off_accessories_to_add: list[str] = None, on_accessories_to_add: list[str] = None
    ) -> tuple[str, list[str]]:
        "Looks for accessories for a given outfit"
        outfit_access = glob(os.path.join(os.path.dirname(out_path), "*", ""))
        off_acc = []
        on_acc = []
        if not outfit_access:
            return out_path, off_acc, on_acc
        for direct, ext in itertools.product(outfit_access, self.accepted_extensions):
            if acc_list := glob(os.path.join(direct, f"*{ext}")):
                acc_dict = {x.split(os.sep)[-1]: x for x in acc_list}
                for key, value in acc_dict.items():
                    if key == f"off{ext}":
                        off_acc.append(value)
                    else:
                        on_acc.append(value)
        off_acc.extend(off_accessories_to_add or ())
        on_acc.extend(on_accessories_to_add or ())
        return out_path, off_acc, on_acc

    def check_character_mutation_is_valid(self, path_to_pose: str, mutation: str) -> bool:
        "Check if faces for a given mutation exists"
        face_found = False
        for ext in self.accepted_extensions:
            # Check for any outfits/faces
            face_found = face_found or bool(
                glob(os.path.join(path_to_pose, "faces", "mutations", mutation, "face", f"*{ext}"))
            )
            if face_found:
                return True
        return False

    def get_outfits(self, path_to_pose: str, character_name: str) -> None | list[Tuple[str, list[str], list[str]]]:
        "Get outfits and accessories for a given pose"
        outfits: list[Tuple[str, list[str], list[str]]] = []
        off_pose_level_accessories = []
        on_pose_level_accessories = []
        # Scan for off accessories
        for ext in self.accepted_extensions:
            off_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"off{ext}")))
            on_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"on*{ext}")))
        for ext in self.accepted_extensions:
            outfits.extend(
                (x, list(off_pose_level_accessories), list(on_pose_level_accessories))
                for x in glob(os.path.join(path_to_pose, "outfits", f"*{ext}"))
            )
            outfits.extend(
                self.find_access(x, off_pose_level_accessories, on_pose_level_accessories)
                for x in glob(os.path.join(path_to_pose, "outfits", "*", f"*{ext}"))
                if f"{os.sep}acc_" not in x
            )
            outfits_in_folders = [
                x[0] for x in outfits if (x[1] or x[2])
            ]  # Get folders that have outfits and an off or on accessory
            outfit_folders = [x.rsplit(os.sep, 1)[0] for x in outfits_in_folders]
            # If there are pose accessories, outfits not in folders will mess up this count.
            # So we get that number and subtract 1 for the copy that will be left in
            # We use max to make sure its not a negative number
            non_folder_outfits_count = max(outfit_folders.count(os.path.join(path_to_pose, "outfits")) - 1, 0)
            outfits = [
                x
                for x in outfits
                if (isinstance(x, str) and not x.endswith(f"_inverted{ext}"))
                or (isinstance(x, tuple) and not x[0].endswith(f"_inverted{ext}"))
            ]
            if len(set(outfit_folders)) + non_folder_outfits_count != len(outfit_folders):
                dup = sorted({x for x in outfit_folders if outfit_folders.count(x) > 1})
                print(
                    f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                    + "contains more than one outfit with an accessory in single folder.",
                )
                print(
                    "Doing this will result in the second outfit in the folder not being able to access any accessories from the folder."
                )
                print("Consider making a second folder for this outfit.")
                print("Folder names: ")
                char_folder_path = os.sep.join(path_to_pose.rsplit(os.sep, 2)[1:])
                for x in dup:
                    print("\t" + (char_folder_path + x.replace(path_to_pose, "")).replace(os.sep, "/"))
                input("Press Enter to exit...")
                sys.exit(1)

        if not outfits:
            print(
                f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                + "does not contain outfits. Skipping.",
            )
            return None
        outfits = self.remove_path_duplicates_no_ext(outfits)
        return outfits

    def get_faces(
        self, path_to_pose: str, character_name: str, mutation: str = None, face_folder: str = None
    ) -> None | list[str]:
        "Attempts to get the faces for a given pose, a mutation or different face folder can adjust where it will look"
        folder_to_look_in = face_folder or "face"
        faces: list[str] = []
        face_path = os.path.join(
            path_to_pose, "faces", *(("mutations", mutation) if mutation else ""), folder_to_look_in
        )
        for ext in self.accepted_extensions:
            faces.extend(glob(os.path.join(face_path, f"*{ext}")))
        if not faces and not face_folder:  # Only error if no folder is given
            mutation_string = f' for mutation "{mutation}"' if mutation else ""
            print(
                f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                + f"does not contain faces in folder {folder_to_look_in}{mutation_string}. Skipping.",
            )
            return None
        faces = self.remove_path_duplicates_no_ext(faces)
        return faces

    def remove_path_duplicates_no_ext(self, a: list[str | tuple[str]]) -> list[str | tuple[str]]:
        "Attempts to remove duplicates from a list of str/tuples of strings"
        seen = set()
        result = []
        for item in a:
            parse_item = (
                os.sep.join(item.split(os.sep)[-2:]).split(".", maxsplit=1)[0]
                if isinstance(item, str)
                else os.sep.join(item[0].split(os.sep)[-2:]).split(".", maxsplit=1)[0]
            )

            if parse_item not in seen:
                seen.add(parse_item)
                result.append(item)
        return result
