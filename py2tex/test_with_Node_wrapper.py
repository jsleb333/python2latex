from py2tex import TexEnvironment


class Node:
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return self.label

    @classmethod
    def link(cls, env):
        class LinkedCls(cls):
            def __new__(cls, *a, **k):
                node = super().__new__(cls)
                return env.new(node)
        return LinkedCls

class TikzPicture(TexEnvironment):
    pass


node = Node.link(TikzPicture(''))

a = node('hehe')
b = node('haha')
c = tikzpic.new(Node('hihi'))
