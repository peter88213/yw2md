[Project homepage](https://peter88213.github.io/yw2md)

---

The yw2md Python script converts yWriter 7 projects to Markdown 
and creates new yWriter 7 projects from Markdown formatted text documents.

There are two variants, which are distinguished by the file extension: 
*yw2md.pyw* has a graphical user interface, and *yw2md.py* is for the command line. 



## Usage

### Intended usage

The included installation script prompts you to create a shortcut on the desktop. 

- You can launch the program by double-clicking on the shortcut icon. Then the program loads the
  last opened file on start, if any, or shows a file picker dialog.   
- You can launch the program by dragging a yWriter project file and dropping it on the shortcut icon. 
- You can launch the program on the command line passing the yWriter project file as an argument.
- You can launch the program via a batch file.

### Options

#### Comments at the beginning of the scene are scene titles

*When checked:*

- When converting from yw7 to md, prefix scene titles as comments.
- When converting from md to yw, convert comments at scene start to scene titles.


*When unchecked:*

- When converting from yw7 to md, do not prefix scene titles as comments.
- When converting from md to yw, do not convert comments at scene start to scene titles.


#### The scenes in the yWriter project are Markdown formatted

*When checked:*

- When converting scenes from yw7 to md, do not double the linefeeds.
- When converting scenes from md to yw, use Markdown.


*When unchecked:* 

- When converting scenes from yw7 to md, double the linefeeds.
- When converting scenes from md to yw, use yWriter's genuine bold/italic markup.


### Select file

If no file is selected, you first have to select a file. Click on the **Select file** 
button and choose a yWriter or Markdown file with the file picker dialog.

You can change the selection at any time.


#### Convert

Start file conversion by clicking on the **Convert** button. The result will be indicated.



# Markdown reference

By default, *yw2md* converts a Markdown subset according to the following specificatiions:

### Paragraphs

Paragraphs in Markdown are separated by a blank line.
Single blank lines in yWriter scenes are Markdown-encoded by three blank lines.

### Headings

#### Level 1 heading used for parts (chapters marked as beginning of a new section in yWriter)
`# One hash character at the start of the line`

#### Level 2 heading used for chapters
`## Two hash characters at the start of the line`

### Emphasis

#### Italic 
`*single asterisks*`

**Note** : A `*` surrounded with spaces will be treated as a literal asterisk.

#### Bold 
`**double asterisks**`

### Comments

- Comments at the start of a scene are condsidered scene titles by default.
- All other comments are converted between Markdown comments and yWriter comments.

`<!---A HTML comment with one additional hyphen--->`

