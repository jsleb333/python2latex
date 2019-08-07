from py2tex import TexObject, TexCommand


class DefineColor(TexCommand):
    def __init__(self, color_name, *rgb):
        super().__init__('definecolor', color_name, 'rgb', ','.join([str(c) for c in rgb]))


class Color(TexObject):
    """
    """
    color_count = 0
    def __init__(self, r, g, b, color_name=''):
        super().__init__('color')
        self.rgb = (r, g, b)
        Color.color_count += 1
        self.color_name = color_name or f'color{Color.color_count}'
        self.add_to_preamble(DefineColor(self.color_name, *self.rgb))

    def build(self):
        return self.color_name
