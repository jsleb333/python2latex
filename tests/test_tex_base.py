import pytest
from inspect import cleandoc

from py2tex.tex_base import *


class TestTexObject:
    def setup(self):
        self.tex_obj = TexObject('DefaultTexObject')

    def test_add_text(self):
        tex_obj = TexObject('test')
        tex_obj.add_text(r"This is raw \LaTeX")
        assert tex_obj.body == [r"This is raw \LaTeX"]

    def test_append(self):
        tex_obj = TexObject('test')
        tex_obj.append(r"This is raw \LaTeX")
        assert tex_obj.body == [r"This is raw \LaTeX"]

    def test_iadd(self):
        tex_obj = TexObject('test')
        tex_obj += r"This is raw \LaTeX"
        assert tex_obj.body == [r"This is raw \LaTeX"]

    def test_add_package_without_options(self):
        package_name = 'package'
        self.tex_obj.add_package(package_name)
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name] == {}

    def test_add_package_with_options(self):
        package_name = 'package'
        options = ('spam', 'egg')
        self.tex_obj.add_package(package_name, 'spam', 'egg', answer=42, question="We don't know")
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name] == {'spam':'', 'egg':'', 'answer':42, 'question':"We don't know"}

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


class TestTexEnvironment:

    def test_new(self):
        env = TexEnvironment('test')
        other_env = TexEnvironment('other')
        returned_object = env.new(other_env)
        assert returned_object is other_env
        assert env.body[0] is other_env

    def test_build_default(self):
        assert TexEnvironment('test').build() == '\\begin{test}\n\\end{test}'

    def test_build_with_label(self):
        env = TexEnvironment('test', label='some_label')
        env.add_text('some text')

        assert env.build() == cleandoc(
            r'''
            \begin{test}
            \label{test:some_label}
            some text
            \end{test}
            ''')
        env.label_pos = 'bottom'
        assert env.build() == cleandoc(
            r'''
            \begin{test}
            some text
            \label{test:some_label}
            \end{test}
            ''')

    def test_build_with_parameters(self):
        assert TexEnvironment('test', 'param1', 'param2').build() == cleandoc(
            r'''
            \begin{test}{param1}{param2}
            \end{test}
            ''')

    def test_build_with_options(self):
        assert TexEnvironment('test', options='option1').build() == cleandoc(
            r'''
            \begin{test}[option1]
            \end{test}
            ''')
        assert TexEnvironment('test', options=('option1', 'option2')).build() == cleandoc(
            r'''
            \begin{test}[option1, option2]
            \end{test}
            ''')
        assert TexEnvironment('test', options=('spam', 'egg'), answer=42).build() == cleandoc(
            r'''
            \begin{test}[spam, egg, answer=42]
            \end{test}
            ''')

    def test_build_with_parameters_and_options(self):
        assert TexEnvironment('test', 'param1', 'param2', options=('spam', 'egg'), answer=42).build() == cleandoc(
            r'''
            \begin{test}[spam, egg, answer=42]{param1}{param2}
            \end{test}
            ''')

