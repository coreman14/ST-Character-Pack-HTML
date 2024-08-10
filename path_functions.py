"Functions relating to dealing with the file system"
import itertools
import os
import re
import sys
from argparse import ArgumentTypeError
from glob import glob
from typing import Callable, Tuple
from classes import ImagePath, Accessory
import classes

ACCEPTED_EXT = [".webp", ".png"]
OUTFIT_PRIO = [
    "uniform",
    "suit",
    "casual",
    "dress",
    "nude",
    "under",
    "underwear",
]


def find_access(
    out_path: str, off_accessories_to_add: list[str] = None, on_accessories_to_add: list[str] = None
) -> tuple[str, list[str]]:
    "Looks for accessories for a given outfit"
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


def check_character_is_valid(path_to_pose: str) -> bool:
    "Check if character is valid. Valid is having at least 1 face or outfit in non mutated places"
    face_found = False
    outfit_found = False
    for ext in ACCEPTED_EXT:
        # Check for any outfits/faces
        outfit_found = (
            outfit_found
            or bool([x for x in glob(os.path.join(path_to_pose, "outfits", f"*{ext}"))])
            or bool([x for x in glob(os.path.join(path_to_pose, "outfits", "*", f"*{ext}"))])
        )
        face_found = face_found or bool(glob(os.path.join(path_to_pose, "faces", "face", f"*{ext}")))
        if face_found and outfit_found:
            return True
    return False


def check_character_mutation_is_valid(path_to_pose: str, mutation: str) -> bool:
    "Check if faces for a given mutation exists"
    face_found = False
    for ext in ACCEPTED_EXT:
        # Check for any outfits/faces
        face_found = face_found or bool(
            glob(os.path.join(path_to_pose, "faces", "mutations", mutation, "face", f"*{ext}"))
        )
        if face_found:
            return True
    return False


def get_outfits(path_to_pose: str, character_name: str) -> None | list[Tuple[str, list[str], list[str]]]:
    "Get outfits and accessories for a given pose"
    outfits: list[Tuple[str, list[str], list[str]]] = []
    off_pose_level_accessories = []
    on_pose_level_accessories = []
    # Scan for off accessories
    for ext in ACCEPTED_EXT:
        off_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"off{ext}")))
        on_pose_level_accessories.extend(glob(os.path.join(path_to_pose, "outfits", "acc_*", f"on*{ext}")))
    for ext in ACCEPTED_EXT:
        outfits.extend(
            (x, list(off_pose_level_accessories), list(on_pose_level_accessories))
            for x in glob(os.path.join(path_to_pose, "outfits", f"*{ext}"))
        )
        outfits.extend(
            find_access(x, off_pose_level_accessories, on_pose_level_accessories)
            for x in glob(os.path.join(path_to_pose, "outfits", "*", f"*{ext}"))
            if f"{os.sep}acc_" not in x
        )
        outfits_in_folders = [
            x[0] for x in outfits if (x[1] or x[2])
        ]  # Get folders that have outfits and an off or on accessory
        outfit_folders = [x.rsplit(os.sep, 1)[0] for x in outfits_in_folders]
        # If there are pose accessories, outfits not in folders will mess up this count.
        # So we get that number and subtract 1 for the copy that will be left in
        # We use max to make sure its not a negative number
        non_folder_outfits_count = max(outfit_folders.count(os.path.join(path_to_pose, "outfits")) - 1, 0)
        outfits = [
            x
            for x in outfits
            if (isinstance(x, str) and not x.endswith(f"_inverted{ext}"))
            or (isinstance(x, tuple) and not x[0].endswith(f"_inverted{ext}"))
        ]
        if len(set(outfit_folders)) + non_folder_outfits_count != len(outfit_folders):
            dup = sorted({x for x in outfit_folders if outfit_folders.count(x) > 1})
            print(
                f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
                + "contains more than one outfit with an accessory in single folder.",
            )
            print(
                "Doing this will result in the second outfit in the folder not being able to access any accessories from the folder."
            )
            print("Consider making a second folder for this outfit.")
            print("Folder names: ")
            char_folder_path = os.sep.join(path_to_pose.rsplit(os.sep, 2)[1:])
            for x in dup:
                print("\t" + (char_folder_path + x.replace(path_to_pose, "")).replace(os.sep, "/"))
            sys.exit(1)

    if not outfits:
        print(
            f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
            + "does not contain outfits. Skipping.",
        )
        return None
    outfits = remove_path_duplicates_no_ext(outfits)
    return outfits


