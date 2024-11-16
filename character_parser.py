from dataclasses import dataclass, field
from functools import partial
from typing import Callable, ClassVar, Tuple
from classes import Character, Pose, Outfit, ImagePath, Accessory
import classes
import re
import os
from collections import defaultdict
from base_parser import ParserBase
import sort_functions
import sys
from glob import glob


@dataclass
class CharacterParser(ParserBase):
    "A reusable class for creating a character. This will create a character object by giving a character path to parse"
    outfit_priority: list[str]
    max_height_constant: float
    do_trim: bool
    remove_empty: bool
    remove_empty_pixels: bool
    clean_path_function: Callable = field(init=False, repr=False)
    current_pose_letter: str = field(init=False, repr=False)

    FILES_THAT_COULD_BE_REMOVED: ClassVar[list[str]] = []

    def __post_init__(self):
        self.clean_path_function = partial(self.remove_path, path_to_remove=self.input_path)

    def parse(self, character_name: str) -> Character:
        "Create a character from a given character path"
        self.current_character_name = character_name
        pose_list = []
        for pose_path in [
            os.path.join(self.input_path, "characters", character_name, path)
            for path in os.listdir(os.path.join(self.input_path, "characters", character_name))
            if os.path.isdir(os.path.join(self.input_path, "characters", character_name, path))
        ]:
            self.current_pose_letter = pose_path.split(os.sep)[-1]
            invalid = self.is_character_invalid(pose_path)
            if invalid:
                print(
                    f"Character {character_name} is not valid for pose {self.current_pose_letter}. Reason: {invalid}."
                )
                continue
            if char_pose := self.create_character(
                pose_path,
            ):
                pose_list.append(Pose(self.input_path, self.current_pose_letter, *char_pose))

        if pose_list:
            return Character(character_name, pose_list, self.max_height_constant)
        return None

    def create_character(
        self,
        pose_path: str,
    ) -> None | tuple[list[Outfit], list[ImagePath], list[ImagePath], ImagePath, list[ImagePath]]:
        """
        Gets all the require inputs for a given pose
        """
        mutation = None

        outfits = self.get_outfits(pose_path)

        char_yml: dict = self.get_yaml()
        excluded_accessories = char_yml.get("poses", {}).get(self.current_pose_letter, {}).get("excludes", {})
        face_direction = char_yml.get("poses", {}).get(self.current_pose_letter, {}).get("facing", "left")
        inverse_accessories = defaultdict(list)
        for k, v in excluded_accessories.items():
            for x in v:
                inverse_accessories[x].append(k)

        outfit_tuple = self.get_default_outfit(
            outfits,
        )
        default_outfit_name = outfit_tuple[0].file_name
        mutation = None
        mutations: dict[str, list[str]]
        if mutations := char_yml.get("mutations", {}):
            for key, value in mutations.items():
                if any(x in default_outfit_name for x in value):
                    if self.check_character_mutation_is_valid(pose_path, key):
                        mutation = key
                    else:
                        print(
                            f'WARNING: Character "{self.current_character_name}" for pose "{self.current_pose_letter}" default outfit of "{default_outfit_name}"'
                            + f' has mutation "{key}", but no faces are provided for that mutation.',
                        )
                    break

        faces = self.get_faces(pose_path, mutation)
        blushes = self.get_faces(pose_path, mutation, face_folder="blush")

        self.update_outfits_with_face_accessories(pose_path, outfits, char_yml)
        widths = []
        heights = []
        bb_boxes = []
        for width, height, bbox in map(self.open_image_and_get_measurements, faces):
            widths.append(width)
            heights.append(height)
            bb_boxes.append(bbox)

        faces: list[ImagePath] = list(
            map(
                ImagePath,
                map(self.clean_path_function, faces),
                widths,
                heights,
                bb_boxes,
            )
        )
        faces.sort(key=sort_functions.face_sort_imp)
        for width, height, bbox in map(self.open_image_and_get_measurements, blushes):
            widths.append(width)
            heights.append(height)
            bb_boxes.append(bbox)

        blushes: list[ImagePath] = list(
            map(
                ImagePath,
                map(self.clean_path_function, blushes),
                widths,
                heights,
                bb_boxes,
            )
        )
        blushes.sort(key=sort_functions.face_sort_imp)

        widths.clear()
        heights.clear()
        bb_boxes.clear()
        for width, height, bbox in map(self.open_image_and_get_measurements, outfits):
            widths.append(width)
            heights.append(height)
            bb_boxes.append(bbox)

        new_outfits: list[Outfit] = []
        outfit_obj: list[str | list[str]]
        for outfit_obj, width, height, box in zip(outfits, widths, heights, bb_boxes):
            outfit_path = ImagePath(self.clean_path_function(outfit_obj[0]), width, height, box)
            out_name = self.get_outfit_name(outfit_obj[0], pose_path)
            image_paths_on_access = []
            image_paths_off_access = []
            if outfit_obj[1]:
                no_blank_off_access = [x for x in outfit_obj[1] if None not in self.open_image_and_get_measurements(x)]
                image_paths_off_access = [
                    ImagePath(self.clean_path_function(x), *self.open_image_and_get_measurements(x))
                    for x in no_blank_off_access
                ]
                # get Layering for default accessories
                image_paths_off_access = [
                    Accessory(
                        self.get_name_for_accessory(x),
                        "",
                        x,
                        self.get_layering_for_accessory(x),
                        self.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_MAIN_PAGE),
                        self.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_ACCESSORY_PAGE),
                    )
                    for x in image_paths_off_access
                ]
            if outfit_obj[2]:
                no_blank_on_access = [x for x in outfit_obj[2] if None not in self.open_image_and_get_measurements(x)]
                image_paths_on_access = [
                    ImagePath(self.clean_path_function(x), *self.open_image_and_get_measurements(x))
                    for x in no_blank_on_access
                ]
                # get Layering for default accessories
                image_paths_on_access = [
                    Accessory(
                        self.get_name_for_accessory(x),
                        self.get_state_for_accessory(x),
                        x,
                        self.get_layering_for_accessory(x),
                        self.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_MAIN_PAGE),
                        self.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_ACCESSORY_PAGE),
                    )
                    for x in image_paths_on_access
                ]
                if out_name in inverse_accessories:
                    access_to_remove = []
                    for access in image_paths_on_access:
                        if access.is_pose_level_accessory and access.name in inverse_accessories[out_name]:
                            access_to_remove.append(access)
                    for access in access_to_remove:
                        image_paths_on_access.remove(access)
            new_outfits.append(Outfit(outfit_path, image_paths_off_access, image_paths_on_access))

        new_outfits.sort(key=lambda x: x.path.path.split(os.sep)[-1].split(".")[0])
        return new_outfits, faces, blushes, *outfit_tuple, face_direction

    def get_default_outfit(
        self,
        outfit_data: list[tuple[str]],
    ) -> Tuple[ImagePath, list[ImagePath, str, int]]:
        """Returns best default outfit for headshot.


        Can take optional priority list to change what outfit is shown on main page
        """

        # adjust outfit_priority based on pass in

        default_outfit = None
        for x in self.outfit_priority:
            if default_outfit:
                break
            for outfit_tuple in outfit_data:
                if re.search(f"{re.escape(os.sep)}{x}\\.", outfit_tuple[0]):
                    default_outfit = outfit_tuple
                    break
        if not default_outfit:
            default_outfit = outfit_data[0]

        image_paths_access = []

        outfit_image = ImagePath(
            self.remove_path(default_outfit, self.input_path), *self.open_image_and_get_measurements(default_outfit)
        )
        no_blank_access = [x for x in default_outfit[1] if None not in self.open_image_and_get_measurements(x)]
        image_paths_access = [
            ImagePath(self.remove_path(x, self.input_path), *self.open_image_and_get_measurements(x))
            for x in no_blank_access
        ]
        # get Layering for default accessories
        image_paths_access = [
            Accessory(
                "",
                "",
                x,
                self.get_layering_for_accessory(x),
                self.get_scaled_image_height(outfit_image, x, classes.HEIGHT_OF_MAIN_PAGE),
            )
            for x in image_paths_access
        ]

        return (
            outfit_image,
            image_paths_access,
        )

    def remove_path(self, a: str | tuple[str], path_to_remove: str) -> str | tuple[str]:
        """Removes full path from a string or tuple of strings"""
        return (
            a.replace(path_to_remove + os.sep, "").replace(os.sep, "/")
            if isinstance(a, str)
            else a[0].replace(path_to_remove + os.sep, "").replace(os.sep, "/")
        )

    def get_layering_for_accessory(self, image: ImagePath) -> str:
        "Checks if the accessory has a layer other than 0"
        if image.clean_path.startswith("acc_"):
            acc_folder = image.clean_path.split("/")[0]
        else:
            acc_folder = image.clean_path.split("/")[-2]
        return acc_folder[-2:] if acc_folder[-2] in ("+", "-") else "0"

    def get_scaled_image_height(self, outfit: ImagePath, accessory: ImagePath, page_height: int) -> int:
        "Find the height to be display on based on the outfit height and page height"
        return round((accessory.height / outfit.height) * page_height)

    def get_name_for_accessory(self, image: ImagePath) -> str:
        "The name of the accessory. Bracelet, hair, etc"
        if image.clean_path.startswith("acc_"):
            acc_folder = image.clean_path.split("/")[0].replace("acc_", "")
        else:
            acc_folder = image.clean_path.split("/")[-2]
        return re.split("[+-]", acc_folder)[0]

    def get_state_for_accessory(self, image: ImagePath) -> str:
        "The state for the accessory. The bracelets in the blue state (Filename on_blue)"

        acc_file = image.clean_path.split("/")[-1]
        if not acc_file.startswith("on"):
            return ""
        if "on." in acc_file:
            return ""
        return acc_file.split("_", maxsplit=1)[1].rsplit(".", 1)[0]

    def get_outfit_name(self, outfit_path: str, path_to_pose: str):
        "Calculate name of outfit"
        span_name = outfit_path.replace(f"{path_to_pose}{os.sep}outfits{os.sep}", "").split(os.sep)
        return span_name[0] if len(span_name) > 1 else span_name[0].split(".")[0]

    def update_outfits_with_face_accessories(
        self, pose: str, outfits: list[tuple[str, list[str], list[str]]], char_yml
    ):
        "Find any face accessories and add them to the outfits"
        # end_string = os.path.join("mutations", mutation, "face", "*/") if mutation else os.path.join("face", "*/")
        faces_of_accessories = []
        for path_of_face_accessory in glob(os.path.join(pose, "faces", "face", "*/")):
            self.glob_for_face_accessories(pose, path_of_face_accessory, faces_of_accessories)

        mutations_dict = {}
        mutations_check = char_yml and "mutations" in char_yml
        if mutations_check:
            for mutation in char_yml["mutations"]:
                mutation_face_list = []
                for path_of_face_accessory in glob(os.path.join(pose, "faces", "mutations", mutation, "face", "*/")):
                    self.glob_for_face_accessories(pose, path_of_face_accessory, mutation_face_list)
                mutations_dict[mutation] = mutation_face_list

        for outfit_path, _, on_accessories in outfits:
            outfit_to_check = self.get_outfit_name(outfit_path, pose)
            if (
                mutations_check
                and mutations_dict
                and any(outfit_to_check in char_yml["mutations"][mutation] for mutation in char_yml["mutations"])
            ):
                mutation = next(
                    (key for key, value in char_yml["mutations"].items() if outfit_to_check in value),
                    "",
                )
                on_accessories.extend(mutations_dict[mutation])
            else:
                on_accessories.extend(faces_of_accessories)

    def glob_for_face_accessories(self, pose: str, path_to_glob: str, list_to_append: list[str]):
        "Attempt to find face accessories for a given pose"
        for path_of_face_accessory in glob(path_to_glob):
            files = self.natural_sort(os.listdir(path_of_face_accessory))
            if not files:
                print(
                    f"Error: Face accessory was not found for accessory '{path_of_face_accessory.removesuffix(os.sep).split(os.sep)[-1]}',"
                    + f" for pose '{pose.split(os.sep)[-2:]}'",
                )
                input("Press Enter to exit...")
                sys.exit(1)
            list_to_append.append(os.path.join(path_of_face_accessory, files[0]))

    def convert(self, text: str) -> int | str:
        "Convert a string to a number if possible"
        return int(text) if text.isdigit() else text.lower()

    def alpha_num_key(self, key: str):
        "Convert a string to a list of string and number"
        return [self.convert(c) for c in re.split("([0-9]+)", key)]

    def natural_sort(self, l: list[str]):
        "Naturally sort the list"
        return sorted(l, key=self.alpha_num_key)

    # Taken and edited from https://git.student-transfer.com/st/student-transfer/-/blob/master/tools/asset-ingest/trim-image.py
    def open_image_and_get_measurements(
        self, name: str | list[str]
    ) -> tuple[int, int, None] | tuple[int, int, tuple[int, int, int, int] | None]:
        """Opens the given image or first image in the list, then returns the size and bound box.
        If do_trim is true, will trim the image before
        Setting remove_empty as true will remove any blank image.
        """
        name, trim_img = self.attempt_to_open_image(name, remove_empty_pixels=self.remove_empty_pixels)
        image_size = trim_img.size
        # if trim_img.mode != "RGBA":
        #     trim_img = trim_img.convert("RGBA")
        bbox = trim_img.split()[-1].getbbox()
        if not bbox:
            if f"{os.sep}face{os.sep}" in name or "/face/" in name:
                return (*image_size, None)
            if self.remove_empty:
                os.remove(name)
            elif name not in self.FILES_THAT_COULD_BE_REMOVED:
                self.FILES_THAT_COULD_BE_REMOVED.append(name)
                print(f"{name} is empty, it can be removed")
            return (*image_size, None)

        amount_to_trim = bbox[2:]

        if amount_to_trim != image_size and self.do_trim:
            trim_img = trim_img.crop((0, 0) + amount_to_trim)
            bbox = trim_img.getbbox()
            trim_img.save(name)
            image_size = trim_img.size
        return (*image_size, bbox)
