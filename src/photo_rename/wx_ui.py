from typing import List
from os.path import normpath, join, isfile, splitext
from os import listdir, rename
from datetime import datetime

import wx
from PIL import Image

EXIF_DATETIME_TAG = 0x132
EXIF_DATETIME_ORIG_TAG = 0x9003
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
# OUTPUT_DATE_FORMAT = "%Y_%m_%d_%H%M%S"
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
TABLE_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"


__version__ = "0.1.0"


class RenameEntry:
    filename: str
    date: datetime
    output: str

    def __init__(self, filename: str, date: datetime) -> None:
        self.filename = filename
        self.date = date
        self.output = "_".join([date.strftime(OUTPUT_DATE_FORMAT), filename])

    def as_list(self):
        return [self.filename, self.date, self.output]


def grab_image_datetime(path: str) -> datetime | None:
    with Image.open(path) as image:
        exifdata = image.getexif()
        date = exifdata.get(EXIF_DATETIME_ORIG_TAG)
        if date is None:
            date = exifdata.get(EXIF_DATETIME_TAG)
            if date is None:
                return None

        return datetime.strptime(date, EXIF_DATE_FORMAT)


entries: List[RenameEntry] = []


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw) -> None:
        super(MainFrame, self).__init__(*args, **kw)

        self._makeManu()

        # create a panel in the frame
        pnl = wx.Panel(self)
        list = wx.ListView(pnl, -1)
        list.AppendColumn("Original file", format=wx.LIST_FORMAT_CENTER)
        list.AppendColumn("Date taken", format=wx.LIST_FORMAT_CENTER)
        list.AppendColumn("Renamed file", format=wx.LIST_FORMAT_CENTER)

        list.Append(["item1", "19/11/2025 10:00", "item1_19_11_2025"])
        list.Append(["item2", "20/11/2025 10:00", "item2_20_11_2025"])
        list.Append(["item3", "21/11/2025 10:00", "item3_21_11_2025"])

        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(list, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 15))
        # pnl.SetSizer(sizer)

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

    def _makeManu(self):
        fileMenu = wx.Menu()
        dirSelectionItem = fileMenu.Append(
            0, "&Open Directory", "Select a rename directory"
        )
        self.Bind(wx.EVT_MENU, self.OnDirSelection, dirSelectionItem)
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

    def OnExit(self, event):
        self.Close(True)

    def OnAbout(self, event):
        wx.MessageBox("About message", "About title", wx.OK | wx.ICON_INFORMATION)

    def OnDirSelection(self, event):
        dialog = wx.DirDialog(self, "Select directory containing photos to rename")
        if dialog.ShowModal() == wx.ID_OK:
            dir = normpath(dialog.GetPath())

            for item in listdir(dir):
                if isfile(join(dir, item)):
                    _, file_extension = splitext(item)
                    if file_extension.lower() in (".jpg", ".jpeg"):
                        photo_path = join(dir, item)
                        date = grab_image_datetime(photo_path)
                        if date is not None:
                            entries.append(RenameEntry(item, date))
                        else:
                            print("Found photo but without date.")

            if len(entries) < 1:
                pass

            print(entries)


def main():
    app = wx.App()
    frame = MainFrame(None, title="hello world")
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