def get_faces(
    path_to_pose: str, character_name: str, mutation: str = None, face_folder: str = None
) -> None | list[str]:
    "Attempts to get the faces for a given pose, a mutation or different face folder can adjust where it will look"
    folder_to_look_in = face_folder or "face"
    faces: list[str] = []
    face_path = os.path.join(path_to_pose, "faces", *(("mutations", mutation) if mutation else ""), folder_to_look_in)
    for ext in ACCEPTED_EXT:
        faces.extend(glob(os.path.join(face_path, f"*{ext}")))
    if not faces and not face_folder:  # Only error if no folder is given
        mutation_string = f' for mutation "{mutation}"' if mutation else ""
        print(
            f'Error: Character "{character_name}" with corresponding pose "{path_to_pose.split(os.sep)[-1]}" '
            + f"does not contain faces in folder {folder_to_look_in}{mutation_string}. Skipping.",
        )
        return None
    faces = remove_path_duplicates_no_ext(faces)
    return faces


def remove_path_duplicates_no_ext(a: list[str | tuple[str]]) -> list[str | tuple[str]]:
    "Attempts to remove duplicates from a list of str/tuples of strings"
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


def remove_path(a: str | tuple[str], path_to_remove: str) -> str | tuple[str]:
    """Removes full path from a string or tuple of strings"""
    return (
        a.replace(path_to_remove + os.sep, "").replace(os.sep, "/")
        if isinstance(a, str)
        else a[0].replace(path_to_remove + os.sep, "").replace(os.sep, "/")
    )


def get_default_outfit(
    outfit_data: list[tuple[str]],
    trim_images: Callable,
    path_to_remove: str,
    outfit_prio: list[str],
) -> Tuple[ImagePath, list[ImagePath, str, int]]:
    """Returns best default outfit for headshot.


    Can take optional priority list to change what outfit is shown on main page
    """

    # adjust outfit prio based on pass in
    outfit_prio = outfit_prio or OUTFIT_PRIO

    default_outfit = None
    for x in outfit_prio:
        if default_outfit:
            break
        for outfit_tuple in outfit_data:
            if re.search(f"{re.escape(os.sep)}{x}\\.", outfit_tuple[0]):
                default_outfit = outfit_tuple
                break
    if not default_outfit:
        default_outfit = outfit_data[0]

    image_paths_access = []

    outfit_image = ImagePath(remove_path(default_outfit, path_to_remove), *trim_images(default_outfit))
    no_blank_access = [x for x in default_outfit[1] if None not in trim_images(x)]
    image_paths_access = [ImagePath(remove_path(x, path_to_remove), *trim_images(x)) for x in no_blank_access]
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
    "Checks if the accessory has a layer other than 0"
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


def get_outfit_name(outfit_path: str, path_to_pose: str):
    "Calculate name of outfit"
    span_name = outfit_path.replace(f"{path_to_pose}{os.sep}outfits{os.sep}", "").split(os.sep)
    return span_name[0] if len(span_name) > 1 else span_name[0].split(".")[0]


def get_scaled_image_height(outfit: ImagePath, accessory: ImagePath, page_height: int) -> int:
    "Find the height to be display on based on the oufit height and page height"
    return round((accessory.height / outfit.height) * page_height)


def update_outfits_with_face_accessories(pose: str, outfits: list[tuple[str, list[str], list[str]]], char_yml):
    "Find any face accessories and add them to the outfits"
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

    for outfit_path, _, on_accessories in outfits:
        outfit_to_check = get_outfit_name(outfit_path, pose)
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


def glob_for_face_accessories(pose: str, path_to_glob: str, list_to_append: list[str]):
    "Attempt to find face accessories for a given pose"
    for path_of_face_accessory in glob(path_to_glob):
        files = natural_sort(os.listdir(path_of_face_accessory))
        if not files:
            print(
                f"Error: Face accessory was not found for accessory '{path_of_face_accessory.removesuffix(os.sep).split(os.sep)[-1]}',"
                + f" for pose '{pose.split(os.sep)[-2:]}'",
            )
            sys.exit(1)
        list_to_append.append(os.path.join(path_of_face_accessory, files[0]))


def convert(text: str) -> int | str:
    "Convert a string to a number if possible"
    return int(text) if text.isdigit() else text.lower()


def alphanum_key(key: str):
    "Convert a string to a list of string and number"
    return [convert(c) for c in re.split("([0-9]+)", key)]


def natural_sort(l: list[str]):
    "Naturally sort the list"
    return sorted(l, key=alphanum_key)
