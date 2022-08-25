import os
import re
import sys

import yaml

import classes
import html_arg_functions
import path_functions
import sort_functions
from print_functions import bounds_print


def bounds(regex, path, name, skip_if_same, print_faces, print_outfits):
    pose_letter = path.split(os.sep)[-1]
    if regex is None or re.match(regex, name):
        faces, outfits = path_functions.get_faces_and_outfits(path, name)
        if None in [faces, outfits]:
            return

        print(f"Character {name}: Pose {pose_letter}")
        if print_faces:
            faces.sort(key=sort_functions.sort_by_numbers)
            print("Faces")
            bounds_print(faces, skip_if_same)
        if print_outfits:
            outfits.sort(key=sort_functions.face_sort_outtuple)
            print()
            print("Outfits")
            bounds_print(outfits, skip_if_same)

        print()


def get_yaml(inputdir, name):
    try:
        with open(
            os.path.join(inputdir, "characters", name, "character.yml"),
            "r",
            encoding="utf8",
        ) as char_file:
            return yaml.safe_load(char_file)
    except FileNotFoundError:
        print(
            f"ERROR: Could not find character YML for {name}, please use the jsontoyaml utility by using -j or --jsontoyaml"
        )
        input("Press Enter to exit...")
        sys.exit(1)
    except yaml.YAMLError as error:
        print(f"ERROR: Character YML for {name}, could not be read.\nInfo: {error}")

        input("Press Enter to exit...")
        sys.exit(1)


def create_character(trim, remove, name, paths, outfit_prio):
    """
    Mutations broke. When mutation broke, it returns None and then logic needs to be implemented to handle it.
    It needs to check beforehand and if it doesn't have one we need to find a mutation, then get an outfit that fixes it plus change the path to faces
    1. Reorder method to check for default outfits first, then do faces after.
    """
    path, inputdir = paths
    faces, outfits = path_functions.get_faces_and_outfits(path, name)
    if None in [faces, outfits]:
        return

    char_yml = get_yaml(inputdir, name)

    outfit_tuple = path_functions.get_default_outfit(
        outfits,
        char_data=char_yml,
        trim_images=trim,
        full_path=inputdir,
        outfit_prio=outfit_prio,
    )
    if not outfit_tuple:
        mutation = list(char_yml["mutations"])[0]
        outfit_tuple = path_functions.get_default_outfit(
            outfits,
            char_data=char_yml,
            trim_images=trim,
            full_path=inputdir,
            mutation=mutation,
            outfit_prio=outfit_prio,
        )
        faces = path_functions.get_mutated_faces(path, name, mutation)
    widths = []
    heights = []
    bboxs = []
    for width, height, bbox in map(trim, faces):
        widths.append(width)
        heights.append(height)
        bboxs.append(bbox)

    faces: list[classes.ImagePath] = list(
        map(
            classes.ImagePath,
            map(remove, faces),
            widths,
            heights,
            bboxs,
        )
    )
    faces.sort(key=sort_functions.face_sort_imp)

    widths.clear()
    heights.clear()
    bboxs.clear()
    for width, height, bbox in map(trim, outfits):
        widths.append(width)
        heights.append(height)
        bboxs.append(bbox)

    outfits: list[classes.ImagePath] = list(
        map(
            classes.ImagePath,
            map(remove, outfits),
            widths,
            heights,
            bboxs,
        )
    )

    outfits.sort(key=lambda x: x.path.split(os.sep)[-1].split(".")[0])
    return outfits, faces, *outfit_tuple


def create_html_file(args, scenario_title, html_snips, chars_tuple):
    html_snip1, html_snip2, html_snip3 = html_snips
    html_snip2 = html_arg_functions.update_html_arg_snip2(args, html_snip2)
    html_snip3 = html_arg_functions.update_html_arg_snip3(args, html_snip3)
    chars_with_poses, chars = chars_tuple
    with open(
        os.path.join(args.inputdir, args.name), "w+", encoding="utf8"
    ) as html_file:
        html_file.write(html_snip1 + scenario_title)
        html_file.write(html_snip2)
        html_file.write(
            scenario_title
            + '"; var characterArray=['
            + ", ".join(str(x) for x in chars_with_poses)
            + "]; var jsonData={ "
            + "".join(str(x) for x in chars)
            + "};"
        )
        # Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
        html_file.write(html_snip3)
    print(f"Outputted to HTML at {os.path.join(args.inputdir, args.name)}", end="")
    input(
        ", press enter to exit...",
    )
    print()
