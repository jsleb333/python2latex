from functools import wraps
from py2tex import TexEnvironment, TexCommand


class Node(TexCommand):
    """
    This is a node.
    """
    def __init__(self, label):
        """
        Args:
            label (str): Label of the node.
        """
        self.label = label

    def __repr__(self):
        return self.label

    def some_func(self):
        pass

class Draw:
    pass



class TikzPicture(TexEnvironment):
    def bind(self, *clss):
        binded_clss = tuple(self._bind(cls) for cls in clss)
        return binded_clss[0] if len(binded_clss) == 1 else binded_clss

    def _bind(self, cls_to_bind):
        class BindedCls(cls_to_bind):
            @wraps(cls_to_bind.__new__)
            def __new__(cls, *args, **kwargs):
                isinstance = cls_to_bind.__new__(cls)
                return self.new(isinstance)
        BindedCls.__name__ = 'Binded' + cls_to_bind.__name__
        BindedCls.__qualname__ = 'Binded' + cls_to_bind.__qualname__
        BindedCls.__doc__ = f"\tThis is a {cls_to_bind.__name__} object binded to {repr(self)}. Each time an instance is created, it is appended to the body of {repr(self)}. Everything else is identical.\n\n" + str(cls_to_bind.__doc__)
        return BindedCls



tikzpic = TikzPicture('Pic')
node, draw = tikzpic.bind(Node, Draw)

a = node('hehe')
b = node('haha')
c = tikzpic.new(Node('hihi'))
d = draw()
Node('hoho')
Node('hyhy')

print(tikzpic.body)
