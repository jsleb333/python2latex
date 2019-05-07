import pytest
from pytest import fixture
from inspect import cleandoc

from py2tex.tikzpicture import *


class TestTikzPicture:
    def test_(self):
        pass


class TestNode:
    def setup(self):
        Node.n_instances = 0

    def test_n_instances_incremented_on_instanciation(self):
        n1 = Node('n1')
        assert Node.n_instances == 1
        n2 = Node('n2')
        assert Node.n_instances == 2

    def test_default_node_name(self):
        n = Node('')
        assert n.name == 'node1'
        n = Node('')
        assert n.name == 'node2'

    def test_non_default_node_name(self):
        n = Node('', 'name')
        assert n.name == 'name'

    def test_build_default(self):
        n = Node('label')
        assert n.build() == r'\node(node1) at (0, 0) {label};'

    def test_build_with_options(self):
        n = Node('label', 'node name', 'draw', align='center')
        assert n.build() == r'\node[draw, align=center](node name) at (0, 0) {label};'


class TestPosition:
    def test_position_from_tuple(self):
        pos = Position(3.3,4.4)
        assert pos.build() == '(3.3, 4.4)'

    def test_add_other_position(self):
        pos = Position(1,2) + Position(3,4)
        assert pos.pos == (4,6)

    def test_iadd_other_position(self):
        pos = Position(1,2)
        pos += Position(3,4)
        assert pos.pos == (4,6)
