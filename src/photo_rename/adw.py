import sys
from os import rename
from os.path import join

import photo_rename.lib as lib

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk


config = lib.Config()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.box_main = Gtk.Box(spacing=20, orientation=Gtk.Orientation.HORIZONTAL)
        self.box_main.set_margin_bottom(20)
        self.box_main.set_margin_top(20)
        self.box_main.set_margin_start(20)
        self.box_main.set_margin_end(20)
        self.set_content(self.box_main)

        self.box_sidebar = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.VERTICAL, width_request=150
        )
        self.box_main.append(self.box_sidebar)

        self.btn_open_dir = Gtk.Button(label="Select directory")
        self.box_sidebar.append(self.btn_open_dir)
        self.btn_open_dir.connect("clicked", self.on_btn_open_dir_clicked)

        self.box_sidebar.append(Gtk.Box(margin_top=15))

        self.btn_uncheck_all = Gtk.Button(label="Uncheck All", visible=False)
        self.btn_uncheck_all.connect("clicked", self.on_btn_uncheck_all_clicked)
        self.box_sidebar.append(self.btn_uncheck_all)

        self.btn_check_all = Gtk.Button(label="Check All", visible=False)
        self.btn_check_all.connect("clicked", self.on_btn_check_all_clicked)
        self.box_sidebar.append(self.btn_check_all)

        self.box_sidebar.append(Gtk.Box(margin_top=10))

        self.btn_rename = Gtk.Button(label="Rename", visible=False)
        self.btn_rename.connect("clicked", self.on_btn_rename_clicked)
        self.box_sidebar.append(self.btn_rename)

        self.box_sidebar.append(Gtk.Box(vexpand=True))

        self.btn_prefs = Gtk.Button(label="Preferences")
        self.box_sidebar.append(self.btn_prefs)
        self.btn_prefs.connect("clicked", self.on_btn_prefs_clicked)

        self.btn_about = Gtk.Button(label="About")
        self.box_sidebar.append(self.btn_about)
        self.btn_about.connect("clicked", self.on_btn_about_clicked)

        self.btn_quit = Gtk.Button(label="Quit")
        self.box_sidebar.append(self.btn_quit)
        self.btn_quit.connect("clicked", self.on_btn_quit_clicked)

        self.box_content = Gtk.Box(
            spacing=10, orientation=Gtk.Orientation.VERTICAL, hexpand=True
        )
        self.box_main.append(self.box_content)

        self._entries = []
        self._new_entries_grid()
        self.no_entries_label = Gtk.Label(
            label="No entries found, select a directory with images inside",
            margin_top=15,
            margin_bottom=15,
            hexpand=True,
        )
        self._refresh_entries()

        self.dialog_select_dir = Gtk.FileDialog(
            title="Chose directory with images",
            modal=True,
        )

    def _new_entries_grid(self):
        if hasattr(self, "grid_entries") and self.grid_entries is not None:
            self.box_content.remove(self.grid_entries)

        self.grid_entries = Gtk.Grid(row_spacing=15, column_spacing=15, hexpand=True)

        self.box_content.append(self.grid_entries)

    def _refresh_entries(self):
        self._new_entries_grid()

        if len(self._entries) > 0:
            self.btn_rename.set_visible(True)
            self.btn_uncheck_all.set_visible(True)
            self.btn_check_all.set_visible(True)

            self.grid_entries.attach(
                Gtk.Label(
                    label='<span weight="bold" size="large">Select</span>',
                    use_markup=True,
                ),
                0,
                0,
                1,
                1,
            )

            self.grid_entries.attach(
                Gtk.Label(
                    hexpand=True,
                    label='<span weight="bold" size="large">Original file name</span>',
                    use_markup=True,
                ),
                1,
                0,
                1,
                1,
            )
            self.grid_entries.attach(
                Gtk.Label(
                    label='<span weight="bold" size="large">Date taken</span>',
                    use_markup=True,
                ),
                2,
                0,
                1,
                1,
            )
            self.grid_entries.attach(
                Gtk.Label(
                    hexpand=True,
                    label='<span weight="bold" size="large">Output file name</span>',
                    use_markup=True,
                ),
                3,
                0,
                1,
                1,
            )

            for i, entry in enumerate(self._entries):
                check = Gtk.CheckButton(active=entry.rename, halign=Gtk.Align.CENTER)
                check.connect("toggled", self.on_select_rename_toggled, i)
                self.grid_entries.attach(check, 0, i + 1, 1, 1)
                self.grid_entries.attach(
                    Gtk.Label(hexpand=True, label=entry.filename), 1, i + 1, 1, 1
                )
                self.grid_entries.attach(
                    Gtk.Label(label=entry.date.strftime(config.table_date_format)),
                    2,
                    i + 1,
                    1,
                    1,
                )
                self.grid_entries.attach(
                    Gtk.Label(hexpand=True, label=entry.output), 3, i + 1, 1, 1
                )
        else:
            self.grid_entries.attach(self.no_entries_label, 0, 0, 3, 1)
            self.btn_rename.set_visible(False)
            self.btn_uncheck_all.set_visible(False)
            self.btn_check_all.set_visible(False)

    def on_select_rename_toggled(self, widget: Gtk.CheckButton, i):
        self._entries[i].rename = widget.get_active()

    def on_btn_about_clicked(self, _):
        dialog = Adw.AboutDialog(
            application_name="Photo Renamer",
            version=lib.__version__,
            developer_name="Krzysztof Lewandowski",
            license_type=Gtk.License.MIT_X11,
            comments="Automatically rename your photos based on EXIF data",
            website="https://github.com/athrail/photo-rename",
            copyright="© 2025 Krzysztof Lewandowski",
        )
        dialog.present(parent=self)

    def on_btn_quit_clicked(self, _):
        sys.exit(0)

    def on_btn_prefs_clicked(self, _):
        def on_pref_output_format_entry_changed(widget):
            if not isinstance(widget, Adw.EntryRow):
                return

            config.output_date_format = widget.get_text()

        def on_pref_table_format_entry_changed(widget):
            if not isinstance(widget, Adw.EntryRow):
                return

            config.table_date_format = widget.get_text()

        page1 = Adw.PreferencesPage(title="Preferences")
        pref_group_format = Adw.PreferencesGroup(
            title="Format", description="Preferences on formatting of the file names"
        )
        page1.add(pref_group_format)
        pref_output_format_entry = Adw.EntryRow(
            title="Output date format", text=config.output_date_format
        )
        pref_output_format_entry.connect("changed", on_pref_output_format_entry_changed)
        pref_table_format_entry = Adw.EntryRow(
            title="Table date format", text=config.table_date_format
        )
        pref_table_format_entry.connect("changed", on_pref_table_format_entry_changed)
        pref_group_format.add(pref_output_format_entry)
        pref_group_format.add(pref_table_format_entry)

        dialog = Adw.PreferencesDialog(title="Preferences", can_close=True)
        dialog.add(page1)
        dialog.present(parent=self)

    def on_btn_open_dir_clicked(self, _):
        self.dialog_select_dir.select_folder(
            parent=self, callback=self.on_open_dir_callback
        )

    def on_open_dir_callback(self, dialog: Gtk.FileDialog, task: Gio.Task):
        if task.had_error():
            return

        file = dialog.select_folder_finish(task)
        if file is None:
            return

        self.selected_dir = file.get_path()
        if self.selected_dir is None:
            return

        self._entries = lib.traverse_dir_for_images(self.selected_dir, config)

        self._refresh_entries()

    def on_btn_rename_clicked(self, _):
        if not hasattr(self, "selected_dir") or self.selected_dir is None:
            print(hasattr(self, "selected_dir"))
            print(self.selected_dir)
            return

        entries = [entry for entry in self._entries if entry.rename]
        if len(entries) == 0:
            self._show_alert(
                heading="No files selected",
                body="You need to select at least one file to start renaming",
            )
            return

        try:
            for entry in entries:
                rename(
                    join(self.selected_dir, entry.filename),
                    join(self.selected_dir, entry.output),
                )
        except Exception as e:
            self._show_alert(
                heading="Error during rename",
                body=f"Encountered an error during renaming of the photos.\n\n{e}",
            )
            return

        self._show_alert(
            heading="Finished renaming",
            body="Files have been renamed based on contained EXIF data",
        )

        self._entries.clear()
        self._refresh_entries()

    def on_btn_uncheck_all_clicked(self, _):
        for i in range(len(self._entries)):
            if (check := self.grid_entries.get_child_at(0, i + 1)) is not None:
                if isinstance(check, Gtk.CheckButton):
                    check.set_active(False)

    def on_btn_check_all_clicked(self, _):
        for i in range(len(self._entries)):
            if (check := self.grid_entries.get_child_at(0, i + 1)) is not None:
                if isinstance(check, Gtk.CheckButton):
                    check.set_active(True)

    def _show_alert(self, heading: str, body: str):
        alert = Adw.AlertDialog(heading=heading, body=body)
        alert.add_response("ok", "_OK")
        alert.choose(parent=self)


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
