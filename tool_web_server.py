import asyncio
import hashlib
import os
from zipfile import ZipFile
from contextlib import asynccontextmanager
import traceback
from fasthtml.common import fast_app, serve, FileResponse
from fasthtml import ft, FastHTML
from html_main import main
from shutil import rmtree


async def print_task(sleep: int):
    while True:
        for x in [x for x in os.listdir("tmp") if x.endswith(".zip")]:
            path = "tmp/" + x
            folder_path = path.replace(".zip", "")
            error_path = folder_path + ".error"
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

                    main(["-s", "-i", folder_path + "/" + path_to_yml_file])
                    index_location = folder_path + "/" + path_to_yml_file + "/index.html"
                    with ZipFile(path, "a") as f:
                        f.write(index_location, path_to_yml_file + "/index.html")
                    await asyncio.sleep(5)
                    rmtree(folder_path)
                except Exception:
                    print("Something went wrong")
                    print(traceback.format_exc())
                    with open(error_path, "w") as x:
                        pass
                os.rename(path, path + "-completed")

        await asyncio.sleep(sleep)


@asynccontextmanager
async def lifespan(app: FastHTML):
    asyncio.create_task(print_task(5))
    yield
    # Add any logs or commands before shutting down.
    print("It is shutting down...")


app: FastHTML
app, rt = fast_app(debug=True, lifespan=lifespan)


"""
1. Allow user to upload file.
2. Save it and name it with a hash so we can not process a file more than once in 30 minutes
3. Write a multiprocess function that will process the file. We need to figure out how to deal with errors.
4. Once the file is processed, add -completed to the end.
5. During this whole time, the user is returned a div that is checking every 5 seconds if the file is done.
6. If it's not done, continue returning the progress. The progress is reported via a file with the name as "<file_hash>.<current_progress>.<total>"
7. If total = max, it means the characters are done, but the HTML is being processed.
8. When done, return a download link to the file. 
9. Delete any cleanup files
10. Delete the ZIP file after 30 minutes

"""


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


def returnCompletedState(filename, link_to_file):
    return ft.Div(
        ft.P(f"Completed HTML for {filename}. You can download it ", ft.A("here", hx_get=link_to_file)),
        ft.A(f"Click here to upload another file", hx_get="/"),
        id="form",
    )


os.makedirs("tmp", exist_ok=True)
serve()
