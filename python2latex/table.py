import numpy as np
from python2latex import TexEnvironment, TexCommand, build, bold, italic
from python2latex import FloatingTable, FloatingEnvironmentMixin


"""
TODO:
    - Convert 'multicell' into Multirow and Multicol Tex commands
"""

class Rule(TexCommand):
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
        rule += f"{{{self.start+1}-{self.end}}}"
        return rule


class Table(FloatingEnvironmentMixin, super_class=FloatingTable):
    """
    Implements a (floating) 'table' environment. Wraps many features for easy usage and flexibility, such as:
        - Supports slices to set items.
        - Easy and automatic multirow and multicolumn cells.
        - Automatically highlights best value inside a region of the table.
    To do so, the brackets access [] (__getitem__) has been repurposed to select an area and returns a SelectedArea object. Announced features are defined on SelectedArea objects only. To access the actual data inside the table, use the 'data' attribute with brackets.

    TODO:
        - Maybe: Add a 'insert_row' and 'insert_column' methods.
    """
    def __init__(self, shape=(1,1), alignment='c', float_format='.2f', position='h!', as_float_env=True, top_rule=True, bottom_rule=True, label=''):
        """
        Args:
            shape (tuple of 2 ints): Shape of the table.
            alignment (str or sequence of str, either 'c', 'r', or 'l'): Alignment of the text inside the columns. If a sequence, it should be the same length as the number of columns. If only a string, it will be used for all columns.
            float_format (str): Standard Python float formating available.
            as_float_env (bool): If True (default), will wrap a 'tabular' environment with a floating 'table' environment. If False, only the 'tabular' is constructed.
            position (str, either 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility. Only valid if as_float_env is True.
            top_rule, bottom_rule (bool): Whether or not the table should have outside rules.
            label (str): Label of the environment.
        """
        super().__init__(as_float_env=as_float_env, position=position, label=label, label_pos='top')

        self.tabular = TexEnvironment('tabular')
        self.add_package('booktabs')
        self.body.append(self.tabular)

        self.top_rule = top_rule
        self.bottom_rule = bottom_rule

        self.shape = shape
        self.alignment = [alignment]*shape[1] if len(alignment) == 1 else alignment
        self.float_format = float_format
        self.data = np.full(shape, '', dtype=object)

        self.rules = {}
        self.multicells = []
        self.highlights = []

    def __getitem__(self, idx):
        return SelectedArea(self, idx)

    def __setitem__(self, idx, value):
        selected_area = self[idx]
        if isinstance(value, (str, int, float)) and selected_area.size > 1:
            # There are multirows or multicolumns to treat
            selected_area.multicell(value)
        else:
            self.data[idx] = value

    def __repr__(self):
        return repr(self.data)

    def _apply_multicells(self, table_format):
        for idx, v_align, h_align, v_shift in self.multicells:

            start_i, stop_i, step = idx[0].indices(self.shape[0])
            start_j, stop_j, step = idx[1].indices(self.shape[1])

            table_format[start_i, slice(start_j, stop_j-1)] = ''
            cell_shape = table_format[idx].shape

            if start_i == stop_i - 1:
                self.data[start_i, start_j] = f"\\multicolumn{{{cell_shape[1]}}}{{{h_align}}}{{{self.data[start_i, start_j]}}}"
            else:
                shift = ''
                if v_shift:
                    shift = f'[{v_shift}]'
                self.data[start_i, start_j] = f"\\multirow{{{cell_shape[0]}}}{{{v_align}}}{shift}{{{self.data[start_i, start_j]}}}"

            if start_j < stop_j - 1 and start_i < stop_i - 1:
                self.data[start_i, start_j] = f"\\multicolumn{{{cell_shape[1]}}}{{{h_align}}}{{{self.data[start_i, start_j]}}}"

        return table_format

    def build(self):
        row, col = self.data.shape
        # Format floats
        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, float):
                    value = f'{{value:{self.float_format}}}'.format(value=value)
                self.data[i,j] = build(value, self)

        # Apply highlights
        for i, j, highlight in self.highlights:
            if highlight == 'bold':
                command = bold
            elif highlight == 'italic':
                command = italic
            self.data[i,j] = command(self.data[i,j])

        # Build the tabular
        table_format = np.array([[' & ']*(self.shape[1]-1) + [r'\\']]*self.shape[0], dtype=object)
        table_format = self._apply_multicells(table_format)
        for i, (row, row_format) in enumerate(zip(self.data, table_format)):
            self.tabular.body.append(''.join(str(build(item, self)) for pair in zip(row, row_format) for item in pair))
            if i in self.rules:
                for rule in self.rules[i]:
                    self.tabular.body.append(build(rule))
        build(self.tabular)

        self.tabular.head.parameters += (''.join(self.alignment),)
        if self.top_rule:
            self.tabular.body.insert(0, r"\toprule")
        if self.bottom_rule:
            self.tabular.append(r'\bottomrule')

        return super().build()


