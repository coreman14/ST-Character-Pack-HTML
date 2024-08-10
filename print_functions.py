"Functions for printing text in a special way"
import os
from collections import Counter

from colorama import Fore, Style

from classes import CropBox
from image_functions import return_bb_box


def bounds_print(to_print: list[str], skip_if_same: bool, split_str=os.sep):
    """Prints the real calculate size of each file. Will highlight any files where the size is different than the others"""
    print(Style.RESET_ALL, end="")
    print_box = []
    print_name = []
    for image_path in to_print:
        if not isinstance(image_path, str):
            image_path = image_path[0]
        if bb_box := return_bb_box(image_path):
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
