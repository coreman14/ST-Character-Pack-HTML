"Functions to deal with images"
import os
import sys
from PIL import Image, UnidentifiedImageError
from PIL.Image import Image as ImageType
import numpy as np

FILES_THAT_COULD_BE_REMOVED = []


def attempt_to_open_image(name: str | list[str]) -> tuple[str | list[str], ImageType] | tuple[str, ImageType]:
    """Attempts to open image. Treats image as a string first, then on failure treats it as a list."""
    return_name = name
    try:
        try:
            image = Image.open(name)
        except AttributeError:
            image = Image.open(name[0])
            return_name = name[0]
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        if "faces" in name:
            img_np = np.array(image)
            img_np[img_np < (0, 0, 0, 255)] = 0
            image = Image.fromarray(img_np)
        return return_name, image

    except UnidentifiedImageError as pil_error:
        print()
        print(f"Error: {pil_error}. Please try to re convert the file to png or webp.")
        sys.exit(1)


def return_bb_box(name: str | list[str]) -> tuple[int, int, int, int]:
    """Opens the given image or first image in the list, then returns the bounding box of the image."""
    name, trim_img = attempt_to_open_image(name)
    if trim_img.mode != "RGBA":
        trim_img = trim_img.convert("RGBA")
    bbox = trim_img.split()[-1].getbbox()
    return bbox or (0, 0, 0, 0)


# Taken and edited from https://git.student-transfer.com/st/student-transfer/-/blob/master/tools/asset-ingest/trim-image.py
def open_image_and_get_measurements(
    name: str | list[str], do_trim=False, remove_empty=False
) -> tuple[int, int, None] | tuple[int, int, tuple[int, int, int, int] | None]:
    """Opens the given image or first image in the list, then returns the size and bound box.
    If do_trim is true, will trim the image before
    Setting remove_empty as true will remove any blank image.
    """
    name, trim_img = attempt_to_open_image(name)
    image_size = trim_img.size
    # if trim_img.mode != "RGBA":
    #     trim_img = trim_img.convert("RGBA")
    bbox = trim_img.split()[-1].getbbox()
    if not bbox:
        if f"{os.sep}face{os.sep}" in name or "/face/" in name:
            return (*image_size, None)
        if remove_empty:
            os.remove(name)
        elif name not in FILES_THAT_COULD_BE_REMOVED:
            trim_img.show()
            FILES_THAT_COULD_BE_REMOVED.append(name)
            print(f"{name} is empty, it can be removed")
        return (*image_size, None)

    amount_to_trim = bbox[2:]

    if amount_to_trim != image_size and do_trim:
        trim_img = trim_img.crop((0, 0) + amount_to_trim)
        bbox = trim_img.getbbox()
        trim_img.save(name)
        image_size = trim_img.size
    return (*image_size, bbox)
