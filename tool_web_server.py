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
from fasthtml.common import fast_app, serve, FileResponse
from fasthtml import ft, FastHTML
from html_main import main

DIR_OF_HOLDING = "tmp"


def print_task():
    # The last thing missing from this is the ability to remove old files to save space. I think we go 30 mins
    while True:
        print("Looking for files to update")
        for x in [x for x in os.listdir(path=DIR_OF_HOLDING) if x.endswith(".zip")]:
            path = "tmp/" + x
            file_hash = x.split(".")[0]
            folder_path = path.replace(".zip", "")
            error_path = folder_path + ".error"
            print(f"Found file {x}")
            if folder_path not in os.listdir(DIR_OF_HOLDING):
                yml_file_found = False
                path_to_yml_file = ""
                list_of_files_to_write = []
                try:
                    with ZipFile(path, "r") as f:
                        list_of_files_to_write = f.namelist()
                        for file in f.namelist():
                            yml_file_found = yml_file_found or "/scenario.yml" in file
                            if yml_file_found and not path_to_yml_file:
                                path_to_yml_file = os.path.dirname(file)
                                break
                        if yml_file_found:
                            os.makedirs(folder_path, exist_ok=True)
                            f.extractall(folder_path)
                        else:
                            with open(error_path, "w", encoding="utf8") as x:
                                x.write("Couldn't find YML file")
                            os.rename(path, path + "-completed")
                            continue
                    print("File x has scenario.yml. Processing file")

                    error = False
                    os_error = None

                    f = io.StringIO()
                    with redirect_stdout(f):
                        try:
                            main(["-s", "-i", folder_path + "/" + path_to_yml_file, "-hp", file_hash])
                        except OSError:
                            os_error = "OSError: Please contact server Admin to fix or wait 30 minutes."
                        except Exception:
                            error = True
                    if error or os_error:
                        print("Something went wrong with HTML processing, printing debug log")
                        with open(error_path, "w", encoding="utf8") as x:
                            if os.error:
                                x.write(os_error)
                            else:
                                x.write(f.getvalue())
                        os.rename(path, path + "-completed")
                        continue

                    index_location = folder_path + "/" + path_to_yml_file + "/index.html"
                    with ZipFile(path, "w") as f:
                        for file in list_of_files_to_write:
                            f.write(folder_path + "/" + file, file)
                        if path_to_yml_file + "/index.html" not in list_of_files_to_write:
                            f.write(index_location, path_to_yml_file + "/index.html")
                    sleep(5)
                    rmtree(folder_path)
                    print("Finished Processing File")
                except Exception:
                    print("Something went wrong")
                    print(traceback.format_exc())
                    with open(error_path, "w", encoding="utf8") as x:
                        x.write(traceback.format_exc())
                os.rename(path, path + "-completed")

        files = [os.path.join(DIR_OF_HOLDING, f) for f in os.listdir(DIR_OF_HOLDING)]  # add path to each file
        for file in filter(lambda x: os.path.getmtime(x) < (time() - (60 * 30)), files):
            if os.path.isdir(file):
                rmtree(file)
            else:
                os.remove(file)
        sleep(30)


app: FastHTML
app, rt = fast_app()
app.routes.pop()


def progress_html(progress_file: str, file_hash: str):
    # A div that pings the progress url and checks if it is done. It comes here if it is in the middle of processing
    # If numbers are equal, say that it creating the HTML.
    x = progress_file.split(".")
    total = x[-1]
    current = x[-2]
    return ft.Div(
        ft.H3("Processing zip file"),
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


def starting_html(file_hash: str):
    return ft.Div(
        ft.H2("File has been uploaded."),
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
        ft.H3(
            "Failed to create HTML file. Please check fix the errors listed below. Then try again.", style="color: red"
        ),
        ft.A(
            "Click here to upload another file",
            hx_get="/",
            hx_target="closest body",
            style="display:block; padding-bottom: 15px;",
        ),
        ft.Textarea(error_text, style="height: 60vh"),
    )


def return_completed_state(link_to_file: str):
    link_to_file = link_to_file.replace(".zip-completed", "").replace(os.sep, "/").split("/")[-1]
    filename = link_to_file.split(".", 1)[1] + ".zip"
    link_to_file = f"/downloadCompletedZip/{link_to_file}"
    return ft.Div(
        ft.P(f"Completed HTML for {filename}. You can download it ", ft.A("here", href=link_to_file)),
        ft.A("Click here to upload another file", hx_get="/", hx_target="closest body"),
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
        ft.Title("Create HTML for character pack"),
        ft.Titled(
            "HTML Creator",
            ft.Div(
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

t = Thread(target=print_task)
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
