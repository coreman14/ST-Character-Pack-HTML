import os

from PIL import Image, UnidentifiedImageError


def tryOpenImageIter(name, index=0):
    try:
        try:
            return name, Image.open(name)
        except AttributeError:
            return name[index], Image.open(name[index])
    except UnidentifiedImageError as pil_error:
        print()
        print(f"Error: {pil_error}. Please try to re convert the file to png or webp.")


def return_bb_box(name):
    name, trim_img = tryOpenImageIter(name, index=0)
    if trim_img.mode != "RGBA":
        trim_img = trim_img.convert("RGBA")
    bbox = trim_img.split()[-1].getbbox()
    return bbox or (0, 0, 0, 0)


# Taken and edited from https://git.student-transfer.com/st/student-transfer/-/blob/master/tools/asset-ingest/trim-image.py
def trimImage(name, do_trim=False, remove_empty=False):
    name, trim_img = tryOpenImageIter(name)
    tsize = trim_img.size
    if trim_img.mode != "RGBA":
        trim_img = trim_img.convert("RGBA")
    bbox = trim_img.split()[-1].getbbox()
    if not bbox:
        if f"{os.sep}face{os.sep}" in name or "/face/" in name:
            return (*tsize, None)
        print(f"{name} is empty, it can be removed")
        if remove_empty:
            os.remove(name)
        return (*tsize, None)
    trimmedSize = bbox[2:]

    if trimmedSize != trim_img.size and do_trim:
        trim_img = trim_img.crop((0, 0) + trimmedSize)
        bbox = trim_img.getbbox()
        trim_img.save(name)
    return (*trim_img.size, bbox)
