# [ST-Character-Pack-HTML](https://github.com/coreman14/ST-Character-Pack-HTML)

Inspired by the [Holy Pack](https://www.tfgames.site/phpbb3/viewtopic.php?f=72&t=15688), ST-Character-Pack-HTML will create an HTML file for a scenario or character pack to replace having to browse using the in game sprite viewer or File explorer. Basic demo [here](https://coreman14.github.io/ST-Character-Pack-HTML/).

## Features

-   No prep work is required. Just create the file and go.
-   No additional files will be created during the process. The HTML file generated is the only file made.
-   Betters the browsing experience. With this added, the user will not have to load into ST to see all the characters, or navigate it with a file explorer.
-   The HTML is written in pure HTML, JavaScript and CSS so it can be easily customized.
-   No dependencies are used, so the file can be used with no internet connection.
-   Stats about the character are shown on the main page, allowing users to better find a character that fits their needs.
-   Show's all expression's on the characters page, so it can be a replacement for an expression sheet.
-   Expression sheet can be toggled to show blush faces.
-   Includes keyboard shortcuts for navigation that can be turned off.

## Running the program

I've made a small website that when you upload the ZIP to, will generate the HTML file inside the zip. You can find it [here](https://html.coreman14.com/). It does not handle big files well, so please download the tool if the upload is taking a while.

For Windows, just download the [EXE](https://github.com/coreman14/ST-Character-Pack-HTML/releases/latest/download/HTMLCreator.exe) from the [Latest release](https://github.com/coreman14/ST-Character-Pack-HTML/releases/latest), place it into the scenario folder you wish to create the HTML for, next to the `scenario.yml` file, and run it by double-clicking or from the command line.

On Mac, Unix and other OSes, install Python 3.10 or greater, then download one of the PYZ files from the [Latest release](https://github.com/coreman14/ST-Character-Pack-HTML/releases/latest) and install the requirements.

The script requires a few additional packages for processing images and YAML files. If you do not want to install these requirements locally, download the `STHtml_includes_requirements.pyz` file. When ran this will unzip the requirements needed.

If you are ok with installing these requirements to your machine, download the `STHtml.pyz` then run the command `python -m pip install pyyaml pillow colorama`. After it finishes installing, you can run the PYZ file.

## Arguments

For an up-to-date list, run the file with `-h` which will print all options. You can then add any to the command line.

Certain arguments will be recognized and used if written in `scenario.yml` file.
Those arguments are listed below:

| Argument              | Description                                                                                                                                                                                              | Command line example              | YML entry example                                    |
| :-------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ---------------------------------------------------- |
| Outfit priority       | Change the list of outfits that is used to determine the default outfit on the main page. This completely replaces the default outfit priority order. In scenario.yml, this must be a list.              | `-op gym swimsuit casual uniform` | `outfitpriority: [ gym, swimsuit, casual, uniform ]` |
| Max height Multiplier | Change how much of the body is shown on the expression sheet. The bigger the number, the lower the expression sheet will show. Default is 1.07                                                           | `-mhm 1.4`                        | `maxheightmultiplier: 1.4`                           |
| Outfit height         | Change the height of the outfits shown on the default page. Default value is 200                                                                                                                         | `-oh 300`                         | `outfitheight: 300`                                  |
| Accessory Height      | Change the height of the accessory viewer. Default value is 400                                                                                                                                          | `-ah 300`                         | `accessoryheight: 300`                               |
| Favorite Icon         | Change the icon that is displayed in the tab bar in a browser. Recommended size is a square image around 32x32. If you are using backslashes `\` in the YML file, do not use quotes or double them `\\`. | `-fi assets/icon.png`             | `favicon: assets/icon.png`                           |

## Other features and uses

### Bounds

The idea behind bounds is that sometimes, small invisible pixel's may not be fully clear from an image. When this happens, the file size may appear bigger, and it may result in the HTML file being bigger than needed. The idea of bounds is to give the smallest size that the image can be cropped to.

Example:

```properties
HTMLCreator.exe -b

Faces:
 Actual Image Size 463x206 0.webp
 Actual Image Size 463x206 1.webp
 Actual Image Size 500x206 2.webp
```

The last image, `2.webp` would be highlighted as it is different, which may be causing problems.

### JSON Converter

This is taken from the [Student Transfer Utils](https://utils.student-transfer.com).

This will walk through the input directory looking for any files that end in `json`. When found it will read the file, then output the contents in a `yml` file and remove the JSON file.

This can be run using by adding `-cj` when running the program. This will not output an HTML file after it is completed and must be run again.

### Image trimmer

This is taken from the [Student Transfer Utils](https://utils.student-transfer.com). When ran this will remove as much of the image as possible to save space.

This only removes it from the bottom and right part of the image, so it will not affect the character itself.

If your characters feature any transparency, do not use the trim image function. PIL does not play well with transparency.

To use the trimmer, add `-t` when running the program

## Notes

When running the program, do not stop the program. Doing so can corrupt your images.

There are some files that pillow does not like to read. When this happens, it should output the full path to the file

```js
Error: cannot identify image file "C:\\StudentTransfer\\A deal with the devil\\characters\\corneliasaya\\a\\faces\\face\\0.png". Please convert the file to png or webp.
```

When this happens, bring image into a photo editor, and save it. Or if there is more than one, run the files through a converter.
