"""Provide a class for Markdown file representation. 

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re

from pywriter.pywriter_globals import ERROR
from pywriter.file.file_export import FileExport
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene


class MdFile(FileExport):
    """Markdown file representation.

    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = 'Markdown file'
    EXTENSION = '.md'
    SUFFIX = ''
    SCENE_DIVIDER = '* * *'
    _fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''
    _partTemplate = '\n# ${Title}\n\n'
    _chapterTemplate = '\n## ${Title}\n\n'
    _sceneTemplate = '<!---${Title}--->${SceneContent}\n\n'
    _sceneDivider = f'\n\n{SCENE_DIVIDER}\n\n'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            markdown_mode -- bool: if True, the scenes in the yWriter project are Markdown formatted.
            scene_titles -- bool: if True, associate comments at the beginning of the scene with scene titles
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._markdownMode = kwargs['markdown_mode']
        self._sceneTitles = kwargs['scene_titles']
        if not self._sceneTitles:
            self._sceneTemplate = self._sceneTemplate.replace('<!---${Title}--->', '')

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        Suppress the chapter title if necessary.
        Extends the superclass method.
        """
        chapterMapping = super()._get_chapterMapping(chId, chapterNumber)
        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''
        return chapterMapping

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to Markdown.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if quick:
            # Just clean up a one-liner without sophisticated formatting.
            if text is None:
                return ''
            else:
                return text

        MD_REPLACEMENTS = [
            ('[i] ', ' [i]'),
            ('[b] ', ' [b]'),
            ('[s] ', ' [s]'),
            ('[i]', '*'),
            ('[/i]', '*'),
            ('[b]', '**'),
            ('[/b]', '**'),
            ('/*', '<!---'),
            ('*/', '--->'),
            ('  ', ' '),
        ]
        if not self._markdownMode:
            MD_REPLACEMENTS.insert(0, ('\n', '\n\n'))
        try:
            for yw, md in MD_REPLACEMENTS:
                text = text.replace(yw, md)
            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
            # Remove highlighting, alignment, and underline tags
        except AttributeError:
            text = ''
        return text

    def _convert_to_yw(self, text):
        """Convert Markdown to yWriter 7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        Return a yw7 markup string.
        Overrides the superclass method.
        """
        if not self._markdownMode:
            text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
            text = re.sub('\*([^ ].+?[^ ])\*', '[i]\\1[/i]', text)
            MD_REPLACEMENTS = [
                ('\n\n', '\n'),
                ('<!---', '/*'),
                ('--->', '*/'),
            ]
            try:
                for md, yw in MD_REPLACEMENTS:
                    text = text.replace(md, yw)
            except AttributeError:
                text = ''
        return text

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        LOW_WORDCOUNT = 10
        # Defines the difference between "Outline" and "Draft" 
        def write_scene_content(scId, lines):
            if scId is not None:
                text = '\n'.join(lines)
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
                cnvText = self._convert_to_yw(mdText)
                mdLines = (cnvText).split('\n')
        except(FileNotFoundError):
            return f'{ERROR}"{os.path.normpath(self.filePath)}" not found.'

        except:
            return f'{ERROR}Can not parse "{os.path.normpath(self.filePath)}".'

        if self._markdownMode:
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
                self.scenes[scId].title = f'Scene {scCount}'
                if self._sceneTitles and mdLine.startswith(commentStart):
                    # The scene title is prefixed as a comment.
                    try:
                        scTitle, scContent = mdLine.split(
                            sep=commentEnd, maxsplit=1)
                        self.scenes[scId].title = scTitle.lstrip(commentStart)
                        lines = [scContent]
                    except:
                        lines = [mdLine]
                else:
                    lines = [mdLine]
        return 'Markdown formatted text converted to novel structure.'
