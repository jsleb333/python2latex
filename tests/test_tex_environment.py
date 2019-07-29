import pytest
from inspect import cleandoc

from py2tex.tex_environment import *
from py2tex.tex_base import *


class TestTexEnvironment:
    def test_add_text(self):
        env = TexEnvironment('test')
        env.add_text(r"This is raw \LaTeX")
        assert env.body == [r"This is raw \LaTeX"]

    def test_append(self):
        env = TexEnvironment('test')
        env.append(r"This is raw \LaTeX")
        assert env.body == [r"This is raw \LaTeX"]

    def test_iadd(self):
        env = TexEnvironment('test')
        env += r"This is raw \LaTeX"
        assert env.body == [r"This is raw \LaTeX"]

    def test_new(self):
        env = TexEnvironment('test')
        other_env = TexEnvironment('other')
        returned_object = env.new(other_env)
        assert returned_object is other_env
        assert env.body[0] is other_env

    def test_contains(self):
        env = TexEnvironment('test')
        assert 'spam' not in env
        new_obj = TexObject('New Object')
        env.append(new_obj)
        assert new_obj in env

    def test__bind(self):
        env = TexEnvironment('test')
        BindedObject = env.bind(TexObject)
        assert BindedObject.__name__ == 'BindedTexObject'
        assert BindedObject.__qualname__ == 'BindedTexObject'
        assert BindedObject.__doc__ != TexObject.__doc__
        assert issubclass(BindedObject, TexObject)

    def test_bind_one_object(self):
        env = TexEnvironment('test')
        BindedObject = env.bind(TexObject)
        other = BindedObject('OtherObject')
        assert other in env

    def test_bind_two_objects(self):
        env = TexEnvironment('test')
        class SubTexObj(TexObject): pass
        BindedObject, BindedSubObject = env.bind(TexObject, SubTexObj)
        other = BindedObject('OtherObject')
        subother = BindedSubObject('OtherSubObject')
        assert other in env
        assert subother in env

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

    def test_build_with_recursive_env(self):
        level1 = TexEnvironment('level1')
        level1.add_text('level1')
        level2 = level1.new(TexEnvironment('level2'))
        level2.add_text('level2')
        assert level1.build() == cleandoc(
            r'''
            \begin{level1}
            level1
            \begin{level2}
            level2
            \end{level2}
            \end{level1}
            ''')
