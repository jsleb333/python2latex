# Change log

## Version 0.1.6

### August 6, 2019

- Added Color object.
- Packages now use TexCommand objects to build.
- 'header' variable name changed to 'preamble'.
- The preamble is now part of TexObject instead of Document to allow adding lines from any level.
- 'build' function now takes a 'parent' arguments to correctly and safely collect all packages and preamble lines from all levels.

### July 26, 2019

- Added automatic opening of pdf viewer after build to pdf.

## Version 0.1.5

### March 21, 2019

- Added binding mechanism for TexObject to instances of TexEnvironment to alleviate syntax.
- Changed many internal Tex generation to use TexCommand instead.
- TexObject no longer have a 'body' attribute.
