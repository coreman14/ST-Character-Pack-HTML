"""Given a path and defaults, parse a character into a character object and return it."""

from dataclasses import dataclass, field
from typing import Tuple
import re
import os
from collections import defaultdict
import sys
from glob import glob
from character_parser_classes import (
    Character,
    CropBox,
    Pose,
    Outfit,
    ImagePath,
    Accessory,
    Face,
    Blush,
    OutfitImagePath,
)
from base_parser import ParserBase

type path = str


@dataclass
class CharacterParser(ParserBase):
    "A reusable class for creating a character. This will create a character object by using the input path and the given characters name."
    outfit_priority: list[str]
    max_height_constant: float
    trim_and_save_image: bool
    delete_empty_images: bool
    remove_empty_pixels_for_faces: bool
    current_pose_letter: str = field(init=False, repr=False)

    def parse(self, character_name: str) -> Character:
        "Create a character from a given character name and {input_path}. Goes through each pose defined in the character folder."
        self.current_character_name = character_name
        pose_list = []
        for pose_path in [
            os.path.join(self.input_path, "characters", character_name, path)
            for path in os.listdir(os.path.join(self.input_path, "characters", character_name))
            if os.path.isdir(os.path.join(self.input_path, "characters", character_name, path))
        ]:
            self.current_pose_letter = pose_path.split(os.sep)[-1]
            self.pose_path = pose_path
            if self.pose_path:
                self.read_character_yml()
                if char_pose := self.parse_character_pose():
                    pose_list.append(char_pose)

        if pose_list:
            return Character(character_name, pose_list, self.max_height_constant)
        return None

    def parse_character_pose(
        self,
    ) -> tuple[list[Outfit], list[Face], list[Blush], ImagePath, list[Accessory], str]:
        # 4th return is the default outfit
        """
        Creates a character pose object from the set {pose_path}.
        """

        face_direction: str = (
            self.character_config.get("poses", {}).get(self.current_pose_letter, {}).get("facing", "left")
        )
        # Get the list of outfits
        outfits = self.get_pose_outfits_paths()
        # Using that list of outfits, get the default outfit mutation
        mutation = self.get_default_outfit_mutation(outfits)
        # Get faces and blushes using that mutation
        faces, blushes = self.get_pose_faces(mutation)
        # Get the default outfit imagepath + accessories and pass in the max height of the faces so the crop boxes come out right
        c = CropBox.cropbox_from_multiple_images((x.cropbox for x in faces))
        face_height = c.bottom if c is not None else 0
        default_outfit, default_accessories = self.get_default_outfit(outfits, face_height=face_height)
        # Convert the outfits from imagepath to Outfit objects

        outfits = self.convert_outfit_paths_to_objects(outfits)
        new_pose = Pose(
            self.input_path,
            self.current_pose_letter,
            outfits,
            faces,
            blushes,
            default_outfit,
            facing_direction=face_direction,
        )
        new_pose.add_default_accessories(default_accessories)
        return new_pose

    def convert_outfit_paths_to_objects(self, outfit_data: list[Tuple[path, list[path], list[path]]]):
        """Creates the outfits objects for the pose."""
        inverse_accessories = defaultdict(list)
        for k, v in (
            self.character_config.get("poses", {}).get(self.current_pose_letter, {}).get("excludes", {}).items()
        ):
            for x in v:
                inverse_accessories[x].append(k)

        self.update_outfits_with_face_accessories(outfit_data)

        outfits_with_measurements: list[OutfitImagePath] = []
        for outfit, off_accessories, on_accessories in outfit_data:
            measurements = self.open_image_and_get_measurements(outfit)
            outfits_with_measurements.append(
                OutfitImagePath(
                    self.remove_input_path(outfit),
                    measurements[0],
                    measurements[1],
                    measurements[2],
                    off_accessories,
                    on_accessories,
                )
            )

        new_outfits: list[Outfit] = []
        for outfit in outfits_with_measurements:
            image_paths_on_access = []
            image_paths_off_access = []
            if outfit.off_accessories:
                image_paths_off_access = self.create_outfit_accessories_imagepaths(outfit.off_accessories)
            if outfit.on_accessories:
                image_paths_on_access = self.create_outfit_accessories_imagepaths(outfit.on_accessories)

            new_outfit = Outfit(outfit)
            new_outfit.add_on_accessories(image_paths_on_access, inverse_accessories)
            new_outfit.add_off_accessories(image_paths_off_access)
            new_outfits.append(new_outfit)

        new_outfits.sort(key=lambda x: x.path.path.split(os.sep)[-1].split(".")[0])
        return new_outfits

    def get_default_outfit_mutation(self, outfit_data: list[Tuple[path, list[path], list[path]]]):
        "Finds the default outfit then return the mutation that the default outfit will use"
        default_outfit = self.get_default_outfit(outfit_data, skip_parsing=True)
        return self.check_default_outfit_mutation_is_valid(default_outfit[0])

    def check_default_outfit_mutation_is_valid(self, default_outfit: path) -> str | None:
        """Checks if the default_outfit mutation is valid.

        If the mutation is valid, it will return the mutation for the default outfit.

        If the mutation is invalid, it will print a message, then if strict_mode is true, it will exit the program, else it will return none
        """
        mutations: dict[str, list[str]]
        default_outfit_file = default_outfit.split(os.sep)[-1].split(".")[0]
        if mutations := self.character_config.get("mutations", {}):
            for key, value in mutations.items():
                if any(x in default_outfit_file for x in value):
                    if self.check_pose_mutation_is_valid(key):
                        return key

                    print(
                        f'{"ERROR" if self.strict_mode else "WARNING"}: Character "{self.current_character_name}" '
                        + f'for pose "{self.current_pose_letter}" '
                        + f'default outfit of "{default_outfit_file}"'
                        + f' has mutation "{key}", but no faces are provided for that mutation.',
                    )
                    if self.strict_mode:
                        input("Press Enter to exit...")
                        sys.exit(1)
                    return None
        return None

    def create_outfit_accessories_imagepaths(self, outfit_acessories_list: list[ImagePath]):
        """Convert a list of ImagePath of accessories to a list of Accessory.
        If inverse_accessories is given, Accessories will be checked against the dict and removed if they are found for the outfit
        """
        image_paths_access = []
        for x in outfit_acessories_list:
            if measurements := self.open_image_and_get_measurements(x):
                image_paths_access.append(ImagePath(self.remove_input_path(x), *measurements))

        return image_paths_access

    def get_pose_faces(self, mutation: str):
        "Returns the face and blush object used to initialize a pose. Mutation can be none"
        faces_paths = self.get_pose_face_paths(mutation)
        faces: list[Face] = []

        for face in faces_paths:
            faces.append(Face(self.remove_input_path(face), *self.open_image_and_get_measurements(face)))
        faces.sort(key=self.face_sort_imp)

        blush_paths = self.get_pose_face_paths(mutation, face_folder="blush")
        blushes: list[Blush] = []

        for blush in blush_paths:
            blushes.append(Face(self.remove_input_path(blush), *self.open_image_and_get_measurements(blush)))
        blushes.sort(key=self.face_sort_imp)

        # Don't combine faces if no blushes are present
        if blushes:
            file_names_faces = [x.file_name for x in faces]
            file_names_blushes = [x.file_name for x in blushes]
            for index, x in enumerate(file_names_blushes):
                if x not in file_names_faces:
                    faces.append(blushes[index])
            for index, x in enumerate(file_names_faces):
                if x not in file_names_blushes:
                    blushes.append(faces[index])
            faces.sort(key=self.face_sort_imp)
            blushes.sort(key=self.face_sort_imp)

        return faces, blushes

    def get_default_outfit(
        self,
        outfit_data: list[Tuple[path, list[path], list[path]]],
        skip_parsing: bool = False,
        face_height: int = None,
    ) -> Tuple[ImagePath, list[ImagePath]]:
        """Calculates the default outfit that should be used in expression sheets and needed accessories."""

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
        if skip_parsing:
            return default_outfit

        outfit_image = ImagePath(
            self.remove_input_path(default_outfit), *self.open_image_and_get_measurements(default_outfit, face_height)
        )
        image_paths_access = []
        for x in default_outfit[1]:
            if measurements := self.open_image_and_get_measurements(x, face_height):
                image_paths_access.append(
                    ImagePath(
                        self.remove_input_path(x),
                        *measurements,
                    )
                )
        return (
            outfit_image,
            image_paths_access,
        )

    def remove_input_path(self, a: str | tuple[str]) -> str | tuple[str]:
        """Removes the {input_path} from a string or the first string in a tuple"""
        return (
            a.replace(self.input_path + os.sep, "").replace(os.sep, "/")
            if isinstance(a, str)
            else a[0].replace(self.input_path + os.sep, "").replace(os.sep, "/")
        )

    def get_outfit_name(self, outfit_path: str):
        "Calculates the name of outfit_path"
        span_name = outfit_path.replace(f"{self.pose_path}{os.sep}outfits{os.sep}", "").split(os.sep)
        return span_name[0] if len(span_name) > 1 else span_name[0].split(".")[0]

    def update_outfits_with_face_accessories(self, outfits: list[tuple[str, list[str], list[str]]]):
        """Go through the list of outfits and add any face accessories that are found.
        This calculates the mutation for each outfit to avoid false positives"""
        faces_of_accessories = []
        for path_of_face_accessory in glob(os.path.join(self.pose_path, "faces", "face", "*/")):
            self.glob_for_face_accessories(path_of_face_accessory, faces_of_accessories)

        mutations_dict = {}
        mutations_check = self.character_config and "mutations" in self.character_config
        if mutations_check:
            for mutation in self.character_config["mutations"]:
                mutation_face_list = []
                for path_of_face_accessory in glob(
                    os.path.join(self.pose_path, "faces", "mutations", mutation, "face", "*/")
                ):
                    self.glob_for_face_accessories(path_of_face_accessory, mutation_face_list)
                mutations_dict[mutation] = mutation_face_list

        for outfit_path, _, on_accessories in outfits:
            outfit_to_check = self.get_outfit_name(outfit_path)
            if (
                mutations_check
                and mutations_dict
                and any(
                    outfit_to_check in self.character_config["mutations"][mutation]
                    for mutation in self.character_config["mutations"]
                )
            ):
                mutation = next(
                    (key for key, value in self.character_config["mutations"].items() if outfit_to_check in value),
                    "",
                )
                on_accessories.extend(mutations_dict[mutation])
            else:
                on_accessories.extend(faces_of_accessories)

    def glob_for_face_accessories(self, path_to_glob: path, list_to_append: list[str]):
        """Attempt to find face accessories for a given pose.
        If the path was empty, it will print a message, then if strict_mode is true, it will exit the program, else it will return none
        """
        for path_of_face_accessory in glob(path_to_glob):
            files = self.natural_sort(os.listdir(path_of_face_accessory))
            if not files:
                print(
                    f"{"ERROR" if self.strict_mode else "WARNING"}: Face accessory was not "
                    + f"found for accessory '{path_of_face_accessory.removesuffix(os.sep).split(os.sep)[-1]}',"
                    + f" for pose '{self.pose_path.split(os.sep)[-2:]}'",
                )
                if self.strict_mode:
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
        self, name: str | list[str], max_height=None
    ) -> tuple[int, int, None | tuple[int, int, int, int]] | None:
        """Opens the given image or first image in the list, then returns the size and bound box.
        If {trim_and_save_image} is true, any changes to the image will be saved
        Setting remove_empty as true will remove any blank image.
        """
        name, trim_img = self.attempt_to_open_image(name, remove_empty_pixels=self.remove_empty_pixels_for_faces)
        image_size = trim_img.size

        bbox = trim_img.getbbox()
        if not bbox:
            if f"{os.sep}face{os.sep}" in name or "/face/" in name:
                return (*image_size, None)
            if self.delete_empty_images:
                os.remove(name)
            else:
                print(f"{name} is empty, it can be removed")
            return (*image_size, None)

        amount_to_trim = bbox[2:]

        if amount_to_trim != image_size and self.trim_and_save_image:
            trim_img = trim_img.crop((0, 0) + amount_to_trim)
            bbox = trim_img.getbbox()
            trim_img.save(name)
            image_size = trim_img.size

        if max_height:
            bbox = trim_img.crop((0, 0, trim_img.width, max_height)).getbbox()
        return (*image_size, bbox)

    def face_sort_imp(self, image: ImagePath):
        "Return a sortable version of the given file"
        return self.sort_by_numbers(image.path, sep="/")

    def __hash__(self) -> int:
        return 1
