"""
Things to do:
    1. Find way to do updates (Show what was added if the pack is updated).
        A. Find character array to find new poses/characters.
        B. The character array must have a tru/false after the pose number if it is new.
        C. Read the json and then check for new outfits.

"""


import os
import sys
from functools import partial

from colorama import init

import args_functions
import classes
import image_functions
import main_functions
import path_functions

html_snip1 = r"""<!DOCTYPE html><html lang="en"> <head> <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no"><title>"""  # Add Scenario Title before continue
html_snip2 = r''' Viewer</title> <script src="https://code.jquery.com/jquery-3.5.0.js"></script> <style>body{text-align: center;}#canvas{padding-top: 10px;}.outerDiv{position: relative; text-align: center}.characterswrap{display: flex; flex-wrap: wrap; justify-content: center; /* here we just put the only child div to the center */ background-color: White; /*Background Replace*/}.charactersrow{display: flex; flex-grow: 1; flex-direction: column; justify-content: center; /* here we just put the only child div to the center */}.character{margin: 20px 10px 0 0; padding: 0px 0px 14px 0px; display: flex; flex-wrap: wrap; justify-content: center; /* here we just put the only child div to the center */ border-radius: 0.5px; border-color: grey; border-style: solid; position: relative;}.character2{margin: 10px 10px 0 0; padding: 0px 0px; height: 220px; display: flex; flex-wrap: nowrap; justify-content: center; /* here we just put the only child div to the center */ border-radius: 0.5px; border-color: grey; border-style: solid; position: relative;}.character2Container{display: flex; flex-wrap: wrap; justify-content: center; /* here we just put the only child div to the center */}.character span{position: absolute; background-color: grey; color: White; width: 100%;}.character2 span{position: absolute; background-color: grey; color: White; width: 100%;}.characterImagesOutfit{height: 200px; position: relative; padding-top: 20px; left: 0px;}.characterposename{position: absolute; left: 50%; transform: translate(-50%, -21%); z-index: 31; background-color: grey; color: White; width: 100%;}#ToggleText{/*Stolen From W3*/ width: 160px; position: fixed; top: 10px; right: 12px; font-size: 24px; display: none;}.popup{background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 8px 0; margin-left: -80px; z-index: 1;}#HelpText{position: absolute; top: 7%; width: 450px; padding: 10px 15px; padding-bottom: 15px; margin-left: auto; margin-right: auto; left: 0; right: 0; visibility: hidden; z-index: 32;}#HelpTitle{font-size: 24px; display: block;}.HelpLine{display: block;}#backbutton{display: inline-block; vertical-align: sub; padding-right: 3px;}#title{display: inline-block;}</style> </head> <body> <span id="ToggleText" class="popup"></span> <span id="HelpText" class="popup" ><span id="HelpTitle">Character Viewer Shortcuts</span> <br><span class="HelpLine" >Pipe | BackSlash: Disable and enable these shortcuts.</span > <br><span class="HelpLine" >UpArrow: Return to this page from any page.</span > <br><span class="HelpLine" >Backspace: Return to previous page. This shortcut will always be enabled.</span > <br><span class="HelpLine" >Left/Right Arrow: Navigate through characters in alphabetical order.</span > <br><span class="HelpLine" id="PoseHelp" >Equals/Minus: Increase or decrease how many poses a character must have to be shown.</span ><br><span class="HelpLine" id="OutfitHelp" >Enter: Toggle outfit view. This view shows all the outfits for a character. Current status: </span> </span> <a id="backbutton">Back</a> <h1 id="title" onmouseover="popouthelp()" onmouseout="hidehelp()"> Text </h1> <div id="imageList" class="characterswrap"></div><div id="imageList2"></div><script>/* jshint esversion: 11, -W083*/ function popouthelp(){var popup=document.getElementById("HelpText"); popup.style.visibility="visible";}function hidehelp(){var popup=document.getElementById("HelpText"); popup.style.visibility="hidden";}function parseTextBool(textToParse){return textToParse=="true" ? true : false;}function getTextWidth(text, font){const canvas=getTextWidth.canvas || (getTextWidth.canvas=document.createElement("canvas")); const context=canvas.getContext("2d"); context.font=font; const metrics=context.measureText(text); return metrics.width;}function loadImages(extra_path, index_start, sources, callback){var images={}; var loadedImages=0; var numImages=0; for (var _ in sources){numImages++;}for (var src in sources){images[src]=new Image(); images[src].onload=function (){if (++loadedImages >=numImages){callback(images);}}; if (src >=index_start){images[src].src=extra_path + sources[src];}else{images[src].src=sources[src];}}}function makeCharURL(namepose, urlToMend){var splitted=namepose.toString().split(","); urlToMend.searchParams.set("character", splitted[0]); urlToMend.searchParams.set("pose", splitted[1]);}String.prototype.rsplit=function (sep, maxsplit=0){var split=this.split(sep); return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat( split.slice(-maxsplit) ) : split;}; var disable_keys=parseTextBool( sessionStorage.getItem("disable_keys") ); if (disable_keys==false){sessionStorage.setItem("disable_keys", false); disable_keys=false;}$("#ToggleText").text( disable_keys ? "Keyboard shortcuts are disabled." : "Keyboard shortcuts are enabled." ); var scenario="'''
# Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
html_snip3 = r"""$("#backbutton").empty(); indexLen=characterArray.length - 1; file_name=location.pathname.split("/").pop() || "."; var max_poses=Math.max(...characterArray.map((o)=> o[2])); var static_url_addons=""; function* enumerate(it, start=0){let i=start; for (const x of it) yield [i++, x];}const urlParams=new URLSearchParams(window.location.search); var newURL=new URL( location.protocol + "//" + location.host + location.pathname ); var homeURL=new URL( location.protocol + "//" + location.host + location.pathname ); var pose_filter=urlParams.get("pcount") && /^\d+$/.test(urlParams.get("pcount")) ? parseInt(urlParams.get("pcount")) : 1; if (pose_filter > max_poses){pose_filter=max_poses;}var outfit_filter=urlParams.get("outfitview") && /^[1]$/.test(urlParams.get("outfitview")) ? true : false; if (outfit_filter){newURL.searchParams.set("outfitview", "1"); homeURL.searchParams.set("outfitview", "1"); document .getElementById("imageList") .classList.replace("characterswrap", "charactersrow"); scenario +=" Outfit View";}if (pose_filter > 1){newURL.searchParams.set("pcount", pose_filter); homeURL.searchParams.set("pcount", pose_filter);}document.getElementById("PoseHelp").innerHTML +=" Current filter: >=" + pose_filter; document.getElementById("OutfitHelp").innerHTML +=outfit_filter ? "On" : "Off"; var urlIndex=urlParams.get("index"); if (urlIndex > indexLen || urlIndex < 0){urlIndex=undefined;}var selectedCharacter=urlParams.get("character") ? urlParams.get("character") : undefined; var selectedPose=urlParams.get("pose") ? urlParams.get("pose") : undefined; if ( selectedCharacter==undefined || selectedPose==undefined || urlIndex !=undefined ){selectedCharacter=undefined; selectedPose=undefined;}else if ( selectedCharacter !=undefined && (!(selectedCharacter in jsonData) || !(selectedPose in jsonData[selectedCharacter].poses)) ){selectedCharacter=undefined; selectedPose=undefined;}else{newURL.searchParams.set("character", selectedCharacter); newURL.searchParams.set("pose", selectedPose);}if (urlIndex !=undefined){selectedCharacter=characterArray[urlIndex][0]; selectedPose=characterArray[urlIndex][1]; newURL.searchParams.set("index", urlIndex);}window.history.replaceState(scenario, scenario, newURL.toString()); var rect_height=32; if (selectedCharacter==undefined){title.textContent=scenario; var url2=new URL(newURL.toString()); Object.entries(jsonData).forEach( ([character, characterData])=>{if ( pose_filter > 1 && Object.keys(characterData.poses).length < pose_filter ){return;}url2.searchParams.set("character", character); var html=""; charElement=document.createElement("div"); if (outfit_filter){Object.entries(characterData.poses).forEach( ([pose, poseData])=>{var outfitPath=poseData.outfit_path + poseData.default_outfit; var outfits=poseData.outfits.map( (outfit)=> [ poseData.outfit_path + outfit, outfit.split("/").pop(),] ); url2.searchParams.set("pose", pose); characterDiv=document.createElement("div"); characterDiv.classList.add("character"); span=document.createElement("span"); span.textContent=character + "_" + pose; characterDiv.appendChild(span); for (const outfit of outfits){charLink=document.createElement("a"); charLink.href=url2.toString(); characterDiv.appendChild(charLink); outerDiv=document.createElement("div"); outerDiv.classList.add("outerDiv"); charLink.appendChild(outerDiv); img=document.createElement("img"); img.src=outfit[0]; img.alt=outfit[1].rsplit(".")[0]; img.classList.add("characterImagesOutfit"); outerDiv.appendChild(img); nameDiv=document.createElement("div"); nameDiv.classList.add("characterposename"); nameDiv.textContent=outfit[1].rsplit(".")[0]; outerDiv.appendChild(nameDiv);}charElement.appendChild(characterDiv);}); $("#imageList").append(charElement);}else{characterDiv=document.createElement("div"); characterDiv.classList.add("character"); span=document.createElement("span"); span.textContent=character; characterDiv.appendChild(span); Object.entries(characterData.poses).forEach( ([pose, poseData])=>{url2.searchParams.set("pose", pose); var outfitPath=poseData.outfit_path + poseData.default_outfit; charLink=document.createElement("a"); charLink.href=url2.toString(); characterDiv.appendChild(charLink); outerDiv=document.createElement("div"); outerDiv.classList.add("outerDiv"); charLink.appendChild(outerDiv); img=document.createElement("img"); img.src=outfitPath; img.alt=poseData.default_outfit.rsplit(".")[0]; img.classList.add("characterImagesOutfit"); outerDiv.appendChild(img); nameDiv=document.createElement("div"); nameDiv.classList.add("characterposename"); nameDiv.textContent=pose; outerDiv.appendChild(nameDiv);}); charElement.appendChild(characterDiv); $("#imageList").append(charElement);}});}else{var character=jsonData[selectedCharacter]; const out_start=character.poses[selectedPose].outfit_path; title.textContent=selectedCharacter + "_" + selectedPose; $("#backbutton").append( "<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA4UlEQVR42mNgGAWjgAKQnZlZk5WV0TBwlmdm/AdjejsiKyMjB245vR0BtLwCaOFvNAd8z8pK9xgYn4McQ0fLR6LPszISsPj8c1ZWms1AWT6QPk9/P5A+pyrGV8Kl0NpyvA4ABvN6WluO1wENDQ0swGw3f8AcAAOZmRmzsWi8nZaWJkK3SgeHI+5nZGQo0K/my8zsxuaIrKwslYENiYyMx4MhJJ7npKeb0DEk0psxHZH+PictTYOeITF9wEMC1PxCdwQwdPrp2i4EWYiUIOeDCjC6t4zBIZGVMXlALB8FwwYAANeQ3GvAWTt8AAAAAElFTkSuQmCC' style='height: 25px;width: auto;padding-top: 10px;'>" ); $("#backbutton").attr("href", homeURL.toString()); characterContainer=document.createElement("div"); characterContainer.classList.add("character2Container"); var html="<div class='character2Container'>"; let outfits=Object.keys( character.poses[selectedPose].outfits ); Object.entries(character.poses[selectedPose].outfits).forEach( ([index, outfit])=>{var outfitPath=out_start + outfit; var outfitName=outfit.split("/").pop(); var char2=document.createElement("div"); char2.classList.add("character2"); char2.style.minWidth=getTextWidth(outfitName, '16px "Times New Roman"') + 5 + "px"; outImg=document.createElement("img"); outImg.src=outfitPath; outImg.alt=outfitName.rsplit(".")[0]; outImg.classList.add("characterImagesOutfit"); char2.appendChild(outImg); outName=document.createElement("span"); outName.textContent=outfit.split("/").pop().rsplit(".")[0]; char2.appendChild(outName); characterContainer.appendChild(char2);}); $("#imageList").append(characterContainer); newCanvas=document.createElement("canvas"); newCanvas.id="canvas"; $("#imageList2").append(newCanvas); html=""; var face_path=character.poses[selectedPose].face_path; var total_images=character.poses[selectedPose].faces.length; var columns=parseInt(Math.sqrt(total_images)); var rows=parseInt(Math.ceil(total_images / columns)); const image_padding=10; var canvas=document.getElementById("canvas"); var default_outfit=[].concat( out_start + character.poses[selectedPose].default_outfit ); if ( character.poses[selectedPose].default_accessories.length > 0 ){for (var src in character.poses[selectedPose] .default_accessories){character.poses[selectedPose].default_accessories[src]=out_start + character.poses[selectedPose].default_accessories[ src];}default_outfit=default_outfit.concat( character.poses[selectedPose].default_accessories );}const skip_num=default_outfit.length; character.poses[selectedPose].faces=default_outfit.concat( character.poses[selectedPose].faces ); var context=canvas.getContext("2d"); var left_crop=character.poses[selectedPose].default_left_crop; var right_crop=character.poses[selectedPose].default_right_crop; var top_crop=character.poses[selectedPose].default_top_crop; var nheight=parseInt( character.poses[selectedPose].max_face_height - top_crop + rect_height ); var nwidth=right_crop - left_crop; canvas.height=(nheight + image_padding) * rows; canvas.width=nwidth * columns; loadImages( face_path, skip_num, character.poses[selectedPose].faces, function (images){var current_column=0; var swidth=0; var sheight=0; for (const [index, element] of enumerate( character.poses[selectedPose].faces )){if (index < skip_num){continue;}if (index % 2==1){context.fillStyle="Black"; /*Color1 replace*/}else{context.fillStyle="#121212"; /*Color2 replace*/}context.fillRect( swidth, sheight, nwidth, nheight + image_padding ); for (var i=0; i < skip_num; i++){context.drawImage( images[i], left_crop, top_crop, nwidth, nheight, swidth, sheight, nwidth, nheight );}context.drawImage( images[index], left_crop, top_crop, nwidth, nheight, swidth, sheight, nwidth, nheight ); context.font="24pt Calibri"; txt_str=selectedPose + "_" + element .split("/") .pop() .split(".")[0] .replace("%23", "#"); context.fillStyle="White"; /*rect color*/ context.fillRect( swidth, sheight + nheight - rect_height, nwidth, rect_height + image_padding ); context.fillStyle="Black"; /*text color*/ context.fillText( txt_str, (nwidth - getTextWidth(txt_str, context.font)) / 2 + swidth, sheight + nheight - (rect_height - image_padding) / 2 / 2 ); swidth +=nwidth; current_column++; if (current_column >=columns){sheight +=nheight + image_padding; swidth=0; current_column=0;}}}); document.title=scenario + " " + selectedCharacter + "_" + selectedPose;}$("body").bind("keydown", function (event){var char_index; var replaceUrl; if ( event.key=="Backspace" && selectedCharacter !=undefined ){history.back();}else if (event.code=="Backslash"){disable_keys=!disable_keys; sessionStorage.setItem("disable_keys", disable_keys); $("#ToggleText").finish(); $("#ToggleText") .text( disable_keys ? "Keyboard shortcuts are disabled." : "Keyboard shortcuts are enabled." ) .fadeIn(1250) .delay(3000) .fadeOut(2000);}else if (disable_keys){}else if ( event.key=="ArrowUp" && selectedCharacter !=undefined ){window.location.href=homeURL.toString();}else if (event.key=="ArrowRight"){if ( selectedCharacter !=undefined && urlIndex==undefined ){newIndex=characterArray.findIndex((element)=> element .toString() .includes( [selectedCharacter, selectedPose].toString() ) ); do{newIndex=newIndex==indexLen ? 0 : newIndex + 1;}while ( pose_filter > 1 && characterArray[newIndex][2] < pose_filter ); makeCharURL(characterArray[newIndex], newURL); window.location.href=newURL.toString();}else if (urlIndex==undefined){char_index=0; while ( pose_filter > 1 && characterArray[char_index][2] < pose_filter ){char_index++;}newURL.searchParams.set("index", char_index); window.location.href=newURL.toString();}else{do{urlIndex=urlIndex - 1 + 2 > indexLen ? 0 : urlIndex - 1 + 2;}while ( pose_filter > 1 && characterArray[urlIndex][2] < pose_filter ); newURL.searchParams.set("index", urlIndex); window.location.href=newURL.toString();}}else if (event.key=="ArrowLeft"){if ( selectedCharacter !=undefined && urlIndex==undefined ){newIndex=characterArray.findIndex((element)=> element .toString() .includes( [selectedCharacter, selectedPose].toString() ) ); do{newIndex=newIndex==0 ? indexLen : newIndex - 1;}while ( pose_filter > 1 && characterArray[newIndex][2] < pose_filter ); makeCharURL(characterArray[newIndex], newURL); window.location.href=newURL.toString();}else if (urlIndex==undefined){char_index=indexLen; while ( pose_filter > 1 && characterArray[char_index][2] < pose_filter ){char_index--;}newURL.searchParams.set("index", char_index); window.location.href=newURL.toString();}else{do{urlIndex=urlIndex - 1 < 0 ? indexLen : urlIndex - 1;}while ( pose_filter > 1 && characterArray[urlIndex][2] < pose_filter ); newURL.searchParams.set("index", urlIndex); window.location.href=newURL.toString();}}else if (event.code=="Minus"){old_pose_filter=pose_filter; pose_filter=pose_filter - 1 < 1 ? 1 : pose_filter - 1; newURL.searchParams.set("pcount", pose_filter); if (old_pose_filter==pose_filter){return;}else if (title.textContent==scenario){window.location.href=newURL.toString();}else{replaceUrl=new URL(window.location.href); if (static_url_addons.includes("pcount")){static_url_addons=static_url_addons.replace( "pcount=" + old_pose_filter, "pcount=" + pose_filter );}else{static_url_addons=static_url_addons + "&pcount=" + pose_filter;}if (pose_filter !=old_pose_filter){p_help=document.getElementById("PoseHelp"); p_help.textContent=p_help.textContent.replace( ">=" + old_pose_filter, ">=" + pose_filter );}replaceUrl.searchParams.set("pcount", pose_filter); window.history.replaceState( scenario, scenario, replaceUrl.toString() );}}else if (event.code=="Equal"){old_pose_filter=pose_filter; pose_filter=pose_filter + 1 > max_poses ? max_poses : pose_filter + 1; newURL.searchParams.set("pcount", pose_filter); if (old_pose_filter==pose_filter){return;}else if (title.textContent==scenario){window.location.href=newURL.toString();}else{replaceUrl=new URL(window.location.href); if (static_url_addons.includes("pcount")){static_url_addons=static_url_addons.replace( "pcount=" + old_pose_filter, "pcount=" + pose_filter );}else{static_url_addons=static_url_addons + "&pcount=" + pose_filter;}if (pose_filter !=old_pose_filter){p_help=document.getElementById("PoseHelp"); p_help.textContent=p_help.textContent.replace( ">=" + old_pose_filter, ">=" + pose_filter );}replaceUrl.searchParams.set("pcount", pose_filter); window.history.replaceState( scenario, scenario, replaceUrl.toString() );}}else if (event.code=="Enter"){old_outfit_filter=outfit_filter ? 1 : 0; old_outfit_word=outfit_filter ? "On" : "Off"; outfit_filter=!outfit_filter; new_outfit_filter=outfit_filter ? 1 : 0; new_outfit_word=outfit_filter ? "On" : "Off"; newURL.searchParams.set("outfitview", new_outfit_filter); if (title.textContent==scenario){window.location.href=newURL.toString();}else{replaceUrl=new URL(window.location.href); if (static_url_addons.includes("outfitview")){static_url_addons=static_url_addons.replace( "outfitview=" + old_outfit_filter, "outfitview=" + new_outfit_filter );}else{static_url_addons=static_url_addons + "&outfitview=" + new_outfit_filter;}o_help=document.getElementById("OutfitHelp"); o_help.textContent=o_help.textContent.replace( "Current status: " + old_outfit_word, "Current status: " + new_outfit_word ); replaceUrl.searchParams.set( "outfitview", new_outfit_filter ); window.history.replaceState( scenario, scenario, replaceUrl.toString() );}}}); </script> </body></html>"""
init(convert=True)
html_snips = (html_snip1, html_snip2, html_snip3)


