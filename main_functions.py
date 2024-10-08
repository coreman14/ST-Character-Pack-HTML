"Main runner functions for the program"
from argparse import Namespace
import os
import re
import sys
import json
from collections import defaultdict
from typing import Callable
import yaml


import classes
from classes import Character, ImagePath, Accessory, Outfit
from html_arg_functions import update_html
import path_functions
import sort_functions
from print_functions import bounds_print
import json2yaml
import args_functions

YML_FAILS = []
JSON_CONVERT_ASK = False


def bounds(
    regex: re.Pattern, path: str, input_dir: str, name: str, skip_if_same: bool, print_faces: bool, print_outfits: bool
):
    """Output the minimum size of each image for the character.
    Use it to find invisible pixels left over from editing"""
    pose_letter = path.split(os.sep)[-1]
    if (regex is None or re.match(regex, name)) and path_functions.check_character_is_valid(path):
        char_yml: dict = get_yaml(input_dir, name)
        outfits = path_functions.get_outfits(path, name)
        faces = path_functions.get_faces(path, name)
        blushes = path_functions.get_faces(path, name, face_folder="blush")

        mutations: dict[str, list[str]]
        print(f"Character {name}: Pose {pose_letter}")
        if print_faces:
            faces.sort(key=sort_functions.sort_by_numbers)

            print("Faces")
            bounds_print(faces, skip_if_same)
            if blushes:
                blushes.sort(key=sort_functions.sort_by_numbers)
                print("Blush faces")
                bounds_print(blushes, skip_if_same)
            if mutations := char_yml.get("mutations", {}):
                for key in [x for x in mutations.keys() if path_functions.check_character_mutation_is_valid(path, x)]:
                    faces = path_functions.get_faces(path, name, key)
                    if faces:
                        faces.sort(key=sort_functions.sort_by_numbers)
                        print(f'Mutation "{key}" face')
                        bounds_print(faces, skip_if_same)
                    blushes = path_functions.get_faces(path, name, key, face_folder="blush")
                    if blushes:
                        blushes.sort(key=sort_functions.sort_by_numbers)
                        print(f'Mutation "{key}" blush face')
                        bounds_print(blushes, skip_if_same)
        if print_outfits:
            outfits.sort(key=sort_functions.face_sort_out_tuple)
            print()
            print("Outfits")
            bounds_print(outfits, skip_if_same)

        print()


def get_yaml(input_dir: str, name: str) -> dict:
    "Get the YAML file for the character"
    try:
        with open(
            os.path.join(input_dir, "characters", name, "character.yml"),
            "r",
            encoding="utf8",
        ) as char_file:
            return yaml.safe_load(char_file) or {}
    except FileNotFoundError:
        global JSON_CONVERT_ASK
        json_ask_finish = "anything else to skip"
        if args_functions.STRICT_ERROR_PARSING:
            json_ask_finish = "anything else to exit"
        if (
            os.path.exists(os.path.join(input_dir, "characters", name, "character.json"))
            and args_functions.INPUT_DIR != ""
            and name not in YML_FAILS
        ):
            if not JSON_CONVERT_ASK:
                print(f"ERROR: Could not find character YML for {name}, but found a json file.")
                response = input(
                    f"Would you like to convert all JSON files to YAML? (y for yes, {json_ask_finish}): ",
                )
                JSON_CONVERT_ASK = True
            else:
                response = ""
            if response.lower() in ["y"]:
                json2yaml.json2yaml(input_dir=args_functions.INPUT_DIR)
                return get_yaml(input_dir, name)
            elif not args_functions.STRICT_ERROR_PARSING:
                pass
            else:
                sys.exit(1)
        elif not args_functions.STRICT_ERROR_PARSING:
            pass
        else:
            print(f"ERROR: Could not find character YML for {name}")
            input("Press Enter to exit...")
            sys.exit(1)
        if name not in YML_FAILS:
            print(
                f"Could not find config info for {name}. "
                + "Using blank configuration. To disable this feature, use enable strict mode using --strict",
            )
            YML_FAILS.append(name)
        return {}
    except yaml.YAMLError as error:
        print(f"ERROR: Character YML for {name}, could not be read.\nInfo: {error}")

        input("Press Enter to exit...")
        sys.exit(1)


