import os
from datetime import datetime as dt
import itertools
import csv
import numpy as np

from python2latex import FloatingFigure, FloatingEnvironmentMixin, TexEnvironment, TexCommand, Color, default_palette, PREDEFINED_PALETTES


class _AxisProperty:
    def __init__(self, param_name):
        self.param_name = param_name

    def __get__(self, obj, cls=None):
        return obj.kwoptions[
            self.param_name] if self.param_name in obj.kwoptions else None

    def __set__(self, obj, value):
        obj.kwoptions[self.param_name] = value


class _AxisTicksProperty(_AxisProperty):
    def __set__(self, obj, value):
        value = '{' + ','.join(f"{v:.3f}" for v in value) + '}'
        obj.kwoptions[self.param_name] = value


class _AxisTicksLabelsProperty(_AxisProperty):
    def __set__(self, obj, value):
        value = '{' + ','.join(value) + '}'
        obj.kwoptions[self.param_name] = value


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
    def __init__(self,
                 *X_Y,
                 plot_name=None,
                 plot_path='.',
                 width=r'.8\textwidth',
                 height=r'.45\textwidth',
                 grid=True,
                 grid_style=('dashed', 'gray!50'),
                 marks=False,
                 lines=True,
                 palette=default_palette,
                 axis_y='left',
                 axis_x='bottom',
                 position='h!',
                 as_float_env=True,
                 label='',
                 caption='',
                 caption_pos='bottom',
                 caption_space='',
                 **axis_kwoptions):
        """
        Args:
            X_Y (tuple of sequences of points to plot):
                If only one sequence is passed, it will be considered as the Y components of the plot and the X will goes from 0 to len(Y)-1. If more than one sequence is passed, the sequences are treated in pairs (X,Y) of sequences of points. (This behavior copies matplotlib.pyplot.plot).
            plot_name (str):
                Name of the plot. Used to save data to a csv.
            plot_path (str):
                Path of the plot. Used to save data to a csv. Default is current working directory.
            width (str):
                Width of the figure. Can be any LaTeX length.
            height (str):
                Height of the figure. Can be any LaTeX length.
            grid (Union[bool, str]):
                Whether if the grid if shown on not. If a string, should be one of pgfplots valid argument for 'grid' such as 'major', 'minor' and 'none'. Defaults to 'major'.
            grid_style (Iterable[str]):
                Iterable of options for the grid.
            marks (bool or str):
                Whether to plot coordinates with or without marks. If a str, should be the radius of the marks with any LaTeX length.
            lines (bool or str):
                Whether to link coordinates with lines or not. If a str, should be the width of the lines with any LaTeX length.
            axis_x (str, either 'bottom' or 'top'):
                Where the x axis should appear (bottom or top).
            axis_y (str, either 'left' or 'right'):
                Where the y axis should appear (left or right).
            palette (Union[str, Iterable]):
                Iterable that yields colors to use for line plots or name of the palette. The string can be 'holi' (default), 'aube' and 'aurore' (See the example 'predefined palettes comparison' for details). The iterable should yield either tuple of 3 floats between 0 and 1 interpreted as rgb colors, or python2latex Color objects for more flexibility. If the number of colors is less than the number of line plots, it will loop automatically. Default is 'holi', a dynamic colorblind-friendly palette that will generate as many distinct colors as there are line plots.
            position (str, either 'h', 't', 'b', with optional '!'):
                Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility. Only valid if as_float_env is True.
            as_float_env (bool):
                If True (default), will wrap a 'tikzpicture' environment with a floating 'figure' environment. If False, only the 'tikzpicture' is constructed.
            label (str):
                Label of the environment.
            caption, caption_pos, caption_space:
                See _FloatingEnvironment for description.
            axis_kwoptions (dict):
                pgfplots keyword options for the axis. All underscore will be replaced by spaces when converted to LaTeX parameters.
        """
        super().__init__(as_float_env=as_float_env,
                         position=position,
                         label=label,
                         caption=caption,
                         caption_pos=caption_pos,
                         caption_space=caption_space)

        self.add_package('tikz')
        self.add_package('pgfplots')
        self.add_package('pgfplotstable')

        self.tikzpicture = self.new(TexEnvironment('tikzpicture'))

        self.plot_name = plot_name or f"plot-{dt.now().strftime(r'%Y-%m-%d %Hh%Mm%Ss')}"
        self.plot_path = plot_path
        self.plot_filepath = os.path.join(self.plot_path, self.plot_name+'.csv').replace('\\', '/')

        self.axis = Axis(width=width,
                         height=height,
                         grid=grid,
                         grid_style=grid_style,
                         marks=marks,
                         lines=lines,
                         palette=palette,
                         axis_y=axis_y,
                         axis_x=axis_x,
                         plot_filepath=self.plot_filepath,
                         **axis_kwoptions)

        self.tikzpicture.add_text(self.axis)

        iter_X_Y = iter(X_Y)
        for x, y in zip(iter_X_Y, iter_X_Y):
            self.axis.add_plot(x, y)
        if len(X_Y) % 2 != 0:  # Copies matplotlib.pyplot.plot() behavior
            self.axis.add_plot(np.arange(len(X_Y[-1])), X_Y[-1])

    def __getattr__(self, name):
        if name in ['x_min', 'x_max', 'y_min', 'y_max', 'x_label', 'y_label', 'x_ticks', 'y_ticks', 'x_ticks_labels', 'y_ticks_labels', 'title', 'legend_position']:
            return getattr(self.axis, name)
        else:
            return getattr(self, name)

    def __setattr__(self, name, value):
        if name in ['x_min', 'x_max', 'y_min', 'y_max', 'x_label', 'y_label', 'x_ticks', 'y_ticks', 'x_ticks_labels', 'y_ticks_labels', 'title', 'legend_position']:
            setattr(self.axis, name, value)
        object.__setattr__(self, name, value)

    def save_to_csv(self):
        os.makedirs(self.plot_path, exist_ok=True)
        plots = self.axis.plots
        matrix_plot = self.axis.matrix_plot

        with open(self.plot_filepath, 'w', newline='') as file:
            writer = csv.writer(file)

            titles = [coor for p in plots for coor in (f'x{p.id_number}', f'y{p.id_number}')]
            if matrix_plot:
                titles += [
                    f'x{matrix_plot.id_number}',
                    f'y{matrix_plot.id_number}',
                    f'z{matrix_plot.id_number}'
                ]
            writer.writerow(titles)
            data = [x_y for p in plots for x_y in (p.X, p.Y)]
            if matrix_plot:
                XX, YY = np.meshgrid(matrix_plot.X, matrix_plot.Y)
                data += [XX.reshape(-1), YY.reshape(-1), matrix_plot.Z.T.reshape(-1)]

            for row in itertools.zip_longest(*data, fillvalue=''):
                writer.writerow(row)

    def add_plot(self, *args, **kwargs):
        return self.axis.add_plot(*args, **kwargs)

    def add_matrix_plot(self, *args, **kwargs):
        return self.axis.add_matrix_plot(*args, **kwargs)

    def build(self):
        self.save_to_csv()
        return super().build()


