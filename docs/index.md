The yw2md Python script converts yWriter 6/7 projects to Markdown 
and creates new yWriter 7 projects from Markdown formatted text documents.

## Requirements

* [Python 3](https://www.python.org). Python 3.4 or more recent will work. However, Python 3.7 or above is highly recommended.

## Download and install

[Download the latest release (version 1.3.6)](https://raw.githubusercontent.com/peter88213/yw2md/master/dist/yw2md_v1.3.6.zip)

* Unzip the downloaded zipfile "yw2md_v1.3.6.zip" into a new folder and open "README.md" for usage instructions.

[Changelog](changelog)

## Usage, Markdown reference

See the [instructions for use](usage)

## Customize the Markdown export

If you know the  _Python_  programming language, you easily 
can make your own converter. The zipfile includes a template for 
modification. The script  *my_yw2md.pyw* uses the original script 
as a library and defines easy-to-adapt subclasses for Markdown conversion. 

All you need is the two Python files coming with the distributed package. 
All the rest one can see on GitHub is for IDE configuration, documentation, 
library administration, building, testing, versioning, packaging etc., 
and I recommend you to ignore it for the first time, because all that comes 
with a bunch of dependencies that might be quite time-consuming to resolve. 

## License

yw2md is distributed under the [MIT
License](http://www.opensource.org/licenses/mit-license.php).
