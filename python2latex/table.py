from numbers import Real, Integral
import numpy as np

from python2latex import FloatingTable, FloatingEnvironmentMixin
from python2latex import TexEnvironment, TexCommand, build, bold, italic
"""
TODO:
- Remove as_float_env?
- Add col_space params
"""


class Table(FloatingEnvironmentMixin, super_class=FloatingTable):
    """
    Implements a (floating) 'table' environment. Wraps many features for easy usage and flexibility, such as:
        - Supports slices to set items via bracket access.
        - Easy and automatic multirow and multicolumn cells.
        - Automatically highlights best value inside a region of the table.
        - Apply commands to every cells in a region.
        - Quick way to insert rules and partial rules.
        - Customizable number formatting.
    To do so, the brackets access [] (__getitem__ and __setitem__) has been repurposed to select an area and returns a SelectedArea object, which is a kind of view of the table. To access the actual data inside the table, use the 'data' attribute with brackets.

    Feature implementations:
        SelectedArea objects defines multiple methods and properies to edit the table that wraps LaTeX commands. These are 'format_spec' to choose the format specifier of numbers, 'add_rule' to insert rules, 'multicell' to merge cells, 'apply_command' to apply custom commands, 'highlight_best' to highlight the best value in a given region, and 'divide_cell' to divide a cell in multiple subcells. See the documentation of each method for more details.

    Table vs Tabular:
        The Table class is a wrapper of the floating TeX environment 'table' (with integrated 'tabular' environment), while the Tabular class implements the 'tabular' TeX environment. As such, Tabular does the hard work, while Table is simply a wrapper to make TeX tables creation easier.

        The Table object created will instaciate a Tabular object with the arguments passed at the initialization. The Tabular object is accessible via the 'tabular' attribute and is appended to the body. Attribute access of the Table objects are rerouted to the underlying Tabular object. For example, 'table.data' will actually return 'table.tabular.data'. This is done via the __getattr__ method.

    Building the table:
        The build phase of the Table object relies on the build phase of the Tabular object. The 'build' method follows some steps, which order could be relevant when making complex Tables. The order is:
            1. Append the alignment to the tabular TeX environment (e.g. {ccc} for 3 centered columns table).
            2. Format all numbers to specifications using 'format(number, format_spec)'.
            3. Call the 'build' method (or cast to string) every cells.
            4. Apply chronologically all commands added with the 'apply_command' and the 'highlight_best' methods.
            5. Apply 'multicolumn' and 'multirow' commands if necessary.
            6. Piece together the table into a single string, inserting rules where needed.
    """
    def __init__(self,
                 shape=(1, 1),
                 alignment='c',
                 float_format='.2f',
                 decimal_separator='.',
                 int_format='d',
                 top_rule=True,
                 bottom_rule=True,
                 as_float_env=True,
                 position='h!',
                 label='',
                 caption='',
                 caption_pos='top',
                 caption_space='6pt',
                 **kwoptions):
        """
        Args:
            shape (tuple of 2 ints): Shape of the table.

            alignment (str or sequence of str, either 'c', 'r', or 'l'): Alignment of the text inside the columns. If a sequence, it should be the same length as the number of columns. If only a string, it will be used for all columns.

            float_format (str): Standard Python float formating available used as default for every float in the table. To change specific cell formats, use the 'change_format' method on a selected area.

            decimal_separator (str): Character used as decimal separator. Default is '.'. Useful for typesetting numbers in other languages such as French, where the comma is used instead.

            int_format (str): Standard Python int formating available used as default for every int in the table. To change specific cell formats, use the 'change_format' method on a selected area.

            top_rule, bottom_rule (bool): Whether or not the table should have border rules.

            as_float_env (bool): If True (default), will wrap a 'tabular' environment with a floating 'table' environment. If False, only the 'tabular' is constructed.

            The following arguments are only valid if 'as_float_env' is set to True.

            position (str, either 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility.

            label (str): Label of the environment.

            caption (str): Caption of the table.

            caption_pos (str, either 'top' or 'bottom'): Position of the caption, either above (top) the table or below (bottom). Default is 'top' since captions are conventionally above the Table.

            caption_space (str, valid TeX length): Space between the caption and the table. Can be any valid TeX length (e.g. '5pt').
        """
        super().__init__(as_float_env=as_float_env, position=position, label=label, caption=caption, caption_pos=caption_pos, caption_space=caption_space, **kwoptions)

        self.tabular = Tabular(shape=shape,
                               alignment=alignment,
                               float_format=float_format,
                               decimal_separator=decimal_separator,
                               int_format=int_format,
                               top_rule=top_rule,
                               bottom_rule=bottom_rule)
        self.body.append(self.tabular)

    def __getattr__(self, name):
        if name in vars(self):
            return getattr(self, name)
        else:
            return getattr(self.tabular, name)

    def __getitem__(self, idx):
        return self.tabular[idx]

    def __setitem__(self, idx, value):
        self.tabular[idx] = value

    def __repr__(self):
        return repr(self.tabular)