class Axis(TexEnvironment):
    """
    Implementation of an axis environment.
    """
    def __init__(self,
                 *options,
                 width=r'.8\textwidth',
                 height=r'.45\textwidth',
                 grid=True,
                 grid_style=('dashed', 'gray!50'),
                 marks=False,
                 lines=True,
                 palette=default_palette,
                 axis_y='left',
                 axis_x='bottom',
                 plot_filepath=None,
                 **kwoptions):
        """
        Args:
            options (Tuple[str]):
                String options to pass to the axis.
            plot_name (str):
                Name of the plot. Used to save data to a csv.
            plot_path (str):
                Path of the plot. Used to save data to a csv. Default is current working directory.
            width (str):
                Width of the figure. Can be any LaTeX length.
            height (str):
                Height of the figure. Can be any LaTeX length.
            grid (Union[bool, str]):
                Whether if the grid if shown on not. If a string, should be one of pgfplots valid argument for 'grid' such as 'major', 'minor' and 'none'. Defaults to 'major'.
            grid_style (Iterable[str]):
                Iterable of options for the grid.
            marks (bool or str):
                Whether to plot coordinates with or without marks. If a str, should be the radius of the marks with any LaTeX length.
            lines (bool or str):
                Whether to link coordinates with lines or not. If a str, should be the width of the lines with any LaTeX length.
            palette (Union[str, Iterable]):
                Iterable that yields colors to use for line plots or name of the palette. The string can be 'holi' (default), 'aube' and 'aurore' (See the example 'predefined palettes comparison' for details). The iterable should yield either tuple of 3 floats between 0 and 1 interpreted as rgb colors, or python2latex Color objects for more flexibility. If the number of colors is less than the number of line plots, it will loop automatically. Default is 'holi', a dynamic colorblind-friendly palette that will generate as many distinct colors as there are line plots.
            axis_x (str, either 'bottom' or 'top'):
                Where the x axis should appear (bottom or top).
            axis_y (str, either 'left' or 'right'):
                Where the y axis should appear (left or right).
            plot_filepath (str):
                Location where the data used for the plot is saved.
            axis_kwoptions (dict):
                pgfplots keyword options for the axis. All underscore will be replaced by spaces when converted to LaTeX parameters.
        """
        options += (
            f'grid style={{{", ".join(grid_style)}}}',
            f'axis y line*={axis_y}',
            f'axis x line*={axis_x}',
        )

        if grid is True:
            grid = 'major'
        elif grid is False or grid is None:
            grid = 'none'

        super().__init__('axis',
                         options=options,
                         width=width,
                         height=height,
                         grid=grid,
                         **kwoptions)

        self.add_package('tikz')
        self.add_package('pgfplots')
        self.add_package('pgfplotstable')

        self.default_plot_kwoptions = {}
        self.default_plot_options = []

        if not marks or marks == '0pt':
            marks = False
            self.default_plot_options.append('no markers')
        else:
            if not isinstance(marks, str):
                marks = '2pt'
            self.default_plot_kwoptions['mark size'] = marks

        if not lines or lines == '0pt':
            if marks:
                self.default_plot_options.append('only marks')
        else:
            if not isinstance(lines, str):
                lines = '1.25pt'
            self.default_plot_kwoptions['line width'] = lines


        self.plots = []
        self.matrix_plot = None

        self.plot_filepath = plot_filepath

        if isinstance(palette, str):
            palette = PREDEFINED_PALETTES[palette]
        self.color_iterator = itertools.cycle(palette)

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
    title = _AxisProperty('title')
    legend_position = _AxisProperty('legend pos')

    def add_plot(self, X, Y, *options, color=None, legend=None, forget_plot=True, **kwoptions):
        """
        Adds a plot to the axis.

        Args:
            X (sequence of numbers): X coordinates.
            Y (sequence of numbers): Y coordinates.
            options (Tuple[Union(str, TexObject]): Options for the plot. Colors can be specified here as strings of the whole color, e.g. 'black', 'red', 'blue', etc. See pgfplots '\addplot[options]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
            color (Union[Tuple[float], str, Color]): Color used for the line plot. Can be a tuple of 3 floats between 0 and 1, interpreted as rgb color, a string corresponding to a valid existing or predefined color (e.g. using the xcolor package with dvipsnames option), or a python2latex Color object. If None, the color palette passed at the initialization will be used. Passing a color will *not use* the next color in the color palette. Note that one can set the color without the keyword 'color', as TikZ does not use the color keyword. This will however skip the next color in the color palette.
            legend (str): Entry of the plot.
            forget_plot (bool): forget_plot is used to correctly present the legend. Default behavior is to add 'forget plot' option when no legend is provided. However, this can lead to incompatibility when plotting histograms. It is advised to set it to False in that case.
            kwoptions (Dict[str, Union(str, TexObject)): Keyword options for the plot. See pgfplots '\addplot[kwoptions]' for possible options. All underscores are replaced by spaces when converted to LaTeX.

        Returns: LinePlot object.
        """
        if color is None: # Color should precede passed options
            color = next(self.color_iterator)
            if isinstance(color, tuple):
                color = Color(*color)
            options = (color,) + options
        else:
            if isinstance(color, tuple): # Color should follow other options
                color = Color(*color)
            options += (color,)

        line_plot = LinePlot(X, Y, *options, plot_filepath=self.plot_filepath, legend=legend, forget_plot=forget_plot, **kwoptions)
        self.plots.append(line_plot)
        self += line_plot

        return line_plot

    def add_matrix_plot(self, X, Y, Z, *options, colorbar=True, **kwoptions):
        """
        Adds a matrix plot to the axis.

        Args:
            X (sequence of numbers): X coordinates. Should have the same length as the first dimension of Z.
            Y (sequence of numbers): Y coordinates. Should have the same length as the second dimension of Z.
            Z (Array of numbers of dim (x_dim, y_dim)): Z coordinates.
            options (Union[Tuple[str], str, TexObject]): Options for the plot. See pgfplots '\addplot[options]' for
            possible options. All underscores are replaced by spaces when converted to LaTeX.
            colorbar (str): Colorbar legend.
            kwoptions (tuple of str): Keyword options for the plot. See pgfplots '\addplot[kwoptions]' for possible
            options. All underscores are replaced by spaces when converted to LaTeX.

        Returns: MatrixPlot object.
        """
        if colorbar:
            self.options += ('colorbar', )
        self.matrix_plot = MatrixPlot(X, Y, Z, *options, plot_filepath=self.plot_filepath, **kwoptions)
        self += self.matrix_plot

        return self.matrix_plot

    def build(self):
        every_plot_options = ', '.join(self.default_plot_options)
        every_plot_kwoptions = ', '.join('='.join([k, v]) for k, v in self.default_plot_kwoptions.items())
        if every_plot_kwoptions:
            every_plot_options += ', ' + every_plot_kwoptions
        self.options += (
            f"every axis plot/.append style={{{every_plot_options}}}",
        )

        return super().build()


