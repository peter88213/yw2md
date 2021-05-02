[Project homepage](https://peter88213.github.io/yw2md)


The yw2md Python script converts yWriter 6/7 projects to Markdown 
and creates new yWriter 7 projects from Markdown formatted text documents.

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


#### optional arguments:

`-h, --help`  show this help message and exit

`--silent`  suppress error messages and the request to confirm overwriting

`--md`  when creating a yWriter project, use Markdown for the scenes

`--notitles`  scene titles are not prefixed as comments
