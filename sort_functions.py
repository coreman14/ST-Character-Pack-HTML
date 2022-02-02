import os
from typing import Protocol


class ImagePath(Protocol):
    path: str
    width: int
    height: int

    @property
    def clean_path(self):
        ...


def sort_by_numbers(path: str, sep=os.sep):
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
    return ("0" * (3 - len(num))) + path.split(os.sep)[-1].split(".")[0]


def face_sort_imp(image: ImagePath):
    return sort_by_numbers(image.path, sep="/")


def face_sort_outtuple(image: ImagePath):
    return sort_by_numbers(image[0])
