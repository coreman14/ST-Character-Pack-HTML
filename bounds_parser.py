"This holds anything related to printing the bounds of an object"
from dataclasses import dataclass
import os
import re
from collections import Counter

from colorama import Fore, Style


from character_parser_classes import Character, CropBox
from base_parser import ParserBase

type path = str


@dataclass
class BoundsParser(ParserBase):
    "A reusable class for the bounds function. After init, it will print the output by calling parse with the character path"

    regex: str
    skip_if_same: bool
    print_faces: bool
    print_outfits: bool

    def parse(self, character_name: str) -> Character:
        "Run bounds check on given character"
        self.current_character_name = character_name
        for pose_path in [
            os.path.join(self.input_path, "characters", character_name, path)
            for path in os.listdir(os.path.join(self.input_path, "characters", character_name))
            if os.path.isdir(os.path.join(self.input_path, "characters", character_name, path))
        ]:
            self.read_character_yml()
            self.pose_path = pose_path
            if self.pose_path:
                self.parse_pose_bounds()

    def parse_pose_bounds(self):
        """Output the minimum size of each image for the character.
        Use it to find invisible pixels left over from editing"""

        pose_letter = self.input_path.split(os.sep)[-1]
        if self.regex is None or re.match(self.regex, self.current_character_name):
            outfits = self.get_pose_outfits_paths()
            faces = self.get_pose_face_paths()

            mutations: dict[str, list[str]]
            print(f"Character {self.current_character_name}: Pose {pose_letter}")
            if self.print_faces:
                faces.sort(key=self.sort_by_numbers)

                print("Faces")
                self.print_bounds(faces, self.skip_if_same)
                if blushes := self.get_pose_face_paths(face_folder="blush"):
                    blushes.sort(key=self.sort_by_numbers)
                    print("Blush faces")
                    self.print_bounds(blushes, self.skip_if_same)
                if mutations := self.character_config.get("mutations", {}):
                    for key in [x for x in mutations.keys() if self.check_pose_mutation_is_valid(x)]:
                        if faces := self.get_pose_face_paths(key):
                            faces.sort(key=self.sort_by_numbers)
                            print(f'Mutation "{key}" face')
                            self.print_bounds(faces, self.skip_if_same)
                        if blushes := self.get_pose_face_paths(key, face_folder="blush"):
                            blushes.sort(key=self.sort_by_numbers)
                            print(f'Mutation "{key}" blush face')
                            self.print_bounds(blushes, self.skip_if_same)
            if self.print_outfits:
                outfits.sort(key=self.face_sort_out_tuple)
                print()
                print("Outfits")
                self.print_bounds(outfits, self.skip_if_same)

            print()

    def print_bounds(self, to_print: list[path], skip_if_same: bool, split_str=os.sep):
        """Prints the real calculate size of each file. Will highlight any files where the size is different than the others"""
        print(Style.RESET_ALL, end="")
        if not to_print:
            print("No images found")
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

    def return_bb_box(self, name: path | list[path]) -> tuple[int, int, int, int]:
        """Opens the given image or first image in the list, then returns the bounding box of the image."""
        # For bounds, we should never trim the image, it should reflect what is shown in the game.
        # We do empty pixel remove in the HTML because it makes it easier to do it's job
        name, trim_img = self.attempt_to_open_image(name, remove_empty_pixels=False)
        if trim_img.mode != "RGBA":
            trim_img = trim_img.convert("RGBA")
        bbox = trim_img.split()[-1].getbbox()
        return bbox or (0, 0, 0, 0)

    def face_sort_out_tuple(self, image: tuple[str]):
        "Return a sortable version of the given file"
        return self.sort_by_numbers(image[0])
