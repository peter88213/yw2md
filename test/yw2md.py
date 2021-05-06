#!/usr/bin/env python3
"""Markdown converter for yWriter projects. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse



class Ui():
    """Superclass for UI facades, implementing a 'silent mode'."""

    def __init__(self, title):
        """Initialize text buffers for messaging.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """The application may use a subclass  
        for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """What's the converter going to do?"""
        self.infoWhatText = message

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message

    def finish(self):
        """To be overwritten by subclasses requiring
        special action to finish user interaction.
        """

from tkinter import *
from tkinter import messagebox


class UiTk(Ui):
    """UI subclass implementing a Tkinter facade."""

    def __init__(self, title, description=None):
        """Prepare the graphical user interface. """

        if description is None:
            description = __doc__
            # Just for legacy compatibility

        self.root = Tk()
        self.root.geometry("800x360")
        self.root.title(title)
        self.header = Label(self.root, text=description)
        self.header.pack(padx=5, pady=5)
        self.appInfo = Label(self.root, text='')
        self.appInfo.pack(padx=5, pady=5)
        self.successInfo = Label(self.root)
        self.successInfo.pack(fill=X, expand=1, padx=50, pady=5)
        self.processInfo = Label(self.root, text='')
        self.processInfo.pack(padx=5, pady=5)

        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        return messagebox.askyesno('WARNING', text)

    def set_info_what(self, message):
        """What's the converter going to do?"""

        self.infoWhatText = message
        self.appInfo.config(text=message)

    def set_info_how(self, message):
        """How's the converter doing?"""

        self.infoHowText = message
        self.processInfo.config(text=message)

        if message.startswith('SUCCESS'):
            self.successInfo.config(bg='green')

        else:
            self.successInfo.config(bg='red')

    def show_edit_button(self, edit_cmd):
        self.root.editButton = Button(text="Edit", command=edit_cmd)
        self.root.editButton.config(height=1, width=10)
        self.root.editButton.pack(padx=5, pady=5)

    def finish(self):
        self.root.quitButton = Button(text="Quit", command=quit)
        self.root.quitButton.config(height=1, width=10)
        self.root.quitButton.pack(padx=5, pady=5)
        self.root.mainloop()
#!/usr/bin/env python3
import re

from string import Template




class WorldElement():
    """Story world element representation.
    # xml: <LOCATIONS><LOCATION> or # xml: <ITEMS><ITEM>
    """

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>


class Character(WorldElement):
    """yWriter character representation.
    # xml: <CHARACTERS><CHARACTER>
    """

    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        WorldElement.__init__(self)

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>



class Scene():
    """yWriter scene representation.
    # xml: <SCENES><SCENE>
    """

    # Emulate an enumeration for the scene status

    STATUS = [None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']
    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int # xml: <Status>

        self.sceneNotes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('\[.+?\]|\.|\,| -', '', self._sceneContent)
        # Remove yWriter raw markup for word count

        wordList = text.split()
        self.wordCount = len(wordList)

        text = re.sub('\[.+?\]', '', self._sceneContent)
        # Remove yWriter raw markup for letter count

        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)
from urllib.parse import quote


