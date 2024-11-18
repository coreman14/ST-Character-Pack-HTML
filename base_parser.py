"Contains the base class for a parser object. This class holds methods that all types of parsers may need"
from dataclasses import dataclass, field
from typing import ClassVar, Tuple
import os
import sys
from glob import glob
import itertools
import yaml
import json2yaml
from PIL import Image, UnidentifiedImageError
from PIL.Image import Image as ImageType
import numpy as np


@dataclass()
class ParserBase:
    "Contains methods that a parser may need"
    input_path: str
    strict_mode: bool
    asked_for_json_convert: bool = field(init=False, repr=False)
    current_character_name: ClassVar[str] = ""
    accepted_extensions: ClassVar[list[str]] = [".webp", ".png"]
    # To make sure the warning about a blank config is not said more than once per character, we track the characters we said
    failed_yml_converts: ClassVar[list[str]] = []

    def is_character_invalid(self, path_to_pose: str) -> str:
        """Check if character is invalid.
        An invalid character has no faces or outfits or both.
        If the given character is invalid, returns a string containing the reason it's invalid.
        If the character is valid, it returns a empty string"""
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
        # If it gets here, assume we couldn't find outfits
        return "No outfits exists"

    def get_yaml(self) -> dict:
        "Get the YAML file for the character"
        try:
            with open(
                os.path.join(self.input_path, "characters", self.current_character_name, "character.yml"),
                "r",
                encoding="utf8",
            ) as char_file:
                return yaml.safe_load(char_file) or {}
        except yaml.YAMLError as error:
            if self.current_character_name not in self.failed_yml_converts:
                print(
                    f"{"ERROR" if self.strict_mode else "WARNING"}: Character "
                    + f"YML for {self.current_character_name}, could not be read.\nInfo: {error}"
                )
                if self.strict_mode:
                    input("Press Enter to exit...")
                    sys.exit(1)
                print("Continuing blank configuration. To disable this feature, use enable strict mode using --strict")
                self.failed_yml_converts.append(self.current_character_name)
            return {}
        except FileNotFoundError:
            json_ask_finish = "anything else to skip"
            if self.strict_mode:
                json_ask_finish = "anything else to exit"
            if (
                os.path.exists(
                    os.path.join(self.input_path, "characters", self.current_character_name, "character.json")
                )
                and not self.asked_for_json_convert
            ):
                self.asked_for_json_convert = True
                print(f"ERROR: Could not find character YML for {self.current_character_name}, but found a json file.")
                response = input(
                    f"Would you like to convert all JSON files to YAML? (y for yes, {json_ask_finish}): ",
                )
                if response.lower() in ["y"]:
                    json2yaml.json2yaml(self.input_path)
                    return self.get_yaml()
                self.failed_yml_converts.append(self.current_character_name)
                if self.strict_mode:
                    sys.exit(1)
            elif self.strict_mode:
                print(f"ERROR: Could not find character YML for {self.current_character_name}")
                input("Press Enter to exit...")
                sys.exit(1)

            elif self.current_character_name not in self.failed_yml_converts:
                print(
                    f"Could not find config info for {self.current_character_name}. "
                    + "Using blank configuration. To disable this feature, use enable strict mode using --strict",
                )
                self.failed_yml_converts.append(self.current_character_name)
            return {}

    def find_access(
        self, out_path: str, off_accessories_to_add: list[str] = None, on_accessories_to_add: list[str] = None
    ) -> tuple[str, list[str]]:
        "Looks for accessories for a given outfit"
        off_acc = []
        on_acc = []
        outfit_access = glob(os.path.join(os.path.dirname(out_path), "*", ""))
        if outfit_access:
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

    # Inverted still works the same. If it's in the same folder it loses accessories. So one outfit per accessory folder
    def get_outfits(self, path_to_pose: str) -> None | list[Tuple[str, list[str], list[str]]]:
        "Get outfits and accessories for a given pose"
        outfits: list[Tuple[str, list[str], list[str]]] = []
        off_pose_level_accessories: list[str] = []
        on_pose_level_accessories: list[str] = []
        # Scan for off accessories
        for ext in self.accepted_extensions:
            off_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"off{ext}")))
            on_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"on*{ext}")))
        for ext in self.accepted_extensions:
            glob_outfits = [
                self.find_access(x, off_pose_level_accessories, on_pose_level_accessories)
                for x in glob(os.path.join(path_to_pose, "outfits", "*", f"*{ext}"))
                if f"{os.sep}acc_" not in x
            ]
            # Get the folder names of the outfits we pulled in a set to remove dups
            outfit_folders = [x[0].rsplit(os.sep, 1)[0] for x in glob_outfits]
            # Check if there is more than one outfit in a folder
            if len(set(outfit_folders)) != len(outfit_folders):
                print(
                    f'{"ERROR" if self.strict_mode else "WARNING"}: Character "{self.current_character_name}" '
                    + f'with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                    + "has a folder containing more than one outfit.",
                )
                print(
                    "This will cause any outfits that do not match the name to lose access to the folders accessories."
                )
                print("Move the offending outfits to a different folder.")
                print("Folder names: ")
                dup = sorted({x for x in outfit_folders if outfit_folders.count(x) > 1})
                char_folder_path = os.sep.join(path_to_pose.rsplit(os.sep, 2)[1:])
                for x in dup:
                    print("\t" + (char_folder_path + x.replace(path_to_pose, "")).replace(os.sep, "/"))
                if self.strict_mode:
                    input("Press Enter to exit...")
                    sys.exit(1)
            # Check if a folder outfit is not named the same
            if any(
                x[0][0].rsplit(os.sep, 1)[-1] != x[1].rsplit(os.sep, 1)[-1] + f"{ext}"
                for x in zip(glob_outfits, outfit_folders)
            ):
                print(
                    f'{"ERROR" if self.strict_mode else "WARNING"}: Character "{self.current_character_name}" '
                    + f'with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                    + "has a outfit folder where the image file does not match the name of the folder.",
                )
                print("This will cause the image to show up twice. Once as the image name and once as the folder name")
                print("The one with the image name will not be able to access the accessories in the folder.")
                print("This also applies for inverted outfits.")
                print("Rename the outfits to match the folder name.")
                print("Folder names: ")

                mismatches = sorted(
                    x[1]
                    for x in zip(glob_outfits, outfit_folders)
                    if x[0][0].rsplit(os.sep, 1)[-1] != x[1].rsplit(os.sep, 1)[-1] + f"{ext}"
                )
                char_folder_path = os.sep.join(path_to_pose.rsplit(os.sep, 2)[1:])
                for x in mismatches:
                    print("\t" + (char_folder_path + x.replace(path_to_pose, "")).replace(os.sep, "/"))
                if self.strict_mode:
                    input("Press Enter to exit...")
                    sys.exit(1)
            # Add them after
            outfits.extend(glob_outfits)
            # Deal with outfit folders first to avoid false positives from global accessories
            outfits.extend(
                (x, list(off_pose_level_accessories), list(on_pose_level_accessories))
                for x in glob(os.path.join(path_to_pose, "outfits", f"*{ext}"))
            )
            outfits = [x for x in outfits if not x[0].endswith(f"_inverted{ext}")]

        if not outfits:
            print(
                f'Error: Character "{self.current_character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                + "does not contain outfits. Skipping.",
            )
            return None
        outfits = self.remove_path_duplicates_no_ext(outfits)
        return outfits

    def get_faces(self, path_to_pose: str, mutation: str = None, face_folder: str = None) -> None | list[str]:
        "Attempts to get the faces for a given pose, a mutation or different face folder can adjust where it will look"
        folder_to_look_in = face_folder or "face"
        faces: list[str] = []
        face_path = os.path.join(
            path_to_pose, "faces", ((f"mutations{os.sep}{mutation}") if mutation else ""), folder_to_look_in
        )
        for ext in self.accepted_extensions:
            faces.extend(glob(os.path.join(face_path, f"*{ext}")))
        if not faces and not face_folder:  # Only error if no folder is given
            mutation_string = f' for mutation "{mutation}"' if mutation else ""
            print(
                f'Error: Character "{self.current_character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
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

    def attempt_to_open_image(
        self, name: str | list[str], remove_empty_pixels: bool = True
    ) -> tuple[str | list[str], ImageType] | tuple[str, ImageType]:
        """Attempts to open image. Treats image as a string first, then on failure treats it as a list."""
        return_name = name
        try:
            try:
                image = Image.open(name)
            except AttributeError:
                image = Image.open(name[0])
                return_name = name[0]
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            if "faces" in name and remove_empty_pixels:
                img_np = np.array(image)
                img_np[img_np < (0, 0, 0, 255)] = 0
                image = Image.fromarray(img_np)
            return return_name, image

        except UnidentifiedImageError as pil_error:
            print()
            print(f"Error: {pil_error}. Please try to re convert the file to png or webp.")
            input("Press Enter to exit...")
            sys.exit(1)
