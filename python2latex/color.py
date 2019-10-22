from python2latex import TexObject, TexCommand


class DefineColor(TexCommand):
    def __init__(self, color_name, *rgb):
        super().__init__('definecolor', color_name, 'rgb', ','.join([str(c) for c in rgb]))


class Color(TexObject):
    """
    Colors can be defined and then used in conjunction with Plots as options. They will automatically be added to the preamble of the document when builded to tex.
    """
    color_count = 0
    def __init__(self, r, g, b, color_name=''):
        """
        Args:
            r, b, g (float): rgb values between 0 and 1.
            color_name (str): Name of the color that will be used in the tex file. If no name is specified, a color number will be given automatically.
        """
        super().__init__('color')
        self.rgb = (r, g, b)
        Color.color_count += 1
        self.color_name = color_name or f'color{Color.color_count}'
        self.add_to_preamble(DefineColor(self.color_name, *self.rgb))

    def build(self):
        return self.color_name
