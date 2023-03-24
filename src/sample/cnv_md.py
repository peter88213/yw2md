"""Markdown converter for yWriter projects.

This is a yw2md sample application.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
from pywriter.ui.ui_tk import UiTk
from pywriter.converter.yw_cnv_ff import YwCnvFf
from pywriter.yw.yw7_file import Yw7File
from yw2mdlib.md_file import MdFile
from yw2mdlib.new_project_factory import NewProjectFactory

SUFFIX = ''


class MdConverter(YwCnvFf):
    """A converter class for html export."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [MdFile]

    def __init__(self):
        """Extends the superclass constructor.

        Delegate the newProjectFactory to a project
        specific implementation that accepts the
        .md file extension.
        Extends the super class constructor.
        """
        super().__init__()
        self.newProjectFactory = NewProjectFactory()


def run(sourcePath, suffix=None, markdownMode=False, noTitles=False):
    ui = UiTk('yWriter import/export')
    converter = MdConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix, 'markdown_mode': markdownMode,
              'scene_titles': not noTitles}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
