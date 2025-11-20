from typing import List
from os.path import normpath, join
from os import rename

import typer
from rich import print
from rich.console import Console
from rich.table import Table

import photo_rename.lib as lib

console = Console()


def print_rename_table(entries: List[lib.RenameEntry]):
    print("[bold green]Following renames will be performed[/bold green]")
    table = Table(title="Rename list")
    table.add_column("Original file")
    table.add_column("Date taken")
    table.add_column("Renamed file")

    for entry in entries:
        table.add_row(
            entry.filename, entry.date.strftime(lib.TABLE_DATE_FORMAT), entry.output
        )

    console.print(table)
    print()


def main(input: str):
    print(f"[bold green]Welcome to photo-rename version {lib.__version__}[/bold green]")
    input = normpath(input)
    print(f"[blue]Looking for photos at:[/blue] [bold yellow]{input}[/bold yellow]")

    entries = lib.traverse_dir_for_images(input)

    if len(entries) < 1:
        print(
            "[bold yellow]No files that can be renamed found. Exiting...[/bold yellow]"
        )
        return

    print_rename_table(entries)

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
