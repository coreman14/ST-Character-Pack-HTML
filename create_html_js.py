"Main runner functions for the program"
from argparse import Namespace

import os
import json
import sys
import re
import zipfile
import yaml
import minify_html

from classes import Character


def read_base_html_file():
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        file_path = os.path.join(base_path, relative_path)
        if not os.path.exists(file_path):
            # Assume its the zip file and return false
            return False
        return file_path

    def read_from_zipfile(relative_path):
        with zipfile.ZipFile(sys.argv[0]) as zf:
            with zf.open(relative_path) as f:
                return f.read().decode("utf-8")

    if html_file_path := resource_path("base.html"):
        with open(html_file_path, "r", encoding="utf8") as html_file:
            html = html_file.read()
    else:
        html = read_from_zipfile("base.html")
    return html


def clean_line(line: str):
    "We do any text changes here, such as removing the end slash from br tags."
    # Replace single line comments in multiline comments (Comments aren't minified well)
    if match := re.match(r"""(.*;\s*|^\s*)\/\/(?=(?:[^"']*("|')[^"']*("|'))*[^"']*$)(.*)""", line):
        line = match.group(1)
        comment = "/*" + match.group(4) + "*/"
        comment += line
        line = comment
    line = re.sub("([\\.#]\\w*) {", "\\1{", line)
    line = re.sub(" ([=]+) ", "\\1", line)
    return line.replace("\n", "").replace("\r", "").strip()


def create_html_file(args: Namespace, chars: list[Character], split_files=False):
    "Create the HTML file for the scenario"
    html = read_base_html_file()
    html = html.replace("FAVICONHERE", args.favicon)
    html = update_html(args, html)
    html, html2 = html.split("/*SPLIT HERE*/", maxsplit=1)
    with open(os.path.join(args.inputdir, args.name), "w+", encoding="utf8") as html_file:
        full_html = html
        if split_files:
            full_html += f'</script><script src="{args.jsonname}"></script><script>var jsonData = data.characters;scenario=data.scenario;prefix=data.prefix;'

        else:
            full_html += f'scenario="{args.titlename}";prefix="{args.prefix}";'
            full_html += "var jsonData={ " + "".join(str(x) for x in chars) + "};"
        # Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
        full_html += html2
        full_html = minify_html.minify(  # pylint: disable=no-member
            full_html,
            minify_css=True,
            ensure_spec_compliant_unquoted_attribute_values=True,
            keep_html_and_head_opening_tags=True,
            do_not_minify_doctype=True,
        )
        full_html = "".join(clean_line(x) for x in full_html.split("\n"))
        html_file.write(full_html)
    print(
        f"Outputted to HTML at {os.path.join(args.inputdir, args.name)}",
        end="\n" if split_files else "",
    )

    if not split_files:
        input(
            ", press enter to exit...",
        )
        print()


def create_js(args: Namespace, chars: list[Character]):
    "Create a JS file containing the information needed for the HTML"
    formatted_json = yaml.safe_load(
        '{"scenario": "'
        + args.titlename
        + '", "prefix": "'
        + args.prefix
        + '", "characters": { '
        + "".join(str(x) for x in chars)
        + "}}",
    )
    with open(os.path.join(args.inputdir, args.jsonname), "w+", encoding="utf8") as json_file:
        json_file.write(f"var data = {json.dumps(formatted_json)}")

    print(f"Outputted to JSON at {os.path.join(args.inputdir, args.jsonname)}", end="")
    input(
        ", press enter to exit...",
    )
    print()


def update_html(args: Namespace, string_to_replace: str) -> str:
    """
    Updates the the string_to_replace with a namespace.

    This function will check if the attribute is set before trying to replace
    """
    if hasattr(args, "outfitheight") and args.outfitheight:
        string_to_replace = string_to_replace.replace(
            "height: 200px; /*Main Height replace*/",
            f"height: {args.outfitheight}px; /*Main Height replace*/",
        )
    if hasattr(args, "accessoryheight") and args.accessoryheight:
        string_to_replace = string_to_replace.replace(
            "height: 400px; /*Access Height replace*/",
            f"height: {args.accessoryheight}px; /*Access Height replace*/",
        )
    return string_to_replace
