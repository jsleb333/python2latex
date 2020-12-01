# Change log

## Version 0.4.0

### Decembre 1, 2020
- Add color maps and palettes (dynamic and static), with examples, tests, and predefined cmaps.
- Plot now supports palette as objects or iterable. Defaults to the 'holi' palette.

### November 19, 2020
- Color now supports all models from the xcolor package (i.e. rgb, HTML, hsb, etc.)
- Factored the Axis environement into a standalone class in prevision of adding subplots.
- Can now add a label to line plots as an alternative to the legend.

### July 2, 2020
- Add support for TeX command 'colorbox'.

### June 25, 2020
- Add support for TeX command 'textcolor'.

### June 21, 2020
- Tables now support every kind of int and float by using the Integral and Real types.
- Bad indexing in Tables raises an exception.

### June 16, 2020
- Breaking changes:
    - SelectedArea 'change_format' method removed for a 'format_spec' property and a 'apply_command' method.
    - SelectedArea 'highlight' method removed, as it overlapped the 'apply_command' method purpose.
- Complete rework of Table:
    - New Tabular object handling the mechanics of the table.
    - Table is now a "shell" for a Tabular object, with main purpose to have a floating 'table' environment without boilerplate.
    - Build phase is simplified and more clear. Steps are: Number formatting, individual cell building and then command applications.
- Added 'decimal_separator' parameter to allow comma for other languages typesetting such as French.
- Added 'mean_with_std_table_example.py' with applications for machine learning practitioners.
- Complete test coverage for features of Table.

## Version 0.3.0

### May 1, 2020
- Add individual cell formating in tables
- Add simpler example of tables

### March 26, 2020
- Add caption, caption_pos and caption_space as arguments to _FloatingEnvironment and its children to allow manual space between caption and the content.
- Change the behavior of build to ignore empty strings.

### November 26, 2019
- New Template class to insert tex in already existing file.

## Version 0.2.1

### November 23, 2019
- Added option to star an environment.

## Version 0.2.0

### March 24, 2020
- Add forget_plot argument to add_plot method of Plot class to fix incompatibilities with histogram.

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
