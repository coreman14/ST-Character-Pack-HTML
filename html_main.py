"""
How to finish(in order):
    Read scenario.yml to get title
    Add output of html file
    Add command to change input location (idk)


"""


import argparse
import os
import re
import sys
from functools import partial

import yaml

import classes
import image_functions
import json2yaml
import path_functions
import sort_functions

html_snip1 = """<!DOCTYPE html><html> <head> <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no"/> <title>"""  # Add Scenario Title before continue
html_snip2 = ''' Viewer</title> <script src="https://code.jquery.com/jquery-3.5.0.js"></script> <style>body{text-align: center; background-color: white; /*Background Replace*/}#canvas{padding-top: 10px;}.characters{display: flex; flex-wrap: wrap; justify-content: center; /* here we just put the only child div to the center */}.character{margin: 10px 10px 0 0; padding: 0px 0px; height: 238px; display: flex; flex-wrap: nowrap; justify-content: center; /* here we just put the only child div to the center */ border-radius: 0.5px; border-color: grey; border-style: solid; position: relative;}.character2{margin: 10px 10px 0 0; padding: 0px 0px; height: 220px; display: flex; flex-wrap: nowrap; justify-content: center; /* here we just put the only child div to the center */ border-radius: 0.5px; border-color: grey; border-style: solid; position: relative;}.character2Container{display: flex; flex-wrap: wrap; justify-content: center; /* here we just put the only child div to the center */}.character span{position: absolute; background-color: grey; color: white; width: 100%;}.character2 span{position: absolute; background-color: grey; color: white; width: 100%;}.characterImagesOutfit{height: 200px; position: relative; top: 20px; left: 0px;}.characterposename{position: absolute; left: 50%; top: 100%; transform: translate(-50%, 0%); z-index: 31; background-color: grey; color: white; margin-top: 16px; width: 100%;}#ToggleText{/*Stolen From W3*/ width: 160px; position: fixed; top: 10px; right: 12px; font-size: 24px; display: none;}.popup{background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 8px 0; margin-left: -80px; z-index: 1;}#HelpText{position: absolute; top: 7%; width: 450px; padding: 10px 15px; padding-bottom: 15px; margin-left: auto; margin-right: auto; left: 0; right: 0; visibility: hidden;}#HelpTitle{font-size: 24px; display: block;}.HelpLine{display: block;}#backbutton{display: inline-block; vertical-align: sub; padding-right: 3px;}#title{display: inline-block;}</style> </head> <body> <span id="ToggleText" class="popup"></span> <span id="HelpText" class="popup" ><span id="HelpTitle">Character Viewer Shortcuts</span> <br/><span class="HelpLine" >Pipe | BackSlash: Disable and enable these shortcuts</span > <br/><span class="HelpLine" >UpArrow: Return to this page from any page</span > <br/><span class="HelpLine" >Backspace: Return to previous page</span > <br/><span class="HelpLine" >Left/Right Arrow: Navigate through characters in alphabetical order</span > </span> <a id="backbutton"></a> <h1 id="title" onmouseover="popouthelp()" onmouseout="hidehelp()" ></h1> <div id="imageList" class="characters"></div><div id="imageList2"></div></body> <script type="text/javascript">function popouthelp(){var popup=document.getElementById("HelpText"); popup.style.visibility="visible";}function hidehelp(){var popup=document.getElementById("HelpText"); popup.style.visibility="hidden";}function parseTextBool(textToParse){return textToParse=="true" ? true : false;}function getTextWidth(text, font){const canvas=getTextWidth.canvas || (getTextWidth.canvas=document.createElement("canvas")); const context=canvas.getContext("2d"); context.font=font; const metrics=context.measureText(text); return metrics.width;}function loadImages(extra_path, index_start, sources, callback){var images={}; var loadedImages=0; var numImages=0; for (var src in sources){numImages++;}for (var src in sources){images[src]=new Image(); images[src].onload=function (){if (++loadedImages >=numImages){callback(images);}}; if (src >=index_start){images[src].src=extra_path + sources[src];}else{images[src].src=sources[src];}}}function makeCharURL(namepose){var splitted=namepose.toString().split(","); return "character=" + splitted[0] + "&pose=" + splitted[1];}var disable_keys=parseTextBool( sessionStorage.getItem("disable_keys") ); if (disable_keys==false){sessionStorage.setItem("disable_keys", false); disable_keys=false;}$("#ToggleText").text( disable_keys ? "Keyboard shortcuts are disabled." : "Keyboard shortcuts are enabled." ); var scenario="'''
# Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
html_snip3 = """ indexLen=testArray.length - 1; file_name=location.pathname.split("/").pop() || "."; function* enumerate(it, start=0){let i=start; for (const x of it) yield [i++, x];}const urlParams=new URLSearchParams(window.location.search); var urlIndex=urlParams.get("index"); if (urlIndex > indexLen || urlIndex < 0){urlIndex=undefined;}var selectedCharacter=urlParams.get("character") ? urlParams.get("character") : undefined; var selectedPose=urlParams.get("pose") ? urlParams.get("pose") : undefined; var new_url=file_name + "?"; if ( selectedCharacter==undefined || selectedPose==undefined || urlIndex !=undefined ){selectedCharacter=undefined; selectedPose=undefined;}else if ( selectedCharacter !=undefined && (!(selectedCharacter in jsonData) || !(selectedPose in jsonData[selectedCharacter].poses)) ){selectedCharacter=undefined; selectedPose=undefined;}else{new_url +="character=" + selectedCharacter + "&pose=" + selectedPose;}if (urlIndex !=undefined){selectedCharacter=testArray[urlIndex][0]; selectedPose=testArray[urlIndex][1]; new_url +="index=" + urlIndex;}window.history.pushState(scenario, scenario, new_url); var rect_height=32; if (selectedCharacter==undefined){title.textContent=scenario; Object.entries(jsonData).forEach(([character, characterData])=>{var html="<div class='character'><span>" + character + "</span>"; Object.entries(characterData.poses).forEach( ([pose, poseData])=>{var outfitPath="characters/" + character + "/" + pose + "/outfits/" + poseData.default_outfit; html +="<a href='" + file_name + "?character=" + character + "&pose=" + pose + "'><div style='position:relative;text-align:center'><img class='characterImagesOutfit' src='" + outfitPath + "'/><div class='characterposename'>" + pose + "</div></div></a>";}); html +="</div>"; $("#imageList").append(html); window.history.pushState(scenario, scenario, file_name);});}else{var character=jsonData[selectedCharacter]; const out_start="characters/" + selectedCharacter + "/" + selectedPose + "/outfits/"; title.textContent=selectedCharacter + "_" + selectedPose; $("#backbutton").append("<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA4UlEQVR42mNgGAWjgAKQnZlZk5WV0TBwlmdm/AdjejsiKyMjB245vR0BtLwCaOFvNAd8z8pK9xgYn4McQ0fLR6LPszISsPj8c1ZWms1AWT6QPk9/P5A+pyrGV8Kl0NpyvA4ABvN6WluO1wENDQ0swGw3f8AcAAOZmRmzsWi8nZaWJkK3SgeHI+5nZGQo0K/my8zsxuaIrKwslYENiYyMx4MhJJ7npKeb0DEk0psxHZH+PictTYOeITF9wEMC1PxCdwQwdPrp2i4EWYiUIOeDCjC6t4zBIZGVMXlALB8FwwYAANeQ3GvAWTt8AAAAAElFTkSuQmCC' style='height: 25px;width: auto;padding-top: 10px;'>"); $("#backbutton").attr("href",file_name); var html="<div class='character2Container'>"; let outfits=Object.keys(character.poses[selectedPose].outfits); Object.entries(character.poses[selectedPose].outfits).forEach( ([index, outfit])=>{var outfitPath=out_start + outfit; var outfitName=outfit.split("/").pop(); html +="<div class='character2' style='min-width:" + (getTextWidth(outfitName, '16px "Times New Roman"') + 5) + "px;'><img class='characterImagesOutfit' src='" + outfitPath + "'/><span>" + outfit.split("/").pop() + "</span></div>";}); html +="</div>"; $("#imageList").append(html); html=""; var face_path="characters/" + selectedCharacter + "/" + selectedPose + "/faces/face/"; var total_images=character["poses"][selectedPose]["faces"]; var columns=parseInt(Math.sqrt(total_images.length)); var rows=parseInt(Math.ceil(total_images.length / columns)); const image_padding=10; html +="<canvas id='canvas'/><canvas>"; $("#imageList2").append(html); var canvas=document.getElementById("canvas"); var default_outfit=[].concat( out_start + character.poses[selectedPose].default_outfit ); if (character.poses[selectedPose].default_accessories.length > 0){for (src in character.poses[selectedPose].default_accessories){character.poses[selectedPose].default_accessories[src]=out_start + character.poses[selectedPose].default_accessories[src];}default_outfit=default_outfit.concat( character.poses[selectedPose].default_accessories );}const skip_num=default_outfit.length; character.poses[selectedPose].faces=default_outfit.concat( character.poses[selectedPose].faces ); var context=canvas.getContext("2d"); var left_crop=character.poses[selectedPose].default_left_crop; var right_crop=character.poses[selectedPose].default_right_crop; var top_crop=character.poses[selectedPose].default_top_crop; var nheight=parseInt( character.poses[selectedPose].max_face_height - top_crop + rect_height ); var nwidth=right_crop - left_crop; canvas.height=(nheight + image_padding) * rows; canvas.width=nwidth * columns; loadImages( face_path, skip_num, character.poses[selectedPose].faces, function (images){var current_column=0; var swidth=0; var sheight=0; for (const [index, element] of enumerate( character.poses[selectedPose].faces )){if (index < skip_num){continue;}if (index % 2==1){context.fillStyle="Black";}else{context.fillStyle="#121212";}context.fillRect( swidth, sheight, nwidth, nheight + image_padding ); for (var i=0; i < skip_num; i++){context.drawImage( images[i], left_crop, top_crop, nwidth, nheight, swidth, sheight, nwidth, nheight );}context.drawImage( images[index], left_crop, top_crop, nwidth, nheight, swidth, sheight, nwidth, nheight ); context.font="24pt Calibri"; txt_str=selectedPose + "_" + element .split("/") .pop() .split(".")[0] .replace("%23", "#"); context.fillStyle="white"; /*rect color*/ context.fillRect( swidth, sheight + nheight - rect_height, nwidth, rect_height + image_padding ); context.fillStyle="black"; /*text color*/ context.fillText( txt_str, (nwidth - getTextWidth(txt_str, context.font)) / 2 + swidth, sheight + nheight - (rect_height - image_padding) / 2 / 2 ); swidth +=nwidth; current_column++; if (current_column >=columns){sheight +=nheight + image_padding; swidth=0; current_column=0;}}}); html=""; $("#imageList2").append(html); document.title=scenario + " " + selectedCharacter + "_" + selectedPose;}$("body").bind("keydown", function (event){if (event.key=="Backspace" && selectedCharacter !=undefined){history.back();}else if (event.code=="Backslash"){disable_keys=!disable_keys; sessionStorage.setItem("disable_keys", disable_keys); $("#ToggleText").finish(); $("#ToggleText") .text( disable_keys ? "Keyboard shortcuts are disabled." : "Keyboard shortcuts are enabled." ) .fadeIn(1250) .delay(3000) .fadeOut(2000);}else if (disable_keys){}else if (event.key=="ArrowUp"){window.location.href=file_name;}else if (event.key=="ArrowRight"){if (selectedCharacter !=undefined && urlIndex==undefined){testIndex=testArray.findIndex( (element)=> element.toString()==[selectedCharacter, selectedPose].toString() ); testIndex=testIndex==indexLen ? 0 : testIndex + 1; window.location.href=file_name + "?" + makeCharURL(testArray[testIndex]);}else if (urlIndex==undefined){window.location.href=file_name + "?index=0";}else{window.location.href=file_name + "?index=" + (urlIndex - 1 + 2 > indexLen ? 0 : urlIndex - 1 + 2);}}else if (event.key=="ArrowLeft"){if (selectedCharacter !=undefined && urlIndex==undefined){testIndex=testArray.findIndex( (element)=> element.toString()==[selectedCharacter, selectedPose].toString() ); testIndex=testIndex==0 ? indexLen : testIndex - 1; window.location.href=file_name + "?" + makeCharURL(testArray[testIndex]);}else if (urlIndex==undefined){window.location.href=file_name + "?index=0";}else{window.location.href=file_name + "?index=" + (urlIndex - 1 < 0 ? indexLen : urlIndex - 1);}}}); </script></html>"""


