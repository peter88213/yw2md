#!/usr/bin/env python3
"""Export yWriter project to markdown. 

GUI version using tkinter

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os

from yw2md import YwCnvUi
from yw2md import MdFileFactory
from yw2md import UiTk

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog


class MyGui(UiTk):
    """Implement a Tkinter GUI."""

    def __init__(self, app):
        """Prepare the graphical user interface. """

        UiTk.__init__(self, 'yw2md')

        self.root.selectButton = Button(
            text="Select file", command=app.select_file)
        self.root.selectButton.config(height=1, width=10)
        self.root.selectButton.pack(padx=5, pady=5)

        self.root.runButton = Button(text='Convert', command=app.lift_off)
        self.root.runButton.config(height=1, width=10)
        self.root.runButton.pack(padx=5, pady=5)
        self.root.runButton.config(state='disabled')

        self.root.quitButton = Button(text='Quit', command=quit)
        self.root.quitButton.config(height=1, width=10)
        self.root.quitButton.pack(padx=5, pady=5)

    def finish(self):
        return


class MyConverter(YwCnvUi):
    """yWriter desktop with a Tkinter GUI. 
    """

    def __init__(self, silentMode):
        YwCnvUi.__init__(self)
        self.fileFactory = MdFileFactory()

        if not silentMode:
            self.sourcePath = ''
            self.userInterface = MyGui(self)
            self.userInterface.root.mainloop()

    def select_file(self):
        startDir = os.getcwd()
        file = filedialog.askopenfile(initialdir=startDir)

        if file:
            self.sourcePath = file.name

        if self.sourcePath:
            self.userInterface.set_info_what(
                'File: ' + os.path.normpath(self.sourcePath))
            self.userInterface.root.runButton.config(state='normal')

        else:
            self.userInterface.set_info_what('No file selected')
            self.userInterface.root.runButton.config(state='disabled')

    def lift_off(self):
        if self.sourcePath:
            self.run(self.sourcePath, '')


def run(sourcePath):

    if sourcePath is not None:
        converter = MyConverter(True)
        converter.run(sourcePath)

    else:
        converter = MyConverter(False)


if __name__ == '__main__':

    try:
        sourcePath = sys.argv[1]

        if os.path.isfile(sourcePath):
            run(sourcePath)

    except:
        run(None)
