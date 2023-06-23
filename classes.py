import html
import os
import re
from dataclasses import dataclass
from typing import NamedTuple

from PIL import Image


class ImagePath(NamedTuple):
    """Hold an images location, width and height"""

    path: str
    width: int
    height: int
    cropbox: "CropBox"

    @property
    def clean_path(self):
        return re.sub(
            "characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/",
            "",
            self.path,
        )

    @property
    def folder_path(self):
        return re.sub(
            "(characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/)(.*)",
            "\\1",
            self.path,
        )


class CropBox(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def bbox_from_multiple_pil(cls, bounds_boxes: list[tuple[int]]):
        q = list(bounds_boxes)
        while None in q:
            q.remove(None)
        if not q:
            return None
        if len(q) == 1:
            return cls(*q[0])
        return cls(
            min(x[0] for x in q),
            min(x[1] for x in q),
            max(x[2] for x in q),
            max(x[3] for x in q),
        )

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, CropBox) and self.right == __o.right and self.bottom == __o.bottom

    def __repr__(self) -> str:
        return f"Actual Image Size {self.right}x{self.bottom}"


@dataclass
class Accessory:
    name: str
    group: str | None  # Can be None
    image: ImagePath
    layering_number: str  # [+-][0-9] or 0
    main_page_height: int  # This is the height used on the accessory page based on the height we declare to be. I dont think we'll need a main page height
    accessory_page_height: int = None

    @property
    def accessory_string(self):
        return f'{{"name" : "{self.name}", "group" : "{self.group}", "path" : "{self.image.clean_path}", "layer" : "{self.layering_number}", "main_height" : {self.main_page_height}, "access_height" : {self.accessory_page_height}}}, '

    @property
    def bare_accessory_string(self):
        return f'{{"path" : "{self.image.clean_path}","layer" :  "{self.layering_number}","main_height" :  {self.main_page_height}}}, '


@dataclass
class Pose:
    """Holds a pose's name, outfits and faces"""

    path: str
    name: str
    outfits: list[
        tuple[ImagePath, list[Accessory]]  # This will probably need another list of accessories for the on stuff
    ]  # Group, image, layering, outfit view height, accessory view height
    faces: tuple[ImagePath]
    # accessories_name: list[str]
    # outfit_accessories: dict[str, list[Accessory]]
    default_outfit: ImagePath
    default_accessories: list[Accessory]
    face_height: int = None

    @property
    def formatted_outfit_output(self):
        accessory_strings = []
        outfit_strings = []
        for x in self.outfits:
            accessory_strings.extend(y.accessory_string for y in x[1])
            outfit_strings.append(f'["{x[0].clean_path}", [{",".join(accessory_strings)}]]')
            accessory_strings.clear()
        return f"[{','.join(outfit_strings)}]"

    @property
    def faces_escaped(self):
        return [html.escape(x.clean_path.replace("#", "%23")) for x in self.faces]

    @property
    def face_path(self):
        return self.faces[0].folder_path

    @property
    def outfit_path(self):
        return self.outfits[0][0].folder_path

    @property
    def full_default_outfit(self):
        return os.path.join(self.path, self.default_outfit.path)

    def accessory_images(self):
        return [x.image for x in self.default_accessories]

    @property
    def get_imagebox_faces(self) -> CropBox:
        return CropBox.bbox_from_multiple_pil((x.cropbox for x in self.faces))

    @property
    def outfit_bbox(self):
        ff_box = self.get_imagebox_faces
        face_height = ff_box.bottom if ff_box is not None else 0
        self.face_height = face_height
        boundary_boxes = []
        crop_image = Image.open(self.full_default_outfit)
        backup_box = crop_image.getbbox()
        if crop_image.mode != "RGBA":
            crop_image = crop_image.convert("RGBA")
        crop_image = crop_image.split()[-1].crop((0, 0, crop_image.width, int(face_height)))
        c_bbox = crop_image.getbbox()
        if c_bbox is not None:
            boundary_boxes.append(c_bbox)
        if ff_box is not None:
            boundary_boxes.append((ff_box))
        c_bbox = crop_image.getbbox()
        if c_bbox is not None:
            boundary_boxes.append(c_bbox)
        for accessory in self.accessory_images():
            accessory_image = Image.open(accessory.path).convert("RGBA").split()[-1]
            accessory_image = accessory_image.crop((0, 0, accessory_image.width, int(face_height)))
            a_bbox = accessory_image.getbbox()
            if a_bbox is not None:
                boundary_boxes.append(a_bbox)
        if not boundary_boxes:
            boundary_boxes.append(backup_box)

        return CropBox.bbox_from_multiple_pil(boundary_boxes)


class Character(NamedTuple):
    """Holds a character name along with a list of Pose objects"""

    name: str
    poses: list[Pose]
    max_height_multiplier: float

    def __repr__(self):
        builder = f'"{self.name}": {{"name": "{self.name}", "poses" :{{'
        for pose in self.poses:
            print(f"Creating: {self.name} {pose.name}")
            boundsBox = pose.outfit_bbox
            faceBoundsBox = (
                int(pose.face_height * self.max_height_multiplier) if pose.face_height != 0 else boundsBox.bottom
            )
            acc = "".join(x.bare_accessory_string for x in pose.default_accessories)
            builder += f'"{pose.name}" : {{"max_face_height": {faceBoundsBox}, "face_path": "{pose.face_path}", "faces": {pose.faces_escaped}, '
            builder += f'"outfit_path": "{pose.outfit_path}", "default_outfit" : "{pose.default_outfit.clean_path}", '
            builder += f'"default_accessories" : [ {acc}  ], '
            builder += f'"default_left_crop" : {boundsBox.left}, "default_right_crop" : {boundsBox.right},"default_top_crop" : {boundsBox.top}, "outfits": {pose.formatted_outfit_output}}}, '
        return builder + "}},"
