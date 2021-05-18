#!/usr/bin/env python3
"""Export yWriter project to markdown. 

GUI version using tkinter

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os

from yw2md import Ui
from yw2md import UiCmd
from yw2md import MdConverter
from yw2md import UiTk

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk


class MyGui(UiTk):
    """Extend the Tkinter GUI, 
    and link it to the application.
    """

    def __init__(self, title):
        """Make the converter object visible to the user interface 
        in order to make method calls possible.
        Add the widgets needed to invoke the converter manually.
        """
        UiTk.__init__(self, title)
        self.converter = None

        self.root.geometry("800x420")

        self.markdownMode = BooleanVar()
        self.root.markdownModeCheckbox = ttk.Checkbutton(
            text='Markdown mode', variable=self.markdownMode, onvalue=True, offvalue=False)
        self.root.markdownModeCheckbox.pack()

        self.noSceneTitles = BooleanVar()
        self.root.noSceneTitlesCheckbox = ttk.Checkbutton(
            text='No scene titles', variable=self.noSceneTitles, onvalue=True, offvalue=False)
        self.root.noSceneTitlesCheckbox.pack()

        self.root.selectButton = Button(
            text="Select file", command=self.select_file)
        self.root.selectButton.config(height=1, width=10)
        self.root.selectButton.pack(padx=5, pady=5)

        self.root.runButton = Button(text='Convert', command=self.convert_file)
        self.root.runButton.config(height=1, width=10)
        self.root.runButton.pack(padx=5, pady=5)
        self.root.runButton.config(state='disabled')

        self.root.quitButton = Button(text='Quit', command=quit)
        self.root.quitButton.config(height=1, width=10)
        self.root.quitButton.pack(padx=5, pady=5)

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
                      'noSceneTitles': self.noSceneTitles.get()}
            self.converter.run(self.sourcePath, **kwargs)

    def finish(self):
        """Important: Disable the finish method used by UiTk 
        to start the main loop.
        This is because UiTk uses the main loop only for awaiting
        the exit command after having finished the conversion. 
        """
        return


def run(sourcePath):

    ui = MyGui('yw2md')
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
