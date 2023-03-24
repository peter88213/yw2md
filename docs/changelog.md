[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### v2.2.13

- Library update.

Based on PyWriter v12.1.4

### v2.2.12

- Make it run with old Windows versions.

Based on PyWriter v8.0.11

### v2.2.11

- Modify "shebang" line to make the script run with Python 3.11 under Windows.

Based on PyWriter v8.0.11

### v2.2.10

- Fix a regression from v2.2.9 where file errors are not handled correctly.

Based on PyWriter v8.0.9

### v2.2.9

- Update the PyWriter library for future Python versions.
- Count words like in LibreOffice. See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html.

Based on PyWriter v8.0.9

### v2.2.8 Optional release

- Code refactoring and library update.

Based on PyWriter v7.2.1

### v2.2.7 Bugfix release

- Fix problems that may occur with projects created by a yWriter version prior to 7.0.7.2.

Based on PyWriter v6.0.0

### v2.2.6 Update setup script

- Change the working dir to the script dir on startup in order to avoid "file not found" error.

Based on PyWriter v5.18.0

### v2.2.5 Improved setup

- Catch exceptions in the setup script.

Based on PyWriter v5.18.0

### v2.2.4 Improved word counting

- Fix word counting considering ellipses.

Based on PyWriter v5.12.4

### v2.2.3 Improved word counting

- Fix word counting considering comments, hyphens, and dashes.

Based on PyWriter v5.12.3

### v2.2.2 Optional update

When generating chapters from Markdown import, add chapter type as yWriter version 7.0.7.2+

Based on PyWriter v5.10.1

### v2.2.1 Optional update

- Refactor the code.

Based on PyWriter v5.6.0

### v2.2.0

- Add shortcuts:
    - Ctrl-o to open.
    - Ctrl-q to exit.
- Enable menu shortcuts.
- Display document title on the window frame.
- Save and restore window size and position.

Based on PyWriter v5.2.0

### v2.0.1

- Improve code and documentation quality.

Based on PyWriter v5.0.2

### v2.0.0 New user interface

- Fix a bug where "To do" chapters cause an exception.
- Rework the user interface. 
- Write options back to the configuration file.

Based on PyWriter v5.0.0

### v1.6.1 Bugfix release

- Fix misplaced formatting tags before converting them to Markdown.

Based on PyWriter v3.32.1

### v1.6.0 Drop the support of the .yw6 file format.

Since yWriter5, yWriter6 and yWriter7 all use .yw7 now, the .yw6 conversion is dispensable.

Based on PyWriter v3.28.2

### v1.4.5 Installation script

- Add a Python installation script for the GUI variant.
- Make the installed script executable under Linux.

Based on PyWriter v3.28.1

### v1.4.4 Bugfix release

This release is strongly recommended.
Fix a regression from PyWriter v3.12.5. causing a crash if a scene has an 
hour, but no minute set.

Based on PyWriter v3.16.4

### v1.4.3 Optional update

- Refactor the code for better maintainability.

Based on PyWriter v3.16.0

### v1.4.2 Optional update

- Fix docstrings and add version number.

Based on PyWriter v3.12.5

### v1.4.1 Optional update

- Major refactoring of the yw7 file processing.

Based on PyWriter v3.8.0

### v1.4.0 GUI and command line variant

-    Now there are two variants, which are distinguished by the file extension: 
     _yw2md.pyw_  has a graphical user interface, and  _yw2md.py_  is for the command line. 
-    Update the underlying class library with changed API for better maintainability.
-    Remove the custom script from the distribution.

Based on PyWriter v3.0.0

### v1.3.8 New API

- Make my_yw2md.py easier to modify.

Based on PyWriter v2.17.4 (developmen version)


### v1.3.6 Optional update

Refactor

- Modify project structure
- Implement a regex-based solution for scene dividers.

Based on PyWriter v2.17.4 (developmen version)


### v1.3.5 Bugfix

Fix a bug extracting scene titles the wrong way if the first paragraph
contains more than one comment.

Based on PyWriter v2.17.3


### v1.3.3 Make GUI customization easier

The converter is now even more loosely coupled with its user interface. 
This should make it easier for application developers to customize user interaction, 
and use any GUI framework.

Based on PyWriter v2.17.0 (development version)


### v1.3.2 Add Tk GUI capability

The included UiTk class opens an easy way to create custom variants with graphical user interface.
A simple example is included with my_yw2md.pyw. 

Based on PyWriter v2.16.1


### v1.2.0 New command line options

- In exported md documents, the scene title is prefixed as a comment (can be turned off with `--notitles`).
- In generated yWriter projects, comments at scene start are converted to scene titles (can be turned off with `--notitles`).
- Convert Markdown to yw Markup when writing scenes to yWriter (can be turned off with `--md`).
- Convert double linefeeds to single ones when reading scenes from yWriter (can be turned on with `--md`).

Based on PyWriter v2.16.0


### v1.0.0 Official release

Refactor: Move the MdFile class to the PyWriter library.

Based on PyWriter 2.15.0


### v0.6.0 Add options for yWriter project generation

Add "--md" command line argument to use markdown for the scenes when creating a new yWriter project from a Markdown document.

Based on PyWriter 2.14.4


### v0.5.2 Fix md to yw7 conversion

In v0.5.1, each scene's first line was dropped while parsing a Markdown file for conversion to yWriter. Thus, the first paragraph was lost when having converted double linefeeds to single ones.

Based on PyWriter 2.14.4


### v0.5.1 Fix md to yw7 conversion

In v0.5.0, the MdFile.convert_to_yw() method was never called. Now it's working on the source document's text as a whole.


### v0.5.0 Add md to yw7 conversion

Markdown formatted text documents can now be converted into yWriter 7 projects.

Based on PyWriter 2.14.4


### v0.4.0 Rename the script and change the user interface

- Change the script's file extension from `.pyw` to `.py` and implement a command line-only UI.

Based on PyWriter 2.14.4


### v0.2.1 Service release

- Change the Markdown linefeeds.
- Add a customization template


### v0.2.0
- First public release based on PyWriter v2.14.3.

