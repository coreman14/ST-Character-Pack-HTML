"This holds anything related to printing the bounds of an object"
from dataclasses import dataclass
import os
import re
from collections import Counter

from colorama import Fore, Style


from classes import Character, CropBox
import sort_functions
from base_parser import ParserBase


@dataclass
class BoundsParser(ParserBase):
    "A reusable class for the bounds function. After init, it will print the output by calling parse with the character path"

    regex: str
    skip_if_same: bool
    print_faces: bool
    print_outfits: bool

    def parse(self, character_name: str) -> Character:
        "Run bounds check on given character path"
        for pose_path in [
            os.path.join(self.input_path, "characters", character_name, path)
            for path in os.listdir(os.path.join(self.input_path, "characters", character_name))
            if os.path.isdir(os.path.join(self.input_path, "characters", character_name, path))
        ]:

            self.bounds(
                pose_path,
                character_name,
            )

    def bounds(self, pose_path: str, character_name: str):
        """Output the minimum size of each image for the character.
        Use it to find invisible pixels left over from editing"""

        pose_letter = self.input_path.split(os.sep)[-1]
        if (self.regex is None or re.match(self.regex, character_name)) and not self.is_character_invalid(pose_path):
            char_yml: dict = self.get_yaml(character_name)
            outfits = self.get_outfits(pose_path, character_name)
            faces = self.get_faces(pose_path, character_name)
            blushes = self.get_faces(pose_path, character_name, face_folder="blush")

            mutations: dict[str, list[str]]
            print(f"Character {character_name}: Pose {pose_letter}")
            if self.print_faces:
                faces.sort(key=sort_functions.sort_by_numbers)

                print("Faces")
                self.bounds_print(faces, self.skip_if_same)
                if blushes:
                    blushes.sort(key=sort_functions.sort_by_numbers)
                    print("Blush faces")
                    self.bounds_print(blushes, self.skip_if_same)
                if mutations := char_yml.get("mutations", {}):
                    for key in [x for x in mutations.keys() if self.check_character_mutation_is_valid(pose_path, x)]:
                        faces = self.get_faces(pose_path, character_name, key)
                        if faces:
                            faces.sort(key=sort_functions.sort_by_numbers)
                            print(f'Mutation "{key}" face')
                            self.bounds_print(faces, self.skip_if_same)
                        blushes = self.get_faces(pose_path, character_name, key, face_folder="blush")
                        if blushes:
                            blushes.sort(key=sort_functions.sort_by_numbers)
                            print(f'Mutation "{key}" blush face')
                            self.bounds_print(blushes, self.skip_if_same)
            if self.print_outfits:
                outfits.sort(key=sort_functions.face_sort_out_tuple)
                print()
                print("Outfits")
                self.bounds_print(outfits, self.skip_if_same)

            print()

    def bounds_print(self, to_print: list[str], skip_if_same: bool, split_str=os.sep):
        """Prints the real calculate size of each file. Will highlight any files where the size is different than the others"""
        print(Style.RESET_ALL, end="")
        print_box = []
        print_name = []
        for image_path in to_print:
            if not isinstance(image_path, str):
                image_path = image_path[0]
            if bb_box := self.return_bb_box(image_path):
                print_box.append(CropBox(*bb_box))
            else:
                print_box.append(None)
            print_name.append(image_path.split(split_str)[-1])
        if len(Counter(print_box).most_common()) == 1 and skip_if_same:
            print("All images have the same measurements")
            return
        most_bbox = Counter(print_box).most_common(1)
        most_bbox = None if most_bbox[0][1] == 1 and len(print_box) != 1 else most_bbox[0][0]
        for f_name, bbox in zip(print_name, print_box):
            if bbox:
                print(
                    Fore.RED if bbox != most_bbox else Style.RESET_ALL,
                    bbox,
                    f_name,
                )
        print(Style.RESET_ALL, end="")

    def return_bb_box(self, name: str | list[str]) -> tuple[int, int, int, int]:
        """Opens the given image or first image in the list, then returns the bounding box of the image."""
        name, trim_img = self.attempt_to_open_image(name)
        if trim_img.mode != "RGBA":
            trim_img = trim_img.convert("RGBA")
        bbox = trim_img.split()[-1].getbbox()
        return bbox or (0, 0, 0, 0)
