#!/usr/bin/env python3
"""Export yWriter project to markdown. 

This is an example for easily customizing the yw2md converter.

How it works:

- Place the original yw2md.pyw file somewhere Python can find it. It's now used as a class library.
- Customize the code of the MyExport() subclass to match your special needs.


Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os
import argparse

from yw2md import Converter
from yw2md import MdExport
from yw2md import FileFactory
from yw2md import Yw6File
from yw2md import Yw7File


class MyExport(MdExport):
    """
    *** Edit this class for customization ***
    """

    EXTENSION = '.txt'  # Override '.md'

    # *** Customize fhe following templates if necessary ***

    fileHeader = '''*${Title}*
    
  by the famous, always-award-winning bestseller author
  
_${AuthorName}_  
  
'''

    partTemplate = '\n## ${Title}  \n'  # Make parts look like regular chapters

    chapterTemplate = '\n## ${Title}  \n'  # Use alternative linefeeds

    sceneTemplate = '${SceneContent}  \n'

    sceneDivider = '\n* * *  \n'

    def convert_from_yw(self, text):
        """
        *** Customize this for alternaive Markdown dialects ***
        """
        MD_REPLACEMENTS = [
            ['  ', ' '],
            ['\n', '  \n'],
            ['[i]', '_'],
            ['[/i]', '_'],
            ['[b]', '*'],
            ['[/b]', '*'],
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


class MyFileFactory(FileFactory):
    """This class is needed to instantiate the customized MyExport class.

    *** Do not edit *** 
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

        targetFile = MyExport(fileName + MyExport.SUFFIX + MyExport.EXTENSION)
        targetFile.SUFFIX = MyExport.SUFFIX

        return 'SUCCESS', sourceFile, targetFile


class MyConverter(Converter):
    """This class is needed to instantiate the customized MyExport class. 

    *** Do not edit *** 
    """

    def __init__(self, silentMode):
        Converter.__init__(self, silentMode)
        self.fileFactory = MyFileFactory()


def run(sourcePath, silentMode=True):
    MyConverter(silentMode).run(sourcePath, MyExport.SUFFIX)


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
