from py2tex import TexEnvironment


class Node:
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return self.label

class Draw:
    pass


class TikzPicture(TexEnvironment):
    def bind(self, *clss):
        binded_cls = []
        for cls in clss:
            new_cls = type(f'Binded{cls.__name__}To{self.name}', (cls,), {})
            def new_cls__new__(_cls, *a, **k):
                instance = cls.__new__(_cls)
                return self.new(instance)
            new_cls.__new__ = new_cls__new__
            binded_cls.append(new_cls)
        return binded_cls[0] if len(binded_cls) == 1 else tuple(binded_cls)


tikzpic = TikzPicture('Pic')
node, draw = tikzpic.bind(Node, Draw)

a = node('hehe')
b = node('haha')
c = tikzpic.new(Node('hihi'))

print(tikzpic.body)

print(type(a))
