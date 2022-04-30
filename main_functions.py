import os
import re
import sys

import yaml

import classes
import path_functions
import sort_functions
from print_functions import bounds_print


def bounds(regex, path, name):
    pose_letter = path.split(os.sep)[-1]
    if regex is None or re.match(regex, name):
        faces, outfits = path_functions.get_faces_and_outfits(path, name)
        if None in [faces, outfits]:
            return
        print(f"Character {name}: Pose {pose_letter}")
        faces.sort(key=sort_functions.sort_by_numbers)
        print("Faces")
        bounds_print(faces)

        outfits.sort(key=sort_functions.face_sort_outtuple)
        print()
        print("Outfits")
        bounds_print(outfits)

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
        sys.exit()
    except yaml.YAMLError as error:
        print(f"ERROR: Character YML for {name}, could not be read.\nInfo: {error}")

        input("Press Enter to exit...")
        sys.exit()


def create_character(trim, remove, name, paths):
    path, inputdir = paths
    faces, outfits = path_functions.get_faces_and_outfits(path, name)
    if None in [faces, outfits]:
        return
    char_yml = get_yaml(inputdir, name)
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

    outfit_tuple = path_functions.get_default_outfit(
        outfits,
        char_data=char_yml,
        trim_images=trim,
        full_path=inputdir,
    )
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
    chars_with_poses, chars = chars_tuple
    with open(
        os.path.join(args.inputdir, args.name), "w+", encoding="utf8"
    ) as html_file:
        html_file.write(html_snip1 + scenario_title)
        # Add Scenario Title before continue
        if args.backgroundimage:
            args.backgroundimage = args.backgroundimage.replace("\\", "/")
            html_snip2 = html_snip2.replace(
                "background-color: white; /*Background Replace*/",
                f'background-color: white; /*Background Replace*/background-image: url("{args.backgroundimage}"); /*Background Replace*/',
            )
        if args.backgroundcolor:
            html_snip2 = html_snip2.replace(
                "background-color: white; /*Background Replace*/",
                f"background-color: {args.backgroundcolor}; /*Background Replace*/",
            )

        if args.toppadding:
            html_snip2 = html_snip2.replace(
                ".characters{",
                f".characters{{ padding-top: {args.toppadding}px;",
            )
        if args.titlecolor:
            html_snip2 = html_snip2.replace(
                "#title{",
                f"#title{{ color: {args.titlecolor};",
            )
        if args.charactercolor:
            html_snip2 = html_snip2.replace(
                ".character{",
                f".character{{ background-color: {args.charactercolor};",
            )

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
        html_file.write(
            html_snip3.replace(
                '"black";}else{context.fillStyle="#121212";}',
                f'"black";}}else{{context.fillStyle="{args.color2}";}}',
            )
            .replace(
                'index % 2==1){context.fillStyle="black";',
                f'index % 2==1){{context.fillStyle="{args.color1}";',
            )
            .replace(
                'context.fillStyle="white";/*rect color*/',
                f'context.fillStyle="{args.rectbackgroundcolor}";/*rect color*/',
            )
            .replace(
                'context.fillStyle="black";/*text color*/',
                f'context.fillStyle="{args.textcolor}";/*text color*/',
            )
        )

    input(
        f"Outputted to HTML at {os.path.join(args.inputdir, args.name)}, press enter to exit..."
    )
