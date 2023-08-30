# [ST-Character-Pack-HTML](https://github.com/coreman14/ST-Character-Pack-HTML)

Inspired by the holy [Holy Pack](https://www.tfgames.site/phpbb3/viewtopic.php?f=72&t=15688), ST-Character-Pack-HTML will create a html file for a scenario or character pack to replace having to browse by the in game sprite viewer or File explorer. Basic demo [here](https://coreman14.github.io/ST-Character-Pack-HTML/).

I've also added a json2yaml converter and image trim utility which are taken from [Student Transfer Utils](https://utils.student-transfer.com).

## Features

-   No prep work is required. Just create the file and go.
-   No additional files will be created during the process. The HTML file generated is the only file made.
-   Betters the browsing experience. With this added, the user will not have to load into ST to see all the characters, or navigate it with a file explorer.
-   The html is written in pure JS and CSS and can be used offline. This also allows for customization of the HTML file.
-   Useful information is shown before even clicking on a character (The # of faces a pose has, can set a minimum number of poses)
-   Show's all expression's on the characters page, so it can be a replacement for a expression sheet.
-   Keyboard shortcuts are added and can be turn off with a key press.

## Running the program

For Windows, just download the EXE from the [Latest release](https://github.com/coreman14/ST-Character-Pack-HTML/releases/latest/download/HTMLCreator.exe), place it into the scenario folder you wish to create the HTML for, next to the `scenario.yml` file, and run it by double clicking or from the command line.

For Mac, Unix and other OS's, install Python 3.8 or greater, then download one of the PYZ files from the [Latest release](https://github.com/coreman14/ST-Character-Pack-HTML/releases/latest).

For the script to run, it requires a few additional packages for processing images and YAML files. If you do not want to install these requirements locally, download the `STHtml_includes_requirements.pyz` file. When ran this will unzip the requirements needed.

If you are ok with installing these requirements to your machine, download the `STHtml.pyz` then run the command `python -m pip install pyyaml pillow colorama`. After it finishes installing, you can run the PYZ file.

## Arguments

For an up to date list, run the file with `-h` which will print all options. You can then add any to the command line.

## Other features (Using these disables the HTML output)

Using -b, it will output the size of all the images within the characters folders. This size is the smallest size that the image could become. It will then highlight the largest image. You can also use -re to filter the results. This accepts and uses the value as regex, but it will work if you just put a single name.

## Notes

When running the program, do not stop the program. Doing so can corrupt your images.

If your characters feature any transparency, do not use the trim image function. PIL does not play well with transparency.

There are some files that pillow does not like read. When this happens, it should output the full path to the file

```js
Error: cannot identify image file "C:\\StudentTransfer\\A deal with the devil\\characters\\corneliasaya\\a\\faces\\face\\0.png". Please convert the file to png or webp.
```

When this happens, bring image into a photo editor, and save it. Or if there is more than one, run the files through a converter.