def create_html(args, yml):
    """Main Method"""
    trim_images = partial(
        image_functions.trimImage,
        do_trim=args.trim,
        remove_empty=args.removeempty,
    )
    returnbbbox = partial(
        image_functions.return_bb_box,
        trim_RGB=args.trimrgb,
        remove_empty=args.removeempty,
    )
    remove_path_setup = partial(path_functions.remove_path, full_path=args.inputdir)

    chars: list[classes.Character] = []
    chars_with_poses = []
    for count, character_name in enumerate(
        (
            path
            for path in os.listdir(os.path.join(args.inputdir, "characters"))
            if os.path.isdir(os.path.join(args.inputdir, "characters", path))
        ),
        start=1,
    ):
        char_yml = {}
        if not args.bounds:
            print(f"Character {count}: {character_name}")
        try:
            with open(
                os.path.join(
                    args.inputdir, "characters", character_name, "character.yml"
                ),
                "r",
                encoding="utf8",
            ) as char_file:
                char_yml = yaml.safe_load(char_file)
        except FileNotFoundError:
            print(
                f"ERROR: Could not find character YML for {character_name}, please use the jsontoyaml utility by using -j or --jsontoyaml"
            )
            input("Press Enter to exit...")
            sys.exit()
        except yaml.YAMLError as error:
            print(
                f"ERROR: Character YML for {character_name}, could not be read.\nInfo: {error}"
            )
            input("Press Enter to exit...")
            sys.exit()

        pose_list = []
        for pose_path in [
            os.path.join(args.inputdir, "characters", character_name, path)
            for path in os.listdir(
                os.path.join(args.inputdir, "characters", character_name)
            )
            if os.path.isdir(
                os.path.join(args.inputdir, "characters", character_name, path)
            )
        ]:
            faces, outfits = path_functions.get_faces_and_outfits(pose_path)
            pose_letter = pose_path.split(os.sep)[-1]

            if not outfits:
                print(
                    f'Error: Character "{character_name}" with corresponding pose "{pose_letter}" does not contain outfits. Skipping.'
                )
                continue

            if not faces:
                print(
                    f'Error: Character "{character_name}" with corresponding pose "{pose_letter}" does not contain faces. Skipping now.'
                )
                continue

            if args.bounds:
                if args.regex is None or re.match(args.regex, character_name):
                    print(f"Character {character_name}: Pose {pose_letter}")
                    faces.sort(key=sort_functions.sort_by_numbers)

                    print("Faces")
                    for ipath in faces:
                        if bobobo := returnbbbox(ipath):
                            print(
                                classes.CropBox(*bobobo),
                                ipath.replace(
                                    os.path.join(
                                        args.inputdir,
                                        pose_path,
                                        "faces",
                                        "face",
                                        "",
                                        "",
                                    ),
                                    "",
                                ),
                            )

                    outfits.sort(key=sort_functions.face_sort_outtuple)
                    print()
                    print("Outfits")
                    for ipath in outfits:
                        if not isinstance(ipath, str):
                            ipath = ipath[0]
                        if bobobo := returnbbbox(ipath):
                            print(
                                classes.CropBox(*bobobo),
                                ipath.replace(
                                    os.path.join(
                                        args.inputdir,
                                        pose_path,
                                        "outfits",
                                        "",
                                    ),
                                    "",
                                ),
                            )

                    print()
                continue
            chars_with_poses.append([character_name, pose_letter])
            widths = []
            heights = []
            bboxs = []
            for width, height, bbox in map(trim_images, faces):
                widths.append(width)
                heights.append(height)
                bboxs.append(bbox)

            faces: list[classes.ImagePath] = list(
                map(
                    classes.ImagePath,
                    map(remove_path_setup, faces),
                    widths,
                    heights,
                    bboxs,
                )
            )
            faces.sort(key=sort_functions.face_sort_imp)

            widths.clear()
            heights.clear()
            bboxs.clear()
            for width, height, bbox in map(trim_images, outfits):
                widths.append(width)
                heights.append(height)
                bboxs.append(bbox)

            outfit_tuple = path_functions.get_default_outfit(
                outfits,
                char_data=char_yml,
                trim_images=trim_images,
                full_path=args.inputdir,
            )
            outfits: list[classes.ImagePath] = list(
                map(
                    classes.ImagePath,
                    map(remove_path_setup, outfits),
                    widths,
                    heights,
                    bboxs,
                )
            )

            outfits.sort(key=lambda x: x.path.split(os.sep)[-1].split(".")[0])
            pose_list.append(
                classes.Pose(args.inputdir, pose_letter, outfits, faces, *outfit_tuple)
            )

        if pose_list:
            chars.append(
                classes.Character(character_name, pose_list, args.maxheightmultiplier)
            )

    if args.bounds:
        sys.exit()

    if not chars:
        print(
            "No suitable characters exist. Read what each character is missing and add those to create html."
        )
        input("Press enter to exit...")
        sys.exit()

    print("Creating Html...")
    scenario_title = yml["title"]

    with open(
        os.path.join(args.inputdir, args.name), "w+", encoding="utf8"
    ) as html_file:
        html_file.write(html_snip1 + scenario_title)
        # Add Scenario Title before continue
        html_file.write(
            html_snip2.replace(
                "background-color: white; /*Background Replace*/",
                f"background-color: {args.backgroundcolor}; /*Background Replace*/",
            )
        )
        html_file.write(
            scenario_title
            + '"; var testArray=['
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


def main():
    parser = argparse.ArgumentParser(
        description="Makes an HTML file to browse a scenarios Characters"
    )

    parser.add_argument(
        "-i",
        "--inputdir",
        help="Give input directory to make HTML File for. In directory, there should be scenario.yml and a characters folder.",
        type=path_functions.dir_path,
        default=os.path.abspath(os.path.dirname(__file__))
        if os.path.isdir(os.path.dirname(__file__))
        else os.path.abspath(os.path.dirname(os.sep.join(__file__.split(os.sep)[:-1]))),
    )
    argroup = parser.add_argument_group("Return measurements.")
    argroup.add_argument(
        "-b",
        "--bounds",
        help="Don't make html File. Outbox boundary boxes(how it could be cropped to make smaller) for all files. ",
        action="store_true",
    )
    argroup.add_argument(
        "-re",
        "--regex",
        help="Filter search results by comparing character names to regex.",
        type=re.compile,
    )
    argroup.add_argument(
        "-tr",
        "--trimrgb",
        help="Instead of only checking the alpha layer, check the whole image as given. This can find different dimensions to add in trimming.",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--trim",
        help="Trim images while making html. This uses the same method as website/robotkyoko (if it's in the github)",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--removeempty",
        help="This removes any off accessories that are blank. Off accessories do not need to be present if they don't add anything",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--json2yaml",
        help="Skip HTML and instead convert JSON files to yaml. Will walk through the whole directory and convert any found. Requires YAML for this program to work",
        action="store_true",
    )
    parser.add_argument(
        "-fn",
        "--name",
        help="Change output file name. Default is 'index.html'",
        default="index.html",
    )

    argroup = parser.add_argument_group("CSS Options")
    argroup.add_argument(
        "-c1",
        "--color1",
        help="Change the first color of the expressions sheet generator. Accepts css color code or #RGB value. Default is black",
        default="Black",
    )
    argroup.add_argument(
        "-c2",
        "--color2",
        help="Change the second color of the expressions sheet generator. Accepts css color code or #RGB value. Default is #121212",
        default="#121212",
    )
    argroup.add_argument(
        "-tn",
        "--titlename",
        help="Use given name as Title (On main page) instead of the one from scenario.yaml.",
    )
    argroup.add_argument(
        "--transparent",
        help="Sets both colors to #00000000 (The extra 2 zero mean no alpha) making the squares transparent. ",
        action="store_true",
    )
    argroup.add_argument(
        "-bg",
        "--backgroundcolor",
        help="Changed the background of the whole webpage. This applies for both the main and character pages. Accepts css color code or #RGB value. Default white.",
        default="white",
    )
    argroup.add_argument(
        "-rbg",
        "--rectbackgroundcolor",
        help="Changed the background of the rectangles that hold the face reference on the character page. Accepts css color code or #RGB value. Default white.",
        default="white",
    )
    argroup.add_argument(
        "-txt",
        "--textcolor",
        help="Change the color of the text that says the face references on the character page. Accepts css color code or #RGB value. Default black.",
        default="black",
    )
    argroup.add_argument(
        "-mhm",
        "--maxheightmultiplier",
        help="Change the max face height multiplier. The bigger the number the more it will show of the outfit. Default is 1.07",
        type=float,
        default=1.07,
    )

    args = parser.parse_args()
    if args.json2yaml:
        print("Attempting to convert all JSON to YAML.")
        json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        sys.exit()
    yml_data: dict = {}
    if (
        not os.path.exists(os.path.join(args.inputdir, "scenario.yml"))
        and not args.bounds
    ):
        print(f"Error: Scenario.yaml does not exist in '{args.inputdir}'.")
        response = input(
            "Would you like to convert all JSON files to YAML? (Y|y for yes, anything else to exit): "
        )
        if response.lower() in ["y"]:
            json2yaml.json2yaml(argparse.Namespace(input_dir=args.inputdir))
        else:
            sys.exit()
    if not args.bounds:
        # Try to read YAML:
        with open(
            os.path.join(args.inputdir, "scenario.yml"), "r", encoding="utf8"
        ) as f:
            try:
                yml_data: dict = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(
                    f"Error: Could not read YAML data from scenario.yaml.\nInfo:{exc}"
                )
                input("Press Enter to exit...")
                sys.exit()

        if "title" not in yml_data:
            print("Error: Title Not found in YAML file.")
            input("Press Enter to exit...")
            sys.exit()

        if args.titlename:
            yml_data["title"] = args.titlename

    if "characters" not in os.listdir(args.inputdir):
        print(f"Error: Could not find 'characters' folder in {args.inputdir}")
        input("Press Enter to exit...")
        sys.exit()
    if args.transparent:
        args.color1 = "#00000000"
        args.color2 = "#00000000"
    create_html(args, yml_data)


if __name__ == "__main__":
    main()
