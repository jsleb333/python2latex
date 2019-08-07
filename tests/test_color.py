import pytest
from inspect import cleandoc

from py2tex.color import *
from py2tex.tex_base import *


class TestColor:
    def teardown_method(self, mtd):
        Color.color_count = 0

    def test_init(self):
        color = Color(3,4,5, color_name='spam')
        assert color.build() == 'spam'
        assert color.build_preamble() == '\\definecolor{spam}{rgb}{3,4,5}\n'

    def test_without_color_name(self):
        color = Color(3,4,5)
        assert color.build() == 'color1'
        color2 = Color(3,4,6)
        assert color2.build() == 'color2'
