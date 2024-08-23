from contextlib import redirect_stdout
import hashlib
import io
import os
import argparse
from glob import glob
from zipfile import ZipFile
import traceback
from shutil import rmtree
from threading import Thread
from time import sleep, time
from fasthtml.common import fast_app, serve, FileResponse, Style
from fasthtml import ft, FastHTML
from html_main import main

DIR_OF_HOLDING = "tmp"

css = """
.container > h1 {
    padding-bottom: 0.5em;
}
"""
"""
List of tasks:
    1. Proper logging.
    2. Make a way to pass in perticular arguments like favicon or height.
        For this, we change the main program and not the web server.
        We will make it so that the YML file can override arguments.
        The only thing it cannot do is anything to do with seperating files and bounds/system arguments like strict, silent, hashprogress, etc...

"""


def process_uploaded_files():
    while True:
        print("Looking for files to update")
        files_to_check = os.listdir(DIR_OF_HOLDING)
        for filename in [x for x in files_to_check if x.endswith(".zip")]:
            print(f"Found file {filename}")
            file_hash = filename.split(".")[0]
            zip_file_path = os.path.join(DIR_OF_HOLDING, filename)
            extract_folder_path = zip_file_path.replace(".zip", "")
            error_file_path = extract_folder_path + ".error"
            # Don't try to process a file that is already being processed
            if extract_folder_path not in files_to_check:
                yml_file_folder = ""
                list_of_files_in_zip = []
                try:
                    with ZipFile(zip_file_path, "r") as f:
                        list_of_files_in_zip = f.namelist()
                        for zip_file in list_of_files_in_zip:
                            if "/scenario.yml" in zip_file:
                                yml_file_folder = os.path.dirname(zip_file)
                                break
                        if yml_file_folder:
                            os.makedirs(extract_folder_path, exist_ok=True)
                            f.extractall(extract_folder_path)
                        else:
                            with open(error_file_path, "w", encoding="utf8") as filename:
                                filename.write("Couldn't find YML file")
                            os.rename(zip_file_path, zip_file_path + "-completed")
                            continue
                    print(f"File {filename} has scenario.yml. Processing file")
                    # For a general error we print the HTML creation std_out.
                    general_error = False
                    # Os Error we print a generic message to prevent leaking the dir stuff
                    os_error = False
                    print("Starting HTML creation")
                    f = io.StringIO()
                    with redirect_stdout(f):
                        try:
                            main(["-s", "-i", extract_folder_path + "/" + yml_file_folder, "-hp", file_hash])
                        except OSError:
                            os_error = True
                            print(traceback.format_exc())
                        except Exception:
                            general_error = True
                            print(traceback.format_exc())
                    if general_error or os_error:
                        print("Something went wrong with HTML processing, printing debug log")
                        with open(error_file_path, "w", encoding="utf8") as filename:
                            if os_error:
                                filename.write("OSError: Please contact server Admin to fix or wait 30 minutes.")
                            else:
                                filename.write(f.getvalue())
                        os.rename(zip_file_path, zip_file_path + "-completed")
                        continue

                    index_html_location = extract_folder_path + "/" + yml_file_folder + "/index.html"
                    with ZipFile(zip_file_path, "w") as f:
                        for zip_file in list_of_files_in_zip:
                            f.write(extract_folder_path + "/" + zip_file, zip_file)
                        if yml_file_folder + "/index.html" not in list_of_files_in_zip:
                            f.write(index_html_location, yml_file_folder + "/index.html")
                    sleep(5)
                    rmtree(extract_folder_path)
                    print(f"Finished Processing File {filename}")
                except Exception:
                    print("Something went wrong")
                    print(traceback.format_exc())
                    with open(error_file_path, "w", encoding="utf8") as filename:
                        filename.write("An error has occured. Please contact server Admin to fix or wait 30 minutes.")
                os.rename(zip_file_path, zip_file_path + "-completed")

        files = [os.path.join(DIR_OF_HOLDING, f) for f in os.listdir(DIR_OF_HOLDING)]  # add path to each file
        files_removed = 0
        for zip_file in filter(lambda x: os.path.getmtime(x) < (time() - (60 * 30)), files):
            if os.path.isdir(zip_file):
                rmtree(zip_file)
            else:
                os.remove(zip_file)
            files_removed += 1
        if files_removed:
            print(f"Removed {files_removed} files")
        print("Finished Processing")
        sleep(30)


app: FastHTML
app, rt = fast_app(hdrs=[Style(css)])
app.routes.pop()


def progress_html(progress_file: str, file_hash: str):
    # A div that pings the progress url and checks if it is done. It comes here if it is in the middle of processing
    # If numbers are equal, say that it creating the HTML.
    x = progress_file.split(".")
    total = x[-1]
    current = x[-2]
    return ft.Div(
        ft.H2("Processing zip file", style="color: green;"),
        (
            ft.Div(f"Progress: ", ft.Span(f"{current}/{total}", style="color: green;"), " characters processed")
            if current != total
            else ft.Div("Creating HTML")
        ),
        id="form",
        hx_get=f"/progress/{file_hash}",
        hx_trigger="every 5s",
        hx_swap="outerHTML",
        hx_target="#form",
        style="font-size: 2em;",
    )


