# Change log

## Version 0.2.1

### November 23, 2019
- Added option to star an environment.

## Version 0.2.0

### November 19, 2019
- Reworked Plot so that lines are objects and are built in the order that have been added to the axis.
- Added a MatrixPlot object to make heatmaps.
- Multiple bug fixes in Plot.

### November 18, 2019
- Fixed bug with relative path when building Plot objects.

## Version 0.1.6

### October 21, 2019
- Added documentations throughout the code.
- First release.

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
