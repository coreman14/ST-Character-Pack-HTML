import os

from colorama import Fore, Style

from classes import CropBox


def bounds_print(to_print, bbox_func, split_str=os.sep):
    print(Style.RESET_ALL, end="")
    old_box = None
    for ipath in to_print:
        if not isinstance(ipath, str):
            ipath = ipath[0]
        if bobobo := bbox_func(ipath):
            new_box = CropBox(*bobobo)

            print(
                Fore.RED if old_box not in [None, new_box] else Style.RESET_ALL,
                new_box,
                ipath.split(split_str)[-1],
            )
            old_box = new_box
    print(Style.RESET_ALL, end="")
