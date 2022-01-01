"""Markdown converter for yWriter projects.

This is a yw2md sample application.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
SUFFIX = ''

import sys

from pywriter.ui.ui_tk import UiTk
from pywriter.converter.yw_cnv_ui import YwCnvUi

from pywriter.yw.yw7_file import Yw7File
from pywmd.md_file import MdFile
from pywriter.converter.new_project_factory import NewProjectFactory


class MdConverter(YwCnvUi):
    """A converter class for html export."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [MdFile]

    def __init__(self):
        """Extend the superclass constructor.

        Override newProjectFactory by a project
        specific implementation that accepts the
        .md file extension. 
        """
        YwCnvUi.__init__(self)
        self.newProjectFactory = NewProjectFactory()


def run(sourcePath, suffix=None, markdownMode=False, noSceneTitles=False):
    ui = UiTk('yWriter import/export')
    converter = MdConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix, 'markdownMode': markdownMode,
              'noSceneTitles': noSceneTitles}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
