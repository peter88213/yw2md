[Project homepage](https://peter88213.github.io/yw2md)


The yw2md Python script converts yWriter 6/7 projects to Markdown 
and creates new yWriter 7 projects from Markdown formatted text documents.

The script is meant to be launched from the command line. However, 
if you prefer to use the mouse, you can create a link on the Windows 
desktop, and launch yw2md by dragging the source file and dropping 
it to the link icon. For optional arguments, edit the link's properties.


## Usage
usage: `yw2md.py [-h][--silent][--md] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the source file for the conversion. 

* If it's a yWriter project file with extension 'yw6' or 'yw7', 
a new Markdown formatted text document will be created.
* Otherwise, the source file will be considered a Markdown formatted file 
to be converted to a new yWriter 7 project. 
* Existing yWriter projects are not overwritten.
* Headings are considered chapter titles. 
* Scenes within chapters are separated by `* * *`. 
* In exported md documents, the scene title is prefixed as a comment by default.
* In generated yWriter projects, comments at scene start are converted to scene titles by default.


#### optional arguments:

`-h, --help`  show this help message and exit

`--silent`  suppress error messages and the request to confirm overwriting

`--md`  the scenes in the yWriter project are Markdown formatted

* When converting scenes from yw7 to md, do not double the linefeeds.
* When converting scenes from md to yw, use Markdown.

`--notitles`  do not associate comments at the beginning of the scene with scene titles

* When converting from yw7 to md, do not prefix scene titles as comments.
* When converting from md to yw, do not convert comments at scene start to scene titles.

- - -

## Markdown reference

By default,  _yw2md_  converts a Markdown subset according to the following specificatiions:

### Paragraphs

Paragraphs in Markdown are separated by a blank line.
Single blank lines in yWriter scenes are Markdown-encoded by three blank lines.

### Headings

#### Level 1 heading used for parts (chapters marked as  beginning of a new section in yWriter)
`# One hash character at the start of the line`

#### Level 2 heading used for chapters
`## Two hash characters at the start of the line`

### Emphasis

#### Italic 
`*single asterisks*`

#### Bold 
`**double asterisks**`

### Comments

* Comments at the start of a scene are condsidered scene titles by default.
* All other comments are converted between Markdown comments and yWriter comments.

`<!---A HTML comment with one additional hyphen--->`

