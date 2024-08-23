from contextlib import redirect_stdout
import hashlib
import io
import logging.config
import os
import argparse
from glob import glob
import pathlib
from zipfile import ZipFile
import traceback
from shutil import rmtree
from threading import Thread
from time import sleep, time
import logging

import yaml
from fasthtml.common import fast_app, serve, FileResponse, Style
from fasthtml import ft, FastHTML
from html_main import main

DIR_OF_HOLDING = "tmp"
DIR_OF_LOGGING = "serverConfig/logs"

css = """
.container > h1 {
    padding-bottom: 0.5em;
}
"""

os.makedirs(DIR_OF_HOLDING, exist_ok=True)
os.makedirs(DIR_OF_LOGGING, exist_ok=True)


def setup_logging():
    config_file = pathlib.Path("serverConfig/loggingconfig.yaml")
    with config_file.open() as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


setup_logging()
logger = logging.getLogger("web_server")


def process_uploaded_files():
    while True:
        logger.info("Looking for files to update")
        files_to_check = os.listdir(DIR_OF_HOLDING)
        for filename in [x for x in files_to_check if x.endswith(".zip")]:
            logger.info("Found file %s", filename)
            file_hash = filename.split(".")[0]
            zip_file_path = os.path.join(DIR_OF_HOLDING, filename)
            extract_folder_path = zip_file_path.replace(".zip", "")
            error_file_path = extract_folder_path + ".error"
            # Don't try to process a file that is already being processed
            if extract_folder_path not in files_to_check:
                yml_file_folder = ""
                list_of_files_in_zip = []
                # For a general error we print the HTML creation std_out.
                general_error = False
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
                            general_error = True

                    if general_error:
                        with open(error_file_path, "w", encoding="utf8") as filename:
                            filename.write(
                                "Couldn't find YML file. Please check that the the zip uses YML files instead of JSON."
                            )
                        logger.info("Uploaded file did not contain a YML file.")
                        os.rename(zip_file_path, zip_file_path + "-completed")
                        continue
                    logger.info("File %s has scenario.yml. Processing file", filename)

                    # Os Error we print a generic message to prevent leaking the dir stuff
                    os_error = False
                    error_text = None
                    logger.info("Starting HTML creation")
                    f = io.StringIO()
                    with redirect_stdout(f):
                        try:
                            main(["-s", "-i", extract_folder_path + "/" + yml_file_folder, "-hp", file_hash])
                        except OSError:
                            os_error = True
                            error_text = traceback.format_exc()
                        except Exception:
                            general_error = True
                            error_text = traceback.format_exc()
                    if general_error or os_error:
                        logger.debug(error_text)
                        logger.info("Something went wrong with HTML processing, printing debug log")
                        with open(error_file_path, "w", encoding="utf8") as filename:
                            if os_error:
                                filename.write("OSError: Please contact server Admin to fix or wait 30 minutes.")
                            else:
                                filename.write(f.getvalue())
                                logger.debug(f.getvalue())
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
                    logger.info("Finished Processing File %s", filename)
                except Exception:
                    logger.info("Something went wrong")
                    logger.debug(traceback.format_exc())
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
            logger.info("Removed %d files", files_removed)
        logger.info("Finished Processing")
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
    return FileResponse(f"htmlAssets/{fname}.{ext}")


@rt("/")
def get():
    return (
        ft.Titled(
            "Create HTML for character pack",
            ft.Div(
                ft.A(
                    "Click here for information on this tool",
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

    def sizeof_fmt(num, suffix="B"):
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    logger.info("File was uploaded, %s, with size of: %s", filename, sizeof_fmt(len(contents)))
    # Start hashing
    md5 = hashlib.md5()
    md5.update(contents)
    digests = [x.split(".")[0] for x in os.listdir(DIR_OF_HOLDING)]
    if md5.hexdigest() not in digests:
        with open(f"{DIR_OF_HOLDING}/{md5.hexdigest()}.{filename}", "wb") as f:
            f.write(contents)
        logger.info('File %s was saved at "%s"', filename, f"{DIR_OF_HOLDING}/{md5.hexdigest()}.{filename}")
    else:
        logger.info("File %s is a duplicate, returning error log", filename)
    return decide_div(md5.hexdigest())


@rt("/downloadCompletedZip/{fname:path}")
async def get(fname: str):
    return FileResponse(f"tmp/{fname}.zip-completed", filename=fname.split(".", 1)[1] + ".zip")


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
    parser.add_argument(
        "-dr",
        "--disablereloading",
        help="When true, do not reload the server if file changes happen.",
        action="store_false",
    )
    args = parser.parse_args()
    serve(port=args.port, reload=args.disablereloading, reload_includes="*.py")
