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
from fasthtml.common import fast_app, serve, FileResponse, Style, Script
from fasthtml import ft, FastHTML
from html_main import main

DIR_OF_HOLDING = "tmp"
DIR_OF_LOGGING = "serverConfig/logs"


os.makedirs(DIR_OF_HOLDING, exist_ok=True)
os.makedirs(DIR_OF_LOGGING, exist_ok=True)


def setup_logging():
    config_file = pathlib.Path("serverConfig/pythonloggingconfig.yaml")
    with config_file.open() as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


setup_logging()
logger = logging.getLogger("process_zip_files")


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
        logger.info("Finished Processing Files, Sleeping for 30 seconds")
        sleep(30)


if __name__ == "__main__":
    process_uploaded_files()
