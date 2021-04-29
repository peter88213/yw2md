""" Python unit tests for the yw2md project.

Test suite for yw2md.pyw.

For further information see https://github.com/peter88213/yw2md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import unittest
import yw2md


# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'
TEMPLATE_PATH = '../../template/'

# To be placed in TEST_DATA_PATH:

# Test data
YW7 = 'normal.yw7'
YW7_MD_FORMATTED = 'markdown.yw7'
FROM_NORMAL_FORMATTED = 'normal.md'
FROM_MD_FORMATTED = 'markdown.md'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def copy_file(inputFile, outputFile):
    with open(inputFile, 'rb') as f:
        myData = f.read()
    with open(outputFile, 'wb') as f:
        f.write(myData)
    return()


def remove_all_testfiles():

    try:
        os.remove(TEST_EXEC_PATH + YW7)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + YW7_MD_FORMATTED)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + FROM_NORMAL_FORMATTED)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + FROM_MD_FORMATTED)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):

        try:
            os.mkdir(TEST_EXEC_PATH)

        except:
            pass

        remove_all_testfiles()
        copy_file(TEST_DATA_PATH + YW7, TEST_EXEC_PATH + YW7)
        copy_file(TEST_DATA_PATH + YW7_MD_FORMATTED,
                  TEST_EXEC_PATH + YW7_MD_FORMATTED)

    def test_normal_yw7(self):
        os.chdir(TEST_EXEC_PATH)

        yw2md.run(TEST_EXEC_PATH + YW7, True)

        self.assertEqual(read_file(TEST_EXEC_PATH + FROM_NORMAL_FORMATTED),
                         read_file(TEST_DATA_PATH + FROM_NORMAL_FORMATTED))

    def test_markdown_yw7(self):
        os.chdir(TEST_EXEC_PATH)

        yw2md.run(TEST_EXEC_PATH + YW7_MD_FORMATTED, True)

        self.assertEqual(read_file(TEST_EXEC_PATH + FROM_MD_FORMATTED),
                         read_file(TEST_DATA_PATH + FROM_NORMAL_FORMATTED))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()