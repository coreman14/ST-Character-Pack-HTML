import re


# The points to start and stop the text splitting.
# Each point is a tuple containing the text to look for, and how to parse the line.
# 1 means to only grab it from the found point, 0 means grab the whole line.
START_POINTS = [("", 0), (" Viewer</title>", 1), ("/*Start*/ var characterArray=[];", 0)]
STOP_POINTS = [("<title>", 1), ('scenario="', 1), ("", 0)]


def clean_line(line: str):
    "We do any text changes here, such as removing the end slash from br tags."
    # Replace single line comments in multiline comments (Comments aren't minified well)
    if match := re.match(r"""(.*;\s*)\/\/(?=(?:[^"']*("|')[^"']*("|'))*[^"']*$)(.*)""", line):
        line = match.group(1)
        comment = "/*" + match.group(4) + "*/"
        comment += line
        line = comment
    # Remove the custom favicon from the html
    if 'href="data:image/png' in line:
        line = 'href="FAVICONHERE"\n'
    line = re.sub("([\\.#]\\w*) {", "\\1{", line)
    line = re.sub(" ([=]+) ", "\\1", line)
    return line


def main():
    html_snips = [""]  # Adding blank entry so that we can use a 1 index instead of zero.
    snip_index = 0
    with open("index.html", "r", encoding="utf8") as f:
        lines = f.readlines()

    # Parse with newlines
    # If value is true, we have found a starting point and can start saving lines
    start_extracting = False

    # If value is true, extract the full line
    full_extract = START_POINTS[snip_index][1] == 0
    # I need to change full extract value twice, one for each new snip and once after the first line has run.
    line_to_add = ""
    line: str
    for line in lines:
        # Because we can start and stop on the same line, we need to have it rerun on the same line after it finds one.
        while True:
            line = clean_line(line)
            if not start_extracting and (not START_POINTS[snip_index][0] or START_POINTS[snip_index][0] in line):
                start_extracting = True

            if not start_extracting:
                break
            line = line.replace("\n", "").replace("\r", "").strip()
            line = f" {line} "
            line_to_add += line if full_extract else line[line.index(START_POINTS[snip_index][0]) :]
            # Every line after the first line needs to be full extracted
            full_extract = True
            line_to_add = clean_line(line_to_add)
            if not STOP_POINTS[snip_index][0] or STOP_POINTS[snip_index][0] not in line:
                # If blank, we continue to add to add until the end of the file
                break

            if STOP_POINTS[snip_index][1] == 1:
                line_to_add = line_to_add.replace(
                    line, line[: line.index(STOP_POINTS[snip_index][0]) + len(STOP_POINTS[snip_index][0])]
                )
            html_snips.append(line_to_add)
            snip_index += 1
            full_extract = START_POINTS[snip_index][1] == 0
            start_extracting = False
            line_to_add = ""
    html_snips.append(line_to_add)

    all_lines = []
    snip_counter = 1
    with open("html_main.py", "r", encoding="utf8") as f:
        for line in f:
            if line.startswith(f"html_snip{snip_counter}"):
                quote_to_use = (
                    "'" if html_snips[snip_counter].endswith('"') or html_snips[snip_counter].startswith('"') else '"'
                )
                all_lines.append(
                    f"html_snip{snip_counter} = r{quote_to_use * 3}{html_snips[snip_counter]}{quote_to_use * 3}\n"
                )
                snip_counter += 1
            else:
                all_lines.append(line)

    with open("html_main.py", "w", encoding="utf8") as f:
        f.writelines(all_lines)


if __name__ == "__main__":
    main()
