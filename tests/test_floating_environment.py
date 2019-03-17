import pytest
from inspect import cleandoc

from py2tex.floating_environment import _FloatingEnvironment, FloatingTable, FloatingFigure


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
