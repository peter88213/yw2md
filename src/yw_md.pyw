#!/usr/bin/env python3
"""Export yWriter project to markdown. 

GUI version using tkinter

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywmd.md_converter import MdConverter
from pywriter.ui.ui_tk import UiTk

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

SCT_DESCRIPTION = 'Comments at the beginning of a scene are scene titles.'
MDM_DESCRIPTION = 'The scenes in the yWriter project are Markdown formatted.'


class MyGui(UiTk):
    """Extend the Tkinter GUI, 
    and link it to the application.
    """

    def __init__(self, title, description=None):
        """Make the converter object visible to the user interface 
        in order to make method calls possible.
        Add the widgets needed to invoke the converter manually.
        """
        self.converter = None
        self.infoWhatText = ''
        self.infoHowText = ''
        # UiTk.__init__(self, title)

        self.root = Tk()
        self.root.title(title)

        self.header = Label(self.root, text='Options')
        self.appInfo = Label(self.root, text='')
        self.appInfo.config(height=2, width=60)

        self.successInfo = Label(self.root)
        self.successInfo.config(height=1, width=50)

        self.processInfo = Label(self.root, text='')

        self.SceneTitles = BooleanVar()
        self.SceneTitles.set(False)
        self.root.SceneTitlesCheckbox = ttk.Checkbutton(
            text=SCT_DESCRIPTION, variable=self.SceneTitles, onvalue=False, offvalue=True)

        self.markdownMode = BooleanVar()
        self.root.markdownModeCheckbox = ttk.Checkbutton(
            text=MDM_DESCRIPTION, variable=self.markdownMode, onvalue=True, offvalue=False)

        self.root.selectButton = Button(
            text="Select file", command=self.select_file)
        self.root.selectButton.config(height=1, width=10)

        self.root.runButton = Button(text='Convert', command=self.convert_file)
        self.root.runButton.config(height=1, width=10)
        self.root.runButton.config(state='disabled')

        self.root.quitButton = Button(text='Quit', command=quit)
        self.root.quitButton.config(height=1, width=10)

        self.header.grid(row=1, column=1, sticky=W, padx=20, columnspan=3)
        self.root.SceneTitlesCheckbox.grid(
            row=2, column=1, sticky=W, padx=20, columnspan=3)
        self.root.markdownModeCheckbox.grid(
            row=3, column=1, sticky=W, padx=20, columnspan=3)
        self.appInfo.grid(row=5, column=1, pady=10, columnspan=3)

        self.root.selectButton.grid(
            row=6, column=1, pady=10)
        self.root.runButton.grid(row=6, column=2, pady=10)
        self.root.quitButton.grid(row=6, column=3, pady=10)

        self.successInfo.grid(row=7, column=1, columnspan=3)
        self.processInfo.grid(row=8, column=1, columnspan=3, pady=10)

        self.sourcePath = None
        self.set_info_what('No file selected')
        self.startDir = os.getcwd()

    def start(self):
        """Start the user interface.
        Note: This can not be done in the __init__() method.
        """
        self.root.mainloop()

    def select_file(self):
        """Open a file dialog in order to set the sourcePath property.
        """
        self.processInfo.config(text='')
        self.successInfo.config(
            bg=self.root.cget("background"))

        if self.sourcePath is not None:
            self.startDir = os.path.dirname(self.sourcePath)

        file = filedialog.askopenfile(initialdir=self.startDir)

        if file:
            self.sourcePath = file.name

        if self.sourcePath:
            self.set_info_what(
                'File: ' + os.path.normpath(self.sourcePath))
            self.root.runButton.config(state='normal')

        else:
            self.set_info_what('No file selected')
            self.root.runButton.config(state='disabled')

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        """
        self.processInfo.config(text='')
        self.successInfo.config(
            bg=self.root.cget("background"))

        options = [False, True]

        if self.sourcePath:
            kwargs = {'suffix': '', 'markdownMode': self.markdownMode.get(),
                      'noSceneTitles': self.SceneTitles.get()}
            self.converter.run(self.sourcePath, **kwargs)


def run(sourcePath):

    ui = MyGui('Markdown converter for yWriter projects')
    # instantiate a user interface object

    if sourcePath is not None:

        if os.path.isfile(sourcePath):
            ui.sourcePath = sourcePath
            ui.set_info_what(
                'File: ' + os.path.normpath(sourcePath))
            ui.root.runButton.config(state='normal')

        else:
            sourcepath = None

    converter = MdConverter()
    # instantiate a converter object

    # Create a bidirectional association between the
    # user interface object and the converter object.

    converter.ui = ui
    # make the user interface's methods visible to the converter

    ui.converter = converter
    # make the converter's methods visible to the user interface

    ui.start()


if __name__ == '__main__':

    try:
        sourcePath = sys.argv[1].replace('\\', '/')

    except:
        sourcePath = None

    run(sourcePath)
