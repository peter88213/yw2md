# yw2md - Markdown converter for yWriter projects

For more information, see the [project homepage](https://peter88213.github.io/yw2md) with description and download instructions.

## Development

*yw2md* is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Conventions

See https://github.com/peter88213/PyWriter/blob/main/docs/conventions.md

Exceptions:
- No localization is required.
- The directory structure is modified to minimize dependencies:

```
.
└── yw2md/
    ├── src/
    ├── test/
    └── tools/ 
        └── build.xml
```

### Development tools

- [Python](https://python.org) version 3.10
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and [EGit](https://www.eclipse.org/egit/)
- Apache Ant for building the application script

## Credits

- Frederik Lundh published the [xml pretty print algorithm](http://effbot.org/zone/element-lib.htm#prettyprint).

## License

yw2md is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).

