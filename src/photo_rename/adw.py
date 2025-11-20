import sys
from datetime import datetime
from os import close, listdir, rename
from os.path import normpath, join, isfile, splitext
from pathlib import Path
from typing import List

import gi
from PIL import Image

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk, GLib

__version__ = "0.1.0"

EXIF_DATETIME_TAG = 0x132
EXIF_DATETIME_ORIG_TAG = 0x9003
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
# OUTPUT_DATE_FORMAT = "%Y_%m_%d_%H%M%S"
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
TABLE_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"


def grab_image_datetime(path: str) -> datetime | None:
    with Image.open(path) as image:
        exifdata = image.getexif()
        date = exifdata.get(EXIF_DATETIME_ORIG_TAG)
        if date is None:
            date = exifdata.get(EXIF_DATETIME_TAG)
            if date is None:
                return None

        return datetime.strptime(date, EXIF_DATE_FORMAT)


class RenameEntry:
    filename: str
    date: datetime
    output: str

    def __init__(self, filename: str, date: datetime) -> None:
        self.filename = filename
        self.date = date
        self.output = "_".join([date.strftime(OUTPUT_DATE_FORMAT), filename])

    def __repr__(self) -> str:
        return f"{self.filename} -> {self.output}"

    def __str__(self) -> str:
        return f"{self.filename} -> {self.output}"

    def as_list(self):
        return [self.filename, self.date, self.output]


entries: List[RenameEntry] = []


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.set_margin_bottom(20)
        self.main_box.set_margin_top(20)
        self.main_box.set_margin_start(20)
        self.main_box.set_margin_end(20)
        self.set_child(self.main_box)

        self.sidebar = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.VERTICAL, width_request=150
        )
        self.main_box.append(self.sidebar)

        self.btn_open_dir = Gtk.Button(label="Select photo directory")
        self.sidebar.append(self.btn_open_dir)
        self.btn_open_dir.connect("clicked", self.on_open_directory_clicked)

        self.sidebar.append(Gtk.Box(vexpand=True))

        self.btn_about = Gtk.Button(label="About", tooltip_text="Shows about window")
        self.sidebar.append(self.btn_about)
        self.btn_about.connect("clicked", self.show_about)

        self.rename_button = Gtk.Button(label="Rename", visible=False)
        self.rename_button.connect("clicked", self._rename_photos)
        self.sidebar.insert_child_after(self.rename_button, self.btn_open_dir)

        self.content = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.VERTICAL, hexpand=True
        )
        self.main_box.append(self.content)

        self._new_entries_box()
        self.no_entries_label = Gtk.Label(
            label="No entries found, select a directory with images inside",
            margin_top=15,
            margin_bottom=15,
        )
        self.entries_box.append(self.no_entries_label)

        self.dir_dialog = Gtk.FileDialog(
            title="Chose directory",
            modal=True,
        )

    def _new_entries_box(self):
        if hasattr(self, "entries_box") and self.entries_box is not None:
            self.content.remove(self.entries_box)

        self.entries_box = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.VERTICAL, hexpand=True
        )
        self.content.append(self.entries_box)

    def _refresh_entries(self):
        self._new_entries_box()

        if len(entries) > 0:
            self.rename_button.set_visible(True)
            for entry in entries:
                entry_box = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL, hexpand=True
                )

                entry_box.append(
                    Gtk.Label(
                        label=entry.filename,
                        hexpand=True,
                    )
                )

                entry_box.append(
                    Gtk.Label(
                        label=">",
                    )
                )

                entry_box.append(
                    Gtk.Label(
                        label=entry.output,
                        hexpand=True,
                    )
                )

                self.entries_box.append(entry_box)
        else:
            self.entries_box.append(self.no_entries_label)
            self.rename_button.set_visible(False)

    def show_about(self, _):
        dialog = Adw.AboutWindow(
            transient_for=self,
            application_name="Photo Renamer",
            version=__version__,
            developer_name="Krzysztof Lewandowski",
            license_type=Gtk.License.MIT_X11,
            comments="Automatically rename your photos based on EXIF data",
            website="https://github.com/athrail/photo-rename",
            copyright="© 2025 Krzysztof Lewandowski",
        )
        dialog.set_visible(True)

    def on_open_directory_clicked(self, _):
        self.dir_dialog.select_folder(
            parent=self, callback=self.on_open_directory_callback
        )

    def on_open_directory_callback(self, dialog: Gtk.FileDialog, task: Gio.Task):
        if task.had_error():
            return

        file = dialog.select_folder_finish(task)
        if file is None:
            return

        self.selected_dir = file.get_path()
        if self.selected_dir is None:
            return

        entries.clear()

        for item in listdir(self.selected_dir):
            if isfile(join(self.selected_dir, item)):
                _, file_extension = splitext(item)
                if file_extension.lower() in (".jpg", ".jpeg"):
                    photo_path = join(self.selected_dir, item)
                    date = grab_image_datetime(photo_path)
                    if date is not None:
                        entries.append(RenameEntry(item, date))

        self._refresh_entries()

    def _rename_photos(self, _):
        if not hasattr(self, "selected_dir") or self.selected_dir is None:
            print(hasattr(self, "selected_dir"))
            print(self.selected_dir)
            return

        try:
            for entry in entries:
                print(entry)
                rename(
                    join(self.selected_dir, entry.filename),
                    join(self.selected_dir, entry.output),
                )
        except Exception as e:
            alert = Adw.AlertDialog(
                heading="Error during rename",
                body=f"Encountered an error during renaming of the photos.\n\n{e}",
            )
            alert.add_response("ok", "_OK")
            alert.choose(parent=self)
            return

        alert = Adw.AlertDialog(
            heading="Finished renaming",
            body="Files have been renamed based on contained EXIF data",
        )
        alert.add_response("ok", "_OK")
        alert.choose(parent=self)

        entries.clear()
        self._refresh_entries()


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


def main():
    app = MyApp(application_id="org.athrail.PhotoRename")
    app.run(sys.argv)


if __name__ == "__main__":
    main()
