#!/usr/bin/env python3
""""Provide a tkinter GUI class for the yWriter report generator.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-reporter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import webbrowser
import tkinter as tk
from tkinter import ttk

from pywriter.pywriter_globals import ERROR

from pywriter.ui.main_tk import MainTk
from pywriter.yw.yw7_file import Yw7File
from pywmd.md_file import MdFile


class Yw2mdTk(MainTk):
    """A tkinter GUI class for yWriter report generation.
    """

    def __init__(self, title, **kwargs):
        """Put a text box to the GUI main window.
        Extend the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self.converter = None
        self.sourcePath = None

        #--- Row 1: "Levels" checkboxes (chapters, scenes)

        row1Cnt = 1
        self.header = tk.Label(self.mainWindow, text='Options')
        self.header.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self.SceneTitles = tk.BooleanVar(value=self.kwargs['scene_titles'])
        self.SceneTitlesCheckbox = ttk.Checkbutton(self.mainWindow,
                                                   text='Comments at the beginning of a scene are scene titles.', 
                                                   variable=self.SceneTitles, onvalue=True, offvalue=False)
        self.SceneTitlesCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self._markdownMode = tk.BooleanVar(value=self.kwargs['markdown_mode'])
        self.markdownModeCheckbox = ttk.Checkbutton(self.mainWindow,
                                                    text='The scenes in the yWriter project are Markdown formatted.', 
                                                    variable=self._markdownMode, onvalue=True, offvalue=False)
        self.markdownModeCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

    def extend_menu(self):
        """Add main menu entries.
        Override the superclass template method. 
        """
        self.mainMenu.add_command(label='Convert', command=self.convert_file)
        self.mainMenu.entryconfig('Convert', state='disabled')

    def disable_menu(self):
        """Disable menu entries when no project is open.
        Extend the superclass method.      
        """
        super().disable_menu()
        self.mainMenu.entryconfig('Convert', state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open.
        Extend the superclass method.
        """
        super().enable_menu()
        self.mainMenu.entryconfig('Convert', state='normal')

    def open_project(self, fileName):
        """Create a yWriter project instance and read the file.
        Display project title, description and status.
        Return the file name.
        Extend the superclass method.
        """
        fileName = super().open_project(fileName, fileTypes=self.kwargs['file_types'])

        if not fileName:
            return ''

        self.sourcePath = fileName
        self.enable_menu()
        
        if fileName.endswith(Yw7File.EXTENSION):
            self.titleBar.config(text='Export yWriter chapters and scenes to a Markdown document.')
        
        elif fileName.endswith(MdFile.EXTENSION):
            self.titleBar.config(text='Create a yWriter project from a Markdown document.')
        
        return fileName


    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        """
        self.set_status('')
        self.kwargs['yw_last_open'] =self.sourcePath
        self.kwargs['markdown_mode'] = self._markdownMode.get()
        self.kwargs['scene_titles'] = self.SceneTitles.get()
        self.converter.run(self.sourcePath, **self.kwargs)

