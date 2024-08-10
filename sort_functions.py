"Sorting functions focused around numbered files"
import os
from typing import Protocol


class ImagePath(Protocol):
    "Protocol class to avoid requirement looping"
    path: str
    width: int
    height: int

    @property
    def clean_path(self):
        "Remove unnecessary path info"


def sort_by_numbers(path: str, sep=os.sep):
    "Add numbers to the front of the file name to allow for correct sorting of numbered files"
    face_name = path.split(sep)[-1].split(".")[0]
    num = ""
    letter: str
    for letter in face_name:
        if letter.isdigit():
            num += letter
        else:
            break
    if not num:
        return face_name
    return ("0" * (3 - len(num))) + face_name


def face_sort_imp(image: ImagePath):
    "Return a sortable version of the given file"
    return sort_by_numbers(image.path, sep="/")


def face_sort_out_tuple(image: tuple[str]):
    "Return a sortable version of the given file"
    return sort_by_numbers(image[0])
