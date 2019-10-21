import csv
from datetime import datetime as dt
import numpy as np
import itertools
import os, sys

import python2latex
from python2latex import FloatingFigure, FloatingEnvironmentMixin, TexEnvironment, TexCommand


class _AxisProperty:
    def __init__(self, param_name):
        self.param_name = param_name

    def __get__(self, obj, cls=None):
        return obj.axis.kwoptions[self.param_name] if self.param_name in obj.axis.kwoptions else None

    def __set__(self, obj, value):
        obj.axis.kwoptions[self.param_name] = value


class _AxisTicksProperty(_AxisProperty):
    def __set__(self, obj, value):
        value = '{' + ','.join(f"{v:.3f}" for v in value) + '}'
        obj.axis.kwoptions[self.param_name] = value


class _AxisTicksLabelsProperty(_AxisProperty):
    def __set__(self, obj, value):
        value = '{' + ','.join(value) + '}'
        obj.axis.kwoptions[self.param_name] = value


class Plot(FloatingEnvironmentMixin, super_class=FloatingFigure):
    """
    Implements an easy wrapper to plot curves directly into LaTex. Creates a floating figure if wanted and uses 'pgfplots' to draw the curves.

    It aims to be as easy as matplotlib to use, but to have more beautiful default parameters and to produce directly in LaTeX for easy integration into papers.

    Supported options as properties:
    x_min, x_max, y_min, y_max (number): Sets the limits of the axis.
    x_label, y_label (str): Labels of the axes.
    x_ticks, y_ticks (sequence of float): Positions of the ticks on each axis.
    x_ticks_labels, y_ticks_labels (sequence of str): String to print under each ticks. Should be the same length as x_ticks and y_ticks.
    legend_position (str): Specifies the corner of the legend. Should be a valid combinaisons of two of 'north', 'west', 'south' and 'east'.

    If you know the pgfplots library, all 'axis' environment's parameters can be accessed and modified via the 'self.axis.options' and the 'self.axis.kwoptions' attributes.
    """

    def __init__(self, *X_Y, plot_name=None, plot_path='.', width=r'.8\textwidth', height=r'.45\textwidth', grid=True, marks=False, lines=True, axis_y='left', axis_x='bottom', position='h!', as_float_env=True, label='', **axis_kwoptions):
        """
        Args:
            X_Y (tuple of sequences of points to plot): If only one sequence is passed, it will be considered as the Y components of the plot and the X will goes from 0 to len(Y)-1. If more than one sequence is passed, the sequences are treated in pairs (X,Y) of sequences of points. (This behavior copies matplotlib.pyplot.plot).

            plot_name (str): Name of the plot. Used to save data to a csv.
            plot_path (str): Path of the plot. Used to save data to a csv. Default is current working directory.

            width (str): Width of the figure. Can be any LaTeX length.
            height (str): Height of the figure. Can be any LaTeX length.

            grid (bool or str): Whether if the grid if shown on not. If a string, should be one of pgfplots valid argument for 'grid'.
            marks (bool or str): Whether to plot coordinates with or without marks. If a str, should be the radius of the marks with any LaTeX length.
            lines (bool or str): Whether to link coordinates with lines or not. If a str, should be the width of the lines with any LaTeX length.
            axis_x (str, either 'bottom' or 'top'): Where the x axis should appear (bottom or top).
            axis_y (str, either 'left' or 'right'): Where the y axis should appear (left or right).

            position (str, either 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility. Only valid if as_float_env is True.
            as_float_env (bool): If True (default), will wrap a 'tabular' environment with a floating 'table' environment. If False, only the 'tabular' is constructed.
            label (str): Label of the environment.

            axis_kwoptions (dict): pgfplots keyword options for the axis. All underscore will be replaced by spaces when converted to LaTeX parameters.
        """
        super().__init__(as_float_env=as_float_env, position=position, label=label, label_pos='bottom')

        self.add_package('tikz')
        self.add_package('pgfplots')
        self.add_package('pgfplotstable')

        self.tikzpicture = TexEnvironment('tikzpicture')
        self.add_text(self.tikzpicture)

        if grid is True:
            grid = 'major'
        elif grid is False:
            grid = 'none'

        options = ('grid style={dashed,gray!50}',
                    f'axis y line*={axis_y}',
                    f'axis x line*={axis_x}',
                    # 'axis line style={-latex}',
                    )
        self.axis = TexEnvironment('axis', options=options, width=width, height=height, grid=grid, **axis_kwoptions)
        self.tikzpicture.add_text(self.axis)
        # if not marks:
        #     self.axis.options += ['no marks',]

        self.plot_name = plot_name or f"plot-{dt.now().strftime(r'%Y-%m-%d %Hh%Mm%Ss')}"
        self.plot_path = plot_path
        self.caption = ''

        if not marks:
            mark_size = '0pt'
        elif isinstance(marks, str):
            mark_size = marks
        else:
            mark_size = '2pt'

        if not lines:
            line_width = '0pt'
        elif isinstance(lines, str):
            line_width = lines
        else:
            line_width = '1.25pt'

        self.default_plot_kwoptions = {'line width':line_width,
                                       'mark size':mark_size,
                                       }

        iter_X_Y = iter(X_Y)
        self.plots = []
        for x, y in zip(iter_X_Y, iter_X_Y):
            self.add_plot(x, y)
        if len(X_Y) % 2 != 0: # Copies matplotlib.pyplot.plot() behavior
            self.add_plot(np.arange(len(X_Y[-1])), X_Y[-1])

    x_max = _AxisProperty('xmax')
    x_min = _AxisProperty('xmin')
    y_max = _AxisProperty('ymax')
    y_min = _AxisProperty('ymin')
    x_label = _AxisProperty('xlabel')
    y_label = _AxisProperty('ylabel')
    x_ticks = _AxisTicksProperty('xtick')
    y_ticks = _AxisTicksProperty('ytick')
    x_ticks_labels = _AxisTicksLabelsProperty('xticklabels')
    y_ticks_labels = _AxisTicksLabelsProperty('yticklabels')

    legend_position = _AxisProperty('legend pos')

    def add_plot(self, X, Y, *options, legend=None, **kwoptions):
        """
        Adds a plot to the axis.

        Args:
            X (sequence of numbers): X coordinates.
            Y (sequence of numbers): Y coordinates.
            options (tuple of str): Options for the plot. Colors can be specified here as strings of the whole color, e.g. 'black', 'red', 'blue', etc. See pgfplots '\addplot[options]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
            legend (str): Entry of the plot.
            kwoptions (tuple of str): Keyword options for the plot. See pgfplots '\addplot[kwoptions]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
        """
        X = np.array([x for x in X])
        Y = np.array([y for y in Y])
        self.plots.append((X, Y, legend, options, kwoptions))

    def _build_plots(self):
        for i, (X, Y, legend, options, kwoptions) in enumerate(self.plots):
            plot_path = self.plot_path + '/' + self.plot_name + '.csv'
            plot = self.axis.new(AddPlot(i, plot_path, *options, **kwoptions))

            if legend:
                self.axis += fr"\addlegendentry{{{legend}}}"
            else:
                plot.options += ('forget plot',)

    def save_to_csv(self):
        filepath = os.path.join(self.plot_path, self.plot_name + '.csv')
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)

            titles = [coor for i in range(len(self.plots)) for coor in (f'x{i}', f'y{i}')]
            writer.writerow(titles)
            X_Y = [x_y for x, y, *_ in self.plots for x_y in (x, y)]
            for row in itertools.zip_longest(*X_Y, fillvalue=''):
                writer.writerow(row)

    def build(self):
        self.save_to_csv()
        self._build_plots()

        self.axis.options += (f"every axis plot/.append style={{{', '.join('='.join([k,v]) for k,v in self.default_plot_kwoptions.items())}}}",)

        return super().build()


class AddPlot(TexCommand):
    """
    Simple addplot tex command wrapper.
    """
    def __init__(self, col_number, plot_path, *options, **kwoptions):
        self.col_number = col_number
        # self.plot_path = os.path.abspath(plot_path).replace('\\', '/')
        self.plot_path = plot_path
        super().__init__('addplot', options=options, options_pos='first', **kwoptions)

    def build(self):
        return super().build() + f" table[x=x{self.col_number}, y=y{self.col_number}, col sep=comma]{{{self.plot_path}}};"
