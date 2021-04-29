#!/usr/bin/env python3
"""Export yWriter project to markdown. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os
import argparse

from pywriter.converter.yw_cnv_tk import YwCnvTk
from pywriter.file.file_export import FileExport
from pywriter.converter.file_factory import FileFactory
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File


class MdExport(FileExport):
    """Export content or metadata from an yWriter project to a HTML file.
    """

    DESCRIPTION = 'Markdown export'
    EXTENSION = '.md'
    SUFFIX = ''

    fileHeader = '''**$Title**  
  
*$AuthorName*  
  
'''

    partTemplate = '\n# $Title  \n'

    chapterTemplate = '\n## $Title  \n'

    sceneTemplate = '$SceneContent  \n'

    sceneDivider = ' \n'
    #sceneDivider = '\n* * *\n'

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = FileExport.get_chapterMapping(
            self, chId, chapterNumber)

        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''

        return chapterMapping

    def convert_from_yw(self, text):
        """Convert yw7 markup to markdown.
        """
        MD_REPLACEMENTS = [
            ['  ', ' '],
            ['\n', '  \n'],
            ['[i]', '*'],
            ['[/i]', '*'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['/*', '<!---'],
            ['*/', '--->'],
        ]

        try:

            for r in MD_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)


class MdFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def get_file_objects(self, sourcePath, suffix):
        """Return a tuple with three elements:
        * A message string starting with 'SUCCESS' or 'ERROR'
        * sourceFile: a Novel subclass instance
        * targetFile: a Novel subclass instance
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath)

        elif fileExtension == Yw6File.EXTENSION:
            sourceFile = Yw6File(sourcePath)

        else:
            return 'ERROR: File type is not supported.', None, None

        targetFile = MdExport(fileName + MdExport.SUFFIX + MdExport.EXTENSION)
        targetFile.SUFFIX = MdExport.SUFFIX

        return 'SUCCESS', sourceFile, targetFile


class Converter(YwCnvTk):
    """yWriter converter with a simple tkinter GUI. 
    """

    def __init__(self, silentMode):
        YwCnvTk.__init__(self, silentMode)
        self.fileFactory = MdFileFactory()


def run(sourcePath, silentMode=True):
    Converter(silentMode).run(sourcePath, MdExport.SUFFIX)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export yWriter project to md.',
        epilog='')
    parser.add_argument('sourcePath', metavar='Project',
                        help='yWriter project file')
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    run(args.sourcePath, silentMode)
