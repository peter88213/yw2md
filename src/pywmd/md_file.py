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
    """

    DESCRIPTION = 'Markdown file'
    EXTENSION = '.md'
    SUFFIX = ''

    SCENE_DIVIDER = '* * *'

    fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''
    partTemplate = '\n# ${Title}\n\n'
    chapterTemplate = '\n## ${Title}\n\n'
    sceneTemplate = '<!---${Title}--->${SceneContent}\n\n'
    sceneDivider = f'\n\n{SCENE_DIVIDER}\n\n'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._markdownMode = kwargs['markdown_mode']
        self._sceneTitles = kwargs['scene_titles']

        if not self._sceneTitles:
            self.sceneTemplate = self.sceneTemplate.replace('<!---${Title}--->', '')

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = super().get_chapterMapping(chId, chapterNumber)

        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''

        return chapterMapping

    def convert_from_yw(self, text):
        """Convert yw7 markup to Markdown.
        """

        MD_REPLACEMENTS = [
            ['[i] ', ' [i]'],
            ['[b] ', ' [b]'],
            ['[s] ', ' [s]'],
            ['[i]', '*'],
            ['[/i]', '*'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['/*', '<!---'],
            ['*/', '--->'],
            ['  ', ' '],
        ]

        if not self._markdownMode:
            MD_REPLACEMENTS.insert(0, ['\n', '\n\n'])

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
            # Remove highlighting, alignment, and underline tags

        except AttributeError:
            text = ''

        return text

    def convert_to_yw(self, text):
        """Convert Markdown to yw7 markup.
        """
        if not self._markdownMode:
            text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
            text = re.sub('\*([^ ].+?[^ ])\*', '[i]\\1[/i]', text)

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

        return text

    def read(self):
        """Parse the Markdown file located at filePath
        Return a message beginning with the ERROR constant in case of error.
        """
        LOW_WORDCOUNT = 10

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
                cnvText = self.convert_to_yw(mdText)
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
