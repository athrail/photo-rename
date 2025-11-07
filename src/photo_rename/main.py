from typing import List
from os.path import normpath, join, isfile, splitext
from os import listdir, rename
from datetime import datetime

import typer
from PIL import Image
from rich import print
from rich.console import Console
from rich.table import Table

EXIF_DATETIME_TAG = 0x132
EXIF_DATETIME_ORIG_TAG = 0x9003
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
# OUTPUT_DATE_FORMAT = "%Y_%m_%d_%H%M%S"
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
TABLE_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"

console = Console()


class RenameEntry:
    filename: str
    date: datetime
    output: str

    def __init__(self, filename: str, date: datetime) -> None:
        self.filename = filename
        self.date = date
        self.output = "_".join([date.strftime(OUTPUT_DATE_FORMAT), filename])


def grab_image_datetime(path: str) -> datetime | None:
    with Image.open(path) as image:
        exifdata = image.getexif()
        date = exifdata.get(EXIF_DATETIME_ORIG_TAG)
        if date is None:
            date = exifdata.get(EXIF_DATETIME_TAG)
            if date is None:
                return None

        return datetime.strptime(date, EXIF_DATE_FORMAT)


__version__ = "0.1.0"

entries: List[RenameEntry] = []


def print_rename_table():
    print("[bold green]Following renames will be performed[/bold green]")
    table = Table(title="Rename list")
    table.add_column("Original file")
    table.add_column("Date taken")
    table.add_column("Renamed file")

    for entry in entries:
        table.add_row(
            entry.filename, entry.date.strftime(TABLE_DATE_FORMAT), entry.output
        )

    console.print(table)
    print()


def main(input: str):
    print(f"[bold green]Welcome to photo-rename version {__version__}[/bold green]")
    input = normpath(input)
    print(f"[blue]Looking for photos at:[/blue] [bold yellow]{input}[/bold yellow]")

    for item in listdir(input):
        if isfile(join(input, item)):
            _, file_extension = splitext(item)
            if file_extension.lower() in (".jpg", ".jpeg"):
                photo_path = join(input, item)
                date = grab_image_datetime(photo_path)
                if date is not None:
                    print(
                        f"Found date for file [bold yellow]{photo_path}[/bold yellow] - {date}"
                    )
                    entries.append(RenameEntry(item, date))
                else:
                    print(
                        f'[bold red]Photo at [bold yellow]{photo_path}[/bold yellow] doesn"t contain date information[/bold red]'
                    )

    if len(entries) < 1:
        print(
            "[bold yellow]No files that can be renamed found. Exiting...[/bold yellow]"
        )
        return

    print_rename_table()

    confirm = typer.confirm(
        "Do you want to continue with rename? (this is irreversible so make backup)"
    )
    if not confirm:
        print("[bold yellow]Aborting rename[/bold yellow]")
        return

    try:
        for entry in entries:
            rename(join(input, entry.filename), join(input, entry.output))
            print(
                f"[green bold]Renamed [bold yellow]{entry.filename}[/bold yellow] to [bold yellow]{entry.output}[/bold yellow] successfuly[/green bold]"
            )
    except Exception as e:
        print(
            f'[bold red]Couldn"t rename one of the files due to error: {e}[/bold red]'
        )
        return

    print("[bold blue]All files renamed.[/bold blue]")


def main_cli():
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
