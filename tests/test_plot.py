import pytest
from pytest import fixture
from inspect import cleandoc
import os

from py2tex.plot import Plot, AddPlot


class TestPlot:
    def test_default_plot(self):
        assert Plot(plot_name='plot_test').build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')


class TestAddPlot:
    def test_addplot_command(self):
        addplot = AddPlot(1, './some/path/to/plot.csv', 'red', 'dashed', line_width='2pt')
        assert addplot.build() == r"\addplot[red, dashed, line width=2pt] table[x=x1, y=y1, col sep=comma]{./some/path/to/plot.csv};"
