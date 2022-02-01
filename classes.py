import html
import os
from typing import NamedTuple

from PIL import Image


class ImagePath(NamedTuple):
    """Hold an images location, width and height"""

    path: str
    width: int
    height: int

    def __repr__(self) -> str:
        return f'"{self.path}"'


class CropBox(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def bbox_from_from_pil(cls, bounds_box: tuple[int, int, int, int]):

        return cls(bounds_box[0], bounds_box[1], bounds_box[2], bounds_box[3])

    @classmethod
    def bbox_from_multple_pil(cls, bounds_boxes: list[tuple[int]]):
        q = list(bounds_boxes)
        while None in q:
            q.remove(None)
        if not q:
            return None
        return cls(
            min(x[0] for x in q),
            min(x[1] for x in q),
            max(x[2] for x in q),
            max(x[3] for x in q),
        )

    def return_bbox(self, other: "CropBox"):
        return CropBox(
            min(self.left, other.left),
            min(self.top, other.top),
            max(self.right, other.right),
            max(self.bottom, other.bottom),
        )

    @staticmethod
    def set_of_bbox_from_pil(bounds_boxes: list[tuple[int]]):
        return {CropBox.bbox_from_from_pil(x) for x in bounds_boxes}


class Pose(NamedTuple):
    """Holds a pose's name, outfits and faces"""

    path: str
    name: str
    outfits: tuple[ImagePath]
    faces: tuple[ImagePath]
    default_outfit: ImagePath
    default_accessories: list[ImagePath]

    @property
    def faces_escaped(self):
        return [html.escape(x.path.replace("#", "%23")) for x in self.faces]

    @property
    def full_default_outfit(self):
        return os.path.join(self.path, self.default_outfit.path)

    @property
    def full_accessories_list(self):
        return [os.path.join(self.path, x.path) for x in self.default_accessories]

    @property
    def get_imagebox_faces(self) -> list[str]:
        return CropBox.bbox_from_multple_pil(
            (
                Image.open(os.path.join(self.path, x.path))
                .convert("RGBA")
                .split()[-1]
                .getbbox()
                for x in self.faces
            )
        )

    @property
    def get_max_imagebox_height(self):
        bbox = CropBox.bbox_from_multple_pil(
            (
                Image.open(os.path.join(self.path, x.path))
                .convert("RGBA")
                .split()[3]
                .getbbox()
                for x in self.faces
            )
        )
        if not bbox:
            return self.max_face_height
        return bbox.bottom

    @property
    def default_outfit_height(self):
        return self.default_outfit

    @property
    def outfit_bbox(self):
        face_height = self.get_max_imagebox_height
        bboxs = []
        crop_image = Image.open(self.full_default_outfit)
        backupbb = crop_image.getbbox()
        if crop_image.mode != "RGBA":
            crop_image = crop_image.convert("RGBA")
        crop_image = crop_image.split()[-1].crop(
            (0, 0, crop_image.width, int(face_height))
        )
        c_bbox = crop_image.getbbox()
        if c_bbox is not None:
            bboxs.append(c_bbox)
        ff_box = self.get_imagebox_faces
        if ff_box is not None:
            bboxs.append((ff_box))
        c_bbox = crop_image.getbbox()
        if c_bbox is not None:
            bboxs.append(c_bbox)
        for accessory in self.full_accessories_list:
            accessory_image = Image.open(accessory).convert("RGBA").split()[-1]
            accessory_image = accessory_image.crop(
                (0, 0, accessory_image.width, int(face_height))
            )
            a_bbox = accessory_image.getbbox()
            if a_bbox is not None:
                bboxs.append(a_bbox)
        if not bboxs:
            bboxs.append(backupbb)

        return CropBox.bbox_from_multple_pil(bboxs)

    @property
    def max_face_height(self):
        """Returns biggest face height"""
        return max(x.height for x in self.faces)

    @property
    def max_face_width(self):
        """Returns biggest face width"""
        return max(x.width for x in self.faces)

    @property
    def max_outfit_height(self):
        """Returns biggest outfit height"""
        return self.default_outfit.height

    @property
    def max_outfit_width(self):
        """Returns biggest outfit width"""
        return self.default_outfit.width


class Character(NamedTuple):
    """Holds a character name along with a list of Pose objects"""

    name: str
    poses: list[Pose]

    def __repr__(self):
        print(f"Creating: {self.name}")
        builder = f'"{self.name}": {{"name": "{self.name}", "poses" :{{'
        for pose in self.poses:
            boundsBox = pose.outfit_bbox
            faceBoundsBox = pose.get_max_imagebox_height
            acc = "".join(str(x) + ", " for x in pose.default_accessories)
            builder += f'"{pose.name}" : {{"max_face_height": {faceBoundsBox}, "faces": {pose.faces_escaped}, '
            builder += f'"default_outfit" : {pose.default_outfit}, '
            builder += f'"default_accessories" : [ {acc}  ], '
            builder += f'"default_left_crop" : {boundsBox.left}, "default_right_crop" : {boundsBox.right},"default_top_crop" : {boundsBox.top}, "outfits": {pose.outfits}}}, '
        return builder + "}},"
