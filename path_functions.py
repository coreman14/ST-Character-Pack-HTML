import itertools
import os
import re
import sys
from argparse import ArgumentTypeError
from glob import glob
from typing import Tuple
from classes import ImagePath, Accessory
import classes

ACCEPTED_EXT = [".webp", ".png"]
OUTFIT_PRIO = [
    "uniform",
    ("casual", "dress"),
    "nude",
    ("under", "underwear"),
]


def find_access(out_path, off_accessories_to_add=None, on_accessories_to_add=None) -> tuple[str, list[str]]:
    outfit_access = glob(os.path.join(os.path.dirname(out_path), "*", ""))
    off_acc = []
    on_acc = []
    if not outfit_access:
        return out_path, off_acc, on_acc
    for direct, ext in itertools.product(outfit_access, ACCEPTED_EXT):
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


def get_faces_and_outfits(pose, character_name):
    outfits: list[Tuple[str, list[str], list[str]]] = []
    off_pose_level_accessories = []
    on_pose_level_accessories = []
    # Scan for off accessories
    for ext in ACCEPTED_EXT:
        off_pose_level_accessories.extend(glob(os.path.join(pose, "outfits", "acc_*", f"off{ext}")))
        on_pose_level_accessories.extend(glob(os.path.join(pose, "outfits", "acc_*", f"on*{ext}")))
    for ext in ACCEPTED_EXT:
        outfits.extend(
            (x, list(off_pose_level_accessories), list(on_pose_level_accessories))
            for x in glob(os.path.join(pose, "outfits", f"*{ext}"))
        )
        outfits.extend(
            find_access(x, off_pose_level_accessories, on_pose_level_accessories)
            for x in glob(os.path.join(pose, "outfits", "*", f"*{ext}"))
            if f"{os.sep}acc_" not in x
        )
        outfits_in_folders = [
            x[0] for x in outfits if (x[1] or x[2])
        ]  # Get folders that have outfits and an off or on accessory
        outfit_folders = [x.rsplit(os.sep, 1)[0] for x in outfits_in_folders]
        # If there are pose accessories, outfits not in folders will mess up this count. So we get that number and subtract 1 for the copy that will be left in
        # We use max to make sure its not a negative number
        non_folder_outfits_count = max(outfit_folders.count(os.path.join(pose, "outfits")) - 1, 0)
        outfits = [
            x
            for x in outfits
            if (isinstance(x, str) and not x.endswith(f"_inverted{ext}"))
            or (isinstance(x, tuple) and not x[0].endswith(f"_inverted{ext}"))
        ]
        if len(set(outfit_folders)) + non_folder_outfits_count != len(outfit_folders):
            dup = sorted({x for x in outfit_folders if outfit_folders.count(x) > 1})
            print(
                f'Error: Character "{character_name}" with corresponding pose "{pose.split(os.sep)[-1]}" contains more than one outfit with an accessory in single folder.'
            )
            print(
                "Doing this will result in the second outfit in the folder not being able to access any accessories from the folder."
            )
            print("Consider making a second folder for this outfit.")
            print("Folder names: ")
            char_folder_path = os.sep.join(pose.rsplit(os.sep, 2)[1:])
            for x in dup:
                print("\t" + (char_folder_path + x.replace(pose, "")).replace(os.sep, "/"))
            sys.exit(1)
    faces: list[str] = [
        *glob(os.path.join(pose, "faces", "face", "*.webp")),
        *glob(os.path.join(pose, "faces", "face", "*.png")),
    ]
    if not outfits or not faces:
        out_str = ("" if outfits else "outfits") + ("faces" if not faces and outfits else "" if faces else " and faces")

        print(
            f'Error: Character "{character_name}" with corresponding pose "{pose.split(os.sep)[-1]}" does not contain {out_str}. Skipping.'
        )
        return None, None
    faces = remove_path_duplicates_no_ext(faces)
    outfits = remove_path_duplicates_no_ext(outfits)
    # outfits = [(x, []) for x in outfits]
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
) -> Tuple[ImagePath, list[ImagePath, str, int]]:
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
                    k for k, v in outfit_dict.items() if f"{y}." in v or not isinstance(v, str) and f"{y}." in v[0]
                ]

                for i in del_key:
                    del outfit_dict[i]
    # Create true false dict
    outfit = None
    for x in outfit_prio:
        if outfit:
            break
        for outfit_loop in outfit_dict.values():
            og_outfit = outfit_loop
            if not isinstance(outfit_loop, str):
                outfit_loop = outfit_loop[0]
            if isinstance(x, str) and re.search(f"{x}\\.", outfit_loop):
                outfit = og_outfit
                break
            if isinstance(x, tuple):
                for y in x:
                    if re.search(f"{y}\\.", outfit_loop):
                        outfit = og_outfit
                        break

    image_paths_access = []
    if not outfit_dict:
        return None
    if len(outfit_dict) == 1 or not outfit:
        outfit = list(outfit_dict.values())[0]

    outfit_image = ImagePath(remove_path(outfit, full_path), *trim_images(outfit))
    if not isinstance(outfit, str):
        no_blank_access = [x for x in outfit[1] if None not in trim_images(x)]
        image_paths_access = [ImagePath(remove_path(x, full_path), *trim_images(x)) for x in no_blank_access]
        # get Layering for default accessories
        image_paths_access = [
            Accessory(
                "",
                "",
                x,
                get_layering_for_accessory(x),
                get_scaled_image_height(outfit_image, x, classes.HEIGHT_OF_MAIN_PAGE),
            )
            for x in image_paths_access
        ]

    return (
        outfit_image,
        image_paths_access,
    )


