"Classes for the parsed characters. These classes do not read the file system and must have all relevant information passed in."
import html
import re
from math import ceil
from dataclasses import dataclass, field
from typing import ClassVar, DefaultDict, Literal, NamedTuple


class CropBox(NamedTuple):
    "Holds the max amount of pixels that can be trimmed from an image."
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def cropbox_from_multiple_images(cls, bounds_boxes: list[tuple[int, int, int, int]]):
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


@dataclass(slots=True)
class ImagePath:
    """Hold an images location, width and height and maximum amount it can be cropped"""

    path: str
    width: int
    height: int
    cropbox: CropBox

    @property
    def clean_path(self) -> str:
        """Returns the path from under the defining folder (Outfits/faces)"""
        return re.sub(
            "characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/",
            "",
            self.path,
        )

    @property
    def folder_path(self) -> str:
        """Returns the path from before including the defining folder"""
        return re.sub(
            "(characters/[^/]+/[^/]+/(outfits|faces/face|faces/mutations)/)(.*)",
            "\\1",
            self.path,
        )

    @property
    def file_name(self) -> str:
        "Returns the file name"
        return self.path.split("/")[-1]


@dataclass(slots=True)
class OutfitImagePath(ImagePath):
    "Typing class"
    off_accessories: list[ImagePath]
    on_accessories: list[ImagePath]


class Face(ImagePath):
    "Typing class"


class Blush(ImagePath):
    "Typing class"


@dataclass
class Accessory:
    "Holds information about an accessory"
    name: str
    state: str | None  # Can be None
    image: ImagePath
    layering_number: str  # [+-][0-9] or 0
    main_page_height: int
    accessory_page_height: int = None

    @property
    def is_face(self):
        "Returns True if the accessory path contains the faces folder"
        return "/faces/" in self.image.folder_path

    @property
    def is_pose_level_accessory(self):
        "Returns True if the accessory is a pose level accessory, which contains acc_"
        return False if self.is_face else "/outfits/acc_" in self.image.path.lower()

    @property
    def full_json(self) -> str:
        "Full JSON output for the accessory"
        return (
            f'{{"name" : "{self.name}", "state" : "{self.state}", "path" : "{self.image.path}", "layer" : "{self.layering_number}",'
            + f' "main_height" : {self.main_page_height}, "access_height" : {self.accessory_page_height},'
            + f' "is_face" : {str(self.is_face).lower()}}}'
        )

    @property
    def default_accessory_json(self) -> str:
        "Returns json that is used when the default outfit is needed"
        return f'{{"path" : "{self.image.clean_path}","layer" : "{self.layering_number}","main_height" : {self.main_page_height}}}, '

    @property
    def accessory_picker_json(self) -> str:
        "Returns json that should be used on the accessory picker list"
        return f'{{"name" : "{self.name}", "state" : "{self.state}","is_face" : {str(self.is_face).lower()},}}, '

    @property
    def compare_name(self) -> tuple[str, str | None]:
        "Returns a tuple of the name and state"
        return self.name, self.state

    @classmethod
    def create_accessory_from_imagepath(cls, ouftit, imagePath, is_default=False):
        def get_name_for_accessory(image: ImagePath) -> str:
            "Calculates the name of the accessory."
            if is_default:
                return ""
            if image.clean_path.startswith("acc_"):
                acc_folder = image.clean_path.split("/")[0].replace("acc_", "")
            else:
                acc_folder = image.clean_path.split("/")[-2]
            return re.split("[+-]", acc_folder)[0]

        def get_state_for_accessory(image: ImagePath) -> str:
            "Calculates the state for the given accessory."
            if is_default:
                return ""
            acc_file = image.clean_path.split("/")[-1]
            if not acc_file.startswith("on"):
                return ""
            if "on." in acc_file:
                return ""
            return acc_file.split("_", maxsplit=1)[1].rsplit(".", 1)[0]

        def get_layering_for_accessory(image: ImagePath) -> str:
            "Checks if the accessory has a layer other than 0"
            if image.clean_path.startswith("acc_"):
                acc_folder = image.clean_path.split("/")[0]
            else:
                acc_folder = image.clean_path.split("/")[-2]
            return acc_folder[-2:] if acc_folder[-2] in ("+", "-") else "0"

        def get_scaled_image_height(outfit: ImagePath | Outfit, accessory: ImagePath, page_height: int) -> int:
            "Find the height to be display on based on the outfit height and page height"
            height = outfit.height if isinstance(outfit, ImagePath) else outfit.path.height
            return round((accessory.height / height) * page_height)

        return cls(
            get_name_for_accessory(imagePath),
            get_state_for_accessory(imagePath),
            imagePath,
            get_layering_for_accessory(imagePath),
            get_scaled_image_height(ouftit, imagePath, Pose.HEIGHT_OF_MAIN_PAGE),
            None if is_default else get_scaled_image_height(ouftit, imagePath, Pose.HEIGHT_OF_ACCESSORY_PAGE),
        )


