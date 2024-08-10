"All classes used in this project"
import html
import os
import re
from math import ceil
from dataclasses import dataclass, field
from typing import NamedTuple
from sort_functions import face_sort_imp

from PIL import Image


HEIGHT_OF_MAIN_PAGE = 200
HEIGHT_OF_ACCESSORY_PAGE = 400


class CropBox(NamedTuple):
    "Holds the max amount of pixels that can be trimmed from an image."
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def bbox_from_multiple_pil(cls, bounds_boxes: list[tuple[int, int, int, int]]):
        """Given a list of tuples that have 4 ints, create a cropbox that contains the maximum value that can be trimmed from the image.
        Left and top use the min instead of max as the image is being trimmed from the top left.
        """
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


class ImagePath(NamedTuple):
    """Hold an images location, width and height"""

    path: str
    width: int
    height: int
    cropbox: CropBox

    @property
    def clean_path(self) -> str:
        """Used for compression.
        Removes the first part of the full path (From the html file directory) and leaves only the path inside the folder
        characters/a/b/outfits/dress.png -> dress.png
        """
        return re.sub(
            "characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/",
            "",
            self.path,
        )

    @property
    def folder_path(self) -> str:
        """Does the opposite of clean path. Removes the path inside the folder and returns the before path"""
        return re.sub(
            "(characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/)(.*)",
            "\\1",
            self.path,
        )

    @property
    def file_name(self) -> str:
        "Returns the file name"
        return self.path.split("/")[-1]


@dataclass
class Accessory:
    "Holds information about an accessory"
    name: str
    state: str | None  # Can be None
    image: ImagePath
    layering_number: str  # [+-][0-9] or 0
    main_page_height: int
    accessory_page_height: int = None
    is_face: bool = field(init=False, repr=False)
    is_pose_level_accessory: bool = field(init=False, repr=False)

    def __post_init__(self):
        self.is_face = "/faces/" in self.image.folder_path
        self.is_pose_level_accessory = False if self.is_face else "/outfits/acc_" in self.image.path.lower()

    @property
    def full_json(self) -> str:
        "Full JSON output for the accessory, used for the selected character page"
        return (
            f'{{"name" : "{self.name}", "state" : "{self.state}", "path" : "{self.image.path}", "layer" : "{self.layering_number}",'
            + f' "main_height" : {self.main_page_height}, "access_height" : {self.accessory_page_height},'
            + f' "is_face" : {str(self.is_face).lower()}}}'
        )

    @property
    def default_accessory_json(self) -> str:
        "Short version of the JSON, used when no character is selected"
        return f'{{"path" : "{self.image.clean_path}","layer" : "{self.layering_number}","main_height" : {self.main_page_height}}}, '

    @property
    def proper_name_json(self) -> str:
        "Short version of the JSON, used for the accessory picker list"
        return f'{{"name" : "{self.name}", "state" : "{self.state}","is_face" : {str(self.is_face).lower()},}}, '

    @property
    def compare_name(self) -> tuple[str, str | None]:
        "Returns a tuple of the name and state"
        return self.name, self.state


@dataclass
class Outfit:
    "Holds the outfit and the accessories for given outfit"
    path: ImagePath
    off_accessories: list[Accessory] = field(default_factory=list)
    on_accessories: list[Accessory] = field(default_factory=list)

    def __post_init__(self):
        "If a pose level accessory and outfit level accessory with the same name are both present, remove the pose level one"
        pose_level_on_accessories: list[Accessory] = [x for x in self.on_accessories if x.is_pose_level_accessory]
        pose_level_on_accessories_name: list[str] = [x.name for x in pose_level_on_accessories]
        for accessory in list(x for x in self.on_accessories if not x.is_pose_level_accessory):
            if accessory.name in pose_level_on_accessories_name:
                i = pose_level_on_accessories_name.index(accessory.name)
                self.on_accessories.remove(pose_level_on_accessories[i])
                pose_level_on_accessories_name.remove(accessory.name)
        pose_level_off_accessories: list[Accessory] = [x for x in self.off_accessories if x.is_pose_level_accessory]
        pose_level_off_accessories_name: list[str] = [x.name for x in pose_level_off_accessories]
        for accessory in list(x for x in self.off_accessories if not x.is_pose_level_accessory):
            if accessory.name in pose_level_off_accessories_name:
                i = pose_level_off_accessories_name.index(accessory.name)
                self.off_accessories.remove(pose_level_off_accessories[i])
                pose_level_off_accessories_name.remove(accessory.name)

    @property
    def accessory_names(self):
        """
        Get the list of accessory names for the outfit and make sure any face accessories are marked as such.
        An accessory can be both a face and outfit accessory.
        In this case, It must be counted as a is_face accessory for the deselection to work correctly
        """
        accessory_names: dict[str, Accessory]
        accessory_names = {}
        for accessory in self.on_accessories:
            if accessory.compare_name not in accessory_names:
                accessory_names[accessory.compare_name] = accessory
            elif not accessory_names[accessory.compare_name].is_face and accessory.is_face:
                accessory_names[accessory.compare_name] = accessory
        return {accessory.proper_name_json for accessory in accessory_names.values()}

    @property
    def outfit_string(self) -> str:  # Escape # for outfits
        "Return the outfit json"
        return (
            f'{{"path" : "{html.escape(self.path.clean_path)}", '
            + f'"off_accessories" : [{",".join(y.full_json for y in self.off_accessories)}], '
            + f'"on_accessories" : [{",".join(y.full_json for y in self.on_accessories)}]}}'
        )


