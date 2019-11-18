import pytest
from pytest import fixture
from inspect import cleandoc
import os, shutil

from python2latex.plot import Plot, AddPlot, AddMatrixPlot
from python2latex.color import Color
from python2latex.document import Document


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
            \addplot[red, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
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
            \addplot[red, forget plot, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
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
            \addplot[spam, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
            \addlegendentry{Legend}
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_save_csv_to_right_path(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        plot_name = 'plot_name'
        plot = Plot([1,2,3], [1,2,3], plot_name=plot_name, plot_path=plotpath)
        plot.build()
        assert os.path.exists(plotpath + plot_name + '.csv')
        shutil.rmtree(filepath)

    def test_build_pdf_to_other_relative_path(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        doc_name = 'Doc name'
        plot_name = 'plot_name'
        doc = Document(doc_name, filepath=filepath)
        plot = doc.new(Plot([1,2,3], [1,2,3], plot_name=plot_name, plot_path=plotpath))
        try:
            doc.build(show_pdf=False)
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(plotpath + plot_name + '.csv')
        finally:
            shutil.rmtree('./some_doc_path/')

    def test_add_matrix_plot(self):
        plot = Plot(plot_name='matrix_plot_test')
        plot.add_matrix_plot(list(range(10)), list(range(10)), [[i for i in range(10)] for _ in range(10)])
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, colorbar, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[matrix plot] table[x=x_color, y=y_color, meta=z_color, col sep=comma]{./matrix_plot_test.csv};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('matrix_plot_test.csv')

    def test_build_pdf_with_matrix_plot(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        doc_name = 'Doc name'
        plot_name = 'plot_name'
        doc = Document(doc_name, filepath=filepath)
        X = list(range(10))
        Y = list(range(10))
        Z = [[i for i in range(10)] for _ in range(10)]
        plot = doc.new(Plot(plot_name=plot_name, plot_path=plotpath))
        plot.add_matrix_plot(X, Y, Z)
        try:
            doc.build(show_pdf=False)
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(plotpath + plot_name + '.csv')
        finally:
            # shutil.rmtree('./some_doc_path/')
            pass

class TestAddPlot:
    def test_addplot_command(self):
        add_plot = AddPlot(1, './some/path/to/plot.csv', 'red', 'dashed', line_width='2pt')
        assert add_plot.build() == r"\addplot[red, dashed, line width=2pt] table[x=x1, y=y1, col sep=comma]{./some/path/to/plot.csv};"


class TestAddMatrixPlot:
    def test_addmatrixplot_command(self):
        add_matrix_plot = AddMatrixPlot(1, './some/path/to/plot.csv')
        assert add_matrix_plot.build() == r"\addplot[matrix plot] table[x=x1, y=y1, meta=z1, col sep=comma]{./some/path/to/plot.csv};"
