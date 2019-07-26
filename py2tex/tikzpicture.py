import numpy as np
from py2tex import TexCommand, TexEnvironment, build
from py2tex import FloatingFigure, FloatingEnvironmentMixin


class TikzPicture(FloatingEnvironmentMixin, super_class=FloatingFigure):
    def __init__(self, position='h!', as_float_env=True, label='', caption=''):
        super().__init__(as_float_env=as_float_env, position=position, label=label, caption=caption)
        self.add_package('tikz')
        self.tikzpicture = TexEnvironment('tikzpicture')
        self.add_text(self.tikzpicture)

    def build(self):
        return super().build()


class Node(TexCommand):
    """
    This is a tikz node.
    """
    n_instances = 0
    def __init__(self, label, *options, node_name=None, position=(0,0), **kwoptions):
        """
        Args:
            label (str): Tex string that appears in the node.
            node_name (str): Name of the node to be refered inside the Tex document.
            options: Options of the node.
            position (tuple of numbers or Position object or other Node or Coordinate): Position of the node inside the picture.
            kwoptions: Keyword options of the node. Underscores will be replaced by spaces.
        """
        super().__init__('node', options=options, **kwoptions)
        type(self).n_instances += 1
        self.name = node_name or f'node{self.n_instances}'
        self.label = label
        self.position = Position(*position)

    def build(self):
        command = super().build()

        command += f'({self.name})'
        command += f' at {self.position} '
        command += f'{{{self.label}}};'

        return command


class Coordinate(TexCommand):
    """
    This is a TikZ coordinate.
    """
    n_instances = 0
    def __init__(self, coor_name=None, *options, position=(0,0), **kwoptions):
        """
        Args:
            coor_name (str): Name of the coordinate to be refered inside the Tex document.
            options: Options of the coordinate.
            position (tuple of numbers or Position object or other Node or Coordinate): Position of the coordinate inside the picture.
            kwoptions: Keyword options of the coordinate. Underscores will be replaced by spaces.
        """
        super().__init__('coordinate', options=options, **kwoptions)
        type(self).n_instances += 1
        self.name = coor_name or f'coor{self.n_instances}'
        self.position = Position(*position)

    def build(self):
        command = super().build()

        command += f'({self.name})'
        command += f' at {self.position};'

        return command


class Position:
    """
    Encapsulates a position.
    """
    def __init__(self, *pos):
        """
        Args:
            pos (tuple of float): Position of a TikZ object.
        """
        self.pos = pos

    def __str__(self):
        return self.build()

    @staticmethod
    def _add_pos(pos1, pos2):
        return (pos1[0] + pos2[0], pos1[1] + pos2[1])

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(*self._add_pos(self.pos, other.pos))
        else:
            return NotImplemented
    def __iadd__(self, other):
        if isinstance(other, Position):
            self.pos = self._add_pos(self.pos, other.pos)
            return self
        else:
            return NotImplemented

    def __sub__(self, other):
        return self + -1*other
    def __isub__(self, other):
        self += -1*other
        return self

    @staticmethod
    def _mul_pos(pos, num):
        return (pos[0]*num, pos[1]*num)

    def __mul__(self, num):
        if isinstance(num, (int, float)):
            return Position(*self._mul_pos(self.pos, num))
        else:
            return NotImplemented
    def __imul__(self, num):
        if isinstance(num, (int, float)):
            self.pos = self._mul_pos(self.pos, num)
            return self
        else:
            return NotImplemented
    def __rmul__(self, num):
        return self * num

    def __truediv__(self, num):
        return self * (1/num)
    def __itruediv__(self, num):
        self *= 1/num
        return self

    def build(self):
        return str(self.pos)
