import re


# 1 Means extract from the start of the finding. So if a line is "xxxyyyxxx" and we are given ("yyxxx", 1), we only take the line from yyxxx
START_POINTS = [("", 0), (" Viewer</title>", 1), ('$("#backbutton").empty();', 0)]
STOP_POINTS = [("<title>", 1), ('var scenario="', 1), ("", 0)]


def clean_line(line: str):
    if "<br/>" in line:
        line = line.replace("<br/>", "<br>")
    if "<br />" in line:
        line = line.replace("<br />", "<br>")
    if re.search("<meta.*/>", line):
        line = line.replace("/>", ">")
    line = re.sub("([\\.#]\\w*) {", "\\1{", line)
    line = re.sub(" ([=]+) ", "\\1", line)
    return line


def main():
    html_snips = [""]  # Adding blank entry so that we can use a 1 index instead of zero.
    snip_index = 0
    with open("index.html", "r", encoding="utf8") as f:
        lines = f.readlines()
    if len(lines) > 1:
        # Parse with newlines
        start_extracting = False

        line_to_add = ""
        line: str
        for line in lines:
            while True:
                full_extract = True
                line = clean_line(line)
                if not start_extracting and (not START_POINTS[snip_index][0] or START_POINTS[snip_index][0] in line):
                    start_extracting = True
                    full_extract = START_POINTS[snip_index][1] == 0

                if not start_extracting:
                    break
                line = line.replace("\n", "").replace("\r", "").strip()
                line = f" {line} "
                line_to_add += line if full_extract else line[line.index(START_POINTS[snip_index][0]) :]
                if not STOP_POINTS[snip_index][0] or STOP_POINTS[snip_index][0] not in line:
                    # If blank, we continue to add to add until the end of the file
                    break

                if STOP_POINTS[snip_index][1] == 1:
                    line_to_add = line_to_add.replace(
                        line, line[: line.index(STOP_POINTS[snip_index][0]) + len(STOP_POINTS[snip_index][0])]
                    )
                html_snips.append(line_to_add)
                snip_index += 1
                start_extracting = False
                line_to_add = ""
        html_snips.append(line_to_add)

    else:
        # Parse without
        snip_index = 1
        html_snips.append("")
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

    with open("test_file.py", "w+", encoding="utf8") as f:
        for index, line in enumerate(html_snips[1:], start=1):
            quote_to_use = "'" if line.endswith('"') or line.startswith('"') else '"'
            f.write(f"html_snip{index} = r{quote_to_use * 3}{line}{quote_to_use * 3}\n")


if __name__ == "__main__":
    main()
