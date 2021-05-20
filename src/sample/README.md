# Sample scripts

## Customize the Markdown export

If you know the  _Python_  programming language, you easily 
can make your own converter. The zipfile includes a template for 
modification. The script  *my_yw2md.py* uses the original script 
as a library and defines easy-to-adapt subclasses for Markdown conversion. 

All you need is the two Python files coming with the distributed package. 
All the rest one can see on GitHub is for IDE configuration, documentation, 
library administration, building, testing, versioning, packaging etc., 
and I recommend you to ignore it for the first time, because all that comes 
with a bunch of dependencies that might be quite time-consuming to resolve. 

## A sample Markdown converter application 

The  *cnv_md.py*  script shows the simplest way to create a Markdown converter 
script using the  _pywmd_  and  _pywriter_  libraries.
