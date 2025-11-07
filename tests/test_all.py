from datetime import datetime

from PIL import Image

from photo_rename.main import (
    EXIF_DATE_FORMAT,
    EXIF_DATETIME_TAG,
    EXIF_DATETIME_ORIG_TAG,
    OUTPUT_DATE_FORMAT,
    RenameEntry,
    grab_image_datetime,
)

test_image_path = "test_image.jpg"


def test_something():
    file = "some_file.jpg"
    date = datetime.now()
    date_output = date.strftime(OUTPUT_DATE_FORMAT)

    entry = RenameEntry(file, date)
    assert entry.filename == file
    assert entry.date == date
    assert entry.output == "_".join([date_output, file])


def overwrite_image_exif_tag(fp, tag, value):
    image = Image.open(fp)
    exifdata = image.getexif()
    exifdata[tag] = value
    image.save(test_image_path, exif=exifdata)
    image.close()


def delete_image_exif_tag(fp, tag):
    image = Image.open(fp)
    exifdata = image.getexif()
    del exifdata[tag]
    image.save(test_image_path, exif=exifdata)
    image.close()


def test_date_extraction_original_date():
    date = datetime.now()
    overwrite_image_exif_tag(
        test_image_path, EXIF_DATETIME_ORIG_TAG, date.strftime(EXIF_DATE_FORMAT)
    )

    date_read = grab_image_datetime(test_image_path)
    assert date_read is not None
    assert date_read.day == date.day
    assert date_read.month == date.month
    assert date_read.year == date.year
    assert date_read.hour == date.hour
    assert date_read.minute == date.minute
    assert date_read.second == date.second


def test_date_extraction_modify_date():
    date = datetime.now()
    overwrite_image_exif_tag(
        test_image_path, EXIF_DATETIME_TAG, date.strftime(EXIF_DATE_FORMAT)
    )

    date_read = grab_image_datetime(test_image_path)
    assert date_read is not None
    assert date_read.day == date.day
    assert date_read.month == date.month
    assert date_read.year == date.year
    assert date_read.hour == date.hour
    assert date_read.minute == date.minute
    assert date_read.second == date.second


def test_date_extraction_no_date():
    delete_image_exif_tag(test_image_path, EXIF_DATETIME_TAG)
    delete_image_exif_tag(test_image_path, EXIF_DATETIME_ORIG_TAG)

    date_read = grab_image_datetime(test_image_path)
    assert date_read is None