def return_to_home_link():
    return ft.A(
        "Click here to upload another file",
        hx_get="/",
        hx_target="closest body",
        style="display:block; padding-bottom: 15px;",
    )


def starting_html(file_hash: str):
    return ft.Div(
        ft.H2("File has been uploaded.", style="color: green;"),
        ft.H3("Starting process to generate HTML file"),
        id="form",
        hx_get=f"/progress/{file_hash}",
        hx_trigger="every 5s",
        hx_swap="outerHTML",
        hx_target="#form",
    )


def error_html(error_file: str, file_hash: str):
    with open(error_file, "r", encoding="utf8") as f:
        error_text = f.read()
    folder_name = error_file.replace(".error", "").split(os.sep, 1)[-1]
    error_text = error_text.replace(os.path.abspath(os.path.dirname(error_file)), "")
    error_text = error_text.replace(folder_name + os.sep, f"{folder_name}.zip{os.sep}")
    error_text = error_text.replace(os.sep + file_hash + ".", "")

    return ft.Div(
        ft.H2(
            "Failed to create HTML file. Please check fix the errors listed below. Then try again.", style="color: red"
        ),
        return_to_home_link(),
        ft.Textarea(error_text, style="height: 60vh"),
    )


def return_completed_state(link_to_file: str):
    link_to_file = link_to_file.replace(".zip-completed", "").replace(os.sep, "/").split("/")[-1]
    filename = link_to_file.split(".", 1)[1] + ".zip"
    link_to_file = f"/downloadCompletedZip/{link_to_file}"
    return ft.Div(
        ft.P(f"Completed HTML for {filename}. You can download it ", ft.A("here", href=link_to_file)),
        return_to_home_link(),
        id="form",
        style="font-size:2em;",
    )


def decide_div(file_hash):
    error = glob(f"tmp/{file_hash}.*.error")
    if error:
        return error_html(error[0], file_hash)

    completed_file = glob(f"tmp/{file_hash}.*.zip-completed")
    if completed_file:
        return return_completed_state(link_to_file=completed_file[0])

    progress_files = glob(f"tmp/{file_hash}.*/**/progress*", recursive=True)
    if progress_files:
        return progress_html(progress_files[0], file_hash)
    return starting_html(file_hash=file_hash)


@rt("/progress/{file_hash}")
def get(file_hash: str):
    return decide_div(file_hash)


@app.route("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f"html/{fname}.{ext}")


@rt("/")
def get():
    return (
        ft.Titled(
            "Create HTML for character pack",
            ft.Div(
                ft.A(
                    "Click here to for information",
                    hx_get="/info",
                    hx_target="#form",
                    style="display:block; padding-bottom: 15px;",
                ),
                ft.Form(
                    ft.Label("Upload a character pack in a .zip format", **{"for": "file"}),
                    ft.Input(
                        **{
                            "type": "file",
                            "id": "file",
                            "name": "file",
                            "accept": ".rpy,.zip",
                        },
                    ),
                    ft.Button(
                        "Upload",
                        **{"type": "submit"},
                    ),
                    hx_post="/uploadFile",
                    hx_target="#form",
                    hx_swap="innerHTML",
                    hx_indicator="#notifications",
                    **{"hx-disabled-elt": "find button"},
                ),
                ft.Div("Uploading file...", id="notifications", **{"class": "htmx-indicator"}),
                id="form",
                style="font-size:1.5em;",
            ),
        ),
    )


@rt("/info")
def get():
    return ft.Div(
        ft.H2("Information"),
        ft.P(
            "This website allows users to upload their scenarios or zip files to create an index.html using ",
            ft.A("ST-Charcter-Pack-HTML", href="https://github.com/coreman14/ST-Character-Pack-HTML"),
        ),
        ft.P("You cannot enter any arguments when you upload the character pack to this site."),
        ft.P(
            "You",
            ft.B("can however"),
            "use the few arguments that can be found through the scenario.yml file. You can find these entries ",
            ft.A("here", href="https://github.com/coreman14/ST-Character-Pack-HTML?tab=readme-ov-file#arguments"),
        ),
        return_to_home_link(),
        id="form",
    )


@rt("/uploadFile")
async def post(request):
    async with request.form() as form:
        filename = form["file"].filename
        contents = await form["file"].read()

    # Start hashing
    md5 = hashlib.md5()
    md5.update(contents)
    digests = [x.split(".")[0] for x in os.listdir(DIR_OF_HOLDING)]
    if md5.hexdigest() not in digests:
        with open(f"tmp/{md5.hexdigest()}.{filename}", "wb") as f:
            f.write(contents)
    return decide_div(md5.hexdigest())


@rt("/downloadCompletedZip/{fname:path}")
async def get(fname: str):
    print(fname)
    return FileResponse(f"tmp/{fname}.zip-completed", filename=fname.split(".", 1)[1] + ".zip")


os.makedirs(DIR_OF_HOLDING, exist_ok=True)

t = Thread(target=process_uploaded_files)
t.daemon = True


@app.on_event("startup")
def start_backupthread():
    t.start()


@app.on_event("shutdown")
def stop_backupthread():
    t.join(1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Startup settings for HTML webserver")
    parser.add_argument(
        "-p",
        "--port",
        help="Change the port to broadcast to. Default is 5000",
        type=int,
        default=5000,
    )
    args = parser.parse_args()
    serve(port=args.port)
