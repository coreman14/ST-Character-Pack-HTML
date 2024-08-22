import hashlib
import os
from glob import glob
from zipfile import ZipFile
import traceback
from shutil import rmtree
from threading import Thread
from time import sleep
from fasthtml.common import fast_app, serve, FileResponse
from fasthtml import ft, FastHTML
from html_main import main


def print_task():
    # The last thing missing from this is the ability to remove old files to save space. I think we go 30 mins
    while True:
        print("Looking for files to update")
        for x in [x for x in os.listdir("tmp") if x.endswith(".zip")]:
            path = "tmp/" + x
            file_hash = x.split(".")[0]
            folder_path = path.replace(".zip", "")
            error_path = folder_path + ".error"
            print(f"Found file {x}")
            if folder_path not in os.listdir("tmp"):
                yml_file_found = False
                path_to_yml_file = ""
                try:
                    with ZipFile(path, "r") as f:
                        for file in f.namelist():

                            yml_file_found = yml_file_found or "/scenario.yml" in file
                            if yml_file_found and not path_to_yml_file:
                                path_to_yml_file = os.path.dirname(file)
                                break
                        if yml_file_found:
                            os.makedirs(folder_path, exist_ok=True)
                            f.extractall(folder_path)
                        else:
                            with open(error_path, "w") as x:
                                pass
                            os.rename(path, path + "-completed")
                            continue
                    print("File x has scenario.yml. Processing file")
                    main(["-s", "-i", folder_path + "/" + path_to_yml_file, "-hp", file_hash])
                    index_location = folder_path + "/" + path_to_yml_file + "/index.html"
                    with ZipFile(path, "a") as f:
                        f.write(index_location, path_to_yml_file + "/index.html")
                    sleep(5)
                    rmtree(folder_path)
                except Exception:
                    print("Something went wrong")
                    print(traceback.format_exc())
                    with open(error_path, "w") as x:
                        pass
                os.rename(path, path + "-completed")

        sleep(5)


app: FastHTML
app, rt = fast_app(debug=True)


"""
5. During this whole time, the user is returned a div that is checking every 5 seconds if the file is done.
6. If it's not done, continue returning the progress. The progress is reported via a file with the name as "<file_hash>.<current_progress>.<total>"
7. If total = max, it means the characters are done, but the HTML is being processed.
8. When done, return a download link to the file. 
9. Delete any cleanup files
10. Delete the ZIP file after 30 minutes

"""


def progress_html(file_hash: str):
    # A div that pings the progress url and checks if it is done. It comes here if it is in the middle of processing
    # If numbers are equal, say that it creating the HTML.
    x = file_hash.split(".")
    total = x[-1]
    current = x[-2]
    return ft.Div()


def starting_html(file_hash: str):
    # A div that pings the progress url and checks if it is done. It comes here right after the file has been uploaded as the file probably hasn't been extracted yet
    return ft.Div()


def error_html(file_hash: str):
    # The error div. It comes here if there is an error file. It says, sorry this failed. Reccommends downloading the program to see the error. Please try with another file with a link to the index page.
    return ft.Div()


def returnCompletedState(filename, link_to_file):
    # When the zip file is completed, returns a download link + link to restart the process
    # This also is sent if the file is completed
    return ft.Div(
        ft.P(f"Completed HTML for {filename}. You can download it ", ft.A("here", hx_get=link_to_file)),
        ft.A(f"Click here to upload another file", hx_get="/"),
        id="form",
    )


@rt("/progress/{file_hash}")
def get(file_hash: str):
    progressFiles = glob(f"tmp/{file_hash}.*/**/progress*", recursive=True)
    error = glob(f"tmp/{file_hash}.*.error")
    if error:
        return progress_html(error[0])
    elif progressFiles:
        return progress_html(progressFiles[0])


@rt("/")
def get():
    return (
        ft.Title("Upload a file"),
        ft.Titled(
            "Upload a file",
            ft.Div(
                ft.Form(
                    ft.Label("Select a file to upload:", **{"for": "file"}),
                    ft.Input(
                        **{
                            "type": "file",
                            "id": "file",
                            "name": "file",
                            "accept": ".rpy,.zip",
                        }
                    ),
                    ft.Button(
                        "Upload",
                        **{"type": "submit"},
                    ),
                    hx_post="/uploadFile",
                    hx_target="#notifications",
                    **{"hx-disabled-elt": "find button"},
                ),
                id="form",
            ),
            ft.Div(f"", id="notifications"),
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
    digests = [x.split(".")[0] for x in os.listdir()]
    if md5.hexdigest() not in digests:
        with open(f"tmp/{md5.hexdigest()}.{filename}", "wb") as f:
            f.write(contents)
    return ft.Div("Reviced", id="notifications")


@rt("/downloadZip/{fname:path}")
async def get(fname: str):
    print(fname)
    return FileResponse(f"tmp/{fname}.zip")


os.makedirs("tmp", exist_ok=True)

t = Thread(target=print_task)
t.daemon = True


@app.on_event("startup")
def start_backupthread():
    t.start()


@app.on_event("shutdown")
def stop_backupthread():
    t.join(1.0)


serve()
