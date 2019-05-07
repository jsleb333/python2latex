import numpy as np
from py2tex import TexCommand, TexEnvironment, build
from py2tex import FloatingFigure, FloatingEnvironmentMixin


class TikzPicture(TexEnvironment):
    def __init__(self):
        super().__init__(as_float_env=as_float_env, position=position, label=label, caption=caption)

    def build(self):
        return super().build()


class Node(TexCommand):
    """
    This is a tikz node.
    """
    n_instances = 0
    def __init__(self, label, node_name=None, *options, position=(0,0), **kwoptions):
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
        self.position = position

    def build(self):
        command = super().build()

        command += f'({self.name})'
        command += f' at {self.position} '
        command += f'{{{self.label}}};'

        return command


class Position:
    """
    Encapsulates a position
    """
    def __init__(self, *pos):
        """
        Args:
            pos (tuple of float): Position
        """
        self.pos = pos

    def build(self):
        return str(self.pos)
