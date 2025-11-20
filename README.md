# Photo Renamer

## Description

Small tool for renaming of images based on their EXIF tags.
It looks for DateTimeOriginal (0x9008) tag first and if it's not found then it looks for ModifyDate (0x0132).
Based on that it formats the new name prefixing it with date from tag.

Started as a CLI app using typer and rich.
Now also has GUI framework on GNU/Linux systems through usage of libadwaita.

## Ideas for future

- [ ] extract common code between CLI app and GUI app to a separate module
- [ ] introduce configuration file for output format
- [ ] design even better GUI?
