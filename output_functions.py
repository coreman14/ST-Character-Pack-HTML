"Main runner functions for the program"
from argparse import Namespace
import os
import json
import yaml


from classes import Character
from html_arg_functions import update_html


YML_FAILS = []
JSON_CONVERT_ASK = False


def create_html_file(args: Namespace, html_snips: tuple[str, str, str], chars: list[Character], split_files=False):
    "Create the HTML file for the scenario"
    html_snip1, html_snip2 = html_snips
    html_snip1 = html_snip1.replace("FAVICONHERE", args.favicon)
    html_snip1 = update_html(args, html_snip1)
    with open(os.path.join(args.inputdir, args.name), "w+", encoding="utf8") as html_file:
        html_file.write(html_snip1)
        if split_files:
            html_file.write(
                f'</script><script src="{args.jsonname}"></script><script>var jsonData = data.characters;scenario=data.scenario;prefix=data.prefix;'
            )
        else:
            html_file.write(f'scenario="{args.titlename}";prefix="{args.prefix}";')
            html_file.write("var jsonData={ " + "".join(str(x) for x in chars) + "};")
        # Add scenario title, '"; ", then add the "json" with "var jsonData={ " at start with "};" at the end
        html_file.write(html_snip2)
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
