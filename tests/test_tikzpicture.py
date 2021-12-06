import pytest
from pytest import fixture
from inspect import cleandoc

from python2latex.tikzpicture import *


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

    def test_default_name(self):
        n = Node('')
        assert n.name == 'node1'
        n = Node('')
        assert n.name == 'node2'

    def test_non_default_name(self):
        n = Node('', name='name')
        assert n.name == 'name'

    def test_build_default(self):
        n = Node('label')
        assert n.build() == r'\node(node1) {label};'

    def test_build_with_options(self):
        n = Node('label', options=['draw'], position=(1,0), name='node name', align='center')
        assert n.build() == r'\node[draw, align=center](node name) at (1, 0) {label};'

    def test_node_anchors(self):
        n = Node(name='name')
        assert build(n.north) == 'name.north'
        assert build(n.south_west) == 'name.south west'


class TestCoordinate:
    def setup(self):
        Coordinate.n_instances = 0

    def test_n_instances_incremented_on_instanciation(self):
        n1 = Coordinate('n1')
        assert Coordinate.n_instances == 1
        n2 = Coordinate('n2')
        assert Coordinate.n_instances == 2

    def test_default_coor_name(self):
        n = Coordinate('')
        assert n.name == 'coor1'
        n = Coordinate('')
        assert n.name == 'coor2'

    def test_non_default_coor_name(self):
        n = Coordinate('name')
        assert n.name == 'name'

    def test_build_default(self):
        n = Coordinate(position=(1,2))
        assert n.build() == r'\coordinate(coor1) at (1, 2);'

    def test_build_with_options(self):
        n = Coordinate('coor name', 'draw', align='center')
        assert n.build() == r'\coordinate[draw, align=center](coor name) at (0, 0);'


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

    def test_sub_other_position(self):
        pos = Position(1,2) - Position(3,4)
        assert pos.pos == (-2,-2)

    def test_isub_other_position(self):
        pos = Position(1,2)
        pos -= Position(3,4)
        assert pos.pos == (-2,-2)

    def test_mul_by_number(self):
        pos = Position(1,2) * 3
        assert pos.pos == (3,6)
        pos = 3 * Position(1,2)
        assert pos.pos == (3,6)

    def test_imul_by_number(self):
        pos = Position(1,2)
        pos *= 3
        assert pos.pos == (3,6)

    def test_div_by_number(self):
        pos = Position(3,6) / 3
        assert pos.pos == (1,2)

    def test_idiv_by_number(self):
        pos = Position(3,6)
        pos /= 3
        assert pos.pos == (1,2)