class Tabular(TexEnvironment):
    """
    Implementation of tabular TeX environment.
    """
    def __init__(self,
                 shape=(1, 1),
                 alignment='c',
                 float_format='.2f',
                 decimal_separator='.',
                 int_format='d',
                 top_rule=True,
                 bottom_rule=True,
                 **kwoptions
                 ):
        """
        Args:
            See Table documentation.
        """
        super().__init__('tabular', **kwoptions)
        self.add_package('booktabs')

        self.top_rule = top_rule
        self.bottom_rule = bottom_rule

        self.shape = shape
        self.alignment = [alignment] * shape[1] if isinstance(alignment, str) else alignment
        self.float_format = float_format
        self.decimal_separator = decimal_separator
        self.int_format = int_format
        self.data = np.full(shape, '', dtype=object)

        self.rules = {}
        self.multicells = []
        self.highlights = []
        self.formats_spec = np.full(shape, None, dtype=object)
        self.commands = np.full(shape, None, dtype=object)
        for i in range(shape[0]):
            for j in range(shape[1]):
                self.commands[i, j] = list()

    def __getitem__(self, idx):
        return SelectedArea(self, idx)

    def __setitem__(self, idx, value):
        selected_area = self[idx]
        if isinstance(value, (str, Real, Integral)) and selected_area.size > 1:
            # There are multirows or multicolumns to treat
            selected_area.multicell(value)
        else:
            self.data[idx] = value

    def __repr__(self):
        return repr(self.data)

    def _apply_commands(self, i, j, content):
        command_list = self.commands[i, j]
        for command in command_list:
            content = build(command(content), self)
        return content

    def _format_number(self, i, j, content):
        format_spec = self.formats_spec[i, j]

        if not isinstance(content, (Real, Integral)):
            return content

        if format_spec is not None:
            content = format(content, format_spec)
        elif format_spec is None and isinstance(content, Integral):
            content = format(content, self.int_format)
        elif format_spec is None and isinstance(content, Real): # Fallback to default
            content = format(content, self.float_format)

        if self.decimal_separator != '.':
            content = content.replace('.', self.decimal_separator)

        return content

    def _apply_multicells(self, tex_array, tex_array_format):
        for idx, v_align, h_align, v_shift in self.multicells:

            start_i, stop_i, _ = idx[0].indices(self.shape[0])
            start_j, stop_j, _ = idx[1].indices(self.shape[1])

            tex_array_format[start_i, slice(start_j, stop_j - 1)] = ''
            cell_shape = tex_array[idx].shape
            content = tex_array[start_i, start_j]

            if start_i == stop_i - 1: # Multicolumn only
                content = multicolumn(cell_shape[1], h_align, content)
            else: # Multirow needed
                content = multirow(cell_shape[0], v_align, v_shift, content)

            if start_j < stop_j - 1 and start_i < stop_i - 1: # Multirow and multicolumn needed
                content = multicolumn(cell_shape[1], h_align, content)

            tex_array[start_i, start_j] = content

    def build(self):
        tex = [build(self.head) + '{' + ''.join(self.alignment) + '}']

        if self.top_rule:
            tex.append(r'\toprule')

        tex_array = np.full_like(self.data, '', dtype=object)

        for i, row in enumerate(self.data):
            for j, content in enumerate(row):
                content = self._format_number(i, j, content)
                content = build(content)
                content = self._apply_commands(i, j, content)
                tex_array[i, j] = content

        tex_array_format = np.array([[' & ']*(self.shape[1] - 1) + [r'\\']]*self.shape[0])

        self._apply_multicells(tex_array, tex_array_format)

        for i, (row, row_format) in enumerate(zip(tex_array, tex_array_format)):
            tex.append(''.join(build(item, self) for pair in zip(row, row_format) for item in pair))
            if i in self.rules:
                for rule in self.rules[i]:
                    tex.append(build(rule))

        if self.bottom_rule:
            tex.append(r'\bottomrule')

        tex += [self.tail]
        return self._build_list(tex)