class _Plot(TexCommand):
    """
    Basic Plot object to handle plot data and plot options as well as a tex command wrapper.
    """
    plot_count = 0

    def __init__(self, *options, plot_filepath=None, **kwoptions):
        self.id_number = 1 * _Plot.plot_count
        _Plot.plot_count += 1
        self.plot_filepath = plot_filepath
        super().__init__('addplot', options=options, options_pos='first', **kwoptions)


class LinePlot(_Plot):
    """
    LinePlot object to handle line plots.
    """
    def __init__(self,
                 X, Y,
                 *options,
                 label=None,
                 label_pos=1,
                 label_anchor='west',
                 label_name=None,
                 label_options=list(),
                 legend=None,
                 forget_plot=True,
                 **kwoptions):
        """
        Adds a plot to the axis.

        Args:
            X (sequence of numbers): X coordinates.
            Y (sequence of numbers): Y coordinates.

            options (Union[Tuple[str], str, TexObject]): Options for the plot. Colors can be specified here as strings of the whole color, e.g. 'black', 'red', 'blue', etc. See pgfplots '\addplot[options]' for possible options. All underscores are replaced by spaces when converted to LaTeX.

            label (str): Label of the line plot. Can be used as an alternative for the legend.
            label_pos (float between 0 and 1): Position of the node label. Represent the fraction of the plot. For example, at 0, the label will be at the beginning of the plot, at .5 it will be midway and at 1, the label will be at the end.
            label_anchor (Union[str, int]): Anchor of the node label. Anchors are one of the cardinal directions (north, west, south and east) or a valid combination of them (north west, south east, etc.). Can also be an integer representing the angle in degree of the anchor (0 is equivalent to east, 90 is north, 180 is west and 270 is south).
            label_name (str): Name of the node label if desired for future usage with TikZ.
            label_options (List(str)): Options of the node label. See the TikZ documentation for the options.

            legend (str): Entry of the plot.
            forget_plot (bool): Either or not to forget plot when adding plot. In some case, like histogram, the forget plot option does not allow to have multiple plots near each other. By default the forget_plot is set to True.

            kwoptions (tuple of str): Keyword options for the plot. See pgfplots '\addplot[kwoptions]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
        """
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.legend = legend
        self.forget_plot = forget_plot
        label_name = '(' + label_name + ')' if label_name is not None else ''
        label_options = ', '.join(label_options)
        label_options = ', ' + label_options if label_options else ''
        self.label = ''
        if label is not None:
            self.label = f' node[pos={label_pos}, anchor={label_anchor}{label_options}]{label_name} {{{label}}}'

        super().__init__(*options, **kwoptions)

    def build(self):
        assert self.plot_filepath is not None
        legend = ''
        if self.legend:
            legend = f"\n\\addlegendentry{{{self.legend}}};"
        elif self.forget_plot:
            self.options += ('forget plot', )

        return super().build(
        ) + f" table[x=x{self.id_number}, y=y{self.id_number}, col sep=comma]{{{self.plot_filepath}}}{self.label};" + legend