@dataclass
class Outfit:
    "Holds the outfit and the accessories for given outfit"
    path: ImagePath
    off_accessories: list[Accessory] = field(default_factory=list, init=False)
    on_accessories: list[Accessory] = field(default_factory=list, init=False)

    def order_accessories(self):
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

    def add_on_accessories(self, list_imagepaths: list[ImagePath], inverse_accessories: DefaultDict[str, list[str]]):
        "Create on accessories for this outfit. This will also remove any accessories that are should not be shown"
        self.on_accessories.extend(Accessory.create_accessory_from_imagepath(self, x) for x in list_imagepaths)
        out_name = self.path.file_name.split(".")[0]
        if out_name in inverse_accessories:
            access_to_remove = []
            for access in self.on_accessories:
                if access.is_pose_level_accessory and access.name in inverse_accessories[out_name]:
                    access_to_remove.append(access)
            for access in access_to_remove:
                self.on_accessories.remove(access)
        self.order_accessories()

    def add_off_accessories(self, list_imagepaths: list[ImagePath]):
        "Create on accessories for this outfit."
        self.off_accessories.extend(Accessory.create_accessory_from_imagepath(self, x) for x in list_imagepaths)
        self.order_accessories()

    @property
    def accessory_picker_json_entries(self):
        """
        Returns all the accessory picker list entries for any accessories in this outfit.
        This will also make sure that if an accessory has both a face and a outfit accessory, that accessory will use the is_face version.
        """
        accessory_names: dict[str, Accessory]
        accessory_names = {}
        for accessory in self.on_accessories:
            if accessory.compare_name not in accessory_names:
                accessory_names[accessory.compare_name] = accessory
            elif not accessory_names[accessory.compare_name].is_face and accessory.is_face:
                accessory_names[accessory.compare_name] = accessory
        return {accessory.accessory_picker_json for accessory in accessory_names.values()}

    @property
    def outfit_json(self) -> str:
        "Return the outfit json"
        return (
            f'{{"path" : "{html.escape(self.path.clean_path)}", '
            + f'"off_accessories" : [{",".join(y.full_json for y in self.off_accessories)}], '
            + f'"on_accessories" : [{",".join(y.full_json for y in self.on_accessories)}]}}'
        )