def dir_path(path: str) -> str:
    """Checks if a path is real and returns the full path, else error's out"""
    if os.path.exists(path):
        return os.path.abspath(path)
    raise ArgumentTypeError(f'Output directory "{path}" is not a valid path')


def get_layering_for_accessory(image: ImagePath) -> str:
    if image.clean_path.startswith("acc_"):
        acc_folder = image.clean_path.split("/")[0]
    else:
        acc_folder = image.clean_path.split("/")[-2]
    return acc_folder[-2:] if acc_folder[-2] in ("+", "-") else "0"


def get_name_for_accessory(image: ImagePath) -> str:
    "The name of the accessory. Bracelet, hair, etc"
    if image.clean_path.startswith("acc_"):
        acc_folder = image.clean_path.split("/")[0].replace("acc_", "")
    else:
        acc_folder = image.clean_path.split("/")[-2]
    return re.split("[+-]", acc_folder)[0]


def get_state_for_accessory(image: ImagePath) -> str:
    "The state for the accessory. The bracelets in the blue state (Filename on_blue)"

    acc_file = image.clean_path.split("/")[-1]
    if not acc_file.startswith("on"):
        return ""
    if "on." in acc_file:
        return ""
    return acc_file.split("_", maxsplit=1)[1].rsplit(".", 1)[0]


def get_outfit_name(outfit_path: str, pose_path: str):
    span_name = outfit_path.replace(f"{pose_path}{os.sep}outfits{os.sep}", "").split(os.sep)
    return span_name[0] if len(span_name) > 1 else span_name[0].split(".")[0]


def get_scaled_image_height(outfit: ImagePath, accessory: ImagePath, page_height: int) -> int:
    return round((accessory.height / outfit.height) * page_height)


# def find_access(out_path, off_accessories_to_add=None, on_accessories_to_add=None) -> tuple[str, list[str]]:
#     outfit_access = glob(os.path.join(os.path.dirname(out_path), "*", ""))
#     off_acc = []
#     on_acc = []
#     if not outfit_access:
#         return out_path, off_acc, on_acc
#     for direct, ext in itertools.product(outfit_access, ACCEPTED_EXT):
#         if acc_list := glob(os.path.join(direct, f"*{ext}")):
#             acc_dict = {x.split(os.sep)[-1]: x for x in acc_list}
#             for key, value in acc_dict.items():
#                 if key == f"off{ext}":
#                     off_acc.append(value)
#                 else:
#                     on_acc.append(value)
#     off_acc.extend(off_accessories_to_add or ())
#     on_acc.extend(on_accessories_to_add or ())
#     return out_path, off_acc, on_acc


def update_outfits_with_face_accessories(pose: str, outfits: list[tuple[str, list[str], list[str]]], char_yml):
    # end_string = os.path.join("mutations", mutation, "face", "*/") if mutation else os.path.join("face", "*/")
    faces_of_accessories = []
    for path_of_face_accessory in glob(os.path.join(pose, "faces", "face", "*/")):
        glob_for_face_accessories(pose, path_of_face_accessory, faces_of_accessories)

    mutations_dict = {}
    mutations_check = char_yml and "mutations" in char_yml
    if mutations_check:
        for mutation in char_yml["mutations"]:
            mutation_face_list = []
            for path_of_face_accessory in glob(os.path.join(pose, "faces", "mutations", mutation, "face", "*/")):
                glob_for_face_accessories(pose, path_of_face_accessory, mutation_face_list)
                mutations_dict[mutation] = mutation_face_list
    if not faces_of_accessories or not mutations_dict:
        return

    for outfit_path, _, on_accessories in outfits:
        outfit_to_check = get_outfit_name(outfit_path, pose)
        if mutations_check and any(
            outfit_to_check in char_yml["mutations"][mutation] for mutation in char_yml["mutations"]
        ):
            mutation = next(
                (key for key, value in char_yml["mutations"].items() if outfit_to_check in value),
                "",
            )
            on_accessories.extend(mutations_dict[mutation])
        else:
            on_accessories.extend(faces_of_accessories)


def glob_for_face_accessories(pose, path_to_glob, list_to_append):
    for path_of_face_accessory in glob(path_to_glob):
        files = natural_sort(os.listdir(path_of_face_accessory))
        if not files:
            print(
                f"Error: Face accessory was not found for accessory '{path_of_face_accessory.removesuffix(os.sep).split(os.sep)[-1]}', for pose '{pose.split(os.sep)[-2:]}'"
            )
            sys.exit(1)
        list_to_append.append(files[0])


def convert(text):
    return int(text) if text.isdigit() else text.lower()


def alphanum_key(key):
    return [convert(c) for c in re.split("([0-9]+)", key)]


def natural_sort(l):
    return sorted(l, key=alphanum_key)