class SelectedArea:
    """
    Represents a selected area in a table. Contains a reference to the actual tabular and methods to apply on an area of the tabular.

    SelectedArea objects defines multiple methods to edit the table that wraps LaTeX commands. These are 'format_spec' to choose the format specifier of numbers, 'add_rule' to insert rules, 'multicell' to merge cells, 'apply_command' to apply custom commands, 'highlight_best' to highlight the best value in a given region, and 'divide_cell' to divide a cell in multiple subcells. See the documentation of each method for more details.

    Furthermore, it has a 'data' property to access the actual data of the selected area, as well as 'idx' and 'size' properties, respectively returning the starting and stoping indices of the area and the size of the area.
    """
    def __init__(self, tabular, idx):
        self.tabular = tabular
        self.slices = self._convert_idx_to_slice(idx)

    def _convert_idx_to_slice(self, idx):
        if isinstance(idx, tuple):
            i, j = idx
        else:
            i, j = idx, slice(None)
        if isinstance(i, Integral):
            i = slice(i, i + 1)
        if isinstance(j, Integral):
            j = slice(j, j + 1)
        return i, j

    @property
    def data(self):
        return self.tabular.data[self.slices]

    @data.setter
    def data(self, value):
        self.tabular.data[self.slices] = value

    @property
    def size(self):
        return self.tabular.data[self.slices].size

    @property
    def idx(self):
        start_i, stop_i, _ = self.slices[0].indices(self.tabular.shape[0])
        start_j, stop_j, _ = self.slices[1].indices(self.tabular.shape[1])
        return (start_i, start_j), (stop_i, stop_j)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    @property
    def format_spec(self):
        return self.tabular.formats_spec[self.slices]

    @format_spec.setter
    def format_spec(self, format_spec):
        """
        Changes the format specifications used to format numbers in the selected area.

        Args:
            format_spec (str): Python string format (e.g. '.2f' for float with 2 decimals).
        """
        self.tabular.formats_spec[self.slices] = format_spec

    def add_rule(self, position='below', trim_right=False, trim_left=False):
        """
        Adds a rule below or above the selected area of the tabular.

        Args:
            position (str, either 'below' or 'above'): Position of the rule below or above the selected area.
            trim_left (bool or str): Whether to trim the left end of the rule or not. If True, default trim length is used ('.5em'). If a string, can be any valid LaTeX distance.
            trim_right (bool or str): Same a trim_left, but for the right end.

        Returns self.
        """
        r = 'r' if trim_right else ''
        if isinstance(trim_right, str):
            r += f"{{{trim_right}}}"
        l = 'l' if trim_left else ''
        if isinstance(trim_left, str):
            l += f"{{{trim_left}}}"

        (i_start, j_start), (i_stop, j_stop) = self.idx
        if position == 'below':
            i = i_stop - 1
        else:
            i = i_start - 1

        if i not in self.tabular.rules:
            self.tabular.rules[i] = []

        if self.slices[1] == slice(None) and not trim_left and not trim_right:
            self.tabular.rules[i].append(midrule())
        else:
            self.tabular.rules[i].append(cmidrule(j_start, j_stop, r + l))

        return self

    def multicell(self, value, v_align='*', h_align='c', v_shift=None):
        """
        Merges the selected area into a single cell.

        Args:
            value (str, int or float): Value of the cell.
            v_align (str, ex. '*'): '*' means the same alignment of the other cells in the row. See LaTeX 'multirow' documentation.
            h_align (str, ex. 'c', 'l' or 'r'): See LaTeX 'multicolumn' documentation.
            v_shift (str, any valid length of LaTeX): Vertical shift of the text position of multirow merging.

        Returns self.
        """
        self.tabular.add_package('multicol')
        self.tabular.add_package('multirow')

        self.data = ''  # Erase old value
        multicell_params = (self.slices, v_align, h_align, v_shift)
        self.tabular.multicells.append(multicell_params)  # Save position of multiple cells span

        self.tabular.data[self.idx[0]] = value

        return self

    def apply_command(self, command):
        """
        Will apply the command to the selected cell content. Commands are stored and will be applied chronologically if many commands are added on the same cells.

        N.B. 'highlight_best' will add commands to be applied on the cells. The order in which 'apply_command' and 'highlight_best' are called may have an impact on the final result.

        Args:
            command (Union[TexCommand, callable]): Non-instanciated TexCommand or callable that will receive the cell content as argument. If a callable, should return a valid TeX string.
        """
        for row in self.tabular.commands[self.slices]:
            for command_list in row:
                command_list.append(command)

    def highlight_best(self, mode='high', best='bold', not_best=None, atol=5e-3, rtol=0):
        """
        Highlights the best value(s) inside the selected area of the tabular. Ignores text. If multiple values are equal to an absolute tolerance of atol and relative tolerance of rtol, both are highlighted.

        Args:
            mode (str, either 'high' or 'low'): Determines what is the best value.
            best (Union[str, callable]): Specifies how to highlight the best. Accepted strings are 'bold' and 'italic'. If a callable, the callable will receive the cell content as argument and should output a valid tex command.
            not_best (Union[str, callable, None]): Specifies a command to apply to all other cells that are *not* the best. Accepted strings are 'bold' and 'italic'. If a callable, the callable will receive the cell content as argument and should output a valid tex command.
            atol (float): Absolute tolerance when comparing best.
            atol (float): Relative tolerance when comparing best.

        Returns self.
        """
        if mode == 'high' or mode == 'max':
            best_value = -np.inf
            value_is_better_than_best = lambda value, current_best: value > current_best
        elif mode == 'low' or mode == 'min':
            best_value = np.inf
            value_is_better_than_best = lambda value, current_best: value < current_best
        else:
            raise ValueError(f'Invalid value {mode} for mode argument.')

        if best == 'bold':
            best = bold
        elif best == 'italic':
            best = italic

        if not_best == 'bold':
            not_best = bold
        elif not_best == 'italic':
            not_best = italic

        # Find best value
        best_idx = [(None, None)]
        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, (Real, Integral)) and value_is_better_than_best(value, best_value):
                    best_idx = [(i, j)]
                    best_value = value

        # Find values close to best
        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, (Real, Integral)) and np.isclose(value, best_value, rtol, atol) \
                    and (i, j) not in best_idx:
                    best_idx.append((i, j))

        if best_idx[0][0] is not None: # Best have been found (i.e. there are floats or ints in selected area)
            start_i, start_j = self.idx[0]
            stop_i, stop_j = self.idx[1]

            for i in range(stop_i-start_i):
                for j in range(stop_j-start_j):
                    if (i, j) in best_idx:
                        self.tabular.commands[i+start_i, j+start_j].append(best)
                    elif not_best is not None:
                        self.tabular.commands[i+start_i, j+start_j].append(not_best)

        return self

    def divide_cell(self,
                    shape=(1, 1),
                    alignment='c',
                    float_format=None,
                    decimal_separator=None,
                    int_format=None):
        """
        Divides the selected cell in another subtable. Useful for long title to manually cut for example.

        Args:
            See Tabular documentation.

        Returns a Tabular object.
        """
        if self.size > 1:
            raise RuntimeError('Invalid selected area. It should be of size 1.')

        if float_format is None:
            float_format = self.tabular.float_format
        if decimal_separator is None:
            decimal_separator = self.tabular.decimal_separator
        if int_format is None:
            int_format = self.tabular.int_format

        subtabular = Tabular(shape=shape,
                             alignment=alignment,
                             float_format=float_format,
                             decimal_separator=decimal_separator,
                             int_format=int_format,
                             bottom_rule=False,
                             top_rule=False)
        self.data = subtabular

        subtabular[:,:].format_spec = self.tabular.formats_spec[self.slices]

        return subtabular


