import os
import re
import sys
import json
import yaml

from classes import ImagePath, Accessory, Outfit
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


def create_character(trim, remove, name, paths, outfit_prio, main_page_height=200, accessory_page_height=400):
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
        main_page_height=main_page_height,
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
            main_page_height=main_page_height,
        )
        faces = path_functions.get_mutated_faces(path, name, mutation)
    widths = []
    heights = []
    bboxs = []
    for width, height, bbox in map(trim, faces):
        widths.append(width)
        heights.append(height)
        bboxs.append(bbox)

    faces: list[ImagePath] = list(
        map(
            ImagePath,
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

    new_outfits: list[Outfit] = []
    outfit_obj: list[str | list[str]]
    for outfit_obj, width, height, box in zip(outfits, widths, heights, bboxs):
        if isinstance(outfit_obj, str):
            new_outfits.append(Outfit(ImagePath(remove(outfit_obj), width, height, box)))
        else:
            outfit_path = ImagePath(remove(outfit_obj[0]), width, height, box)
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
                        path_functions.get_page_height_for_accessory(outfit_path, x, main_page_height),
                        path_functions.get_page_height_for_accessory(outfit_path, x, accessory_page_height),
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
                        path_functions.get_page_height_for_accessory(outfit_path, x, main_page_height),
                        path_functions.get_page_height_for_accessory(outfit_path, x, accessory_page_height),
                    )
                    for x in image_paths_on_access
                ]
            new_outfits.append(Outfit(outfit_path, image_paths_off_access, image_paths_on_access))

    new_outfits.sort(key=lambda x: x.path.path.split(os.sep)[-1].split(".")[0])
    return new_outfits, faces, *outfit_tuple


def create_html_file(args, scenario_title, html_snips, chars_tuple, split_files=False):
    html_snip1, html_snip2, html_snip3 = html_snips
    chars_with_poses, chars = chars_tuple
    with open(os.path.join(args.inputdir, args.name), "w+", encoding="utf8") as html_file:
        html_file.write(html_snip1 + scenario_title)
        html_file.write(html_snip2)
        html_file.write(f'{scenario_title}";')
        if split_files:
            html_file.write("var characterArray = data.carray;var jsonData = data.characters;")
        else:
            html_file.write(
                "var characterArray=["
                + ", ".join(str(x) for x in chars_with_poses)
                + "]; var jsonData={ "
                + "".join(str(x) for x in chars)
                + "};"
            )
        # Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
        html_file.write(html_snip3)
    print(
        f"Outputted to HTML at {os.path.join(args.inputdir, args.name)}",
        end="\n" if split_files else "",
    )

    if not split_files:
        input(
            ", press enter to exit...",
        )
        print()


def create_js(args, chars_tuple):
    chars_with_poses, chars = chars_tuple
    formatted_json = yaml.safe_load(
        '{"carray":['
        + ", ".join(str(x) for x in chars_with_poses)
        + '],"characters": { '
        + "".join(str(x) for x in chars)
        + "}}"
    )
    with open(os.path.join(args.inputdir, args.jsname), "w+", encoding="utf8") as json_file:
        json_file.write(f"var data = {json.dumps(formatted_json)}")

    print(f"Outputted to JSON at {os.path.join(args.inputdir, args.jsname)}", end="")
    input(
        ", press enter to exit...",
    )
    print()
