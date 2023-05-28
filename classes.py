import html
import os
import re
from dataclasses import dataclass
from typing import NamedTuple, Tuple, Iterable

from PIL import Image


def clean_start_end_string(cleaning_string: str, chars_to_clean: Iterable[str] = ("/", "\\")):
    for x in chars_to_clean:
        cleaning_string = cleaning_string.strip(x)
    for x in reversed(chars_to_clean):
        cleaning_string = cleaning_string.strip(x)
    return cleaning_string


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

    @property
    def face_folder_path(self):
        return re.sub(
            "(characters/[^/]+/[^/]+/faces/)(.*)",
            "\\2",
            self.path,
        ).rsplit(
            "/", maxsplit=1
        )[0]

    def __repr__(self) -> str:
        return f'"{self.clean_path}"'

    def __str__(self) -> str:
        return f'"{self.clean_path}"'


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


@dataclass(unsafe_hash=True)
class Pose:
    """Holds a pose's name, outfits and faces"""

    drive_path: str
    pose_name: str
    outfits: list[Tuple[ImagePath, list[(ImagePath, str, int)]]]
    faces: dict[str : list[ImagePath]]
    # default_faces: str # Blanked out until I can make the changes to face
    default_outfit: ImagePath
    default_accessories: list[
        (ImagePath, str, int)
    ]  # The STR is the layering, [+-][0-9] or 0. The int is the height to use on the main page
    face_height: int = None

    @property
    def formatted_outfit_output(self):
        accessory_strings = []
        outfit_strings = []
        for x in self.outfits:
            accessory_strings.extend(f'["{y[0].clean_path}", "{y[1]}", {y[2]}]' for y in x[1])
            outfit_strings.append(f'["{x[0].clean_path}", [{",".join(accessory_strings)}]]')
            accessory_strings.clear()
        return f"[{','.join(outfit_strings)}]"

    @property
    def faces_escaped(self):
        return [html.escape(x.clean_path.replace("#", "%23")) for x in self.faces]

    @property
    def face_path(self):
        return clean_start_end_string(self.faces[0].face_folder_path)

    @property
    def outfit_path(self):
        return clean_start_end_string(self.outfits[0][0].folder_path.split("outfits")[-1])

    @property
    def full_default_outfit(self):
        return self.default_outfit.path

    @property
    def full_accessories_list(self):
        return [(os.path.join(self.drive_path, x.path), y, z) for x, y, z in self.default_accessories]

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
        for accessory, _, _ in self.full_accessories_list:
            accessory_image = Image.open(accessory).convert("RGBA").split()[-1]
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

    def build_pose_path(self, pose: str):
        return "/".join(["characters", self.name, pose, ""])

    def __repr__(self):
        builder = f'"{self.name}": {{"name": "{self.name}", "poses" :{{'
        for pose in self.poses:
            print(f"Creating: {self.name} {pose.pose_name}")
            boundsBox = pose.outfit_bbox
            faceBoundsBox = (
                int(pose.face_height * self.max_height_multiplier) if pose.face_height != 0 else boundsBox.bottom
            )
            acc = "".join(f'[{str(x)}, "{y}", {z}], ' for x, y, z in pose.default_accessories)
            builder += f'"{pose.pose_name}" : {{"pose_path": "{self.build_pose_path(pose.pose_name)}", "max_face_height": {faceBoundsBox}, "face_path": "{pose.face_path}", "faces": {pose.faces_escaped}, '
            builder += f'"outfit_path": "{pose.outfit_path}", "default_outfit" : {pose.default_outfit}, '
            builder += f'"default_accessories" : [ {acc}  ], '
            builder += f'"default_left_crop" : {boundsBox.left}, "default_right_crop" : {boundsBox.right},"default_top_crop" : {boundsBox.top}, "outfits": {pose.formatted_outfit_output}}}, '
        return builder + "}},"
