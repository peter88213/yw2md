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


class Yw2mdTk(MainTk):
    """A tkinter GUI class for yWriter report generation.
    """

    def __init__(self, title, **kwargs):
        """Put a text box to the GUI main window.
        Extend the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self.converter = None
        self.tags = []
        self.viewpoints = []
        self.vpIds = []
        self.characters = []
        self.crIds = []
        self.locations = []
        self.lcIds = []
        self.items = []
        self.itIds = []
        self.filterCat = []

        #--- Row 1: "Levels" checkboxes (chapters, scenes)

        row1Cnt = 1
        self.header = tk.Label(self.mainWindow, text='Options')
        self.header.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self.SceneTitles = tk.BooleanVar(value=False)
        self.SceneTitlesCheckbox = ttk.Checkbutton(self.mainWindow,
                                                   text='Comments at the beginning of a scene are scene titles.', variable=self.SceneTitles, onvalue=False, offvalue=True)
        self.SceneTitlesCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

        row1Cnt += 1
        self.markdownMode = tk.BooleanVar()
        self.markdownModeCheckbox = ttk.Checkbutton(self.root,
                                                    text='The scenes in the yWriter project are Markdown formatted.', variable=self.markdownMode, onvalue=True, offvalue=False)
        self.markdownModeCheckbox.grid(row=row1Cnt, column=1, sticky=tk.W, padx=20, columnspan=3)

    def extend_menu(self):
        """Add main menu entries.
        Override the superclass template method. 
        """
        self.mainMenu.add_command(label='Create report', command=self.convert_file)
        self.mainMenu.entryconfig('Create report', state='disabled')

    def disable_menu(self):
        """Disable menu entries when no project is open.
        Extend the superclass method.      
        """
        super().disable_menu()
        self.mainMenu.entryconfig('Create report', state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open.
        Extend the superclass method.
        """
        super().enable_menu()
        self.mainMenu.entryconfig('Create report', state='normal')

    def open_project(self, fileName):
        """Create a yWriter project instance and read the file.
        Display project title, description and status.
        Return the file name.
        Extend the superclass method.
        """
        fileName = super().open_project(fileName)

        if not fileName:
            return ''

        self.ywPrj = Yw7File(fileName)
        message = self.ywPrj.read()

        if message.startswith(ERROR):
            self.close_project()
            self.set_info_how(message)
            return ''

        if self.ywPrj.title:
            titleView = self.ywPrj.title

        else:
            titleView = 'Untitled yWriter project'

        if self.ywPrj.author:
            authorView = self.ywPrj.author

        else:
            authorView = 'Unknown author'

        self.titleBar.config(text=f'{titleView} by {authorView}')
        self.enable_menu()

        self.locations = []
        self.items = []

        #-- Build filter selector lists.

        self.tags = []
        self.vpIds = []
        self.viewpoints = []
        self.crIds = []
        self.characters = []
        self.lcIds = []
        self.locations = []
        self.itIds = []
        self.items = []

        for chId in self.ywPrj.srtChapters:

            for scId in self.ywPrj.chapters[chId].srtScenes:

                if self.ywPrj.scenes[scId].tags:

                    for tag in self.ywPrj.scenes[scId].tags:

                        if not tag in self.tags:
                            self.tags.append(tag)

                if self.ywPrj.scenes[scId].characters:
                    vpId = self.ywPrj.scenes[scId].characters[0]

                    if not vpId in self.vpIds:
                        self.vpIds.append(vpId)
                        self.viewpoints.append(
                            self.ywPrj.characters[vpId].title)

                    for crId in self.ywPrj.scenes[scId].characters:

                        if not crId in self.crIds:
                            self.crIds.append(crId)
                            self.characters.append(
                                self.ywPrj.characters[crId].title)

                if self.ywPrj.scenes[scId].locations:

                    for lcId in self.ywPrj.scenes[scId].locations:

                        if not lcId in self.lcIds:
                            self.lcIds.append(lcId)
                            self.locations.append(
                                self.ywPrj.locations[lcId].title)

                if self.ywPrj.scenes[scId].items:

                    for itId in self.ywPrj.scenes[scId].items:

                        if not itId in self.itIds:
                            self.itIds.append(itId)
                            self.items.append(
                                self.ywPrj.items[itId].title)

        # Initialize the filter category selection widgets.

        self.filterCat = [[], self.tags, self.viewpoints, self.characters, self.locations, self.items]
        self.set_filter_category(0)
        self.filterCatSelection.set(0)

        return fileName

    def close_project(self):
        """Clear the text box.
        Extend the superclass method.
        """
        super().close_project()
        self.filterCat = [[], [], [], [], [], []]
        self.filterCombobox['values'] = []
        self.set_filter_category(0)
        self.filterCatSelection.set(0)
        self.filterCombobox.set('')

    def set_filter_category(self, selection):
        options = self.filterCat[selection]
        self.filterCombobox['values'] = options

        if options:
            self.filterCombobox.set(options[0])

        else:
            self.filterCombobox.set('')

    def convert_file(self):
        """Call the converter's conversion method, if a source file is selected.
        """
        self.set_status('')

        # Filter options.

        filterCat = self.filterCatSelection.get()
        option = self.filterCombobox.current()

        if filterCat == 0:
            sceneFilter = Filter()

        elif filterCat == 1:
            sceneFilter = ScTgFilter(self.tags[option])

        elif filterCat == 2:
            sceneFilter = ScVpFilter(self.vpIds[option])

        elif filterCat == 3:
            sceneFilter = ScCrFilter(self.crIds[option])

        elif filterCat == 4:
            sceneFilter = ScLcFilter(self.lcIds[option])

        elif filterCat == 5:
            sceneFilter = ScItFilter(self.itIds[option])

        self.kwargs = dict(
            yw_last_open=self.ywPrj.filePath,
            outputSelection=str(self.outputSelection.get()),
            suffix=HtmlReport.SUFFIX,
            sceneFilter=sceneFilter,
            showChapters=self.showChapters.get(),
            showScenes=self.showScenes.get(),
            showNormalType=self.showNormalType.get(),
            showUnusedType=self.showUnusedType.get(),
            showNotesType=self.showNotesType.get(),
            showTodoType=self.showTodoType.get(),
            showUnexported=self.showUnexported.get(),
            showNumber=self.showNumber.get(),
            showTitle=self.showTitle.get(),
            showDescription=self.showDescription.get(),
            showViewpoint=self.showViewpoint.get(),
            showTags=self.showTags.get(),
            showNotes=self.showNotes.get(),
            showDate=self.showDate.get(),
            showTime=self.showTime.get(),
            showDuration=self.showDuration.get(),
            showActionPattern=self.showActionPattern.get(),
            showRatings=self.showRatings.get(),
            showWordsTotal=self.showWordsTotal.get(),
            showWordcount=self.showWordcount.get(),
            showLettercount=self.showLettercount.get(),
            showStatus=self.showStatus.get(),
            showCharacters=self.showCharacters.get(),
            showLocations=self.showLocations.get(),
            showItems=self.showItems.get(),
        )
        self.converter.run(self.ywPrj.filePath, **self.kwargs)

        if self.converter.newFile is not None:
            webbrowser.open(self.converter.newFile)
