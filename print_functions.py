import os
from collections import Counter

from colorama import Fore, Style

from classes import CropBox


def bounds_print(to_print, bbox_func, split_str=os.sep):
    print(Style.RESET_ALL, end="")
    print_box = []
    print_name = []
    for ipath in to_print:
        if not isinstance(ipath, str):
            ipath = ipath[0]
        if bobobo := bbox_func(ipath):
            print_box.append(CropBox(*bobobo))
        else:
            print_box.append(None)
        print_name.append(ipath.split(split_str)[-1])

    most_bbox = Counter(print_box).most_common(1)
    most_bbox = (
        None if most_bbox[0][1] == 1 and len(print_box) != 1 else most_bbox[0][0]
    )
    for f_name, bbox in zip(print_name, print_box):
        if bbox:
            print(
                Fore.RED if bbox != most_bbox else Style.RESET_ALL,
                bbox,
                f_name,
            )
    print(Style.RESET_ALL, end="")
