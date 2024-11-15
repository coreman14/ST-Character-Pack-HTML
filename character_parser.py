from dataclasses import dataclass
from typing import Callable
from classes import Character, Pose, Outfit, ImagePath, Accessory
import classes
import os
from collections import defaultdict
import path_functions
from base_parser import ParserBase
import sort_functions


@dataclass
class CharacterParser(ParserBase):
    "A reusable class for creating a character. This will create a character object by giving a character path to parse"
    input_path: str
    trim_function: Callable
    clean_path_function: Callable
    outfit_priority: list[str]
    max_height_constant: float

    def parse(self, path_to_character: str) -> Character:
        "Create a character from a given character path"
        pose_list = []
        for pose_path in [
            os.path.join(self.input_path, "characters", path_to_character, path)
            for path in os.listdir(os.path.join(self.input_path, "characters", path_to_character))
            if os.path.isdir(os.path.join(self.input_path, "characters", path_to_character, path))
        ]:
            pose_letter = pose_path.split(os.sep)[-1]

            if not path_functions.check_character_is_valid(pose_path):
                continue
            if char_pose := self.create_character(
                path_to_character,
                pose_path,
                pose_letter,
            ):
                pose_list.append(Pose(self.input_path, pose_letter, *char_pose))

        if pose_list:
            return Character(path_to_character, pose_list, self.max_height_constant)
        return None

    def create_character(
        self,
        path_to_character: str,
        pose_path: str,
        pose_letter: str,
    ) -> None | tuple[list[Outfit], list[ImagePath], list[ImagePath], ImagePath, list[ImagePath]]:
        """
        Gets all the require inputs for a given pose
        """
        mutation = None

        if not path_functions.check_character_is_valid(pose_path):
            return
        outfits = path_functions.get_outfits(pose_path, path_to_character)

        char_yml: dict = self.get_yaml(self.input_path, path_to_character)
        excluded_accessories = char_yml.get("poses", {}).get(pose_letter, {}).get("excludes", {})
        face_direction = char_yml.get("poses", {}).get(pose_letter, {}).get("facing", "left")
        inverse_accessories = defaultdict(list)
        for k, v in excluded_accessories.items():
            for x in v:
                inverse_accessories[x].append(k)

        outfit_tuple = path_functions.get_default_outfit(
            outfits,
            trim_images=self.trim_function,
            path_to_remove=self.input_path,
            outfit_priority=self.outfit_priority,
        )
        default_outfit_name = outfit_tuple[0].file_name
        mutation = None
        mutations: dict[str, list[str]]
        if mutations := char_yml.get("mutations", {}):
            for key, value in mutations.items():
                if any(x in default_outfit_name for x in value):
                    if path_functions.check_character_mutation_is_valid(pose_path, key):
                        mutation = key
                    else:
                        print(
                            f'WARNING: Character "{path_to_character}" for pose "{pose_letter}" default outfit of "{default_outfit_name}"'
                            + f' has mutation "{key}", but no faces are provided for that mutation.',
                        )
                    break

        faces = path_functions.get_faces(pose_path, path_to_character, mutation)
        blushes = path_functions.get_faces(pose_path, path_to_character, mutation, face_folder="blush")

        path_functions.update_outfits_with_face_accessories(pose_path, outfits, char_yml)
        widths = []
        heights = []
        bb_boxes = []
        for width, height, bbox in map(self.trim_function, faces):
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
        for width, height, bbox in map(self.trim_function, blushes):
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
        for width, height, bbox in map(self.trim_function, outfits):
            widths.append(width)
            heights.append(height)
            bb_boxes.append(bbox)

        new_outfits: list[Outfit] = []
        outfit_obj: list[str | list[str]]
        for outfit_obj, width, height, box in zip(outfits, widths, heights, bb_boxes):
            outfit_path = ImagePath(self.clean_path_function(outfit_obj[0]), width, height, box)
            out_name = path_functions.get_outfit_name(outfit_obj[0], pose_path)
            image_paths_on_access = []
            image_paths_off_access = []
            if outfit_obj[1]:
                no_blank_off_access = [x for x in outfit_obj[1] if None not in self.trim_function(x)]
                image_paths_off_access = [
                    ImagePath(self.clean_path_function(x), *self.trim_function(x)) for x in no_blank_off_access
                ]
                # get Layering for default accessories
                image_paths_off_access = [
                    Accessory(
                        path_functions.get_name_for_accessory(x),
                        "",
                        x,
                        path_functions.get_layering_for_accessory(x),
                        path_functions.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_MAIN_PAGE),
                        path_functions.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_ACCESSORY_PAGE),
                    )
                    for x in image_paths_off_access
                ]
            if outfit_obj[2]:
                no_blank_on_access = [x for x in outfit_obj[2] if None not in self.trim_function(x)]
                image_paths_on_access = [
                    ImagePath(self.clean_path_function(x), *self.trim_function(x)) for x in no_blank_on_access
                ]
                # get Layering for default accessories
                image_paths_on_access = [
                    Accessory(
                        path_functions.get_name_for_accessory(x),
                        path_functions.get_state_for_accessory(x),
                        x,
                        path_functions.get_layering_for_accessory(x),
                        path_functions.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_MAIN_PAGE),
                        path_functions.get_scaled_image_height(outfit_path, x, classes.HEIGHT_OF_ACCESSORY_PAGE),
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