def create_character(
    trim: Callable, remove: Callable, name: str, path: str, input_dir: str, outfit_priority: list[str], pose_letter: str
) -> None | tuple[list[Outfit], list[ImagePath], list[ImagePath], ImagePath, list[ImagePath]]:
    """
    Gets all the require inputs for a given pose
    """
    mutation = None

    if not path_functions.check_character_is_valid(path):
        return
    outfits = path_functions.get_outfits(path, name)

    char_yml: dict = get_yaml(input_dir, name)
    excluded_accessories = char_yml.get("poses", {}).get(pose_letter, {}).get("excludes", {})

    inverse_accessories = defaultdict(list)
    for k, v in excluded_accessories.items():
        for x in v:
            inverse_accessories[x].append(k)

    outfit_tuple = path_functions.get_default_outfit(
        outfits,
        trim_images=trim,
        path_to_remove=input_dir,
        outfit_priority=outfit_priority,
    )
    default_outfit_name = outfit_tuple[0].file_name
    mutation = None
    mutations: dict[str, list[str]]
    if mutations := char_yml.get("mutations", {}):
        for key, value in mutations.items():
            if any(x in default_outfit_name for x in value):
                if path_functions.check_character_mutation_is_valid(path, key):
                    mutation = key
                else:
                    print(
                        f'WARNING: Character "{name}" for pose "{pose_letter}" default outfit of "{default_outfit_name}"'
                        + f' has mutation "{key}", but no faces are provided for that mutation.',
                    )
                break

    faces = path_functions.get_faces(path, name, mutation)
    blushes = path_functions.get_faces(path, name, mutation, face_folder="blush")

    path_functions.update_outfits_with_face_accessories(path, outfits, char_yml)
    widths = []
    heights = []
    bb_boxes = []
    for width, height, bbox in map(trim, faces):
        widths.append(width)
        heights.append(height)
        bb_boxes.append(bbox)

    faces: list[ImagePath] = list(
        map(
            ImagePath,
            map(remove, faces),
            widths,
            heights,
            bb_boxes,
        )
    )
    faces.sort(key=sort_functions.face_sort_imp)
    for width, height, bbox in map(trim, blushes):
        widths.append(width)
        heights.append(height)
        bb_boxes.append(bbox)

    blushes: list[ImagePath] = list(
        map(
            ImagePath,
            map(remove, blushes),
            widths,
            heights,
            bb_boxes,
        )
    )
    blushes.sort(key=sort_functions.face_sort_imp)

    widths.clear()
    heights.clear()
    bb_boxes.clear()
    for width, height, bbox in map(trim, outfits):
        widths.append(width)
        heights.append(height)
        bb_boxes.append(bbox)

    new_outfits: list[Outfit] = []
    outfit_obj: list[str | list[str]]
    for outfit_obj, width, height, box in zip(outfits, widths, heights, bb_boxes):
        outfit_path = ImagePath(remove(outfit_obj[0]), width, height, box)
        out_name = path_functions.get_outfit_name(outfit_obj[0], path)
        image_paths_on_access = []
        image_paths_off_access = []
        if outfit_obj[1]:
            no_blank_off_access = [x for x in outfit_obj[1] if None not in trim(x)]
            image_paths_off_access = [ImagePath(remove(x), *trim(x)) for x in no_blank_off_access]
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
            no_blank_on_access = [x for x in outfit_obj[2] if None not in trim(x)]
            image_paths_on_access = [ImagePath(remove(x), *trim(x)) for x in no_blank_on_access]
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
    return new_outfits, faces, blushes, *outfit_tuple


def create_html_file(args: Namespace, html_snips: tuple[str, str, str], chars: list[Character], split_files=False):
    "Create the HTML file for the scenario"
    html_snip1, html_snip2 = html_snips
    html_snip1 = html_snip1.replace("FAVICONHERE", args.favicon)
    html_snip1 = update_html(args, html_snip1)
    with open(os.path.join(args.inputdir, args.name), "w+", encoding="utf8") as html_file:
        html_file.write(html_snip1)
        if split_files:
            html_file.write(
                f'</script><script src="{args.jsonname}"></script><script>var jsonData = data.characters;scenario=data.scenario;prefix=data.prefix;'
            )
        else:
            html_file.write(f'scenario="{args.titlename}";prefix="{args.prefix}";')
            html_file.write("var jsonData={ " + "".join(str(x) for x in chars) + "};")
        # Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
        html_file.write(html_snip2)
    print(
        f"Outputted to HTML at {os.path.join(args.inputdir, args.name)}",
        end="\n" if split_files else "",
    )

    if not split_files:
        input(
            ", press enter to exit...",
        )
        print()


def create_js(args: Namespace, chars: list[Character]):
    "Create a JS file containing the information needed for the HTML"
    formatted_json = yaml.safe_load(
        '{"scenario": "'
        + args.titlename
        + '", "prefix": "'
        + args.prefix
        + '", "characters": { '
        + "".join(str(x) for x in chars)
        + "}}",
    )
    with open(os.path.join(args.inputdir, args.jsonname), "w+", encoding="utf8") as json_file:
        json_file.write(f"var data = {json.dumps(formatted_json)}")

    print(f"Outputted to JSON at {os.path.join(args.inputdir, args.jsonname)}", end="")
    input(
        ", press enter to exit...",
    )
    print()
