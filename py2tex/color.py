from py2tex import TexObject, TexCommand


class Color(TexObject):
    """
    """
    color_count = 0
    def __init__(self, *rgb, color_name=''):
        self.rgb = rgb
        self.color_count += 1
        if color_name:
            self.color_name = color_name
        else:
            self.color_name = f'color{self.color_count}'
        super().__init__()

    def build(self):
        define_color = TexCommand('definecolor', self.color_name, 'rgb', *self.rgb)


        return super().build()
