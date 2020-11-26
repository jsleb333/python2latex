import sys
from python2latex import TexObject, TexCommand


class DefineColor(TexCommand):
    def __init__(self, color_name, color_model, *color_spec):
        super().__init__('definecolor', color_name, color_model, ','.join(map(str, color_spec)))


class Color(TexObject):
    """
    Colors can be defined and then used in conjunction with Plots as options. They will automatically be added to the preamble of the document when built to tex.
    """
    color_count = 0

    def __init__(self, *color_spec, color_name='', color_model='rgb'):
        """
        Args:
            color_spec (Tuple[Union[float, int]]): The color specification arguments, dependent on the color model. The default color model is rgb, so color_spec should consist in a tuple of 3 floats between 0 and 1. See the note below or the documentation of LaTeX's 'xcolor' package for more info.
            color_name (str): Name of the color that will be used in the tex file. If no name is specified, a color number will be given automatically.
            color_model (str): Model used to represent the color. See the note below or the documentation of LaTeX's 'xcolor' package for more info.

        Note: The available color models and their range of specifications are:
            rgb:    red, green, blue                [0, 1]³
            cmy:    cyan, magenta, yellow           [0, 1]³
            cmyk:   cyan, magenta, yellow, black    [0, 1]⁴
            hsb:    hue, saturation, brightness     [0, 1]³
            Hsb:    hue◦, saturation, brightness    [0, 360] x [0, 1]²
            tHsb:   hue◦, saturation, brightness    [0, 360] x [0, 1]²
            gray:   gray                            [0, 1]
            RGB:    Red, Green, Blue                {0, 1, ..., 255}³
            HTML:   RRGGBB                          {000000, ..., FFFFFF}
            HSB:    Hue, Saturation, Brightness     {0, 1, ..., 240}³
            Gray:   Gray                            {0, 1, ..., 15}
            wave:   lambda (nm)                     [363, 814]
        """
        super().__init__('color')
        self.color_spec = color_spec
        self.color_model = color_model
        Color.color_count += 1
        self.color_name = color_name or f'color{Color.color_count}'
        self.add_to_preamble(DefineColor(self.color_name, self.color_model, *self.color_spec))
        self.add_package('xcolor')

    def build(self):
        return self.color_name


class textcolor(TexCommand):
    """
    Applies \\textcolor{color}{...} command on text.
    """
    def __init__(self, color, text):
        """
        Args:
            color (Union[str,Color]): Name of the color or instance of Color.
            text (str): Text to print in color.
        """
        super().__init__('textcolor', color, text)
        self.add_package('xcolor', 'dvipsnames')


class colorbox(TexCommand):
    """
    Applies \colorbox{color}{...} command on text.
    """
    def __init__(self, color, text):
        """
        Args:
            color (Union[str,Color]): Name of the color or instance of Color.
            text (str): Text to print in colorbox.
        """
        super().__init__('colorbox', color, text)
        self.add_package('xcolor', 'dvipsnames')


PREDEFINED_COLORS = ['black', 'blue', 'brown', 'cyan', 'darkgray', 'gray', 'green', 'lightgray', 'lime', 'magenta', 'olive', 'orange', 'pink', 'purple', 'red', 'teal', 'violet', 'white', 'yellow', 'Apricot', 'Aquamarine', 'Bittersweet', 'Black', 'Blue', 'BlueGreen', 'BlueViolet', 'BrickRed', 'Brown', 'BurntOrange', 'CadetBlue', 'CarnationPink', 'Cerulean', 'CornflowerBlue', 'Cyan', 'Dandelion', 'DarkOrchid', 'Emerald', 'ForestGreen', 'Fuchsia', 'Goldenrod', 'Gray', 'Green', 'GreenYellow', 'JungleGreen', 'Lavender', 'LimeGreen', 'Magenta', 'Mahogany', 'Maroon', 'Melon', 'MidnightBlue', 'Mulberry', 'NavyBlue', 'OliveGreen', 'Orange', 'OrangeRed', 'Orchid', 'Peach', 'Periwinkle', 'PineGreen', 'Plum', 'ProcessBlue', 'Purple', 'RawSienna', 'Red', 'RedOrange', 'RedViolet', 'Rhodamine', 'RoyalBlue', 'RoyalPurple', 'RubineRed', 'Salmon', 'SeaGreen', 'Sepia', 'SkyBlue', 'SpringGreen', 'Tan', 'TealBlue', 'Thistle', 'Turquoise', 'Violet', 'VioletRed', 'White', 'WildStrawberry', 'Yellow', 'YellowGreen', 'YellowOrange']


def textcolor_callable(color):
    """
    Returns a callable which returns a textcolor from some text. This is useful, for instance, in tables as
    a command to color the text of a cell. Functions for the colors of the xcolor and dvipsnames packages are
    already defined as "textNAMEOFTHECOLOR" where NAMEOFTHECOLOR is the name given by their respective packages.

    Example:
        The following code define a text with the defined color:

            from python2latex import textcolor_callable, Color
            my_color_callable = textcolor_callable(Color(1, 0, 0, color_name='my_color'))
            colored_text = my_color_callable('hello')

        The following code define a text with a predefined color:

            from python2latex import textred
            colored_text = textred('hello')

    """
    def color_func(text):
        return textcolor(color, text)
    return color_func


def colorbox_callable(color):
    """
    Returns a callable which returns a colorbox from some text. This is useful, for instance, in tables as
    a command to highlight the text of a cell. Functions for the colors of the xcolor and dvipsnames packages are
    already defined as "colorboxNAMEOFTHECOLOR" where NAMEOFTHECOLOR is the name given by their respective packages.

    Example:
        The following code define a text highlighted by the defined color:

            from python2latex import colorbox_callable, Color
            my_colorbox_callable = colorbox_callable(Color(1, 0, 0, color_name='my_color'))
            highlighted_text = my_colorbox_callable('hello')

        The following code define a text highlighted by a predefined color:

            from python2latex import colorboxred
            highlighted_text = colorboxred('hello')

    """
    def color_func(text):
        return colorbox(color, text)
    return color_func


for color in PREDEFINED_COLORS:
    setattr(sys.modules[__name__], 'text' + color, textcolor_callable(color))
    setattr(sys.modules[__name__], 'colorbox' + color, colorbox_callable(color))
