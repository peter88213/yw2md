""" Build a python script for the yw2md distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the pywriter package.

The PyWriter project (see see https://github.com/peter88213/PyWriter)
must be located on the same directory level as the yw2md project. 

For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE_GUI = 'yw2md_.pyw'
TARGET_FILE_GUI = BUILD + 'yw2md.pyw'
SOURCE_FILE_CMD = 'yw2md_.py'
TARGET_FILE_CMD = BUILD + 'yw2md.py'


def main():
    os.chdir(SRC)

    try:
        os.remove(TARGET_FILE_GUI)

    except:
        pass

    try:
        os.remove(TARGET_FILE_CMD)

    except:
        pass

    inliner.run(SOURCE_FILE_GUI,
                TARGET_FILE_GUI, 'pywmd', '../src/')
    inliner.run(TARGET_FILE_GUI,
                TARGET_FILE_GUI, 'pywriter', '../../PyWriter/src/')
    inliner.run(SOURCE_FILE_CMD,
                TARGET_FILE_CMD, 'pywmd', '../src/')
    inliner.run(TARGET_FILE_CMD,
                TARGET_FILE_CMD, 'pywriter', '../../PyWriter/src/')
    print('Done.')


if __name__ == '__main__':
    main()