class SelectedArea:
    """
    Represents a selected area in a table. Contains a reference to the actual table and methods to apply on an area of the table.
    """
    def __init__(self, table, idx):
        self.table = table
        self.slices = self._convert_idx_to_slice(idx)

    def _convert_idx_to_slice(self, idx):
        if isinstance(idx, tuple):
            i, j = idx
        else:
            i, j = idx, slice(None)
        if isinstance(i, int):
            i = slice(i, i+1)
        if isinstance(j, int):
            j = slice(j, j+1)
        return i, j

    @property
    def data(self):
        return self.table.data[self.slices]
    @data.setter
    def data(self, value):
        self.table.data[self.slices] = value

    @property
    def size(self):
        return self.data.size

    @property
    def idx(self):
        start_i, stop_i, step_i = self.slices[0].indices(self.table.shape[0])
        start_j, stop_j, step_j = self.slices[1].indices(self.table.shape[1])
        return (start_i, start_j), (stop_i, stop_j)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def add_rule(self, position='below', trim_right=False, trim_left=False):
        """
        Adds a rule below or above the selected area of the table.

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

        if i not in self.table.rules:
            self.table.rules[i] = []
        self.table.rules[i].append(Rule(j_start, j_stop, r+l))

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
        self.table.add_package('multicol')
        self.table.add_package('multirow')

        self.data = '' # Erase old value
        multicell_params = (self.slices, v_align, h_align, v_shift)
        self.table.multicells.append(multicell_params) # Save position of multiple cells span

        self.table.data[self.idx[0]] = value

        return self

    def highlight(self, highlight='bold'):
        """
        Highlights the values inside the selected area.

        Args:
            highlight (str, either 'bold' or 'italic'): The value will be highlighted following this parameter.

        Returns self.
        """
        (i_start, j_start), (i_stop, j_stop) = self.idx
        for i in range(i_start, i_stop):
            for j in range(j_start, j_stop):
                self.table.highlights.append((i, j, highlight))

        return self

    def highlight_best(self, mode='high', highlight='bold', atol=5e-3, rtol=0):
        """
        Highlights the best value(s) inside the selected area of the table. Ignores text. If multiple values are equal to an absolute tolerance of atol and relative tolerance of rtol, both are highlighted.

        Args:
            mode (str, either 'high' or 'low'): Determines what is the best value.
            highlight (str, either 'bold' or 'italic'): The best value will be highlighted following this parameter.
            atol (float): Absolute tolerance when comparing best.
            atol (float): Relative tolerance when comparing best.

        Returns self.
        """
        best_idx = [(None, None)]
        if mode == 'high':
            best = -np.inf
            value_is_better_than_best = lambda value, best: value > best
        elif mode == 'low':
            best = np.inf
            value_is_better_than_best = lambda value, best: value < best

        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, (float, int)) and value_is_better_than_best(value, best):
                    best_idx = [(i, j)]
                    best = value
                elif isinstance(value, (float, int)) and np.isclose(value, best, rtol, atol):
                    best_idx.append((i, j))

        if best_idx[0][0] is None: return # No best have been found (i.e. no floats or ints in selected area)
        start_i, start_j = self.idx[0]
        for i, j in best_idx:
            self.table.highlights.append((i+start_i, j+start_j, highlight))

        return self

    def divide_cell(self, shape=(1,1), alignment='c', float_format='.2f'):
        """
        Divides the selected cell in another subtable. Useful for long title to manually cut for example.

        Args:
            See Table documentation.

        Returns a Table object.
        """
        if self.size > 1:
            raise RuntimeError('Invalid selected area. It should be of size 1.')

        subtable = Table(shape, alignment, float_format, as_float_env=False, bottom_rule=False, top_rule=False)
        self.data = subtable
        return subtable
