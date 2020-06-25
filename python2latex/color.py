import sys
from python2latex import TexObject, TexCommand


class DefineColor(TexCommand):
    def __init__(self, color_name, *rgb):
        super().__init__('definecolor', color_name, 'rgb', ','.join([str(c) for c in rgb]))


class Color(TexObject):
    """
    Colors can be defined and then used in conjunction with Plots as options. They will automatically be added to the
    preamble of the document when builded to tex.
    """
    color_count = 0

    def __init__(self, r, g, b, color_name=''):
        """
        Args:
            r, g, b (float): rgb values between 0 and 1.
            color_name (str): Name of the color that will be used in the tex file. If no name is specified, a color
            number will be given automatically.
        """
        super().__init__('color')
        self.rgb = (r, g, b)
        Color.color_count += 1
        self.color_name = color_name or f'color{Color.color_count}'
        self.add_to_preamble(DefineColor(self.color_name, *self.rgb))

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
            text (str): Text to print in bold.
        """
        super().__init__('textcolor', color, text)
        self.add_package('xcolor', 'dvipsnames')


PREDEFINED_COLORS = ['black', 'blue', 'brown', 'cyan', 'darkgray', 'gray', 'green', 'lightgray', 'lime', 'magenta', 'olive', 'orange', 'pink', 'purple', 'red', 'teal', 'violet', 'white', 'yellow', 'Apricot', 'Aquamarine', 'Bittersweet', 'Black', 'Blue', 'BlueGreen', 'BlueViolet', 'BrickRed', 'Brown', 'BurntOrange', 'CadetBlue', 'CarnationPink', 'Cerulean', 'CornflowerBlue', 'Cyan', 'Dandelion', 'DarkOrchid', 'Emerald', 'ForestGreen', 'Fuchsia', 'Goldenrod', 'Gray', 'Green', 'GreenYellow', 'JungleGreen', 'Lavender', 'LimeGreen', 'Magenta', 'Mahogany', 'Maroon', 'Melon', 'MidnightBlue', 'Mulberry', 'NavyBlue', 'OliveGreen', 'Orange', 'OrangeRed', 'Orchid', 'Peach', 'Periwinkle', 'PineGreen', 'Plum', 'ProcessBlue', 'Purple', 'RawSienna', 'Red', 'RedOrange', 'RedViolet', 'Rhodamine', 'RoyalBlue', 'RoyalPurple', 'RubineRed', 'Salmon', 'SeaGreen', 'Sepia', 'SkyBlue', 'SpringGreen', 'Tan', 'TealBlue', 'Thistle', 'Turquoise', 'Violet', 'VioletRed', 'White', 'WildStrawberry', 'Yellow', 'YellowGreen', 'YellowOrange']

def textcolor_callable(color):
    """
    Returns a callable which returns a textcolor from some text. This is useful, for instance, in tables as
    a command to color the text of a cell. Functions for the colors of the xcolor and dvipsnames packages are
    already defined as "textNAMEOFTHECOLOR" where NAMEOFTHECOLOR is the name given their respective packages.

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

import sys
for color in PREDEFINED_COLORS:
    setattr(sys.modules[__name__], 'text' + color, textcolor_callable(color))
