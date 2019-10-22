import pytest
from pytest import fixture
from inspect import cleandoc

from python2latex.floating_environment import *
from python2latex.floating_environment import _FloatingEnvironment

def test_Caption():
    assert Caption('some caption').build() == r'\caption{some caption}'


class Test_FloatingEnvironment:
    def test_floating_environment_default(self):
        env = _FloatingEnvironment('default')
        assert env.build() == cleandoc(
            r'''
            \begin{default}[h!]
            \centering
            \end{default}
            ''')

    def test_floating_environment_with_options(self):
        env = _FloatingEnvironment('with_options', position='t', centered=False)
        assert env.build() == cleandoc(
            r'''
            \begin{with_options}[t]
            \end{with_options}
            ''')

    def test_floating_environment_with_caption(self):
        env = _FloatingEnvironment('with_caption', label='float_env')
        env.caption = 'float caption'
        assert env.build() == cleandoc(
            r'''
            \begin{with_caption}[h!]
            \centering
            \caption{float caption}
            \label{with_caption:float_env}
            \end{with_caption}
            ''')


def test_floating_figure_label_bottom():
    fig = FloatingFigure(label='test_fig')
    fig.add_text('some text')
    assert fig.build() == cleandoc(
        r'''
        \begin{figure}[h!]
        \centering
        some text
        \label{figure:test_fig}
        \end{figure}
        ''')

def test_floating_table_label_top():
    fig = FloatingTable(label='test_table')
    fig.add_text('some text')
    assert fig.build() == cleandoc(
        r'''
        \begin{table}[h!]
        \centering
        \label{table:test_table}
        some text
        \end{table}
        ''')

@fixture
def mixed_float_fig():
    class MixedFloatEnv(FloatingEnvironmentMixin, super_class=FloatingFigure):
        pass
    return MixedFloatEnv

def test_floating_environment_mixin(mixed_float_fig):
    assert mixed_float_fig.__bases__ == (FloatingEnvironmentMixin, FloatingFigure)

def test_floating_environment_mixin_as_float(mixed_float_fig):
    assert mixed_float_fig(as_float_env=True).build() == FloatingFigure().build()

def test_floating_environment_mixin_not_as_float(mixed_float_fig):
    assert mixed_float_fig(as_float_env=False).build() == ''