@dataclass
class Pose:
    "Holds a pose's name, outfits and faces"
    path_to_pose: str
    pose_name: str
    outfits: list[Outfit]
    faces: list[Face]
    blushes: list[Blush]
    default_outfit: ImagePath
    default_accessories: list[Accessory] = field(default_factory=list, init=False)
    facing_direction: Literal["left", "right"] = "left"
    HEIGHT_OF_MAIN_PAGE: ClassVar[int] = 200
    HEIGHT_OF_ACCESSORY_PAGE: ClassVar[int] = 400

    def add_default_accessories(self, list_imagepaths: list[ImagePath]):
        "Create the default accessories for the pose"
        self.default_accessories.extend(
            Accessory.create_accessory_from_imagepath(self.default_outfit, x, is_default=True) for x in list_imagepaths
        )

    @property
    def accessory_picker_json_entries(self):
        "Return a sorted list of all accessories for the accessory picker list"
        accessories_name = []
        for outfit in self.outfits:
            accessories_name.extend(outfit.accessory_picker_json_entries)
        return sorted(set(accessories_name))

    @property
    def face_height(self):
        "Return the height of the face image"
        return self.get_image_box_faces.bottom if self.get_image_box_faces is not None else 0

    @property
    def swap_direction(self):
        "Return if the character is facing to the right."
        return str(self.facing_direction == "right").lower()

    @property
    def formatted_outfit_json(self) -> str:
        "Return the json for all the outfits in a json list"
        return f"[{','.join(x.outfit_json for x in self.outfits)}]"

    @property
    def faces_escaped(self) -> list[str]:
        "Return the file path to each given face"
        return [x.path for x in self.faces]

    @property
    def blushes_escaped(self) -> list[str]:
        "Return the file path to each given blush"
        return [x.path for x in self.blushes]

    @property
    def outfit_path(self) -> str:
        "Return the folder path of the outfits, using the first outfit."
        return self.outfits[0].path.folder_path

    @property
    def get_image_box_faces(self) -> CropBox:
        "Return the max crop of all faces"
        return CropBox.cropbox_from_multiple_images((x.cropbox for x in self.faces))

    @property
    def accessory_view_width(self) -> int:
        "Return the width of the accessory view"
        return ceil(max((x.path.width * (self.HEIGHT_OF_ACCESSORY_PAGE / x.path.height) for x in self.outfits)))

    @property
    def expression_view_bounds_box(self) -> None | CropBox:
        "Return the max crop used for expression sheets"
        boundary_boxes = []
        c_bbox = self.default_outfit.cropbox
        if c_bbox is not None:
            boundary_boxes.append(c_bbox)
        if self.get_image_box_faces is not None:
            boundary_boxes.append((self.get_image_box_faces))
        for accessory in self.default_accessories:
            a_bbox = accessory.image.cropbox
            if a_bbox is not None:
                boundary_boxes.append(a_bbox)

        return CropBox.cropbox_from_multiple_images(boundary_boxes)

    def json_output(self, max_height_multiplier: float):
        "Output the pose class as a JSON Object entry. This output with trailing commas"
        builder = ""
        bounds_box = self.expression_view_bounds_box
        face_bounds_box = int(self.face_height * max_height_multiplier) if self.face_height != 0 else bounds_box.bottom
        acc = "".join(x.default_accessory_json for x in self.default_accessories)
        builder += (
            f'"{self.pose_name}" : {{"max_face_height": {face_bounds_box}, '
            + f'"faces": {self.faces_escaped}, "blushes": {self.blushes_escaped}, '
        )
        builder += f'"max_accessory_outfit_width" : {self.accessory_view_width}, '
        builder += f'"outfit_path": "{self.outfit_path}", "default_outfit" : "{self.default_outfit.clean_path}", '
        builder += f'"default_accessories" : [ {acc} ], '
        if self.swap_direction:
            builder += f'"swap_direction" : {self.swap_direction}, '
        builder += (
            f'"default_left_crop" : {bounds_box.left}, "default_right_crop" : {bounds_box.right},'
            + f'"default_top_crop" : {bounds_box.top},"accessory_names" : [{"".join(self.accessory_picker_json_entries)}], '
            + f'"outfits": {self.formatted_outfit_json}}}, '
        )
        return builder


class Character(NamedTuple):
    """Holds a character name along with a list of Pose objects"""

    name: str
    poses: list[Pose]
    max_height_multiplier: float

    def json_output(self):
        "Output the character class as a JSON Object entry. This output with trailing commas"
        builder = f'"{self.name}": {{ "poses" :{{'
        for pose in self.poses:
            print(f"Creating: {self.name} {pose.pose_name}")
            builder += pose.json_output(self.max_height_multiplier)
        return builder + "}},"
