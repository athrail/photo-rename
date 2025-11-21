from datetime import datetime
from typing import List
from pathlib import Path

from PIL import Image


EXIF_DATETIME_TAG = 0x132
EXIF_DATETIME_ORIG_TAG = 0x9003
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
# OUTPUT_DATE_FORMAT = "%Y_%m_%d_%H%M%S"
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
TABLE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

__version__ = "0.2.0"


class Config:
    def __init__(self) -> None:
        self.output_date_format = OUTPUT_DATE_FORMAT
        self.table_date_format = TABLE_DATE_FORMAT


class RenameEntry:
    def __init__(
        self,
        filename: str,
        date: datetime,
        output_date_format: str = OUTPUT_DATE_FORMAT,
        rename: bool = True,
    ) -> None:
        self.filename = filename
        self.date = date
        self.output = "_".join([date.strftime(output_date_format), filename])
        self.rename = rename


def grab_image_datetime(path: Path) -> datetime | None:
    with Image.open(path) as image:
        exifdata = image.getexif()
        date = exifdata.get(EXIF_DATETIME_ORIG_TAG)
        if date is None:
            date = exifdata.get(EXIF_DATETIME_TAG)
            if date is None:
                return None

        return datetime.strptime(date, EXIF_DATE_FORMAT)


def traverse_dir_for_images(
    location: str, config: Config = Config()
) -> List[RenameEntry]:
    path = Path(location)
    if not path.exists():
        return []

    entries = []

    for item in path.iterdir():
        if Path.is_file(item):
            if item.suffix.lower() in (".jpg", ".jpeg"):
                if (date := grab_image_datetime(item)) is not None:
                    entries.append(
                        RenameEntry(item.name, date, config.output_date_format)
                    )

    return entries