class Novel():
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).
    """

    DESCRIPTION = 'Novel'
    EXTENSION = None
    SUFFIX = None
    # To be extended by file format specific subclasses.

    def __init__(self, filePath):
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.author = None
        # str
        # xml: <PROJECT><AuthorName>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter object.
        # The order of the elements does not matter (the novel's
        # order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene object.
        # The order of the elements does not matter (the novel's
        # order of the scenes is defined by the order of the chapters
        # and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements
        # corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = Object.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = Object.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements
        # corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character object.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements
        # corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a
        # supported type as specified by EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Accept only filenames with the right extension. """

        if self.SUFFIX is not None:
            suffix = self.SUFFIX

        else:
            suffix = ''

        if filePath.lower().endswith(suffix + self.EXTENSION):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(
                suffix + self.EXTENSION, ''))

    def read(self):
        """Parse the file and store selected properties.
        To be overwritten by file format specific subclasses.
        """
        return 'ERROR: read method is not implemented.'

    def merge(self, novel):
        """Copy required attributes of the novel object.
        To be overwritten by file format specific subclasses.
        """
        return 'ERROR: merge method is not implemented.'

    def write(self):
        """Write selected properties to the file.
        To be overwritten by file format specific subclasses.
        """
        return 'ERROR: write method is not implemented.'

    def convert_to_yw(self, text):
        """Convert source format to yw7 markup.
        To be overwritten by file format specific subclasses.
        """
        return text

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        To be overwritten by file format specific subclasses.
        """
        return text

    def file_exists(self):
        """Check whether the file specified by filePath exists. """
        if os.path.isfile(self.filePath):
            return True

        else:
            return False


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    To be overwritten by subclasses providing file type specific 
    markup converters and templates.
    """
    fileHeader = ''
    partTemplate = ''
    chapterTemplate = ''
    notesChapterTemplate = ''
    todoChapterTemplate = ''
    unusedChapterTemplate = ''
    notExportedChapterTemplate = ''
    sceneTemplate = ''
    appendedSceneTemplate = ''
    notesSceneTemplate = ''
    todoSceneTemplate = ''
    unusedSceneTemplate = ''
    notExportedSceneTemplate = ''
    sceneDivider = ''
    chapterEndTemplate = ''
    unusedChapterEndTemplate = ''
    notExportedChapterEndTemplate = ''
    notesChapterEndTemplate = ''
    characterTemplate = ''
    locationTemplate = ''
    itemTemplate = ''
    fileFooter = ''

    def get_string(self, elements):
        """Return a string which is the concatenation of the 
        members of the list of strings "elements", separated by 
        a comma plus a space. The space allows word wrap in 
        spreadsheet cells.
        """
        text = (', ').join(elements)
        return text

    def get_list(self, text):
        """Split a sequence of strings into a list of strings
        using a comma as delimiter. Remove leading and trailing
        spaces, if any.
        """
        elements = []
        tempList = text.split(',')

        for element in tempList:
            elements.append(element.lstrip().rstrip())

        return elements

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        To be overwritten by file format specific subclasses.
        """

        if text is None:
            text = ''

        return(text)

    def merge(self, novel):
        """Copy required attributes of the novel object.
        Return a message beginning with SUCCESS or ERROR.
        """

        if novel.title is not None:
            self.title = novel.title

        else:
            self.title = ''

        if novel.desc is not None:
            self.desc = novel.desc

        else:
            self.desc = ''

        if novel.author is not None:
            self.author = novel.author

        else:
            self.author = ''

        if novel.fieldTitle1 is not None:
            self.fieldTitle1 = novel.fieldTitle1

        else:
            self.fieldTitle1 = 'Field 1'

        if novel.fieldTitle2 is not None:
            self.fieldTitle2 = novel.fieldTitle2

        else:
            self.fieldTitle2 = 'Field 2'

        if novel.fieldTitle3 is not None:
            self.fieldTitle3 = novel.fieldTitle3

        else:
            self.fieldTitle3 = 'Field 3'

        if novel.fieldTitle4 is not None:
            self.fieldTitle4 = novel.fieldTitle4

        else:
            self.fieldTitle4 = 'Field 4'

        if novel.srtChapters != []:
            self.srtChapters = novel.srtChapters

        if novel.scenes is not None:
            self.scenes = novel.scenes

        if novel.chapters is not None:
            self.chapters = novel.chapters

        if novel.srtCharacters != []:
            self.srtCharacters = novel.srtCharacters
            self.characters = novel.characters

        if novel.srtLocations != []:
            self.srtLocations = novel.srtLocations
            self.locations = novel.locations

        if novel.srtItems != []:
            self.srtItems = novel.srtItems
            self.items = novel.items

        return 'SUCCESS'

    def get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section. 
        """
        projectTemplateMapping = dict(
            Title=self.title,
            Desc=self.convert_from_yw(self.desc),
            AuthorName=self.author,
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
        )
        return projectTemplateMapping

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self.chapters[chId].get_title(),
            Desc=self.convert_from_yw(self.chapters[chId].desc),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section. 
        """

        if self.scenes[scId].tags is not None:
            tags = self.get_string(self.scenes[scId].tags)

        else:
            tags = ''

        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []

            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)

            sceneChars = self.get_string(sChList)
            viewpointChar = sChList[0]

        except:
            sceneChars = ''
            viewpointChar = ''

        if self.scenes[scId].locations is not None:
            sLcList = []

            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)

            sceneLocs = self.get_string(sLcList)

        else:
            sceneLocs = ''

        if self.scenes[scId].items is not None:
            sItList = []

            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)

            sceneItems = self.get_string(sItList)

        else:
            sceneItems = ''

        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER

        else:
            reactionScene = Scene.ACTION_MARKER

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self.scenes[scId].title,
            Desc=self.convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self.convert_from_yw(
                self.scenes[scId].sceneContent),
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=self.scenes[scId].date,
            Time=self.scenes[scId].time,
            Day=self.scenes[scId].day,
            Hour=self.scenes[scId].hour,
            Minute=self.scenes[scId].minute,
            LastsDays=self.scenes[scId].lastsDays,
            LastsHours=self.scenes[scId].lastsHours,
            LastsMinutes=self.scenes[scId].lastsMinutes,
            ReactionScene=reactionScene,
            Goal=self.convert_from_yw(self.scenes[scId].goal),
            Conflict=self.convert_from_yw(self.scenes[scId].conflict),
            Outcome=self.convert_from_yw(self.scenes[scId].outcome),
            Tags=tags,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self.convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return sceneMapping

    def get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        """

        if self.characters[crId].tags is not None:
            tags = self.get_string(self.characters[crId].tags)

        else:
            tags = ''

        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER

        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self.characters[crId].title,
            Desc=self.convert_from_yw(self.characters[crId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.characters[crId].aka),
            Notes=self.convert_from_yw(self.characters[crId].notes),
            Bio=self.convert_from_yw(self.characters[crId].bio),
            Goals=self.convert_from_yw(self.characters[crId].goals),
            FullName=FileExport.convert_from_yw(
                self, self.characters[crId].fullName),
            Status=characterStatus,
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        """

        if self.locations[lcId].tags is not None:
            tags = self.get_string(self.locations[lcId].tags)

        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self.locations[lcId].title,
            Desc=self.convert_from_yw(self.locations[lcId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.locations[lcId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section. 
        """

        if self.items[itId].tags is not None:
            tags = self.get_string(self.items[itId].tags)

        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self.items[itId].title,
            Desc=self.convert_from_yw(self.items[itId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.items[itId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def get_fileHeader(self):
        """Process the file header.
        Return a list of strings.
        """
        lines = []
        template = Template(self.fileHeader)
        lines.append(template.safe_substitute(
            self.get_fileHeaderMapping()))
        return lines

    def get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        Return a list of strings.
        """
        lines = []
        firstSceneInChapter = True

        for scId in self.chapters[chId].srtScenes:
            wordsTotal += self.scenes[scId].wordCount
            lettersTotal += self.scenes[scId].letterCount

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.

            if self.scenes[scId].isTodoScene:

                if self.todoSceneTemplate != '':
                    template = Template(self.todoSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isNotesScene or self.chapters[chId].oldType == 1:
                # Scene is "Notes" (new file format) or "Info" (old file
                # format) scene.

                if self.notesSceneTemplate != '':
                    template = Template(self.notesSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isUnused or self.chapters[chId].isUnused:

                if self.unusedSceneTemplate != '':
                    template = Template(self.unusedSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:

                if self.notExportedSceneTemplate != '':
                    template = Template(self.notExportedSceneTemplate)

                else:
                    continue

            else:
                sceneNumber += 1

                template = Template(self.sceneTemplate)

                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self.appendedSceneTemplate != '':
                    template = Template(self.appendedSceneTemplate)

            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self.sceneDivider)

            lines.append(template.safe_substitute(self.get_sceneMapping(
                scId, sceneNumber, wordsTotal, lettersTotal)))

            firstSceneInChapter = False

        return lines, sceneNumber, wordsTotal, lettersTotal

    def get_chapters(self):
        """Process the chapters and nested scenes.
        Return a list of strings.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0

        for chId in self.srtChapters:

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.

            # Has the chapter only scenes not to be exported?

            sceneCount = 0
            notExportCount = 0
            doNotExport = False

            for scId in self.chapters[chId].srtScenes:
                sceneCount += 1

                if self.scenes[scId].doNotExport:
                    notExportCount += 1

            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True

            if self.chapters[chId].chType == 2:

                if self.todoChapterTemplate != '':
                    template = Template(self.todoChapterTemplate)

                else:
                    continue

            elif self.chapters[chId].chType == 1 or self.chapters[chId].oldType == 1:
                # Chapter is "Notes" (new file format) or "Info" (old file
                # format) chapter.

                if self.notesChapterTemplate != '':
                    template = Template(self.notesChapterTemplate)

                else:
                    continue

            elif self.chapters[chId].isUnused:

                if self.unusedChapterTemplate != '':
                    template = Template(self.unusedChapterTemplate)

                else:
                    continue

            elif doNotExport:

                if self.notExportedChapterTemplate != '':
                    template = Template(self.notExportedChapterTemplate)

                else:
                    continue

            elif self.chapters[chId].chLevel == 1 and self.partTemplate != '':
                template = Template(self.partTemplate)

            else:
                template = Template(self.chapterTemplate)
                chapterNumber += 1

            lines.append(template.safe_substitute(
                self.get_chapterMapping(chId, chapterNumber)))

            # Process scenes.

            sceneLines, sceneNumber, wordsTotal, lettersTotal = self.get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            # Process chapter ending.

            if self.chapters[chId].chType == 2 and self.todoChapterEndTemplate != '':
                lines.append(self.todoChapterEndTemplate)

            elif self.chapters[chId].chType == 1 or self.chapters[chId].oldType == 1:

                if self.notesChapterEndTemplate != '':
                    lines.append(self.notesChapterEndTemplate)

            elif self.chapters[chId].isUnused and self.unusedChapterEndTemplate != '':
                lines.append(self.unusedChapterEndTemplate)

            elif doNotExport and self.notExportedChapterEndTemplate != '':
                lines.append(self.notExportedChapterEndTemplate)

            elif self.chapterEndTemplate != '':
                lines.append(self.chapterEndTemplate)

        return lines

    def get_characters(self):
        """Process the characters.
        Return a list of strings.
        """
        lines = []
        template = Template(self.characterTemplate)

        for crId in self.srtCharacters:
            lines.append(template.safe_substitute(
                self.get_characterMapping(crId)))

        return lines

    def get_locations(self):
        """Process the locations.
        Return a list of strings.
        """
        lines = []
        template = Template(self.locationTemplate)

        for lcId in self.srtLocations:
            lines.append(template.safe_substitute(
                self.get_locationMapping(lcId)))

        return lines

    def get_items(self):
        """Process the items.
        Return a list of strings.
        """
        lines = []
        template = Template(self.itemTemplate)

        for itId in self.srtItems:
            lines.append(template.safe_substitute(self.get_itemMapping(itId)))

        return lines

    def get_text(self):
        """Assemple the whole text applying the templates.
        Return a string to be written to the output file.
        """
        lines = self.get_fileHeader()
        lines.extend(self.get_chapters())
        lines.extend(self.get_characters())
        lines.extend(self.get_locations())
        lines.extend(self.get_items())
        lines.append(self.fileFooter)
        return ''.join(lines)

    def write(self):
        """Create a template-based output file. 
        Return a message string starting with 'SUCCESS' or 'ERROR'.
        """
        text = self.get_text()

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Cannot write "' + os.path.normpath(self.filePath) + '".'

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'


class Chapter():
    """yWriter chapter representation.
    # xml: <CHAPTERS><CHAPTER>
    """

    chapterTitlePrefix = "Chapter "
    # str
    # Can be changed at runtime for non-English projects.

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.oldType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

    def get_title(self):
        """Fix auto-chapter titles if necessary 
        """
        text = self.title

        if text:
            text = text.replace('Chapter ', self.chapterTitlePrefix)

        return text


class MdFile(FileExport):
    """Markdown file representation
    """

    DESCRIPTION = 'Markdown converter'
    EXTENSION = '.md'
    SUFFIX = ''

    SCENE_DIVIDER = '* * *'

    fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''

    partTemplate = '\n# ${Title}\n\n'

    chapterTemplate = '\n## ${Title}\n\n'

    sceneTemplate = '<!---${Title}--->${SceneContent}\n\n'

    sceneDivider = '\n\n' + SCENE_DIVIDER + '\n\n'

    def __init__(self, filePath, markdownMode=False, noSceneTitles=False):
        FileExport.__init__(self, filePath)
        self.markdownMode = markdownMode
        self.noSceneTitles = noSceneTitles

        if self.noSceneTitles:
            self.sceneTemplate = self.sceneTemplate.replace(
                '<!---${Title}--->', '')

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = FileExport.get_chapterMapping(
            self, chId, chapterNumber)

        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''

        return chapterMapping

    def convert_from_yw(self, text):
        """Convert yw7 markup to Markdown.
        """

        MD_REPLACEMENTS = [
            ['[i]', '*'],
            ['[/i]', '*'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['/*', '<!---'],
            ['*/', '--->'],
            ['  ', ' '],
        ]

        if not self.markdownMode:
            MD_REPLACEMENTS[:0] = [['\n', '\n\n']]

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)

    def convert_to_yw(self, text):
        """Convert Markdown to yw7 markup.
        """
        if not self.markdownMode:
            SAFE_SCENE_DIVIDER = '~ ~ ~'

            # Save the scene dividers: they may contain asterisks
            # TODO: Better find a regex-based solution

            text = text.replace(self.SCENE_DIVIDER, SAFE_SCENE_DIVIDER)

            def set_bold(i):
                return '[b]' + i.group(1) + '[/b]'

            def set_italic(i):
                return '[i]' + i.group(1) + '[/i]'

            boldMd = re.compile('\*\*(.+?)\*\*')
            text = boldMd.sub(set_bold, text)

            italicMd = re.compile('\*(.+?)\*')
            text = italicMd.sub(set_italic, text)

            # Restore the scene dividers

            text = text.replace(SAFE_SCENE_DIVIDER, self.SCENE_DIVIDER)

            MD_REPLACEMENTS = [
                ['\n\n', '\n'],
                ['<!---', '/*'],
                ['--->', '*/'],
            ]

            try:

                for r in MD_REPLACEMENTS:
                    text = text.replace(r[0], r[1])

            except AttributeError:
                text = ''

        return(text)

    def read(self):
        """Parse the Markdown file located at filePath
        Return a message beginning with SUCCESS or ERROR.
        """
        LOW_WORDCOUNT = 10

        def write_scene_content(scId, lines):

            if scId is not None:
                text = '\n'.join(lines)
                """ Python 3.9+
                text = text.removeprefix('\n')
                if text.startswith('\n'):
                    text = text[len('\n'):]

                """
                self.scenes[scId].sceneContent = text

                if self.scenes[scId].wordCount < LOW_WORDCOUNT:
                    self.scenes[scId].status = Scene.STATUS.index('Outline')

                else:
                    self.scenes[scId].status = Scene.STATUS.index('Draft')

        chCount = 0
        scCount = 0
        lines = []
        chId = None
        scId = None

        try:
            with open(self.filePath, encoding='utf-8') as f:
                mdText = f.read()
                cnvText = self.convert_to_yw(mdText)
                mdLines = (cnvText).split('\n')

        except(FileNotFoundError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" not found.'

        except:
            return 'ERROR: Can not parse "' + os.path.normpath(self.filePath) + '".'

        if self.markdownMode:
            commentStart = '<!---'
            commentEnd = '--->'

        else:
            commentStart = '/*'
            commentEnd = '*/'

        for mdLine in mdLines:

            if mdLine.startswith('#'):

                # Write previous scene.

                write_scene_content(scId, lines)
                scId = None

                # Add a chapter.

                chCount += 1
                chId = str(chCount)
                self.chapters[chId] = Chapter()

                title = mdLine.split('# ')[1]

                self.chapters[chId].title = title
                self.srtChapters.append(chId)
                self.chapters[chId].oldType = '0'

                if mdLine.startswith('# '):
                    self.chapters[chId].chLevel = 1

                else:
                    self.chapters[chId].chLevel = 0

                self.chapters[chId].srtScenes = []

            elif self.SCENE_DIVIDER in mdLine:

                # Write previous scene.

                write_scene_content(scId, lines)
                scId = None

            elif scId is not None:
                lines.append(mdLine)

            elif mdLine and chId is not None:

                # Add a scene; drop the first line if empty.

                scCount += 1
                scId = str(scCount)

                self.scenes[scId] = Scene()
                self.chapters[chId].srtScenes.append(scId)
                self.scenes[scId].status = '1'
                self.scenes[scId].title = 'Scene ' + str(scCount)

                if not self.noSceneTitles and mdLine.startswith(commentStart):

                    # The scene title is prefixed as a comment.

                    try:
                        scTitle, scContent = mdLine.rsplit(
                            sep=commentEnd, maxsplit=1)
                        self.scenes[scId].title = scTitle.lstrip(commentStart)
                        lines = [scContent]

                    except:
                        lines = [mdLine]

                else:
                    lines = [mdLine]

        return 'SUCCESS'



class YwCnv():
    """Converter for yWriter project files.
    """

    def convert(self, sourceFile, targetFile):
        """Read the source file, merge its content with that of the target,
        and write the result to the target file.
        Return a message beginning with SUCCESS or ERROR.
        """

        if sourceFile.filePath is None:
            return 'ERROR: Source "' + os.path.normpath(sourceFile.filePath) + '" is not of the supported type.'

        if not sourceFile.file_exists():
            return 'ERROR: "' + os.path.normpath(sourceFile.filePath) + '" not found.'

        if targetFile.filePath is None:
            return 'ERROR: Target "' + os.path.normpath(targetFile.filePath) + '" is not of the supported type.'

        if targetFile.file_exists() and not self.confirm_overwrite(targetFile.filePath):
            return 'Canceled by user.'

        message = sourceFile.read()

        if message.startswith('ERROR'):
            return message

        message = targetFile.merge(sourceFile)

        if message.startswith('ERROR'):
            return message

        return targetFile.write()

    def confirm_overwrite(self, fileName):
        """Hook for subclasses with UI."""
        return True

import xml.etree.ElementTree as ET


class YwTreeBuilder():
    """Build yWriter project xml tree."""

    def build_element_tree(self, ywProject):
        """Modify the yWriter project attributes of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        To be overwritten by file format specific subclasses.
        """
        root = ywProject._tree.getroot()

        # Write locations to the xml element tree.

        locations = root.find('LOCATIONS')
        sortOrder = 0

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.

        for loc in locations.findall('LOCATION'):
            locations.remove(loc)

        for lcId in ywProject.srtLocations:
            loc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(loc, 'ID').text = lcId

            if ywProject.locations[lcId].title is not None:
                ET.SubElement(
                    loc, 'Title').text = ywProject.locations[lcId].title

            if ywProject.locations[lcId].image is not None:
                ET.SubElement(
                    loc, 'ImageFile').text = ywProject.locations[lcId].image

            if ywProject.locations[lcId].desc is not None:
                ET.SubElement(
                    loc, 'Desc').text = ywProject.locations[lcId].desc

            if ywProject.locations[lcId].aka is not None:
                ET.SubElement(loc, 'AKA').text = ywProject.locations[lcId].aka

            if ywProject.locations[lcId].tags is not None:
                ET.SubElement(loc, 'Tags').text = ';'.join(
                    ywProject.locations[lcId].tags)

            sortOrder += 1
            ET.SubElement(loc, 'SortOrder').text = str(sortOrder)

        # Write items to the xml element tree.

        items = root.find('ITEMS')
        sortOrder = 0

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.

        for itm in items.findall('ITEM'):
            items.remove(itm)

        for itId in ywProject.srtItems:
            itm = ET.SubElement(items, 'ITEM')
            ET.SubElement(itm, 'ID').text = itId

            if ywProject.items[itId].title is not None:
                ET.SubElement(itm, 'Title').text = ywProject.items[itId].title

            if ywProject.items[itId].image is not None:
                ET.SubElement(
                    itm, 'ImageFile').text = ywProject.items[itId].image

            if ywProject.items[itId].desc is not None:
                ET.SubElement(itm, 'Desc').text = ywProject.items[itId].desc

            if ywProject.items[itId].aka is not None:
                ET.SubElement(itm, 'AKA').text = ywProject.items[itId].aka

            if ywProject.items[itId].tags is not None:
                ET.SubElement(itm, 'Tags').text = ';'.join(
                    ywProject.items[itId].tags)

            sortOrder += 1
            ET.SubElement(itm, 'SortOrder').text = str(sortOrder)

        # Write characters to the xml element tree.

        characters = root.find('CHARACTERS')
        sortOrder = 0

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.

        for crt in characters.findall('CHARACTER'):
            characters.remove(crt)

        for crId in ywProject.srtCharacters:
            crt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(crt, 'ID').text = crId

            if ywProject.characters[crId].title is not None:
                ET.SubElement(
                    crt, 'Title').text = ywProject.characters[crId].title

            if ywProject.characters[crId].desc is not None:
                ET.SubElement(
                    crt, 'Desc').text = ywProject.characters[crId].desc

            if ywProject.characters[crId].image is not None:
                ET.SubElement(
                    crt, 'ImageFile').text = ywProject.characters[crId].image

            sortOrder += 1
            ET.SubElement(crt, 'SortOrder').text = str(sortOrder)

            if ywProject.characters[crId].notes is not None:
                ET.SubElement(
                    crt, 'Notes').text = ywProject.characters[crId].notes

            if ywProject.characters[crId].aka is not None:
                ET.SubElement(crt, 'AKA').text = ywProject.characters[crId].aka

            if ywProject.characters[crId].tags is not None:
                ET.SubElement(crt, 'Tags').text = ';'.join(
                    ywProject.characters[crId].tags)

            if ywProject.characters[crId].bio is not None:
                ET.SubElement(crt, 'Bio').text = ywProject.characters[crId].bio

            if ywProject.characters[crId].goals is not None:
                ET.SubElement(
                    crt, 'Goals').text = ywProject.characters[crId].goals

            if ywProject.characters[crId].fullName is not None:
                ET.SubElement(
                    crt, 'FullName').text = ywProject.characters[crId].fullName

            if ywProject.characters[crId].isMajor:
                ET.SubElement(crt, 'Major').text = '-1'

        # Write attributes at novel level to the xml element tree.

        prj = root.find('PROJECT')
        prj.find('Title').text = ywProject.title

        if ywProject.desc is not None:

            if prj.find('Desc') is None:
                ET.SubElement(prj, 'Desc').text = ywProject.desc

            else:
                prj.find('Desc').text = ywProject.desc

        if ywProject.author is not None:

            if prj.find('AuthorName') is None:
                ET.SubElement(prj, 'AuthorName').text = ywProject.author

            else:
                prj.find('AuthorName').text = ywProject.author

        prj.find('FieldTitle1').text = ywProject.fieldTitle1
        prj.find('FieldTitle2').text = ywProject.fieldTitle2
        prj.find('FieldTitle3').text = ywProject.fieldTitle3
        prj.find('FieldTitle4').text = ywProject.fieldTitle4

        # Write attributes at chapter level to the xml element tree.

        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text

            if chId in ywProject.chapters:
                chp.find('Title').text = ywProject.chapters[chId].title

                if ywProject.chapters[chId].desc is not None:

                    if chp.find('Desc') is None:
                        ET.SubElement(
                            chp, 'Desc').text = ywProject.chapters[chId].desc

                    else:
                        chp.find('Desc').text = ywProject.chapters[chId].desc

                levelInfo = chp.find('SectionStart')

                if levelInfo is not None:

                    if ywProject.chapters[chId].chLevel == 0:
                        chp.remove(levelInfo)

                chp.find('Type').text = str(ywProject.chapters[chId].oldType)

                if ywProject.chapters[chId].chType is not None:

                    if chp.find('ChapterType') is not None:
                        chp.find('ChapterType').text = str(
                            ywProject.chapters[chId].chType)
                    else:
                        ET.SubElement(chp, 'ChapterType').text = str(
                            ywProject.chapters[chId].chType)

                if ywProject.chapters[chId].isUnused:

                    if chp.find('Unused') is None:
                        ET.SubElement(chp, 'Unused').text = '-1'

                elif chp.find('Unused') is not None:
                    chp.remove(chp.find('Unused'))

        # Write attributes at scene level to the xml element tree.

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if scId in ywProject.scenes:

                if ywProject.scenes[scId].title is not None:
                    scn.find('Title').text = ywProject.scenes[scId].title

                if ywProject.scenes[scId].desc is not None:

                    if scn.find('Desc') is None:
                        ET.SubElement(
                            scn, 'Desc').text = ywProject.scenes[scId].desc

                    else:
                        scn.find('Desc').text = ywProject.scenes[scId].desc

                # Scene content is written in subclasses.

                if ywProject.scenes[scId].isUnused:

                    if scn.find('Unused') is None:
                        ET.SubElement(scn, 'Unused').text = '-1'

                elif scn.find('Unused') is not None:
                    scn.remove(scn.find('Unused'))

                if ywProject.scenes[scId].isNotesScene:

                    if scn.find('Fields') is None:
                        scFields = ET.SubElement(scn, 'Fields')

                    else:
                        scFields = scn.find('Fields')

                    if scFields.find('Field_SceneType') is None:
                        ET.SubElement(scFields, 'Field_SceneType').text = '1'

                elif scn.find('Fields') is not None:
                    scFields = scn.find('Fields')

                    if scFields.find('Field_SceneType') is not None:

                        if scFields.find('Field_SceneType').text == '1':
                            scFields.remove(scFields.find('Field_SceneType'))

                if ywProject.scenes[scId].isTodoScene:

                    if scn.find('Fields') is None:
                        scFields = ET.SubElement(scn, 'Fields')

                    else:
                        scFields = scn.find('Fields')

                    if scFields.find('Field_SceneType') is None:
                        ET.SubElement(scFields, 'Field_SceneType').text = '2'

                elif scn.find('Fields') is not None:
                    scFields = scn.find('Fields')

                    if scFields.find('Field_SceneType') is not None:

                        if scFields.find('Field_SceneType').text == '2':
                            scFields.remove(scFields.find('Field_SceneType'))

                if ywProject.scenes[scId].status is not None:
                    scn.find('Status').text = str(
                        ywProject.scenes[scId].status)

                if ywProject.scenes[scId].sceneNotes is not None:

                    if scn.find('Notes') is None:
                        ET.SubElement(
                            scn, 'Notes').text = ywProject.scenes[scId].sceneNotes

                    else:
                        scn.find(
                            'Notes').text = ywProject.scenes[scId].sceneNotes

                if ywProject.scenes[scId].tags is not None:

                    if scn.find('Tags') is None:
                        ET.SubElement(scn, 'Tags').text = ';'.join(
                            ywProject.scenes[scId].tags)

                    else:
                        scn.find('Tags').text = ';'.join(
                            ywProject.scenes[scId].tags)

                if ywProject.scenes[scId].field1 is not None:

                    if scn.find('Field1') is None:
                        ET.SubElement(
                            scn, 'Field1').text = ywProject.scenes[scId].field1

                    else:
                        scn.find('Field1').text = ywProject.scenes[scId].field1

                if ywProject.scenes[scId].field2 is not None:

                    if scn.find('Field2') is None:
                        ET.SubElement(
                            scn, 'Field2').text = ywProject.scenes[scId].field2

                    else:
                        scn.find('Field2').text = ywProject.scenes[scId].field2

                if ywProject.scenes[scId].field3 is not None:

                    if scn.find('Field3') is None:
                        ET.SubElement(
                            scn, 'Field3').text = ywProject.scenes[scId].field3

                    else:
                        scn.find('Field3').text = ywProject.scenes[scId].field3

                if ywProject.scenes[scId].field4 is not None:

                    if scn.find('Field4') is None:
                        ET.SubElement(
                            scn, 'Field4').text = ywProject.scenes[scId].field4

                    else:
                        scn.find('Field4').text = ywProject.scenes[scId].field4

                if ywProject.scenes[scId].appendToPrev:

                    if scn.find('AppendToPrev') is None:
                        ET.SubElement(scn, 'AppendToPrev').text = '-1'

                elif scn.find('AppendToPrev') is not None:
                    scn.remove(scn.find('AppendToPrev'))

                # Date/time information

                if (ywProject.scenes[scId].date is not None) and (ywProject.scenes[scId].time is not None):
                    dateTime = ywProject.scenes[scId].date + \
                        ' ' + ywProject.scenes[scId].time

                    if scn.find('SpecificDateTime') is not None:
                        scn.find('SpecificDateTime').text = dateTime

                    else:
                        ET.SubElement(scn, 'SpecificDateTime').text = dateTime
                        ET.SubElement(scn, 'SpecificDateMode').text = '-1'

                        if scn.find('Day') is not None:
                            scn.remove(scn.find('Day'))

                        if scn.find('Hour') is not None:
                            scn.remove(scn.find('Hour'))

                        if scn.find('Minute') is not None:
                            scn.remove(scn.find('Minute'))

                elif (ywProject.scenes[scId].day is not None) or (ywProject.scenes[scId].hour is not None) or (ywProject.scenes[scId].minute is not None):

                    if scn.find('SpecificDateTime') is not None:
                        scn.remove(scn.find('SpecificDateTime'))

                    if scn.find('SpecificDateMode') is not None:
                        scn.remove(scn.find('SpecificDateMode'))

                    if ywProject.scenes[scId].day is not None:

                        if scn.find('Day') is not None:
                            scn.find('Day').text = ywProject.scenes[scId].day

                        else:
                            ET.SubElement(
                                scn, 'Day').text = ywProject.scenes[scId].day

                    if ywProject.scenes[scId].hour is not None:

                        if scn.find('Hour') is not None:
                            scn.find('Hour').text = ywProject.scenes[scId].hour

                        else:
                            ET.SubElement(
                                scn, 'Hour').text = ywProject.scenes[scId].hour

                    if ywProject.scenes[scId].minute is not None:

                        if scn.find('Minute') is not None:
                            scn.find(
                                'Minute').text = ywProject.scenes[scId].minute

                        else:
                            ET.SubElement(
                                scn, 'Minute').text = ywProject.scenes[scId].minute

                if ywProject.scenes[scId].lastsDays is not None:

                    if scn.find('LastsDays') is not None:
                        scn.find(
                            'LastsDays').text = ywProject.scenes[scId].lastsDays

                    else:
                        ET.SubElement(
                            scn, 'LastsDays').text = ywProject.scenes[scId].lastsDays

                if ywProject.scenes[scId].lastsHours is not None:

                    if scn.find('LastsHours') is not None:
                        scn.find(
                            'LastsHours').text = ywProject.scenes[scId].lastsHours

                    else:
                        ET.SubElement(
                            scn, 'LastsHours').text = ywProject.scenes[scId].lastsHours

                if ywProject.scenes[scId].lastsMinutes is not None:

                    if scn.find('LastsMinutes') is not None:
                        scn.find(
                            'LastsMinutes').text = ywProject.scenes[scId].lastsMinutes

                    else:
                        ET.SubElement(
                            scn, 'LastsMinutes').text = ywProject.scenes[scId].lastsMinutes

                # Plot related information

                if ywProject.scenes[scId].isReactionScene:

                    if scn.find('ReactionScene') is None:
                        ET.SubElement(scn, 'ReactionScene').text = '-1'

                elif scn.find('ReactionScene') is not None:
                    scn.remove(scn.find('ReactionScene'))

                if ywProject.scenes[scId].isSubPlot:

                    if scn.find('SubPlot') is None:
                        ET.SubElement(scn, 'SubPlot').text = '-1'

                elif scn.find('SubPlot') is not None:
                    scn.remove(scn.find('SubPlot'))

                if ywProject.scenes[scId].goal is not None:

                    if scn.find('Goal') is None:
                        ET.SubElement(
                            scn, 'Goal').text = ywProject.scenes[scId].goal

                    else:
                        scn.find('Goal').text = ywProject.scenes[scId].goal

                if ywProject.scenes[scId].conflict is not None:

                    if scn.find('Conflict') is None:
                        ET.SubElement(
                            scn, 'Conflict').text = ywProject.scenes[scId].conflict

                    else:
                        scn.find(
                            'Conflict').text = ywProject.scenes[scId].conflict

                if ywProject.scenes[scId].outcome is not None:

                    if scn.find('Outcome') is None:
                        ET.SubElement(
                            scn, 'Outcome').text = ywProject.scenes[scId].outcome

                    else:
                        scn.find(
                            'Outcome').text = ywProject.scenes[scId].outcome

                if ywProject.scenes[scId].characters is not None:
                    characters = scn.find('Characters')

                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)

                    for crId in ywProject.scenes[scId].characters:
                        ET.SubElement(characters, 'CharID').text = crId

                if ywProject.scenes[scId].locations is not None:
                    locations = scn.find('Locations')

                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)

                    for lcId in ywProject.scenes[scId].locations:
                        ET.SubElement(locations, 'LocID').text = lcId

                if ywProject.scenes[scId].items is not None:
                    items = scn.find('Items')

                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)

                    for itId in ywProject.scenes[scId].items:
                        ET.SubElement(items, 'ItemID').text = itId

        self.indent_xml(root)
        ywProject._tree = ET.ElementTree(root)

        return 'SUCCESS'

    def indent_xml(self, elem, level=0):
        """xml pretty printer

        Kudos to to Fredrik Lundh. 
        Source: http://effbot.org/zone/element-lib.htm#prettyprint
        """
        i = "\n" + level * "  "

        if len(elem):

            if not elem.text or not elem.text.strip():
                elem.text = i + "  "

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

            for elem in elem:
                self.indent_xml(elem, level + 1)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i

        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class Yw7TreeCreator(YwTreeBuilder):
    """Create a new yWriter 7 project xml tree."""

    def build_element_tree(self, ywProject):
        """Put the yWriter project attributes to a new xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        """

        root = ET.Element('YWRITER7')

        # Write attributes at novel level to the xml element tree.

        prj = ET.SubElement(root, 'PROJECT')
        ET.SubElement(prj, 'Ver').text = '7'

        if ywProject.title is not None:
            ET.SubElement(prj, 'Title').text = ywProject.title

        if ywProject.desc is not None:
            ET.SubElement(prj, 'Desc').text = ywProject.desc

        if ywProject.author is not None:
            ET.SubElement(prj, 'AuthorName').text = ywProject.author

        if ywProject.fieldTitle1 is not None:
            ET.SubElement(prj, 'FieldTitle1').text = ywProject.fieldTitle1

        if ywProject.fieldTitle2 is not None:
            ET.SubElement(prj, 'FieldTitle2').text = ywProject.fieldTitle2

        if ywProject.fieldTitle3 is not None:
            ET.SubElement(prj, 'FieldTitle3').text = ywProject.fieldTitle3

        if ywProject.fieldTitle4 is not None:
            ET.SubElement(prj, 'FieldTitle4').text = ywProject.fieldTitle4

        # Write locations to the xml element tree.

        locations = ET.SubElement(root, 'LOCATIONS')

        for lcId in ywProject.srtLocations:
            loc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(loc, 'ID').text = lcId

            if ywProject.locations[lcId].title is not None:
                ET.SubElement(
                    loc, 'Title').text = ywProject.locations[lcId].title

            if ywProject.locations[lcId].desc is not None:
                ET.SubElement(
                    loc, 'Desc').text = ywProject.locations[lcId].desc

            if ywProject.locations[lcId].aka is not None:
                ET.SubElement(loc, 'AKA').text = ywProject.locations[lcId].aka

            if ywProject.locations[lcId].tags is not None:
                ET.SubElement(loc, 'Tags').text = ';'.join(
                    ywProject.locations[lcId].tags)

        # Write items to the xml element tree.

        items = ET.SubElement(root, 'ITEMS')

        for itId in ywProject.srtItems:
            itm = ET.SubElement(items, 'ITEM')
            ET.SubElement(itm, 'ID').text = itId

            if ywProject.items[itId].title is not None:
                ET.SubElement(itm, 'Title').text = ywProject.items[itId].title

            if ywProject.items[itId].desc is not None:
                ET.SubElement(itm, 'Desc').text = ywProject.items[itId].desc

            if ywProject.items[itId].aka is not None:
                ET.SubElement(itm, 'AKA').text = ywProject.items[itId].aka

            if ywProject.items[itId].tags is not None:
                ET.SubElement(itm, 'Tags').text = ';'.join(
                    ywProject.items[itId].tags)

        # Write characters to the xml element tree.

        characters = ET.SubElement(root, 'CHARACTERS')

        for crId in ywProject.srtCharacters:
            crt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(crt, 'ID').text = crId

            if ywProject.characters[crId].title is not None:
                ET.SubElement(
                    crt, 'Title').text = ywProject.characters[crId].title

            if ywProject.characters[crId].desc is not None:
                ET.SubElement(
                    crt, 'Desc').text = ywProject.characters[crId].desc

            if ywProject.characters[crId].aka is not None:
                ET.SubElement(crt, 'AKA').text = ywProject.characters[crId].aka

            if ywProject.characters[crId].tags is not None:
                ET.SubElement(crt, 'Tags').text = ';'.join(
                    ywProject.characters[crId].tags)

            if ywProject.characters[crId].notes is not None:
                ET.SubElement(
                    crt, 'Notes').text = ywProject.characters[crId].notes

            if ywProject.characters[crId].bio is not None:
                ET.SubElement(crt, 'Bio').text = ywProject.characters[crId].bio

            if ywProject.characters[crId].goals is not None:
                ET.SubElement(
                    crt, 'Goals').text = ywProject.characters[crId].goals

            if ywProject.characters[crId].fullName is not None:
                ET.SubElement(
                    crt, 'FullName').text = ywProject.characters[crId].fullName

            if ywProject.characters[crId].isMajor:
                ET.SubElement(crt, 'Major').text = '-1'

        # Write attributes at scene level to the xml element tree.

        scenes = ET.SubElement(root, 'SCENES')

        for scId in ywProject.scenes:
            scn = ET.SubElement(scenes, 'SCENE')
            ET.SubElement(scn, 'ID').text = scId

            if ywProject.scenes[scId].title is not None:
                ET.SubElement(scn, 'Title').text = ywProject.scenes[scId].title

            for chId in ywProject.chapters:

                if scId in ywProject.chapters[chId].srtScenes:
                    ET.SubElement(scn, 'BelongsToChID').text = chId
                    break

            if ywProject.scenes[scId].desc is not None:
                ET.SubElement(scn, 'Desc').text = ywProject.scenes[scId].desc

            if ywProject.scenes[scId].sceneContent is not None:
                ET.SubElement(scn,
                              'SceneContent').text = ywProject.scenes[scId].sceneContent
                ET.SubElement(scn, 'WordCount').text = str(
                    ywProject.scenes[scId].wordCount)
                ET.SubElement(scn, 'LetterCount').text = str(
                    ywProject.scenes[scId].letterCount)

            if ywProject.scenes[scId].isUnused:
                ET.SubElement(scn, 'Unused').text = '-1'

            scFields = ET.SubElement(scn, 'Fields')

            if ywProject.scenes[scId].isNotesScene:
                ET.SubElement(scFields, 'Field_SceneType').text = '1'

            elif ywProject.scenes[scId].isTodoScene:
                ET.SubElement(scFields, 'Field_SceneType').text = '2'

            if ywProject.scenes[scId].status is not None:
                ET.SubElement(scn, 'Status').text = str(
                    ywProject.scenes[scId].status)

            if ywProject.scenes[scId].sceneNotes is not None:
                ET.SubElement(
                    scn, 'Notes').text = ywProject.scenes[scId].sceneNotes

            if ywProject.scenes[scId].tags is not None:
                ET.SubElement(scn, 'Tags').text = ';'.join(
                    ywProject.scenes[scId].tags)

            if ywProject.scenes[scId].field1 is not None:
                ET.SubElement(
                    scn, 'Field1').text = ywProject.scenes[scId].field1

            if ywProject.scenes[scId].field2 is not None:
                ET.SubElement(
                    scn, 'Field2').text = ywProject.scenes[scId].field2

            if ywProject.scenes[scId].field3 is not None:
                ET.SubElement(
                    scn, 'Field3').text = ywProject.scenes[scId].field3

            if ywProject.scenes[scId].field4 is not None:
                ET.SubElement(
                    scn, 'Field4').text = ywProject.scenes[scId].field4

            if ywProject.scenes[scId].appendToPrev:
                ET.SubElement(scn, 'AppendToPrev').text = '-1'

            # Date/time information

            if (ywProject.scenes[scId].date is not None) and (ywProject.scenes[scId].time is not None):
                dateTime = ' '.join(
                    ywProject.scenes[scId].date, ywProject.scenes[scId].time)
                ET.SubElement(scn, 'SpecificDateTime').text = dateTime
                ET.SubElement(scn, 'SpecificDateMode').text = '-1'

            elif (ywProject.scenes[scId].day is not None) or (ywProject.scenes[scId].hour is not None) or (ywProject.scenes[scId].minute is not None):

                if ywProject.scenes[scId].day is not None:
                    ET.SubElement(scn, 'Day').text = ywProject.scenes[scId].day

                if ywProject.scenes[scId].hour is not None:
                    ET.SubElement(
                        scn, 'Hour').text = ywProject.scenes[scId].hour

                if ywProject.scenes[scId].minute is not None:
                    ET.SubElement(
                        scn, 'Minute').text = ywProject.scenes[scId].minute

            if ywProject.scenes[scId].lastsDays is not None:
                ET.SubElement(
                    scn, 'LastsDays').text = ywProject.scenes[scId].lastsDays

            if ywProject.scenes[scId].lastsHours is not None:
                ET.SubElement(
                    scn, 'LastsHours').text = ywProject.scenes[scId].lastsHours

            if ywProject.scenes[scId].lastsMinutes is not None:
                ET.SubElement(
                    scn, 'LastsMinutes').text = ywProject.scenes[scId].lastsMinutes

            # Plot related information

            if ywProject.scenes[scId].isReactionScene:
                ET.SubElement(scn, 'ReactionScene').text = '-1'

            if ywProject.scenes[scId].isSubPlot:
                ET.SubElement(scn, 'SubPlot').text = '-1'

            if ywProject.scenes[scId].goal is not None:
                ET.SubElement(scn, 'Goal').text = ywProject.scenes[scId].goal

            if ywProject.scenes[scId].conflict is not None:
                ET.SubElement(
                    scn, 'Conflict').text = ywProject.scenes[scId].conflict

            if ywProject.scenes[scId].outcome is not None:
                ET.SubElement(
                    scn, 'Outcome').text = ywProject.scenes[scId].outcome

            if ywProject.scenes[scId].characters is not None:
                scCharacters = ET.SubElement(scn, 'Characters')

                for crId in ywProject.scenes[scId].characters:
                    ET.SubElement(scCharacters, 'CharID').text = crId

            if ywProject.scenes[scId].locations is not None:
                scLocations = ET.SubElement(scn, 'Locations')

                for lcId in ywProject.scenes[scId].locations:
                    ET.SubElement(scLocations, 'LocID').text = lcId

            if ywProject.scenes[scId].items is not None:
                scItems = ET.SubElement(scn, 'Items')

                for itId in ywProject.scenes[scId].items:
                    ET.SubElement(scItems, 'ItemID').text = itId

        # Write attributes at chapter level to the xml element tree.

        chapters = ET.SubElement(root, 'CHAPTERS')

        sortOrder = 0

        for chId in ywProject.srtChapters:
            sortOrder += 1
            chp = ET.SubElement(chapters, 'CHAPTER')
            ET.SubElement(chp, 'ID').text = chId
            ET.SubElement(chp, 'SortOrder').text = str(sortOrder)

            if ywProject.chapters[chId].title is not None:
                ET.SubElement(
                    chp, 'Title').text = ywProject.chapters[chId].title

            if ywProject.chapters[chId].desc is not None:
                ET.SubElement(chp, 'Desc').text = ywProject.chapters[chId].desc

            if ywProject.chapters[chId].chLevel == 1:
                ET.SubElement(chp, 'SectionStart').text = '-1'

            if ywProject.chapters[chId].oldType is not None:
                ET.SubElement(chp, 'Type').text = str(
                    ywProject.chapters[chId].oldType)

            if ywProject.chapters[chId].chType is not None:
                ET.SubElement(chp, 'ChapterType').text = str(
                    ywProject.chapters[chId].chType)

            if ywProject.chapters[chId].isUnused:
                ET.SubElement(chp, 'Unused').text = '-1'

            sortSc = ET.SubElement(chp, 'Scenes')

            for scId in ywProject.chapters[chId].srtScenes:
                ET.SubElement(sortSc, 'ScID').text = scId

            chFields = ET.SubElement(chp, 'Fields')

            if ywProject.chapters[chId].title is not None:

                if ywProject.chapters[chId].title.startswith('@'):
                    ywProject.chapters[chId].suppressChapterTitle = True

            if ywProject.chapters[chId].suppressChapterTitle:
                ET.SubElement(
                    chFields, 'Field_SuppressChapterTitle').text = '1'

        self.indent_xml(root)
        ywProject._tree = ET.ElementTree(root)

        return 'SUCCESS'


class YwCnvUi(YwCnv):
    """Standalone yWriter converter with a 'silent' user interface. 
    """

    YW_EXTENSIONS = ['.yw5', '.yw6', '.yw7']

    def __init__(self):
        self.userInterface = Ui('')
        self.success = False
        self.fileFactory = None

    def run(self, sourcePath, suffix=None):
        """Create source and target objects and run conversion.
        """
        message, sourceFile, targetFile = self.fileFactory.get_file_objects(
            sourcePath, suffix)

        if not message.startswith('SUCCESS'):
            self.userInterface.set_info_how(message)

        elif not sourceFile.file_exists():
            self.userInterface.set_info_how(
                'ERROR: File "' + os.path.normpath(sourceFile.filePath) + '" not found.')

        elif sourceFile.EXTENSION in self.YW_EXTENSIONS:
            self.export_from_yw(sourceFile, targetFile)

        elif isinstance(targetFile.ywTreeBuilder, Yw7TreeCreator):
            self.create_yw7(sourceFile, targetFile)

        else:
            self.import_to_yw(sourceFile, targetFile)

        self.finish(sourcePath)

    def export_from_yw(self, sourceFile, targetFile):
        """Template method for conversion from yw to other.
        """
        self.userInterface.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')
        message = self.convert(sourceFile, targetFile)
        self.userInterface.set_info_how(message)

        if message.startswith('SUCCESS'):
            self.success = True

    def create_yw7(self, sourceFile, targetFile):
        """Template method for creation of a new yw7 project.
        """
        self.userInterface.set_info_what(
            'Create a yWriter project file from ' + sourceFile.DESCRIPTION + '\nNew project: "' + os.path.normpath(targetFile.filePath) + '"')

        if targetFile.file_exists():
            self.userInterface.set_info_how(
                'ERROR: "' + os.path.normpath(targetFile.filePath) + '" already exists.')

        else:
            message = self.convert(sourceFile, targetFile)
            self.userInterface.set_info_how(message)

            if message.startswith('SUCCESS'):
                self.success = True

    def import_to_yw(self, sourceFile, targetFile):
        """Template method for conversion from other to yw.
        """
        self.userInterface.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')
        message = self.convert(sourceFile, targetFile)
        self.userInterface.set_info_how(message)

        if message.startswith('SUCCESS'):
            self.success = True

    def confirm_overwrite(self, filePath):
        """ Invoked by the parent if a file already exists.
        """
        return self.userInterface.ask_yes_no('Overwrite existing file "' + os.path.normpath(filePath) + '"?')

    def delete_tempfile(self, filePath):
        """If an Office file exists, delete the temporary file."""

        if filePath.endswith('.html'):

            if os.path.isfile(filePath.replace('.html', '.odt')):

                try:
                    os.remove(filePath)

                except:
                    pass

        elif filePath.endswith('.csv'):

            if os.path.isfile(filePath.replace('.csv', '.ods')):

                try:
                    os.remove(filePath)

                except:
                    pass

    def finish(self, sourcePath):
        """Hook for actions to take place after the conversion."""


class UiCmd(Ui):
    """UI subclass implementing a console interface."""

    def __init__(self, title):
        """initialize UI. """
        print(title)

    def ask_yes_no(self, text):
        result = input('WARNING: ' + text + ' (y/n)')

        if result.lower() == 'y':
            return True

        else:
            return False

    def set_info_what(self, message):
        """What's the converter going to do?"""
        print(message)

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message
        print(message)

from abc import ABC
from abc import abstractmethod


class FileFactory(ABC):
    """Abstract class that instantiates a source file object
    and a target file object for conversion.
    """

    @abstractmethod
    def get_file_objects(self, sourcePath, suffix=None):
        """Factory method to be overwritten by subclasses.
        Return a tuple with three elements:
        * A message string starting with 'SUCCESS' or 'ERROR'
        * sourceFile: a Novel subclass instance
        * targetFile: a Novel subclass instance
        """





class YwFile(Novel):
    """Abstract yWriter xml project file representation.
    To be overwritten by version-specific subclasses. 
    """

    def strip_spaces(self, elements):
        """remove leading and trailing spaces from the elements
        of a list of strings.
        """
        stripped = []

        for element in elements:
            stripped.append(element.lstrip().rstrip())

        return stripped

    def read(self):
        """Parse the yWriter xml file located at filePath, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        """

        if self.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        message = self.ywTreeReader.read_element_tree(self)

        if message.startswith('ERROR'):
            return message

        root = self._tree.getroot()

        # Read locations from the xml element tree.

        for loc in root.iter('LOCATION'):
            lcId = loc.find('ID').text
            self.srtLocations.append(lcId)
            self.locations[lcId] = WorldElement()
            self.locations[lcId].title = loc.find('Title').text

            if loc.find('ImageFile') is not None:
                self.locations[lcId].image = loc.find('ImageFile').text

            if loc.find('Desc') is not None:
                self.locations[lcId].desc = loc.find('Desc').text

            if loc.find('AKA') is not None:
                self.locations[lcId].aka = loc.find('AKA').text

            if loc.find('Tags') is not None:

                if loc.find('Tags').text is not None:
                    tags = loc.find('Tags').text.split(';')
                    self.locations[lcId].tags = self.strip_spaces(tags)

        # Read items from the xml element tree.

        for itm in root.iter('ITEM'):
            itId = itm.find('ID').text
            self.srtItems.append(itId)
            self.items[itId] = WorldElement()
            self.items[itId].title = itm.find('Title').text

            if itm.find('ImageFile') is not None:
                self.items[itId].image = itm.find('ImageFile').text

            if itm.find('Desc') is not None:
                self.items[itId].desc = itm.find('Desc').text

            if itm.find('AKA') is not None:
                self.items[itId].aka = itm.find('AKA').text

            if itm.find('Tags') is not None:

                if itm.find('Tags').text is not None:
                    tags = itm.find('Tags').text.split(';')
                    self.items[itId].tags = self.strip_spaces(tags)

        # Read characters from the xml element tree.

        for crt in root.iter('CHARACTER'):
            crId = crt.find('ID').text
            self.srtCharacters.append(crId)
            self.characters[crId] = Character()
            self.characters[crId].title = crt.find('Title').text

            if crt.find('ImageFile') is not None:
                self.characters[crId].image = crt.find('ImageFile').text

            if crt.find('Desc') is not None:
                self.characters[crId].desc = crt.find('Desc').text

            if crt.find('AKA') is not None:
                self.characters[crId].aka = crt.find('AKA').text

            if crt.find('Tags') is not None:

                if crt.find('Tags').text is not None:
                    tags = crt.find('Tags').text.split(';')
                    self.characters[crId].tags = self.strip_spaces(tags)

            if crt.find('Notes') is not None:
                self.characters[crId].notes = crt.find('Notes').text

            if crt.find('Bio') is not None:
                self.characters[crId].bio = crt.find('Bio').text

            if crt.find('Goals') is not None:
                self.characters[crId].goals = crt.find('Goals').text

            if crt.find('FullName') is not None:
                self.characters[crId].fullName = crt.find('FullName').text

            if crt.find('Major') is not None:
                self.characters[crId].isMajor = True

            else:
                self.characters[crId].isMajor = False

        # Read attributes at novel level from the xml element tree.

        prj = root.find('PROJECT')

        if prj.find('Title') is not None:
            self.title = prj.find('Title').text

        if prj.find('AuthorName') is not None:
            self.author = prj.find('AuthorName').text

        if prj.find('Desc') is not None:
            self.desc = prj.find('Desc').text

        if prj.find('FieldTitle1') is not None:
            self.fieldTitle1 = prj.find('FieldTitle1').text

        if prj.find('FieldTitle2') is not None:
            self.fieldTitle2 = prj.find('FieldTitle2').text

        if prj.find('FieldTitle3') is not None:
            self.fieldTitle3 = prj.find('FieldTitle3').text

        if prj.find('FieldTitle4') is not None:
            self.fieldTitle4 = prj.find('FieldTitle4').text

        # Read attributes at chapter level from the xml element tree.

        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text
            self.chapters[chId] = Chapter()
            self.srtChapters.append(chId)

            self.chapters[chId].title = chp.find('Title').text

            if chp.find('Desc') is not None:
                self.chapters[chId].desc = chp.find('Desc').text

            if chp.find('SectionStart') is not None:
                self.chapters[chId].chLevel = 1

            else:
                self.chapters[chId].chLevel = 0

            if chp.find('Type') is not None:
                self.chapters[chId].oldType = int(chp.find('Type').text)

            if chp.find('ChapterType') is not None:
                self.chapters[chId].chType = int(chp.find('ChapterType').text)

            if chp.find('Unused') is not None:
                self.chapters[chId].isUnused = True

            else:
                self.chapters[chId].isUnused = False

            self.chapters[chId].suppressChapterTitle = False

            if self.chapters[chId].title is not None:

                if self.chapters[chId].title.startswith('@'):
                    self.chapters[chId].suppressChapterTitle = True

            for chFields in chp.findall('Fields'):

                if chFields.find('Field_SuppressChapterTitle') is not None:

                    if chFields.find('Field_SuppressChapterTitle').text == '1':
                        self.chapters[chId].suppressChapterTitle = True

                if chFields.find('Field_IsTrash') is not None:

                    if chFields.find('Field_IsTrash').text == '1':
                        self.chapters[chId].isTrash = True

                    else:
                        self.chapters[chId].isTrash = False

                if chFields.find('Field_SuppressChapterBreak') is not None:

                    if chFields.find('Field_SuppressChapterBreak').text == '1':
                        self.chapters[chId].suppressChapterBreak = True

                    else:
                        self.chapters[chId].suppressChapterBreak = False

                else:
                    self.chapters[chId].suppressChapterBreak = False

            self.chapters[chId].srtScenes = []

            if chp.find('Scenes') is not None:

                if not self.chapters[chId].isTrash:

                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        self.chapters[chId].srtScenes.append(scId)

        # Read attributes at scene level from the xml element tree.

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            self.scenes[scId] = Scene()

            self.scenes[scId].title = scn.find('Title').text

            if scn.find('Desc') is not None:
                self.scenes[scId].desc = scn.find('Desc').text

            if scn.find('RTFFile') is not None:
                self.scenes[scId].rtfFile = scn.find('RTFFile').text

            # This is relevant for yW5 files with no SceneContent:

            if scn.find('WordCount') is not None:
                self.scenes[scId].wordCount = int(
                    scn.find('WordCount').text)

            if scn.find('LetterCount') is not None:
                self.scenes[scId].letterCount = int(
                    scn.find('LetterCount').text)

            if scn.find('SceneContent') is not None:
                sceneContent = scn.find('SceneContent').text

                if sceneContent is not None:
                    self.scenes[scId].sceneContent = sceneContent

            if scn.find('Unused') is not None:
                self.scenes[scId].isUnused = True

            else:
                self.scenes[scId].isUnused = False

            for scFields in scn.findall('Fields'):

                if scFields.find('Field_SceneType') is not None:

                    if scFields.find('Field_SceneType').text == '1':
                        self.scenes[scId].isNotesScene = True

                    if scFields.find('Field_SceneType').text == '2':
                        self.scenes[scId].isTodoScene = True

            if scn.find('ExportCondSpecific') is None:
                self.scenes[scId].doNotExport = False

            elif scn.find('ExportWhenRTF') is not None:
                self.scenes[scId].doNotExport = False

            else:
                self.scenes[scId].doNotExport = True

            if scn.find('Status') is not None:
                self.scenes[scId].status = int(scn.find('Status').text)

            if scn.find('Notes') is not None:
                self.scenes[scId].sceneNotes = scn.find('Notes').text

            if scn.find('Tags') is not None:

                if scn.find('Tags').text is not None:
                    tags = scn.find('Tags').text.split(';')
                    self.scenes[scId].tags = self.strip_spaces(tags)

            if scn.find('Field1') is not None:
                self.scenes[scId].field1 = scn.find('Field1').text

            if scn.find('Field2') is not None:
                self.scenes[scId].field2 = scn.find('Field2').text

            if scn.find('Field3') is not None:
                self.scenes[scId].field3 = scn.find('Field3').text

            if scn.find('Field4') is not None:
                self.scenes[scId].field4 = scn.find('Field4').text

            if scn.find('AppendToPrev') is not None:
                self.scenes[scId].appendToPrev = True

            else:
                self.scenes[scId].appendToPrev = False

            if scn.find('SpecificDateTime') is not None:
                dateTime = scn.find('SpecificDateTime').text.split(' ')

                for dt in dateTime:

                    if '-' in dt:
                        self.scenes[scId].date = dt

                    elif ':' in dt:
                        self.scenes[scId].time = dt

            else:
                if scn.find('Day') is not None:
                    self.scenes[scId].day = scn.find('Day').text

                if scn.find('Hour') is not None:
                    self.scenes[scId].hour = scn.find('Hour').text

                if scn.find('Minute') is not None:
                    self.scenes[scId].minute = scn.find('Minute').text

            if scn.find('LastsDays') is not None:
                self.scenes[scId].lastsDays = scn.find('LastsDays').text

            if scn.find('LastsHours') is not None:
                self.scenes[scId].lastsHours = scn.find('LastsHours').text

            if scn.find('LastsMinutes') is not None:
                self.scenes[scId].lastsMinutes = scn.find('LastsMinutes').text

            if scn.find('ReactionScene') is not None:
                self.scenes[scId].isReactionScene = True

            else:
                self.scenes[scId].isReactionScene = False

            if scn.find('SubPlot') is not None:
                self.scenes[scId].isSubPlot = True

            else:
                self.scenes[scId].isSubPlot = False

            if scn.find('Goal') is not None:
                self.scenes[scId].goal = scn.find('Goal').text

            if scn.find('Conflict') is not None:
                self.scenes[scId].conflict = scn.find('Conflict').text

            if scn.find('Outcome') is not None:
                self.scenes[scId].outcome = scn.find('Outcome').text

            if scn.find('Characters') is not None:
                for crId in scn.find('Characters').iter('CharID'):

                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []

                    self.scenes[scId].characters.append(crId.text)

            if scn.find('Locations') is not None:
                for lcId in scn.find('Locations').iter('LocID'):

                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []

                    self.scenes[scId].locations.append(lcId.text)

            if scn.find('Items') is not None:
                for itId in scn.find('Items').iter('ItemID'):

                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []

                    self.scenes[scId].items.append(itId.text)

        return 'SUCCESS: ' + str(len(self.scenes)) + ' Scenes read from "' + os.path.normpath(self.filePath) + '".'

    def merge(self, novel):
        """Copy required attributes of the novel object.
        Return a message beginning with SUCCESS or ERROR.
        """

        if self.file_exists():
            message = self.read()
            # initialize data

            if message.startswith('ERROR'):
                return message

        return self.ywProjectMerger.merge_projects(self, novel)

    def write(self):
        """Open the yWriter xml file located at filePath and 
        replace a set of attributes not being None.
        Return a message beginning with SUCCESS or ERROR.
        """

        if self.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        message = self.ywTreeBuilder.build_element_tree(self)

        if message.startswith('ERROR'):
            return message

        message = self.ywTreeWriter.write_element_tree(self)

        if message.startswith('ERROR'):
            return message

        return self.ywPostprocessor.postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Test whether a .lock file placed by yWriter exists.
        """
        if os.path.isfile(self.filePath + '.lock'):
            return True

        else:
            return False



class Yw6TreeBuilder(YwTreeBuilder):
    """Build yWriter 6 project xml tree."""

    def build_element_tree(self, ywProject):
        """Modify the yWriter project attributes of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        """

        root = ywProject._tree.getroot()

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if ywProject.scenes[scId].sceneContent is not None:
                scn.find(
                    'SceneContent').text = ywProject.scenes[scId].sceneContent
                scn.find('WordCount').text = str(
                    ywProject.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(
                    ywProject.scenes[scId].letterCount)

        root.tag = 'YWRITER6'
        root.find('PROJECT').find('Ver').text = '5'
        ywProject._tree = ET.ElementTree(root)

        return YwTreeBuilder.build_element_tree(self, ywProject)



class YwTreeReader(ABC):
    """Read yWriter xml project file."""

    @abstractmethod
    def read_element_tree(self, ywFile):
        """Parse the yWriter xml file located at filePath, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        To be overwritten by file format specific subclasses.
        """


class Utf8TreeReader(YwTreeReader):
    """Read yWriter xml project file."""

    def read_element_tree(self, ywFile):
        """Parse the yWriter xml file located at filePath, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            ywFile._tree = ET.parse(ywFile.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(ywFile.filePath) + '".'

        return 'SUCCESS: XML element tree read in.'



class YwProjectMerger():
    """Merge two yWriter projects.
    """

    def merge_projects(self, target, source):
        """Overwrite existing target attributes with source attributes.
        Create target attributes, if not existing, but return ERROR.
        Return a message beginning with SUCCESS or ERROR.
        """

        # Merge and re-order locations.

        if source.srtLocations != []:
            target.srtLocations = source.srtLocations
            temploc = target.locations
            target.locations = {}

            for lcId in source.srtLocations:

                # Build a new target.locations dictionary sorted like the
                # source

                target.locations[lcId] = WorldElement()

                if not lcId in temploc:
                    # A new location has been added
                    temploc[lcId] = WorldElement()

                if source.locations[lcId].title:
                    # avoids deleting the title, if it is empty by accident
                    target.locations[lcId].title = source.locations[lcId].title

                else:
                    target.locations[lcId].title = temploc[lcId].title

                if source.locations[lcId].image is not None:
                    target.locations[lcId].image = source.locations[lcId].image

                else:
                    target.locations[lcId].desc = temploc[lcId].desc

                if source.locations[lcId].desc is not None:
                    target.locations[lcId].desc = source.locations[lcId].desc

                else:
                    target.locations[lcId].desc = temploc[lcId].desc

                if source.locations[lcId].aka is not None:
                    target.locations[lcId].aka = source.locations[lcId].aka

                else:
                    target.locations[lcId].aka = temploc[lcId].aka

                if source.locations[lcId].tags is not None:
                    target.locations[lcId].tags = source.locations[lcId].tags

                else:
                    target.locations[lcId].tags = temploc[lcId].tags

        # Merge and re-order items.

        if source.srtItems != []:
            target.srtItems = source.srtItems
            tempitm = target.items
            target.items = {}

            for itId in source.srtItems:

                # Build a new target.items dictionary sorted like the
                # source

                target.items[itId] = WorldElement()

                if not itId in tempitm:
                    # A new item has been added
                    tempitm[itId] = WorldElement()

                if source.items[itId].title:
                    # avoids deleting the title, if it is empty by accident
                    target.items[itId].title = source.items[itId].title

                else:
                    target.items[itId].title = tempitm[itId].title

                if source.items[itId].image is not None:
                    target.items[itId].image = source.items[itId].image

                else:
                    target.items[itId].image = tempitm[itId].image

                if source.items[itId].desc is not None:
                    target.items[itId].desc = source.items[itId].desc

                else:
                    target.items[itId].desc = tempitm[itId].desc

                if source.items[itId].aka is not None:
                    target.items[itId].aka = source.items[itId].aka

                else:
                    target.items[itId].aka = tempitm[itId].aka

                if source.items[itId].tags is not None:
                    target.items[itId].tags = source.items[itId].tags

                else:
                    target.items[itId].tags = tempitm[itId].tags

        # Merge and re-order characters.

        if source.srtCharacters != []:
            target.srtCharacters = source.srtCharacters
            tempchr = target.characters
            target.characters = {}

            for crId in source.srtCharacters:

                # Build a new target.characters dictionary sorted like the
                # source

                target.characters[crId] = Character()

                if not crId in tempchr:
                    # A new character has been added
                    tempchr[crId] = Character()

                if source.characters[crId].title:
                    # avoids deleting the title, if it is empty by accident
                    target.characters[crId].title = source.characters[crId].title

                else:
                    target.characters[crId].title = tempchr[crId].title

                if source.characters[crId].image is not None:
                    target.characters[crId].image = source.characters[crId].image

                else:
                    target.characters[crId].image = tempchr[crId].image

                if source.characters[crId].desc is not None:
                    target.characters[crId].desc = source.characters[crId].desc

                else:
                    target.characters[crId].desc = tempchr[crId].desc

                if source.characters[crId].aka is not None:
                    target.characters[crId].aka = source.characters[crId].aka

                else:
                    target.characters[crId].aka = tempchr[crId].aka

                if source.characters[crId].tags is not None:
                    target.characters[crId].tags = source.characters[crId].tags

                else:
                    target.characters[crId].tags = tempchr[crId].tags

                if source.characters[crId].notes is not None:
                    target.characters[crId].notes = source.characters[crId].notes

                else:
                    target.characters[crId].notes = tempchr[crId].notes

                if source.characters[crId].bio is not None:
                    target.characters[crId].bio = source.characters[crId].bio

                else:
                    target.characters[crId].bio = tempchr[crId].bio

                if source.characters[crId].goals is not None:
                    target.characters[crId].goals = source.characters[crId].goals

                else:
                    target.characters[crId].goals = tempchr[crId].goals

                if source.characters[crId].fullName is not None:
                    target.characters[crId].fullName = source.characters[crId].fullName

                else:
                    target.characters[crId].fullName = tempchr[crId].fullName

                if source.characters[crId].isMajor is not None:
                    target.characters[crId].isMajor = source.characters[crId].isMajor

                else:
                    target.characters[crId].isMajor = tempchr[crId].isMajor

        # Merge scenes.

        mismatchCount = 0

        for scId in source.scenes:

            if not scId in target.scenes:
                target.scenes[scId] = Scene()
                mismatchCount += 1

            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                target.scenes[scId].title = source.scenes[scId].title

            if source.scenes[scId].desc is not None:
                target.scenes[scId].desc = source.scenes[scId].desc

            if source.scenes[scId].sceneContent is not None:
                target.scenes[scId].sceneContent = source.scenes[scId].sceneContent

            if source.scenes[scId].rtfFile is not None:
                target.scenes[scId].sceneContent = source.scenes[scId].sceneContent

            if source.scenes[scId].isUnused is not None:
                target.scenes[scId].isUnused = source.scenes[scId].isUnused

            if source.scenes[scId].isNotesScene is not None:
                target.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene

            if source.scenes[scId].isTodoScene is not None:
                target.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene

            if source.scenes[scId].status is not None:
                target.scenes[scId].status = source.scenes[scId].status

            if source.scenes[scId].sceneNotes is not None:
                target.scenes[scId].sceneNotes = source.scenes[scId].sceneNotes

            if source.scenes[scId].tags is not None:
                target.scenes[scId].tags = source.scenes[scId].tags

            if source.scenes[scId].field1 is not None:
                target.scenes[scId].field1 = source.scenes[scId].field1

            if source.scenes[scId].field2 is not None:
                target.scenes[scId].field2 = source.scenes[scId].field2

            if source.scenes[scId].field3 is not None:
                target.scenes[scId].field3 = source.scenes[scId].field3

            if source.scenes[scId].field4 is not None:
                target.scenes[scId].field4 = source.scenes[scId].field4

            if source.scenes[scId].appendToPrev is not None:
                target.scenes[scId].appendToPrev = source.scenes[scId].appendToPrev

            if source.scenes[scId].date is not None:
                target.scenes[scId].date = source.scenes[scId].date

            if source.scenes[scId].time is not None:
                target.scenes[scId].time = source.scenes[scId].time

            if source.scenes[scId].minute is not None:
                target.scenes[scId].minute = source.scenes[scId].minute

            if source.scenes[scId].hour is not None:
                target.scenes[scId].hour = source.scenes[scId].hour

            if source.scenes[scId].day is not None:
                target.scenes[scId].day = source.scenes[scId].day

            if source.scenes[scId].lastsMinutes is not None:
                target.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes

            if source.scenes[scId].lastsHours is not None:
                target.scenes[scId].lastsHours = source.scenes[scId].lastsHours

            if source.scenes[scId].lastsDays is not None:
                target.scenes[scId].lastsDays = source.scenes[scId].lastsDays

            if source.scenes[scId].isReactionScene is not None:
                target.scenes[scId].isReactionScene = source.scenes[scId].isReactionScene

            if source.scenes[scId].isSubPlot is not None:
                target.scenes[scId].isSubPlot = source.scenes[scId].isSubPlot

            if source.scenes[scId].goal is not None:
                target.scenes[scId].goal = source.scenes[scId].goal

            if source.scenes[scId].conflict is not None:
                target.scenes[scId].conflict = source.scenes[scId].conflict

            if source.scenes[scId].outcome is not None:
                target.scenes[scId].outcome = source.scenes[scId].outcome

            if source.scenes[scId].characters is not None:
                target.scenes[scId].characters = []

                for crId in source.scenes[scId].characters:

                    if crId in target.characters:
                        target.scenes[scId].characters.append(crId)

            if source.scenes[scId].locations is not None:
                target.scenes[scId].locations = []

                for lcId in source.scenes[scId].locations:

                    if lcId in target.locations:
                        target.scenes[scId].locations.append(lcId)

            if source.scenes[scId].items is not None:
                target.scenes[scId].items = []

                for itId in source.scenes[scId].items:

                    if itId in target.items:
                        target.scenes[scId].append(itId)

        # Merge chapters.

        scenesAssigned = []

        for chId in source.chapters:

            if not chId in target.chapters:
                target.chapters[chId] = Chapter()
                mismatchCount += 1

            if source.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                target.chapters[chId].title = source.chapters[chId].title

            if source.chapters[chId].desc is not None:
                target.chapters[chId].desc = source.chapters[chId].desc

            if source.chapters[chId].chLevel is not None:
                target.chapters[chId].chLevel = source.chapters[chId].chLevel

            if source.chapters[chId].oldType is not None:
                target.chapters[chId].oldType = source.chapters[chId].oldType

            if source.chapters[chId].chType is not None:
                target.chapters[chId].chType = source.chapters[chId].chType

            if source.chapters[chId].isUnused is not None:
                target.chapters[chId].isUnused = source.chapters[chId].isUnused

            if source.chapters[chId].suppressChapterTitle is not None:
                target.chapters[chId].suppressChapterTitle = source.chapters[chId].suppressChapterTitle

            if source.chapters[chId].suppressChapterBreak is not None:
                target.chapters[chId].suppressChapterBreak = source.chapters[chId].suppressChapterBreak

            if source.chapters[chId].isTrash is not None:
                target.chapters[chId].isTrash = source.chapters[chId].isTrash

            if source.chapters[chId].srtScenes is not None:
                target.chapters[chId].srtScenes = []

                for scId in source.chapters[chId].srtScenes:

                    if (scId in target.scenes) and not (scId in scenesAssigned):
                        target.chapters[chId].srtScenes.append(scId)
                        scenesAssigned.append(scId)

        # Merge attributes at novel level.

        if source.title:
            # avoids deleting the title, if it is empty by accident
            target.title = source.title

        if source.desc is not None:
            target.desc = source.desc

        if source.author is not None:
            target.author = source.author

        if source.fieldTitle1 is not None:
            target.fieldTitle1 = source.fieldTitle1

        if source.fieldTitle2 is not None:
            target.fieldTitle2 = source.fieldTitle2

        if source.fieldTitle3 is not None:
            target.fieldTitle3 = source.fieldTitle3

        if source.fieldTitle4 is not None:
            target.fieldTitle4 = source.fieldTitle4

        if source.srtChapters != []:
            target.srtChapters = []

            for chId in source.srtChapters:
                target.srtChapters.append(chId)

        if mismatchCount > 0:
            return 'ERROR: Project structure mismatch.'

        else:
            return 'SUCCESS'



class YwTreeWriter(ABC):
    """Write yWriter 7 xml project file."""

    @abstractmethod
    def write_element_tree(self, ywProject):
        """Write back the xml element tree to a yWriter xml file located at filePath.
        Return a message beginning with SUCCESS or ERROR.
        To be overwritten by file format specific subclasses.
        """


class Utf8TreeWriter(YwTreeWriter):
    """Write utf-8 encoded yWriter project file."""

    def write_element_tree(self, ywProject):
        """Write back the xml element tree to a yWriter xml file located at filePath.
        Return a message beginning with SUCCESS or ERROR.
        """

        try:
            ywProject._tree.write(
                ywProject.filePath, xml_declaration=False, encoding='utf-8')

        except(PermissionError):
            return 'ERROR: "' + os.path.normpath(ywProject.filePath) + '" is write protected.'

        return 'SUCCESS'

from html import unescape


class YwPostprocessor(ABC):

    @abstractmethod
    def postprocess_xml_file(self, ywFile):
        '''Postprocess the xml file created by ElementTree:
        Put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text.
        Return a message beginning with SUCCESS or ERROR.
        To be overwritten by file format specific subclasses.
        '''

    def format_xml(self, text):
        '''Postprocess the xml file created by ElementTree:
           Insert the missing CDATA tags,
           and replace xml entities by plain text.
        '''

        cdataTags = ['Title', 'AuthorName', 'Bio', 'Desc',
                     'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                     'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                     'AKA', 'ImageFile', 'FullName', 'Goals',
                     'Notes', 'RTFFile', 'SceneContent',
                     'Outcome', 'Goal', 'Conflict']
        # Names of yWriter xml elements containing CDATA.
        # ElementTree.write omits CDATA tags, so they have to be inserted
        # afterwards.

        lines = text.split('\n')
        newlines = []

        for line in lines:

            for tag in cdataTags:
                line = re.sub('\<' + tag + '\>', '<' +
                              tag + '><![CDATA[', line)
                line = re.sub('\<\/' + tag + '\>',
                              ']]></' + tag + '>', line)

            newlines.append(line)

        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)

        return text


class Utf8Postprocessor(YwPostprocessor):
    """Postprocess ANSI encoded yWriter project."""

    def postprocess_xml_file(self, filePath):
        '''Postprocess the xml file created by ElementTree:
        Put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text.
        Return a message beginning with SUCCESS or ERROR.
        '''

        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()

        text = self.format_xml(text)
        text = '<?xml version="1.0" encoding="utf-8"?>\n' + text

        try:

            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Can not write "' + os.path.normpath(filePath) + '".'

        return 'SUCCESS: "' + os.path.normpath(filePath) + '" written.'


class Yw6File(YwFile):
    """yWriter 6 project file representation."""

    DESCRIPTION = 'yWriter 6 project'
    EXTENSION = '.yw6'

    def __init__(self, filePath):
        YwFile.__init__(self, filePath)
        self.ywTreeReader = Utf8TreeReader()
        self.ywProjectMerger = YwProjectMerger()
        self.ywTreeBuilder = Yw6TreeBuilder()
        self.ywTreeWriter = Utf8TreeWriter()
        self.ywPostprocessor = Utf8Postprocessor()




class Yw7TreeBuilder(YwTreeBuilder):
    """Build yWriter 7 project xml tree."""

    def build_element_tree(self, ywProject):
        """Modify the yWriter project attributes of an existing xml element tree.
        Return a message beginning with SUCCESS or ERROR.
        """

        root = ywProject._tree.getroot()

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if ywProject.scenes[scId].sceneContent is not None:
                scn.find(
                    'SceneContent').text = ywProject.scenes[scId].sceneContent
                scn.find('WordCount').text = str(
                    ywProject.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(
                    ywProject.scenes[scId].letterCount)

            try:
                scn.remove(scn.find('RTFFile'))

            except:
                pass

        root.tag = 'YWRITER7'
        root.find('PROJECT').find('Ver').text = '7'
        ywProject._tree = ET.ElementTree(root)

        return YwTreeBuilder.build_element_tree(self, ywProject)


class Yw7File(YwFile):
    """yWriter 7 project file representation.
    """

    DESCRIPTION = 'yWriter 7 project'
    EXTENSION = '.yw7'

    def __init__(self, filePath):
        YwFile.__init__(self, filePath)
        self.ywTreeReader = Utf8TreeReader()
        self.ywProjectMerger = YwProjectMerger()
        self.ywTreeBuilder = Yw7TreeBuilder()
        self.ywTreeWriter = Utf8TreeWriter()
        self.ywPostprocessor = Utf8Postprocessor()



class YwProjectCreator(YwProjectMerger):
    """Create a new project.
    """

    def merge_projects(self, target, source):
        """Create target attributes with source attributes.
        Return a message beginning with SUCCESS or ERROR.
        """
        YwProjectMerger.merge_projects(self, target, source)
        return 'SUCCESS'


class MdFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def __init__(self, markdownMode=False, noSceneTitles=False):
        self.markdownMode = markdownMode
        self.noSceneTitles = noSceneTitles

    def get_file_objects(self, sourcePath, suffix=MdFile.SUFFIX):
        """Return a tuple with three elements:
        * A message string starting with 'SUCCESS' or 'ERROR'
        * sourceFile: a Novel subclass instance
        * targetFile: a Novel subclass instance
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath)
            isYwProject = True

        elif fileExtension == Yw6File.EXTENSION:
            sourceFile = Yw6File(sourcePath)
            isYwProject = True

        else:
            isYwProject = False

        if isYwProject:
            targetFile = MdFile(
                fileName + suffix + MdFile.EXTENSION, self.markdownMode, self.noSceneTitles)
            targetFile.SUFFIX = suffix

        else:
            sourceFile = MdFile(
                sourcePath, self.markdownMode, self.noSceneTitles)
            targetFile = Yw7File(fileName + Yw7File.EXTENSION)
            targetFile.ywTreeBuilder = Yw7TreeCreator()
            targetFile.ywProjectMerger = YwProjectCreator()

        return 'SUCCESS', sourceFile, targetFile


class Converter(YwCnvUi):
    """yWriter converter with a command line UI. 
    """

    def __init__(self, silentMode, markdownMode=False, noSceneTitles=False):
        YwCnvUi.__init__(self)
        self.fileFactory = MdFileFactory(markdownMode, noSceneTitles)

        if not silentMode:
            self.userInterface = UiCmd('Export yWriter project to Markdown')


def run(sourcePath, silentMode=True, markdownMode=False, noSceneTitles=False):
    Converter(silentMode, markdownMode, noSceneTitles).run(
        sourcePath, MdFile.SUFFIX)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Markdown converter for yWriter projects.',
        epilog='')
    parser.add_argument('sourcePath', metavar='Sourcefile',
                        help="The path of the source file for the conversion. "
                        "If it's a yWriter project file with extension 'yw6' or 'yw7', "
                        "a new Markdown formatted text document will be created. "
                        "Otherwise, the source file will be considered a Markdown "
                        "formatted file to be converted to a new yWriter 7 project. "
                        "Existing yWriter projects are not overwritten.")

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    parser.add_argument('--md',
                        action="store_true",
                        help='the scenes in the yWriter project are Markdown formatted')
    parser.add_argument('--notitles',
                        action="store_true",
                        help='do not associate comments at the beginning of the scene with scene titles')
    args = parser.parse_args()

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    if args.md:
        markdownMode = True

    else:
        markdownMode = False

    if args.notitles:
        noSceneTitles = True

    else:
        noSceneTitles = False

    if os.path.isfile(args.sourcePath):
        run(args.sourcePath, silentMode, markdownMode, noSceneTitles)

    else:
        print('ERROR: File not found.')