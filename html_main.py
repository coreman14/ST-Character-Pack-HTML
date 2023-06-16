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

html_snip1 = r""" <!DOCTYPE html>  <html lang="en">  <head>  <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" >  <title>"""
# Add Scenario Title before continue
html_snip2 = r''' Viewer</title>  <style>  body {  text-align: center;  }  #imageList2{  padding-top: 10px;  }  .outerDiv{  position: relative;  text-align: center;  }  .characterswrap{  display: flex;  flex-wrap: wrap;  justify-content: center; /* here we just put the only child div to the center */  background-color: White; /*Background Replace*/  }  .charactersrow{  display: flex;  flex-grow: 1;  flex-direction: column;  justify-content: center; /* here we just put the only child div to the center */  }  .character{  margin: 20px 10px 0 0;  padding: 0px 0px 14px 0px;  display: flex;  flex-wrap: wrap;  justify-content: center; /* here we just put the only child div to the center */  border-radius: 0.5px;  border-color: grey;  border-style: solid;  position: relative;  }  .character2{  margin: 10px 10px 0 0;  padding: 0px 0px;  height: 220px;  display: flex;  flex-wrap: nowrap;  justify-content: center; /* here we just put the only child div to the center */  border-radius: 0.5px;  border-color: grey;  border-style: solid;  position: relative;  }  .character2Container{  display: flex;  flex-wrap: wrap;  justify-content: center; /* here we just put the only child div to the center */  }  .character span {  position: absolute;  background-color: grey;  color: White;  width: 100%;  }  #changeBox {  position: absolute;} .character2 span {  position: absolute;  background-color: grey;  color: White;  width: 100%;  }  .characterImagesOutfit{  height: 200px;  position: relative;  padding-top: 20px;  left: 0px;  }  .characterImagesOutfitA{  position: absolute;  padding-top: 20px;  left: 0px;  }  .characterposename{  position: absolute;  left: 50%;  transform: translate(-50%, -21%);  z-index: 31;  background-color: grey;  color: White;  width: 100%;  }  #ToggleText{  /*Stolen From W3*/  width: 160px;  position: fixed;  top: 10px;  right: 18px;  font-size: 24px;  opacity: 0;  }  #ToggleText.fade{  /*Stolen From W3*/  opacity: 0;  animation: fade 6.25s linear;  }  @keyframes fade {  0%,  100% {  opacity: 0;  }  20%,  68% {  opacity: 1;  }  }  .rotateUp,  .rotateDown{  transition: all 0.75s ease-out;  position: relative;  }  .rotateUp{  transform: rotateX(180deg);  }  .rotateDownNoAnimation{  position: relative;  }  .hidden{  max-height: 0px;  }  .hidden,  .unhidden{  transition: all 0.75s ease-out;  overflow-y: hidden;  }  .unhiddennoanimation{  overflow-y: hidden;  }  #favDialog{  background-color: #8d8d8d;  color: #000000;  text-align: center;  border-radius: 15px;  padding: 8px 8px;  overflow: hidden;  border: #fff;  border-width: 6px;  border-style: solid;  max-width: 80%;  top: -230px;  }  #favDialog::backdrop {  background-color: rgba(0, 0, 0, 0.8);  }  #HelpTitle{  font-size: 48px;  display: block;  color: #fff;  }  .HelpLine{  display: block;  font-size: 24px;  }  .characterPageHelp{  display: block;  font-size: 24px;  color: #fff;  }  .boldenText{  font-weight: bold;  }  #backbutton{  display: inline-block;  vertical-align: sub;  padding-right: 3px;  height: 25px;  width: auto;  padding-top: 10px;  }  #infoButton{  display: inline-block;  vertical-align: sub;  padding-right: 3px;  height: 25px;  width: auto;  padding-top: 10px;  }  #title{  display: inline-block;  }  #titleExtra{  display: inline-block;  }  .invertInfo{  filter: invert(0.6);  }  #hideButton{  padding-top: 2px;  }  </style>  </head>  <body>  <span id="ToggleText" class="popup"></span>  <dialog id="favDialog" onclick="event.target==this && this.close()">  <span  ><span id="HelpTitle">Character Viewer Shortcuts</span> <br>  <span class="HelpLine"><span class="boldenText">Backspace:</span> Return to previous page. </span><br>  <span class="HelpLine"  ><span class="boldenText">BackSlash:</span> Disable and enable the shortcuts below.</span  ><br><span class="HelpLine"  ><span class="boldenText">UpArrow:</span> Return to the character selection page.</span  >  <br><span class="HelpLine"  ><span class="boldenText">Left/Right Arrow:</span> Navigate through characters in alphabetical  order.</span  ><br><span class="HelpLine" id="PoseHelp"  ><span class="boldenText">Equals/Minus:</span> Increase or decrease how many poses a character must  have to be shown. This affects both the main character page and the left/right navigation.</span  ><br><span class="HelpLine" id="OutfitHelp"  ><span class="boldenText">Enter:</span> Toggle outfit view. On the main character page, this will  show all outfits instead of one per pose. Current status: </span  ><br><br id="renameCharacterBR1" ><span  class="HelpLine characterPageHelp"  id="renameCharacter1"  ></span  ><br id="renameCharacterBR2" ><span class="HelpLine characterPageHelp" id="renameCharacter2"></span  ></span>  </dialog>  <a  id="backbutton"  onmouseover="this.classList.add('invertInfo')"  onmouseout="this.classList.remove('invertInfo')"  >Back</a  >  <h1  id="titleExtra"  onmouseover="this.classList.add('invertInfo')"  onmouseout="this.classList.remove('invertInfo')"  href="#titleExtra"  >  Text  </h1>  <h1 id="title" onmouseover="this.classList.add('invertInfo')" onmouseout="this.classList.remove('invertInfo')">  Text  </h1>  <div  id="infoButton"  onclick="popouthelp()"  onmouseover="this.classList.add('invertInfo')"  onmouseout="this.classList.remove('invertInfo')"  >  <img  src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAINSURBVFhHxZe7SgQxFIZH8VLYWNhY2AjiAyh4wcJCtLIRBF9AfAltBPUNxJfQXlAUtfRSC2IvCFoJ2uj/rfllZd2ZZNm4H/zJMJucc3ZykjlTdJqu0MfQJy1JC9KENCYNSvAqPUjX0ol0LH1IbQEn29Kz9BkpxjLHAbbMmvQk2fCttCnNS8NSbxDX3OM3xng8c7GRTI90INnQpTQnxcLYC8nzsYXNKBh4KDHxTVqXUnLFMGdDwga2sBkVhP/5izTDjSZsSWdBq9xoAjacP9guhfXyPy9zDnsSY1FZADAt+Uk0zQky1gnHY68iJQBgORiLjz93B9uGASRczJoPSCNBMWDzXMIHvn7BIeN1Ssn2VGYlfOALnz8sS/zAHs7NnYQvfBbdNILjFY5CH0NqDhi2IyzSOADOdrgKfU7sY5LGAfBigfvQ58Q+RmkcgLcFyZEb+6j5dAAdwwHwPoeh0OfEPmo+HQDFBIyHPif28UjjAKhkIOchZOzjhsYBnIZ+JfQ5sQ/Kth/6pdSjuJWDqOEo9hN4l/a/L4tdqZUCpAps7nxf1nw1FK0dfx1DfUFCEVFGSgBTUmVBYlySsU5lQcQGgHPnV2VJBrFFaVUAzGmpKAUG+kkgKhkyOBbGUqx6PraindfDejkx0b99mNRDxmb7NEvZ7/44pZKhmOB9bge8WDjbOV454dr6cZqRovgCfJ2xnbN9A/cAAAAASUVORK5CYII="  title="Shortcuts and Info"  alt="Info button"  >  </div>  <div id="hideDiv" class="unhidden"><div id="imageList" class="characterswrap"></div></div>  <div id="hideButton">  <img  src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAUBAMAAADSJhiXAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAGUExURWBgYP///w85EMkAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAXSURBVCjPY8ADGAVxgFGpYSSFCzAwAABZWxzDrkDX/gAAAABJRU5ErkJggg=="  id="changeBox"  alt="Box for arrow">  <img  src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAUCAYAAAAgCAWkAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGhSURBVFhH7dY7KIVhHMfx41rkFhIGZHAZiBRKGWQwyEgGJZeiJCUiRgaLZMMmg41MCpsMisXAhEKJEiH3+P6U+vc66OBclF99hvOe8z7P/7zP+1xc//kj6cUMkl8/BWaCUYhZtOuCu6ThCs84RwdCEEhJwSgeoDr3kYh36YJ+YG2gBP5OFFpxCFvfJVrgNpXYgb3hCROIhz9SgVXYmjQyulaMTxOOAVzDNnCKJgTBF8nGNB5h69hFIzxKBhZgGxI9kXx4K3EYxAlsv2cYQSy+nRrswTasYdZEjMFvphZbsH3dYx55+JVEYhh3sB0doQ4/TREW4XyltADpYXolOViG7VCWkAVPo2V1HBew7ekhdSMaXk891KEt4BZDiMBX0SLShgPYNjTyk8iET6P5MgZ3q001Pko51uG8bwVl8GsKsAZbmGjSpuMtqdBRyTnvtLg0QPMyIKLzUjO0F9lCtVf1ow86ItnvbqBFJQkBmQRMQacGW7jTHHLhqw34RynFJpx/YhtVCMOfSig6oddLS28PvDovfDHMOrYrx9Do/OfruFwvjpSeW9iun1cAAAAASUVORK5CYII="  class="rotateUp"  id="changeArrow"  alt="Arrow for hiding">  </div>  <div id="imageList2"></div>  <script>  /* jshint esversion: 11, -W083*/ var new_name="";  function popouthelp() {  var dialog=document.getElementById("favDialog");  dialog.showModal();  }  function parseTextBool(textToParse) {  return textToParse=="true" ? true : false;  }  function getTextWidth(text, font) {  const canvas=getTextWidth.canvas || (getTextWidth.canvas=document.createElement("canvas"));  const context=canvas.getContext("2d");  context.font=font;  const metrics=context.measureText(text);  return metrics.width;  }  function compareDefaultAcc(a, b) {  a=parseInt(a[1]);  b=parseInt(b[1]);  if (a < b) {  return -1;  }  if (a > b) {  return 1;  }  return 0;  }  function loadImages(extra_path, index_start, sources, callback) {  var images={};  var loadedImages=0;  var numImages=0;  for (var _ in sources) {  numImages++;  }  for (var src in sources) {  images[src]=new Image();  images[src].onload=function () {  if (++loadedImages >= numImages) {  callback(images);  }  };  if (src >= index_start) {  images[src].src=extra_path + sources[src];  } else {  images[src].src=sources[src];  }  }  }  function makeCharURL(namepose, urlToMend) {  var splitted=namepose.toString().split(",");  urlToMend.searchParams.set("character", splitted[0]);  urlToMend.searchParams.set("pose", splitted[1]);  }  function getLayeringOrderOutfits(out_start, outfit, outfits) {  var default_outfit=[].concat(out_start + outfit);  if (outfits.length > 0) {  var negativeOffset=0;  outfits.sort(compareDefaultAcc);  for (var src in outfits) {  outfits[src][0]=out_start + outfits[src][0];  if (parseInt(outfits[src][1]) < 0) {  default_outfit.splice(negativeOffset, 0, [].concat(outfits[src][0], outfits[src][2]));  negativeOffset++;  } else {  default_outfit.push([].concat(outfits[src][0], outfits[src][2]));  }  }  }  return default_outfit;  }  function getLayeringOrder(out_start, outfit, character_obj) {  var default_outfit=[].concat(out_start + outfit);  if (character_obj.default_accessories.length > 0) {  var negativeOffset=0;  character_obj.default_accessories.sort(compareDefaultAcc);  for (var src in character_obj.default_accessories) {  character_obj.default_accessories[src][0]= out_start + character_obj.default_accessories[src][0];  if (parseInt(character_obj.default_accessories[src][1]) < 0) {  default_outfit.splice(  negativeOffset,  0,  [].concat(  character_obj.default_accessories[src][0],  character_obj.default_accessories[src][2]  )  );  negativeOffset++;  } else {  default_outfit.push(  [].concat(  character_obj.default_accessories[src][0],  character_obj.default_accessories[src][2]  )  );  }  }  }  return default_outfit;  }  function getLayeringOrderFlat(out_start, outfit, character_obj) {  var default_outfit=getLayeringOrder(out_start, outfit, character_obj);  for (var i=0; i < default_outfit.length; i++) {  if (Array.isArray(default_outfit[i])) {  default_outfit[i]=default_outfit[i][0];  }  }  return default_outfit;  }  function outputOutfitCopyString(outfit) {  if (selectedCharacter != null) {  navigator.clipboard.writeText("outfit " + body_name + " " + outfit);  document.getAnimations().forEach((animation) => {  animation.cancel();  });  document.querySelector("#ToggleText").textContent='Copied outfit "' + outfit + '" to clipboard';  setTimeout(function () {  document.querySelector("#ToggleText").classList.add("fade");  }, 6.25);  document.querySelector("#ToggleText").classList.remove("fade");  }  }  function outputFaceCopyString(face_name) {  if (selectedCharacter != null) {  navigator.clipboard.writeText("show " + body_name + " " + face_name);  document.getAnimations().forEach((animation) => {  animation.cancel();  });  document.querySelector("#ToggleText").textContent='Copied face "' + face_name + '" to clipboard';  setTimeout(function () {  document.querySelector("#ToggleText").classList.add("fade");  }, 6.25);  document.querySelector("#ToggleText").classList.remove("fade");  }  }  function makeNewBody(new_name=undefined, reset=false) {  title.title="Click to change body";  titleExtra.title="Click to reset body";  if (new_name==undefined) {  new_name=prompt("Enter new body name");  }  if (new_name==undefined || new_name=="") {  return;  }  if (new_name != selectedCharacter) {  titleExtra.textContent="(" + new_name + ") ";  newURL.searchParams.set("body_name", new_name);  body_name=new_name;  } else {  titleExtra.textContent="";  if (reset) {  newURL.searchParams.delete("body_name");  }  body_name=selectedCharacter;  }  replaceUrl=new URL(window.location.href);  if (!newURL.searchParams.has("body_name")) {  static_url_addons=static_url_addons.replace("body_name=" + body_name, "");  replaceUrl.searchParams.delete("body_name");  } else {  if (static_url_addons.includes("body_name")) {  static_url_addons=static_url_addons.replace(  "body_name=" + body_name,  "body_name=" + new_name  );  } else {  static_url_addons=static_url_addons + "body_name=" + new_name;  }  replaceUrl.searchParams.set("body_name", new_name);  }  window.history.replaceState(scenario, scenario, replaceUrl.toString());  }  function changeToFaceNumbering(element) {  name=String(element.name);  body=name.rsplit("_", 1)[0];  pose=name.rsplit("_", 1)[1];  name_element=element.querySelector(".characterposename");  name_element.textContent=String(jsonData[body].poses[pose].faces.length) + " Faces";  }  function changeToPose(element) {  name=String(element.name);  pose=name.rsplit("_", 1)[1];  name_element=element.querySelector(".characterposename");  name_element.textContent=String(pose);  }    function manipImageList() {  elDiv=document.querySelector("#hideDiv");  if (elDiv.classList.contains("hidden")) {  elDiv.classList.add("unhidden");  elDiv.classList.remove("hidden");  document.querySelector("#changeArrow").classList.remove("rotateDown");  document.querySelector("#changeArrow").classList.remove("rotateDownNoAnimation");  document.querySelector("#changeArrow").classList.add("rotateUp");  sessionStorage.setItem("areOutfitsHidden", "false");  elDiv.style.maxHeight=elDiv.getAttribute("currentHeight");  calculateImageListMaxHeight(false); /*We have to redo it for some reason for everything to work*/  } else {  elDiv.style.maxHeight=elDiv.getAttribute("currentHeight");  elDiv.classList.add("hidden");  elDiv.classList.remove("unhidden");  elDiv.classList.remove("unhiddennoanimation");  elDiv.style.maxHeight="";  document.querySelector("#changeArrow").classList.add("rotateDown");  document.querySelector("#changeArrow").classList.remove("rotateUp");  sessionStorage.setItem("areOutfitsHidden", "true");  }  }  function calculateImageListMaxHeight(assignClasses=true) {  elDiv=document.querySelector("#hideDiv");  elDiv.setAttribute("currentHeight", elDiv.scrollHeight + "px");  if (elDiv.classList.contains("unhidden") || elDiv.classList.contains("unhiddennoanimation")) {  if (assignClasses===true) {  document.querySelector("#hideDiv").classList.remove("unhidden");  document.querySelector("#hideDiv").classList.add("unhiddennoanimation");  }  elDiv.style.maxHeight=elDiv.scrollHeight + "px";  }  }  String.prototype.rsplit=function (sep, maxsplit=0) {  var split=this.split(sep);  return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;  };  var disable_keys=parseTextBool(sessionStorage.getItem("disable_keys"));  if (disable_keys==false) {  sessionStorage.setItem("disable_keys", false);  disable_keys=false;  }  document.querySelector("#ToggleText").textContent=disable_keys  ? "Keyboard shortcuts are disabled."  : "Keyboard shortcuts are enabled.";  var scenario="'''
# Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
html_snip3 = r""" document.querySelector("#backbutton").replaceChildren();  titleExtra.textContent="";  indexLen=characterArray.length - 1;  file_name=location.pathname.split("/").pop() || ".";  var max_poses=Math.max(...characterArray.map((o) => o[2]));  var static_url_addons="";  function* enumerate(it, start=0) {  let i=start;  for (const x of it) yield [i++, x];  }  const urlParams=new URLSearchParams(window.location.search);  var newURL=new URL(location.protocol + "//" + location.host + location.pathname);  var homeURL=new URL(location.protocol + "//" + location.host + location.pathname);  var pose_filter= urlParams.get("pcount") && /^\d+$/.test(urlParams.get("pcount"))  ? parseInt(urlParams.get("pcount"))  : 1;  if (pose_filter > max_poses) {  pose_filter=max_poses;  }  var outfit_filter=urlParams.get("outfitview") && /^[1]$/.test(urlParams.get("outfitview")) ? true : false;  if (outfit_filter) {  newURL.searchParams.set("outfitview", "1");  homeURL.searchParams.set("outfitview", "1");  document.getElementById("imageList").classList.replace("characterswrap", "charactersrow");  scenario += " Outfit View";  }  if (pose_filter > 1) {  newURL.searchParams.set("pcount", pose_filter);  homeURL.searchParams.set("pcount", pose_filter);  }  document.getElementById("PoseHelp").innerHTML += " Current filter: >=" + pose_filter;  document.getElementById("OutfitHelp").innerHTML += outfit_filter ? "On" : "Off";  var urlIndex=urlParams.get("index");  if (urlIndex > indexLen || urlIndex < 0) {  urlIndex=undefined;  }  var selectedCharacter=urlParams.get("character") ? urlParams.get("character") : undefined;  var selectedPose=urlParams.get("pose") ? urlParams.get("pose") : undefined;  var body_name=urlParams.get("body_name") ? urlParams.get("body_name") : undefined;  if (selectedCharacter==undefined || selectedPose==undefined || urlIndex != undefined) {  selectedCharacter=undefined;  selectedPose=undefined;  body_name=undefined;  } else if (  selectedCharacter != undefined &&  (!(selectedCharacter in jsonData) || !(selectedPose in jsonData[selectedCharacter].poses))  ) {  selectedCharacter=undefined;  selectedPose=undefined;  body_name=undefined;  } else {  newURL.searchParams.set("character", selectedCharacter);  newURL.searchParams.set("pose", selectedPose);  if (body_name != undefined) {  newURL.searchParams.set("body_name", body_name);  }  }  if (urlIndex != undefined) {  selectedCharacter=characterArray[urlIndex][0];  selectedPose=characterArray[urlIndex][1];  newURL.searchParams.set("index", urlIndex);  newURL.searchParams.set("body_name", body_name);  }  window.history.replaceState(scenario, scenario, newURL.toString());  var rect_height=32;  if (selectedCharacter==undefined) {  document.querySelector("#title").onmouseover="";  document.querySelector("#renameCharacterBR1").remove();  document.querySelector("#renameCharacterBR2").remove();  document.querySelector("#hideButton").remove();  title.textContent=scenario;  var url2=new URL(newURL.toString());  Object.entries(jsonData).forEach(([character, characterData]) => {  if (pose_filter > 1 && Object.keys(characterData.poses).length < pose_filter) {  return;  }  url2.searchParams.set("character", character);  var html="";  charElement=document.createElement("div");  if (outfit_filter) {  Object.entries(characterData.poses).forEach(([pose, poseData]) => {  var outfits=poseData.outfits.map((outfit) => [  outfit[0],  outfit[0].split("/").pop(),  outfit[1],  ]);  url2.searchParams.set("pose", pose);  characterDiv=document.createElement("div");  characterDiv.classList.add("character");  span=document.createElement("span");  span.textContent=character + "_" + pose;  characterDiv.appendChild(span);  for (const outfit of outfits) {  charLink=document.createElement("a");  charLink.href=url2.toString();  characterDiv.appendChild(charLink);  outerDiv=document.createElement("div");  outerDiv.classList.add("outerDiv");  outerDiv.title=outfit[0];  charLink.appendChild(outerDiv);  var default_outfit=getLayeringOrderOutfits(  poseData.outfit_path,  outfit[0],  outfit[2]  );  for (var i of default_outfit) {  img=document.createElement("img");  var image_path;  if (Array.isArray(i)) {  image_path=i[0];  img.style.height=i[1] + "px";  img.classList.add("characterImagesOutfitA");  } else {  image_path=i;  img.classList.add("characterImagesOutfit");  }  img.src=image_path;  img.alt=image_path.rsplit("/")[0].rsplit(".")[0];  outerDiv.appendChild(img);  }  nameDiv=document.createElement("div");  nameDiv.classList.add("characterposename");  nameDiv.textContent=outfit[1].rsplit(".")[0];  outerDiv.appendChild(nameDiv);  }  charElement.appendChild(characterDiv);  });  document.querySelector("#imageList").append(charElement);  } else {  characterDiv=document.createElement("div");  characterDiv.classList.add("character");  span=document.createElement("span");  span.textContent=character;  characterDiv.appendChild(span);  Object.entries(characterData.poses).forEach(([pose, poseData]) => {  url2.searchParams.set("pose", pose);  var outfitPath=poseData.outfit_path + poseData.default_outfit;  var default_outfit=getLayeringOrder(  poseData.outfit_path,  poseData.default_outfit,  poseData  );  charLink=document.createElement("a");  charLink.href=url2.toString();  characterDiv.appendChild(charLink);  outerDiv=document.createElement("div");  outerDiv.classList.add("outerDiv");  outerDiv.title=poseData.default_outfit;  charLink.appendChild(outerDiv);  for (var i of default_outfit) {  img=document.createElement("img");  var image_path;  if (Array.isArray(i)) {  image_path=i[0];  img.style.height=i[1] + "px";  img.classList.add("characterImagesOutfitA");  } else {  image_path=i;  img.classList.add("characterImagesOutfit");  }  img.src=image_path;  img.alt=image_path.rsplit("/")[0].rsplit(".")[0];  outerDiv.appendChild(img);  }  nameDiv=document.createElement("div");  nameDiv.classList.add("characterposename");  nameDiv.textContent=pose;  outerDiv.name=character + "_" + pose;  outerDiv.addEventListener("mouseover", function (evt) {  changeToFaceNumbering(this);  });  outerDiv.addEventListener("mouseout", function (evt) {  changeToPose(this);  });  outerDiv.appendChild(nameDiv);  });  charElement.appendChild(characterDiv);  document.querySelector("#imageList").appendChild(charElement);  }  });  } else {  show_outfits=parseTextBool(sessionStorage.getItem("areOutfitsHidden"));  title.textContent=selectedCharacter + "_" + selectedPose;  document.querySelector("#renameCharacter1").textContent= "Clicking on the outfits or faces will copy the text to change to that outfit or the show statement for face to your clipboard";  document.querySelector("#renameCharacter2").textContent= "Clicking on the page title will allow you to enter a new character for the copied text";  new_name=sessionStorage.getItem("body_name");  var character=jsonData[selectedCharacter];  const out_start=character.poses[selectedPose].outfit_path;  title.addEventListener("click", function () {  makeNewBody();  });  titleExtra.addEventListener("click", function () {  makeNewBody(selectedCharacter, true);  });  makeNewBody(body_name ? body_name : selectedCharacter);  hideButton.addEventListener("click", function () {  manipImageList();  });  backButton=document.createElement("img");  backButton.title="Back to Main page";  backButton.src= "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA4UlEQVR42mNgGAWjgAKQnZlZk5WV0TBwlmdm/AdjejsiKyMjB245vR0BtLwCaOFvNAd8z8pK9xgYn4McQ0fLR6LPszISsPj8c1ZWms1AWT6QPk9/P5A+pyrGV8Kl0NpyvA4ABvN6WluO1wENDQ0swGw3f8AcAAOZmRmzsWi8nZaWJkK3SgeHI+5nZGQo0K/my8zsxuaIrKwslYENiYyMx4MhJJ7npKeb0DEk0psxHZH+PictTYOeITF9wEMC1PxCdwQwdPrp2i4EWYiUIOeDCjC6t4zBIZGVMXlALB8FwwYAANeQ3GvAWTt8AAAAAElFTkSuQmCC";  document.querySelector("#backbutton").append(backButton);  document.querySelector("#backbutton").href=homeURL.toString();  characterContainer=document.createElement("div");  characterContainer.classList.add("character2Container");  var html="<div class='character2Container'>";  let outfits=Object.keys(character.poses[selectedPose].outfits);  Object.entries(character.poses[selectedPose].outfits).forEach(([index, outfit]) => {  var outfitName=outfit[0].split("/").pop().rsplit(".")[0];  var default_outfit=getLayeringOrderOutfits(out_start, outfit[0], outfit[1]);  var char2=document.createElement("div");  char2.classList.add("character2");  char2.title=outfit[0];  char2.addEventListener("click", function () {  outputOutfitCopyString(outfitName);  });  char2.style.minWidth=getTextWidth(outfitName, '16px "Times New Roman"') + 5 + "px";  for (var i of default_outfit) {  img=document.createElement("img");  var image_path;  if (Array.isArray(i)) {  image_path=i[0];  img.style.height=i[1] + "px";  img.classList.add("characterImagesOutfitA");  } else {  image_path=i;  img.classList.add("characterImagesOutfit");  }  img.src=image_path;  img.alt=image_path.rsplit("/")[0].rsplit(".")[0];  char2.appendChild(img);  }  outName=document.createElement("span");  outName.textContent=outfitName;  char2.appendChild(outName);  characterContainer.appendChild(char2);  });  document.querySelector("#imageList").append(characterContainer);    html="";  var face_path=character.poses[selectedPose].face_path;  const image_padding=10;  var default_outfit=getLayeringOrderFlat(  out_start,  character.poses[selectedPose].default_outfit,  character.poses[selectedPose]  );  const skip_num=default_outfit.length;  character.poses[selectedPose].faces=default_outfit.concat(character.poses[selectedPose].faces);  var left_crop=character.poses[selectedPose].default_left_crop;  var right_crop=character.poses[selectedPose].default_right_crop;  var top_crop=character.poses[selectedPose].default_top_crop;  var nheight=parseInt(character.poses[selectedPose].max_face_height - top_crop + rect_height);  var nwidth=right_crop - left_crop;  loadImages(face_path, skip_num, character.poses[selectedPose].faces, function (images) {  for (const [index, element] of enumerate(character.poses[selectedPose].faces)) {  if (index < skip_num) {  continue;  }  txt_str=selectedPose + "_" + element.split("/").pop().split(".")[0].replace("%23", "#");  newCanvas=document.createElement("canvas");  newCanvas.id=txt_str;  newCanvas.title=txt_str;  newCanvas.height=nheight + image_padding;  newCanvas.width=nwidth;  newCanvas.classList.add("faceCanvas");  newCanvas.addEventListener("click", function (evt) {  outputFaceCopyString(this.id);  });  context=newCanvas.getContext("2d");  document.querySelector("#imageList2").append(newCanvas);  if (index % 2==1) {  context.fillStyle="Black"; /*Color1 replace*/  } else {  context.fillStyle="#121212"; /*Color2 replace*/  }  context.fillRect(0, 0, nwidth, nheight + image_padding);  for (var i=0; i < skip_num; i++) {  context.drawImage(images[i], left_crop, top_crop, nwidth, nheight, 0, 0, nwidth, nheight);  }  context.drawImage(images[index], left_crop, top_crop, nwidth, nheight, 0, 0, nwidth, nheight);  context.font="24pt Calibri";  context.fillStyle="White";  /*rect color*/ context.fillRect(  0,  0 + nheight - rect_height,  nwidth,  rect_height + image_padding  );  context.fillStyle="Black";  /*text color*/ context.fillText(  txt_str,  (nwidth - getTextWidth(txt_str, context.font)) / 2 + 0,  0 + nheight - (rect_height - image_padding) / 2 / 2  );  }  });  document.title=scenario + " " + selectedCharacter + "_" + selectedPose;  hideDiv.setAttribute("currentHeight", hideDiv.scrollHeight + "px");  hideDiv.style.maxHeight=hideDiv.scrollHeight + "px";  if (show_outfits) {  hideDiv.style.maxHeight="0px";  hideDiv.classList.add("hidden");  hideDiv.classList.remove("unhidden");  document.querySelector("#changeArrow").classList.remove("rotateUp");  document.querySelector("#changeArrow").classList.add("rotateDownNoAnimation");  }  }  window.addEventListener("resize", (event) => {  calculateImageListMaxHeight();  });  window.addEventListener("load", (event) => {  calculateImageListMaxHeight();  });  document.querySelector("body").addEventListener("keydown", (event) => {  var char_index;  var replaceUrl;  if (event.key=="Backspace") {  history.back();  } else if (event.code=="Backslash") {  disable_keys=!disable_keys;  sessionStorage.setItem("disable_keys", disable_keys);  document.getAnimations().forEach((animation) => {  animation.cancel();  });  document.querySelector("#ToggleText").textContent=disable_keys  ? "Keyboard shortcuts are disabled."  : "Keyboard shortcuts are enabled.";  setTimeout(function () {  document.querySelector("#ToggleText").classList.add("fade");  }, 6.25);  document.querySelector("#ToggleText").classList.remove("fade");  } else if (event.code=="KeyB") {  makeNewBody();  } else if (event.code=="KeyR") {  makeNewBody(selectedCharacter, true);  } else if (event.code=="KeyH" && selectedCharacter != undefined) {  manipImageList();  } else if (event.code=="Enter" && selectedCharacter==undefined) {  old_outfit_filter=outfit_filter ? 1 : 0;  old_outfit_word=outfit_filter ? "On" : "Off";  outfit_filter=!outfit_filter;  new_outfit_filter=outfit_filter ? 1 : 0;  new_outfit_word=outfit_filter ? "On" : "Off";  newURL.searchParams.set("outfitview", new_outfit_filter);  if (title.textContent==scenario) {  window.location.href=newURL.toString();  } else {  replaceUrl=new URL(window.location.href);  if (static_url_addons.includes("outfitview")) {  static_url_addons=static_url_addons.replace(  "outfitview=" + old_outfit_filter,  "outfitview=" + new_outfit_filter  );  } else {  static_url_addons=static_url_addons + "&outfitview=" + new_outfit_filter;  }  o_help=document.getElementById("OutfitHelp");  o_help.textContent=o_help.textContent.replace(  "Current status: " + old_outfit_word,  "Current status: " + new_outfit_word  );  replaceUrl.searchParams.set("outfitview", new_outfit_filter);  window.history.replaceState(scenario, scenario, replaceUrl.toString());  }  } else if (disable_keys) {  } else if (event.key=="ArrowUp" && selectedCharacter != undefined) {  window.location.href=homeURL.toString();  } else if (event.key=="ArrowRight") {  if (selectedCharacter != undefined && urlIndex==undefined) {  newIndex=characterArray.findIndex((element) =>  element.toString().includes([selectedCharacter, selectedPose].toString())  );  do {  newIndex=newIndex==indexLen ? 0 : newIndex + 1;  } while (pose_filter > 1 && characterArray[newIndex][2] < pose_filter);  makeCharURL(characterArray[newIndex], newURL);  window.location.href=newURL.toString();  } else if (urlIndex==undefined) {  char_index=0;  while (pose_filter > 1 && characterArray[char_index][2] < pose_filter) {  char_index++;  }  newURL.searchParams.set("index", char_index);  window.location.href=newURL.toString();  } else {  do {  urlIndex=urlIndex - 1 + 2 > indexLen ? 0 : urlIndex - 1 + 2;  } while (pose_filter > 1 && characterArray[urlIndex][2] < pose_filter);  newURL.searchParams.set("index", urlIndex);  window.location.href=newURL.toString();  }  } else if (event.key=="ArrowLeft") {  if (selectedCharacter != undefined && urlIndex==undefined) {  newIndex=characterArray.findIndex((element) =>  element.toString().includes([selectedCharacter, selectedPose].toString())  );  do {  newIndex=newIndex==0 ? indexLen : newIndex - 1;  } while (pose_filter > 1 && characterArray[newIndex][2] < pose_filter);  makeCharURL(characterArray[newIndex], newURL);  window.location.href=newURL.toString();  } else if (urlIndex==undefined) {  char_index=indexLen;  while (pose_filter > 1 && characterArray[char_index][2] < pose_filter) {  char_index--;  }  newURL.searchParams.set("index", char_index);  window.location.href=newURL.toString();  } else {  do {  urlIndex=urlIndex - 1 < 0 ? indexLen : urlIndex - 1;  } while (pose_filter > 1 && characterArray[urlIndex][2] < pose_filter);  newURL.searchParams.set("index", urlIndex);  window.location.href=newURL.toString();  }  } else if (event.code=="Minus" && selectedCharacter==undefined) {  old_pose_filter=pose_filter;  pose_filter=pose_filter - 1 < 1 ? 1 : pose_filter - 1;  newURL.searchParams.set("pcount", pose_filter);  if (old_pose_filter==pose_filter) {  return;  } else if (title.textContent==scenario) {  window.location.href=newURL.toString();  } else {  replaceUrl=new URL(window.location.href);  if (static_url_addons.includes("pcount")) {  static_url_addons=static_url_addons.replace(  "pcount=" + old_pose_filter,  "pcount=" + pose_filter  );  } else {  static_url_addons=static_url_addons + "&pcount=" + pose_filter;  }  if (pose_filter != old_pose_filter) {  p_help=document.getElementById("PoseHelp");  p_help.textContent=p_help.textContent.replace(">=" + old_pose_filter, ">=" + pose_filter);  }  replaceUrl.searchParams.set("pcount", pose_filter);  window.history.replaceState(scenario, scenario, replaceUrl.toString());  }  } else if (event.code=="Equal" && selectedCharacter==undefined) {  old_pose_filter=pose_filter;  pose_filter=pose_filter + 1 > max_poses ? max_poses : pose_filter + 1;  newURL.searchParams.set("pcount", pose_filter);  if (old_pose_filter==pose_filter) {  return;  } else if (title.textContent==scenario) {  window.location.href=newURL.toString();  } else {  replaceUrl=new URL(window.location.href);  if (static_url_addons.includes("pcount")) {  static_url_addons=static_url_addons.replace(  "pcount=" + old_pose_filter,  "pcount=" + pose_filter  );  } else {  static_url_addons=static_url_addons + "&pcount=" + pose_filter;  }  if (pose_filter != old_pose_filter) {  p_help=document.getElementById("PoseHelp");  p_help.textContent=p_help.textContent.replace(">=" + old_pose_filter, ">=" + pose_filter);  }  replaceUrl.searchParams.set("pcount", pose_filter);  window.history.replaceState(scenario, scenario, replaceUrl.toString());  }  }  });  </script>  </body>  </html> """
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
                for path in os.listdir(os.path.join(args.inputdir, "characters", character_name))
                if os.path.isdir(os.path.join(args.inputdir, "characters", character_name, path))
            ]
        )
        for pose_path in [
            os.path.join(args.inputdir, "characters", character_name, path)
            for path in os.listdir(os.path.join(args.inputdir, "characters", character_name))
            if os.path.isdir(os.path.join(args.inputdir, "characters", character_name, path))
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
                faces, outfits = path_functions.get_faces_and_outfits(pose_path, character_name)
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
                    pose_list.append(classes.Pose(args.inputdir, pose_letter, *char_pose))

        if pose_list:
            chars.append(classes.Character(character_name, pose_list, args.maxheightmultiplier))

    if args.bounds:
        sys.exit()

    if not chars:
        print("No suitable characters exist. Read what each character is missing and add those to create html.")
        input("Press enter to exit...")
        sys.exit(1)

    print("Creating Html...")
    scenario_title = yml["title"]

    if args.onlyjson:
        main_functions.create_js(
            args,
            (chars_with_poses, chars),
        )
    elif args.splitfiles:
        main_functions.create_html_file(
            args,
            scenario_title,
            html_snips,
            (chars_with_poses, chars),
            split_files=True,
        )
        main_functions.create_js(
            args,
            (chars_with_poses, chars),
        )

    else:
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
