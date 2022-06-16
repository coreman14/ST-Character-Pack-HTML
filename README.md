# StHTMLHolyPack

This repo holds python scripts to create an html file similar to what was including in the [Holy Pack](https://www.tfgames.site/phpbb3/viewtopic.php?f=72&t=15688). Basic demo [here](https://coreman14.github.io/StHTMLHolyPack/).

I've made a few changes for usability (Keyboard shortcuts, expression sheets are made when the character page is opened rather than needed before hand).

I've also added a json2yaml converter and image trim utility which are taken from [Student Transfer Utils](https://utils.student-transfer.com).

## Changes from original

I found the html in [HolyPack](https://www.tfgames.site/phpbb3/viewtopic.php?f=72&t=15688) and whichever version I had was missing a few expression sheets. I decided that I could make a script that could generate these and do the expression sheet rendering in JS, meaning less work before and less parts needed.

Here are the changes I made to the look and how it works

General:

-   Add shortcuts to make browsing easier.
    -   Pipe | Backslash: Disable and enable these shortcuts.
    -   Up-arrow: Return to this page from any page.
    -   Backspace: Return to previous page. This shortcut will always be enabled.
    -   Left/Right Arrow: Navigate through characters in alphabetical order.
    -   Equals/Minus: Increase or decrease how many poses a character must have to be shown.
    -   Enter: Toggle outfit view. This view shows all the outfits for a character.
-   Added popup for shortcuts when hovering over the scenario name on any page.
-   Change how the default outfit was selected. It follows how expression sheets are made, but dress has the same priority as casual and it looks for underwear before nude.
-   On the main menu, if you were to change the filename from index.html to anything else, all the links would stop working. This is fixed.

Main Page:

-   Added a title for the main page.
-   Added pose names under each shown outfit on each of the main outfits.
-   Added pose filter. This lets you choose the minimum number of poses a character must have to show.

Character Page:

-   Added back button beside character name.
-   Now says character's name and pose above outfits.
-   Added backgrounds to expression sheet to be able to differ between faces. These can be disabled or changed to any 2 colors.
-   All expression sheets are generated within the html. You don't have to produce the expression sheets separately for this to work.

Outfit Page:

-   This is a new page that lets you see all of the characters outfits for each pose. Demo [here](https://coreman14.github.io/StHTMLHolyPack/?outfitview=1).
-   This was made so that if someone was looking for an outfit to add to an existing character, I matching the pose and outfit would be easier.

## Requirements (>=Python 3.8)

For the script to run, it requires both pillow, colorama and pyyaml. You can use `python -m pip install -r requirements` if you cloned the repository, or `python -m pip install pyyaml pillow colorama`.

If you downloaded the release that includes these packages, they will unzip to `zipapps_cache` when the script is called. They do not self remove but will be extracted from the file whenever ran.

## Usage

To use this util, clone the repo or download the pyz files from [GitHub](https://github.com/coreman14/StHTMLHolyPack).

There are 2 versions, one requires that pillow, colorama and pyyaml are installed beforehand, and one that unzips them from inside.

To run the script:

```bash
python STHtml_[nor|hasr].pyz
#Or if using the cloned version
python html_main.py
```

You can also change the input directory using -i so you don't have to move the script.

If it does not find scenario.yml, it will ask you if you want to convert all JSON to YAML. This will do every JSON in the scenario (characters too).

You can also run this by doing -j on start. You will have to run it again without -j to generate the HTML.

## Arguments

This program includes many customizations you can make to the look of the html file. From changing the title, adding a background image or changing any number of colors, you can make it look as you want without touching the code.

You can also use a config file to avoid having to add the options each time.

For a full up to date list run the file with `-h` which will print all options. You can then add any to the command line.

To use a config file instead, download the [Example.ini](Example.ini) from the repo. This has all currently available options so you can uncomment and start changing.

To use the file, add `-c <REPLACE_WITH_FILENAME>` to your the command line and it will read your settings from it.

## Other features (Using these disables the HTML output)

Using -b, it will output the size of all the images within the characters folders. This size is the smallest size that the image could become. It will then highlight the largest image. You can also use -re to filter the results. This accepts and uses the value as regex, but it will work if you just put a single name.

Note: This was made because some faces contained some not erased pixels that was ruining the trim_image process.

## Notes

If you are trimming images, do not stop the program. Doing so can corrupt your images.

If your characters feature any transparency, do not use the trim image function. PIL does not play well with transparency.

There are some files that pillow does not like read. When this happens, it should output the full path to the file

```js
Error: cannot identify image file "C:\\StudentTransfer\\A deal with the devil\\characters\\corneliasaya\\a\\faces\\face\\0.png". Please convert the file to png or webp.
```

When this happens, bring image into a photo editor and save it. Or if there is more than one, run the files through a converter.

I use [XNConvert](https://www.xnview.com/en/xnconvert/link), but there are many options. If you happen to do this, you can also convert the files to WEBP as they take up less space. Google has [utilities](https://developers.google.com/speed/webp/docs/precompiled) for doing from the command line.

The same process above is used when expression sheets are generated. So, they need to be fixed.
