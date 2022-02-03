# StHTMLHolyPack

This repo holds python scripts to create an html similar to what was including in the holy pack. Basic demo [here](https://coreman14.github.io/StHTMLHolyPack/)

I've made a few changes for usability (Keyboard shortcuts, expression sheets are made in js rather than needed before hand).

I've also added a json2yaml converter and and image trim utility which are taken from [Student Transfer Utils](https://utils.student-transfer.com).

## Changes from original

I found the html in [HolyPack](https://www.tfgames.site/phpbb3/viewtopic.php?f=72&t=15688) and whichever version I got was missing a few expression sheets. I decided on that I could make a script that could generate these and do the expression sheet rendering in JS. So, here are the changes I made to the look and how it works.

General:

-   Add shortcuts to make browsing easier.
    -   Left and right goes between characters.
    -   Up goes back to the main page
    -   Backspace works like the back button in browser.
    -   All shortcuts except Backspace can be disabled and enabled with the Pipe/Backslash key (under Backspace).
-   Added popup for shortcuts when hovering over name on any page.
-   Change how the default outfit was selected. It follows how expression sheets are made, but dress has the same priority as casual and it looks for underwear before nude.
-   On the main menu, if you were to change the filename from index.html to anything else, all the links would stop working. This is fixed.

Main Page:

-   Added a title for the main page.
-   Added pose names under each shown outfit on each of the main outfits.

Character Page:

-   Added back button beside character name.
-   Now says character's name and pose above outfits.
-   Added backgrounds to expression sheet to be able to differ between faces. These can be disabled or changed to any 2 colors.
-   All expression sheets are generated within the html. You don't have to produce the expression sheets separately for this to work.

## Requirements (>=Python 3.8)

For the script to run, it requires both pillow, colorama and pyyaml. You can use `python -m pip install -r requirements` if you cloned the repository, or `python -m pip install pyyaml pillow colorama`.

If you downloaded the release that includes these packages, they will unzip to `zipapps_cache` when the script is called. They do not self remove but will be extracted from the file whenever ran.

## Usage

To use this util, clone the repo or download the pyz files from [GitHub](https://github.com/coreman14/StHTMLHolyPack) as I have yet to grasp how gitlab expects me to do releases.

There are 2 versions, one requires that pillow, colorama and pyyaml are installed beforehand, and one that unzips them from inside.

To run the script:

```bash
python STHtml_[nor|hasr].pyz
#or if using the cloned version
python html_main.py
```

If it does not find scenario.yml, It will ask you if you want to convert all JSON to YAML. This will do every JSON in the scenario (characters too).

You can also run this by doing -j on start. You will have to run it again without -j to generate the HTML.

## Notes

If you are trimming images, do not stop the program. Doing so can corrupt your images.

There are some files that pillow does not like read. When this happens, it should output the full path to the file

```js
Error: cannot identify image file "C:\\StudentTransfer\\A deal with the devil\\characters\\corneliasaya\\a\\faces\\face\\0.png". Please convert the file to png or webp.
```

When this happens, bring image into a photo editor and save it. Or if there is more than one, run the files through a converter.

I use [XNConvert](https://www.xnview.com/en/xnconvert/link), but there are many options. If you happen to do this, you can also convert the files to WEBP as they take up less space. Google has [utilities](https://developers.google.com/speed/webp/docs/precompiled) for doing from the command line.

If you run into this problem, I more or less use the same process for reading images as when expression sheets are generated. So I'd recommend fixing it is you want either.
