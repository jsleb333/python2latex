import pytest
from inspect import cleandoc

from py2tex.tex_base import TexObject, TexEnvironment


class TestTexObject:
    def setup(self):
        self.tex_obj = TexObject('DefaultTexObject')

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


class TestTexEnvironment:
    def test_add_text(self):
        env = TexEnvironment('test')
        env.add_text(r"This is raw \LaTeX")
        assert env.body == [r"This is raw \LaTeX"]

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
            \begin{test}{param1, param2}
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
            \begin{test}[spam, egg, answer=42]{param1, param2}
            \end{test}
            ''')