@dataclass
class Pose:
    "Holds a pose's name, outfits and faces"
    path: str
    name: str
    outfits: list[Outfit]
    faces: list[ImagePath]
    blushes: list[ImagePath]
    default_outfit: ImagePath
    default_accessories: list[Accessory]
    face_height: int = None
    accessories_name: list[str] = field(init=False, repr=False)

    def __post_init__(self):
        self.accessories_name = []
        for outfit in self.outfits:
            self.accessories_name.extend(outfit.accessory_names)
        self.accessories_name = sorted(set(self.accessories_name))
        self._combine_faces()

    def _combine_faces(self):
        """
        Add missing faces to to blushes and faces
        """
        if not self.blushes:
            return
        file_names_faces = [x.file_name for x in self.faces]
        file_names_blushes = [x.file_name for x in self.blushes]
        for index, x in enumerate(file_names_blushes):
            if x not in file_names_faces:
                self.faces.append(self.blushes[index])
        for index, x in enumerate(file_names_faces):
            if x not in file_names_blushes:
                self.blushes.append(self.faces[index])
        self.faces.sort(key=face_sort_imp)
        self.blushes.sort(key=face_sort_imp)

    @property
    def formatted_outfit_output(self) -> str:
        "Return each outfits json"
        return f"[{','.join(x.outfit_string for x in self.outfits)}]"

    @property
    def faces_escaped(self) -> list[str]:
        "Return the file path to each given face"
        return [x.path for x in self.faces]

    @property
    def blushes_escaped(self) -> list[str]:
        "Return the file path to each given blush"
        return [x.path for x in self.blushes]

    @property
    def face_path(self) -> str:
        "Returns the folder path of the faces, using the first face"
        return self.faces[0].folder_path

    @property
    def outfit_path(self) -> str:
        "Return the folder path of the outfits, using the first outfit."
        return self.outfits[0].path.folder_path

    @property
    def full_default_outfit(self) -> str:
        "Return the full path of the default outfit"
        return os.path.join(self.path, self.default_outfit.path)

    def accessory_images(self) -> list[ImagePath]:
        "Return the image object for each default accessory"
        return [x.image for x in self.default_accessories]

    @property
    def get_image_box_faces(self) -> CropBox:
        "Return the max crop of all faces"
        return CropBox.bbox_from_multiple_pil((x.cropbox for x in self.faces))

    @property
    def accessory_view_width(self) -> int:
        "Return the width of the accessory view"
        return ceil(max((x.path.width * (HEIGHT_OF_ACCESSORY_PAGE / x.path.height) for x in self.outfits)))

    @property
    def outfit_bbox(self) -> None | CropBox:
        "Return the max crop used for expression sheets"
        ff_box = self.get_image_box_faces
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
            accessory_image = Image.open(os.path.join(self.path, accessory.path)).convert("RGBA").split()[-1]
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
            bounds_box = pose.outfit_bbox
            face_bounds_box = (
                int(pose.face_height * self.max_height_multiplier) if pose.face_height != 0 else bounds_box.bottom
            )
            acc = "".join(x.default_accessory_json for x in pose.default_accessories)
            builder += (
                f'"{pose.name}" : {{"max_face_height": {face_bounds_box}, '
                + f'"faces": {pose.faces_escaped}, "blushes": {pose.blushes_escaped}, '
            )
            builder += f'"max_accessory_outfit_width" : {pose.accessory_view_width}, '
            builder += f'"outfit_path": "{pose.outfit_path}", "default_outfit" : "{pose.default_outfit.clean_path}", '
            builder += f'"default_accessories" : [ {acc} ], '
            builder += (
                f'"default_left_crop" : {bounds_box.left}, "default_right_crop" : {bounds_box.right},'
                + f'"default_top_crop" : {bounds_box.top},"accessory_names" : [{"".join(pose.accessories_name)}], '
                + f'"outfits": {pose.formatted_outfit_output}}}, '
            )
        return builder + "}},"
