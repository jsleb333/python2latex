import pytest
from inspect import cleandoc

from py2tex.tex_base import *


class TestTexObject:
    def setup(self):
        self.tex_obj = TexObject('DefaultTexObject')

    def test_add_package_without_options(self):
        package_name = 'package'
        self.tex_obj.add_package(package_name)
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name].options == []
        assert self.tex_obj.packages[package_name].kwoptions == {}

    def test_add_package_with_options(self):
        package_name = 'package'
        options = ('spam', 'egg')
        self.tex_obj.add_package(package_name, 'spam', 'egg', answer=42, question="We don't know")
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name].options == ['spam', 'egg']
        assert self.tex_obj.packages[package_name].kwoptions == {'answer':42, 'question':"We don't know"}

    def test_repr(self):
        assert repr(self.tex_obj) == 'TexObject DefaultTexObject'

    def test_build_empty(self):
        assert self.tex_obj.build() == ''


class TestTexCommand:
    def test_command_default(self):
        assert TexCommand('hskip').build() == r'\hskip'

    def test_command_with_parameters(self):
        assert TexCommand('usepackage', 'geometry').build() == r'\usepackage{geometry}'
        assert TexCommand('begin', 'tabular', 'ccc').build() == r'\begin{tabular}{ccc}'

    def test_command_with_parameters_and_options_order_first(self):
        assert TexCommand('command', 'param1', 'param2', options=('spam', 'egg'), top='2cm', bottom='3cm', options_pos='first').build() == r'\command[spam, egg, top=2cm, bottom=3cm]{param1}{param2}'

    def test_command_with_parameters_and_options_order_second(self):
        assert TexCommand('command', 'param1', 'param2', options=('spam', 'egg'), top='2cm', bottom='3cm', options_pos='second').build() == r'\command{param1}[spam, egg, top=2cm, bottom=3cm]{param2}'

    def test_command_with_parameters_and_options_order_last(self):
        assert TexCommand('command', 'param1', 'param2', options=('spam', 'egg'), top='2cm', bottom='3cm', options_pos='last').build() == r'\command{param1}{param2}[spam, egg, top=2cm, bottom=3cm]'

    def test_str(self):
        assert f"{TexCommand('test')}" == r'\test'

def test_bold():
    assert bold('test').build() == r'\textbf{test}'

def test_italic():
    assert italic('test').build() == r'\textit{test}'
