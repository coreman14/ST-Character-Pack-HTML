import itertools
import os
import re
from argparse import ArgumentTypeError
from glob import glob

from classes import ImagePath

ACCEPTED_EXT = [".webp", ".png"]
OUTFIT_PRIO = [
    "uniform",
    ("casual", "dress"),
    "nude",
    ("under", "underwear"),
]


def find_access(out_path) -> tuple[str, list[str]]:
    outfit_access = glob(os.path.join(os.path.dirname(out_path), "*", ""))
    return_acc = []
    if len(outfit_access) == 0:
        return out_path, return_acc
    for direct, ext in itertools.product(outfit_access, ACCEPTED_EXT):
        acc_list = glob(os.path.join(direct, f"*{ext}"))
        if len(acc_list) > 0:
            acc_dict = {x.split(os.sep)[-1]: x for x in acc_list}
            if f"off{ext}" in acc_dict:
                return_acc.append(acc_dict[f"off{ext}"])
    return out_path, return_acc


def get_faces_and_outfits(pose, character_name):
    outfits: list[str] = []
    for ext in ACCEPTED_EXT:
        outfits.extend(glob(os.path.join(pose, "outfits", f"*{ext}")))
        outfits.extend(
            find_access(x) for x in glob(os.path.join(pose, "outfits", "*", f"*{ext}"))
        )

    faces: list[str] = [
        *glob(os.path.join(pose, "faces", "face", "*.webp")),
        *glob(os.path.join(pose, "faces", "face", "*.png")),
    ]
    if not outfits or not faces:
        out_str = ("" if outfits else "outfits") + (
            "faces" if not faces and outfits else "" if faces else " and faces"
        )

        print(
            f'Error: Character "{character_name}" with corresponding pose "{pose.split(os.sep)[-1]}" does not contain {out_str}. Skipping.'
        )
        return None, None
    faces = remove_path_duplicates_no_ext(faces)
    outfits = remove_path_duplicates_no_ext(outfits)
    return faces, outfits


def get_mutated_faces(pose, character_name, mutation):
    faces: list[str] = [
        *glob(os.path.join(pose, "faces", "mutations", mutation, "face", "*.webp")),
        *glob(os.path.join(pose, "faces", "mutations", mutation, "face", "*.png")),
    ]
    if not faces:
        print(
            f'Error: Character "{character_name}" with corresponding pose "{pose.split(os.sep)[-1]}" does not contain faces for mutation "{mutation}". Skipping.'
        )
        return None, None
    faces = remove_path_duplicates_no_ext(faces)
    return faces


def remove_path_duplicates_no_ext(a: list[str | tuple[str]]):
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


def remove_path(a, full_path):
    return (
        a.replace(full_path + os.sep, "").replace(os.sep, "/")
        if isinstance(a, str)
        else a[0].replace(full_path + os.sep, "").replace(os.sep, "/")
    )


def get_default_outfit(
    outfit_data: list[str | tuple[str]],
    char_data: dict,
    trim_images,
    full_path,
    outfit_prio,
    mutation="",
):
    """Returns best default outfit for headshot.


    Can take optional priority list to change what outfit is shown on main page
    """

    # adjust outfit prio based on pass in
    outfit_prio = outfit_prio or OUTFIT_PRIO

    # Check in tuple for outfit
    # Return given/list or blank one
    outfit_dict = {str(i): outfit_data[i] for i in range(len(outfit_data))}
    if char_data and "mutations" in char_data:
        char_data = char_data["mutations"]
        for x in char_data:
            if mutation and x == mutation:
                continue
            for y in char_data[x]:
                del_key = [
                    k
                    for k, v in outfit_dict.items()
                    if f"{y}." in v or not isinstance(v, str) and f"{y}." in v[0]
                ]

                for i in del_key:
                    del outfit_dict[i]
    # Create true false dict
    outfit = None
    for x in outfit_prio:
        if outfit:
            break
        for outfit_loop in outfit_dict.values():
            if not isinstance(outfit_loop, str):
                outfit_loop = outfit_loop[0]
            if isinstance(x, str) and re.search(f"{x}\\.", outfit_loop):
                outfit = outfit_loop
                break
            if isinstance(x, tuple):
                for y in x:
                    if re.search(f"{y}\\.", outfit_loop):
                        outfit = outfit_loop
                        break

    image_paths_access = []
    if not outfit_dict:
        return None
    elif len(outfit_dict) == 1 or not outfit:
        outfit = list(outfit_dict.values())[0]

    if not isinstance(outfit, str):
        no_blank_access = [x for x in outfit[1] if None not in trim_images(x)]
        image_paths_access = [
            ImagePath(remove_path(x, full_path), *trim_images(x))
            for x in no_blank_access
        ]

    return (
        ImagePath(remove_path(outfit, full_path), *trim_images(outfit)),
        image_paths_access,
    )


def dir_path(path: str) -> str:
    """Checks if a path is real and returns the full path, else error's out"""
    if os.path.exists(path):
        return os.path.abspath(path)
    raise ArgumentTypeError(f'Output directory "{path}" is not a valid path')