def main_loop(args, yml):
    """Main Method"""
    trim_images = partial(
        image_functions.trimImage,
        do_trim=args.trim,
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
        if not args.bounds:
            print(f"Character {count}: {character_name}")

        pose_list = []
        # default_outfit = False
        total_poses = len(
            [
                path
                for path in os.listdir(
                    os.path.join(args.inputdir, "characters", character_name)
                )
                if os.path.isdir(
                    os.path.join(args.inputdir, "characters", character_name, path)
                )
            ]
        )
        for pose_path in [
            os.path.join(args.inputdir, "characters", character_name, path)
            for path in os.listdir(
                os.path.join(args.inputdir, "characters", character_name)
            )
            if os.path.isdir(
                os.path.join(args.inputdir, "characters", character_name, path)
            )
        ]:
            pose_letter = pose_path.split(os.sep)[-1]

            if args.bounds:
                main_functions.bounds(
                    args.regex,
                    pose_path,
                    character_name,
                    args.skip_if_same,
                    args.skip_faces,
                    args.skip_outfits,
                )

            else:
                faces, outfits = path_functions.get_faces_and_outfits(
                    pose_path, character_name
                )
                # default_outfit = default_outfit or check_for_default_outfit(outfits)
                if None in [faces, outfits]:
                    continue
                chars_with_poses.append([character_name, pose_letter, total_poses])
                if char_pose := main_functions.create_character(
                    trim_images,
                    remove_path_setup,
                    character_name,
                    (pose_path, args.inputdir),
                    args.outfitprio,
                ):
                    pose_list.append(
                        classes.Pose(args.inputdir, pose_letter, *char_pose)
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
        sys.exit(1)

    print("Creating Html...")
    scenario_title = yml["title"]

    main_functions.create_html_file(
        args,
        scenario_title,
        html_snips,
        (chars_with_poses, chars),
    )


def main():
    args = args_functions.get_args()
    yml_data = args_functions.setup_args(args)
    main_loop(args, yml_data)


if __name__ == "__main__":
    main()
