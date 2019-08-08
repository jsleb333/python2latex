import pytest
from inspect import cleandoc
import os

from py2tex.color import *
from py2tex import build, Document, TexCommand


class TestColor:
    def teardown_method(self, mtd):
        Color.color_count = 0

    def test_init(self):
        color = Color(3,4,5, color_name='spam')
        assert color.build() == 'spam'
        assert color.build_preamble() == '\n\\definecolor{spam}{rgb}{3,4,5}'

    def test_without_color_name(self):
        color = Color(3,4,5)
        assert color.build() == 'color1'
        color2 = Color(3,4,6)
        assert color2.build() == 'color2'

    def test_preamble_appears_in_document(self):
        doc = Document('test')
        color = Color(1,2,3)
        command = TexCommand('somecommand', 'param', options=[color])
        doc += command
        assert doc.build(False, False, False) == cleandoc(
            r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \definecolor{color1}{rgb}{1,2,3}
            \begin{document}
            \somecommand{param}[color1]
            \end{document}'''
            )
