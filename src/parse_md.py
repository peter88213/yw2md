"""Save the result of Markdown-to-yWriter conversion

Just an auxiliary script for development,
to see the result of MdFile.convert_to_yw.
"""
from md_yw import MdFile
import sys


if __name__ == '__main__':
    sourceFile = sys.argv[1]

    with open(sourceFile, encoding='utf-8') as f:
        mdText = f.read()

    dummy = MdFile('')
    text = MdFile.convert_to_yw(dummy, mdText)
    lines = (text).split('\n')
    text = '\n'.join(lines)

    with open('test.md', 'w', encoding='utf-8') as f:
        f.write(text)