class cmidrule(TexCommand):
    """
    Simple rule object to handle rules added to tables.
    """
    def __init__(self, start, end, trim):
        """
        Args:
            start (int): Row index where the rule starts (included).
            end (int): Row index where the rule ends (excluded).
            trim (str): Any valid LaTeX trim value (see the booktabs package).
        """
        self.start = start
        self.end = end
        self.trim = trim
        super().__init__('cmidrule')

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end and self.trim == other.trim

    def build(self):
        rule = super().build()
        if self.trim:
            rule += f"({self.trim})"
        rule += f"{{{self.start + 1}-{self.end}}}"
        return rule


class midrule(TexCommand):
    def __init__(self):
        super().__init__('midrule')

    def __eq__(self, other):
        return isinstance(other, midrule)


class multicolumn(TexCommand):
    def __init__(self, col_span, alignment, cell_content):
        super().__init__('multicolumn')
        self.col_span = col_span
        self.alignment = alignment
        self.cell_content = cell_content

    def build(self):
        return super().build() + f'{{{self.col_span}}}{{{self.alignment}}}{{{build(self.cell_content, self)}}}'


class multirow(TexCommand):
    def __init__(self, col_span, alignment, shift, cell_content):
        super().__init__('multirow')
        self.col_span = col_span
        self.alignment = alignment
        self.shift = shift
        self.cell_content = cell_content

    def build(self):
        shift = f'[{self.shift}]' if self.shift else ''
        return super().build() + f'{{{self.col_span}}}{{{self.alignment}}}{shift}{{{build(self.cell_content, self)}}}'
