import pytest
from pytest import fixture
from inspect import cleandoc
import os

from py2tex.plot import Plot, AddPlot
from py2tex.color import Color


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

    def test_add_plot_with_legend(self):
        plot = Plot(plot_name='plot_test')
        plot.add_plot(list(range(10)), list(range(10)), 'red', legend='Legend', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[red, line width=2pt] table[x=x0, y=y0, col sep=comma]{.\plot_test.csv};
            \addlegendentry{Legend}
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_add_plot_without_legend(self):
        plot = Plot(plot_name='plot_test')
        plot.add_plot(list(range(10)), list(range(10)), 'red', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[red, forget plot, line width=2pt] table[x=x0, y=y0, col sep=comma]{.\plot_test.csv};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_add_plot_with_color_obj(self):
        plot = Plot(plot_name='plot_test')
        color = Color(.1,.2,.3, 'spam')
        plot.add_plot(list(range(10)), list(range(10)), color, legend='Legend', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[spam, line width=2pt] table[x=x0, y=y0, col sep=comma]{.\plot_test.csv};
            \addlegendentry{Legend}
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')


class TestAddPlot:
    def test_addplot_command(self):
        addplot = AddPlot(1, './some/path/to/plot.csv', 'red', 'dashed', line_width='2pt')
        assert addplot.build() == r"\addplot[red, dashed, line width=2pt] table[x=x1, y=y1, col sep=comma]{./some/path/to/plot.csv};"