class MatrixPlot(_Plot):
    """
    MatrixPlot object to handle matrix/image plots AKA heatmaps AKA colormaps.
    """
    def __init__(self, X, Y, Z, *options, point_meta='explicit', **kwoptions):
        """
        Adds a matrix plot to the axis.

        Args:
            X (sequence of numbers): X coordinates. Should have the same length as the first dimension of Z.
            Y (sequence of numbers): Y coordinates. Should have the same length as the second dimension of Z.
            Z (Array of numbers of dim (x_dim, y_dim)): Z coordinates.
            options (Union[Tuple[str], str, TexObject]): Options for the plot. See pgfplots '\addplot[options]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
            colorbar (str): Colorbar legend.
            kwoptions (tuple of str): Keyword options for the plot. See pgfplots '\addplot[kwoptions]' for possible options. All underscores are replaced by spaces when converted to LaTeX.
        """
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.Z = np.array([[z for z in z_row] for z_row in Z])
        assert self.Z.shape == self.X.shape + self.Y.shape

        kwoptions['point meta'] = point_meta
        kwoptions['mesh/rows'] = str(len(self.Y))
        kwoptions['mesh/cols'] = str(len(self.X))
        super().__init__('matrix plot*', *options, **kwoptions)

    def build(self):
        assert self.plot_filepath is not None

        return super().build(
        ) + f" table[x=x{self.id_number}, y=y{self.id_number}, meta=z{self.id_number}, " \
            f"col sep=comma]{{{self.plot_filepath}}};"
