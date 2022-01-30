#!/usr/bin/env python3
"""Export yWriter project to markdown. 

This is an example for easily customizing the yw2md converter.

How it works:

- Place the original yw2md.pyw file somewhere Python can find it. It's now used as a class library.
- Customize the code of the MyFile() subclass to match your special needs.


Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os
import argparse

from yw2md import ERROR
from yw2md import Ui
from yw2md import UiCmd
from yw2md import MdConverter
from yw2md import MdFile
from yw2md import Yw7File


class MyFile(MdFile):
    """Markdown file representation

    *** Edit this class for customization ***
    """

    EXTENSION = '.md'  # Can be changed to another extension
    SCENE_DIVIDER = '* * *'

    ''' Customize fhe following templates if necessary.

A documentation of templates and placeholders is here:
https://github.com/peter88213/PyWriter/tree/master/src/pywriter/file#readme

'''

    fileHeader = '''**${Title}**  
  
*${AuthorName}*  
  
'''

    partTemplate = '\n## ${Title}\n\n'  # Make parts look like regular chapters

    chapterTemplate = '\n## ${Title}\n\n'

    sceneTemplate = '${SceneContent}\n\n'

    sceneDivider = '\n\n' + SCENE_DIVIDER + '\n\n'

    def convert_from_yw(self, text):
        """
        *** Customize this for alternaive Markdown dialects ***
        """
        MD_REPLACEMENTS = [
            ['\n', '\n\n'],
            ['[i]', '*'],
            ['[/i]', '*'],
            ['[b]', '**'],
            ['[/b]', '**'],
            ['/*', '<!---'],
            ['*/', '--->'],
            ['  ', ' '],
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

    def convert_to_yw(self, text):
        """Convert Markdown to yw7 markup.

        *** Customize this for alternaive Markdown dialects ***
        """
        if not self.markdownMode:

            # Save the scene dividers: they may contain asterisks
            # Note: The superclass MdFile implements a regex-based solution
            # here.

            SAFE_SCENE_DIVIDER = '~ ~ ~'
            text = text.replace(self.SCENE_DIVIDER, SAFE_SCENE_DIVIDER)

            text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
            text = re.sub('\*(.+?)\*', '[i]\\1[/i]', text)

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


class MyConverter(MdConverter):
    """A converter class for Markdown export."""
    EXPORT_TARGET_CLASSES = [MyFile]
    CREATE_SOURCE_CLASSES = [MyFile]


def run(sourcePath, silentMode=True, markdownMode=False, noSceneTitles=False):

    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('yw2md')

    converter = MyConverter()
    converter.ui = ui
    kwargs = {'suffix': MdFile.SUFFIX, 'markdownMode': markdownMode,
              'noSceneTitles': noSceneTitles}
    converter.run(sourcePath, **kwargs)


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
        print(f'{ERROR} File not found.')
