[Project homepage](index.md)

## Changelog

### v1.3.2 Add Tk GUI capability

The included UiTk class opens an easy way to create custom variants with graphical user interface.
A simple example is included with my_yw2md.pyw. 

Based on PyWriter v2.16.1


### v1.2.0 New command line options

* In exported md documents, the scene title is prefixed as a comment (can be turned off with `--notitles`).
* In generated yWriter projects, comments at scene start are converted to scene titles (can be turned off with `--notitles`).
* Convert Markdown to yw Markup when writing scenes to yWriter (can be turned off with `--md`).
* Convert double linefeeds to single ones when reading scenes from yWriter (can be turned on with `--md`).

Based on PyWriter v2.16.0


### v1.0.0 Final release

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

* Change the Markdown linefeeds.
* Add a customization template


### v0.2.0
* First public release based on PyWriter v2.14.3.

