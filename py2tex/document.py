import os
from subprocess import DEVNULL, STDOUT, check_call

import numpy as np


class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename):
        self.filename = filename + '.tex'

    def save(self, tex):
        with open(self.filename, 'w', encoding='utf8') as file:
            file.write(tex)

    def _compile_to_pdf(self):
        check_call(['pdflatex', self.filename], stdout=DEVNULL, stderr=STDOUT)


class TexEnvironment:
    def __init__(self, env_name, *parameters, options=None, label_pos='top', parent_doc=None):
        """
        Args:
            env_name (str): Name of the environment.
            parameters (tuple of str): Parameters of the environment, appended inside curly braces {}.
            options (tuple of str): Options to pass to the environment, appended inside brackets [].
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the environment.
            parent_doc (Document object): Parent document of the environment. Used mainly to be able to add packages.
        """
        self.env_name = env_name
        self.body = [] # List of Environments or texts
        self.head = '\\begin{{{env_name}}}'.format(env_name=env_name)
        self.tail = '\\end{{{env_name}}}'.format(env_name=env_name)
        if parameters:
            self.head += f"{{{','.join(parameters)}}}"
        if options:
            self.head += f"[{options}]"
        self.parent_doc = parent_doc
        self.label_pos = label_pos
        self.label = ''

    def add_text(self, text):
        self.body.append(text)

    def new_environment(self, env_name, *parameters, options=None):
        env = TexEnvironment(env_name, *parameters, options=None, parent_doc=self.parent_doc)
        self.body.append(env)
        return env

    def new_table(self, *parameters, position='h!', **options):
        table = Table(*parameters, position, parent_doc=self.parent_doc, **options)
        self.body.append(table)
        return table

    def __repr__(self):
        return f'TexEnvironment {self.env_name}'

    def _build(self):
        label = f"\label{{{self.env_name}:{self.label}}}"
        if self.label:
            if self.label_pos == 'top':
                self.head += '\n' + label
            else:
                self.tail = label + '\n' + self.tail

        for i in range(len(self.body)):
            line = self.body[i]
            if isinstance(line, TexEnvironment):
                line._build()
                self.body[i] = line.body
        first_line = f'\\begin{{{self.env_name}}}'

        self.body = [self.head] + self.body + [self.tail]
        self.body = '\n'.join(self.body)


class Document(TexEnvironment):
    """
    Tex document class.
    """
    def __init__(self, filename, doc_type, *options, **kwoptions):
        super().__init__('document')
        self.head = '\\begin{document}'
        self.tail = '\\end{document}'
        self.filename = filename
        self.file = TexFile(filename)
        self.parent_doc = self

        options = list(options)
        for key, value in kwoptions.items():
            options.append(f"{key}={value}")
        options = '[' + ','.join(options) + ']'

        self.header = [f"\documentclass{options}{{{doc_type}}}"]

        self.packages = {'inputenc':'utf8',
                         'geometry':''}
        self.set_margins('2.5cm')

    def __repr__(self):
        return f'Document {self.filename}'

    def add_package(self, package, *options, **kwoptions):
        options = f"[{','.join(options)}]" if options else ''
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = options

    def set_margins(self, margins, top=None, bottom=None):
        self.margins = {'top':margins,
                         'bottom':margins,
                         'margin':margins}
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom

        self.packages['geometry'] = ','.join(key+'='+value for key, value in self.margins.items())

    def build(self):
        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            self.header.append(f"\\usepackage{options}{{{package}}}")
        self.header = '\n'.join(self.header)

        super()._build()
        self.file.save(self.header + '\n' + self.body)
        self.file._compile_to_pdf()


class Table(TexEnvironment):
    """

    """
    def __init__(self, position='h!', shape=(1,1), alignment='c', float_format='.2f', **kwargs):
        """
        Args:
            position (str, either 'h', 't', 'b', with optional '!'): position of the float. Default is 't'. Combinaisons of letters allow more flexibility.
            kwargs: See TexEnvironment keyword arguments.
            others: See Tabular arguments.
        """
        super().__init__('table', options=position, label_pos='bottom', **kwargs)
        self.head += '\n\centering'
        self.tabular = Tabular(shape, alignment, float_format, **kwargs)
        self.body = [self.tabular]
        self.caption = ''

    def __getitem__(self, idx):
        return self.tabular[idx]

    def __setitem__(self, idx, value):
        self.tabular[idx] = value

    def add_rule(self, *args, **kwargs):
        self.tabular.add_rule(*args, **kwargs)

    def highlight_best(self, *args, **kwargs):
        self.tabular.highlight_best(*args, **kwargs)

    def _build(self):
        if self.caption:
            self.body.append(f"\caption{{{self.caption}}}")
        super()._build()


class Tabular(TexEnvironment):
    """
    Implements the 'tabular' environment from the package 'booktabs'.
    """
    def __init__(self, shape=(1,1), alignment='c', float_format='.2f', **kwargs):
        """
        Args:
            shape (tuple of 2 ints):
            alignment (str, either 'c', 'r', or 'l'):
            float_format (str): Standard Python float formating available.
            kwargs: See TexEnvironment keyword arguments.
        """
        super().__init__('tabular', **kwargs)
        self.parent_doc.add_package('booktabs')

        self.shape = shape
        self.alignment = np.array([alignment]*shape[1], dtype=str)
        self.float_format = float_format
        self.data = np.full(shape, '', dtype=object)
        self.rules = {}
        self.multicells = []
        self.highlights = []

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        if isinstance(idx, tuple):
            i, j = idx
        else:
            i, j = idx, slice(None)

        if isinstance(value, (str, int, float)) and (isinstance(i, slice) or isinstance(j, slice)):
            # There are multirows or multicolumns to treat
            self.parent_doc.add_package('multicol')
            self.parent_doc.add_package('multirow')
            self.data[i,j] = '' # Erase old value
            self.multicells.append((i,j)) # Save position of multiple cells span
            if isinstance(i, slice):
                i, stop, end = i.indices(self.shape[0])
            if isinstance(j, slice):
                j, stop, end = j.indices(self.shape[1])

            self.data[i,j] = value # Top left corner of slice contains the value
        else:
            self.data[idx] = value

    def highlight_best(self, rows=None, cols=None, mode='high', highlight='bold'):
        """
        Args:
            rows (int or tuple of 2 ints or None or slice): Start and stop of the rows of the region of interest. If None, all the rows are selected.
            cols (int or tuple of 2 ints or None or slice): Start and stop of the columns of the region of interest. If None, all the columns are selected.
            mode (str, either 'high' or 'low'): Determines what is the best value.
            highlight (str, either 'bold' or 'italic'): The best value will be highlighted following this parameter.
        """
        if rows is None:
            rows = slice(slice(None).indices(self.shape[0]))
        if cols is None:
            cols = slice(slice(None).indices(self.shape[1]))

        if isinstance(rows, int):
            rows = slice(rows, rows+1)
        if isinstance(cols, int):
            cols = slice(cols, cols+1)

        if isinstance(rows, tuple):
            rows = slice(*rows)
        if isinstance(cols, tuple):
            cols = slice(*cols)

        if mode == 'high':
            idx = np.argmax(self.data[rows, cols], axis=None)
        elif mode == 'low':
            idx = np.argmin(self.data[rows, cols], axis=None)

        i, j = np.unravel_index(idx, self.data[rows, cols].shape)
        i += rows.start
        j += cols.start
        self.highlights.append((i,j,highlight))

    def add_rule(self, row, col_start=None, col_end=None, trim_right=False, trim_left=False):
        """
        Args:
            row (int): Row number under which the rule will be placed.
            col_start, col_end (int or None): Columns from which the rule will stretch. Standard slicing indexing from Python is used (first index is 0, last is excluded, not the same as LaTeX). If both are None (default) and both trim are False, the rule will go all the way across and will be a standard "\midrule". Else, the "\cmidrule" command is used.
            trim_left (bool or str): Whether to trim the left end of the rule or not. If True, default trim length is used ('.5em'). If a string, can be any valid LaTeX distance.
            trim_right (bool or str): Same a trim_left, but for the right end.
        """
        r = 'r' if trim_right else ''
        if isinstance(trim_right, str):
            r += f"{{{trim_right}}}"
        l = 'l' if trim_left else ''
        if isinstance(trim_left, str):
            l += f"{{{trim_left}}}"
        self.rules[row] = (col_start, col_end, r+l)

    def _build_rule(self, start, end, trim):
        if start is None and end is None and not trim:
            rule = "\midrule"
        else:
            rule = "\cmidrule"
            if trim:
                rule += f"({trim})"
            start, end, step = slice(start, end).indices(self.shape[1])
            rule += f"{{{start+1}-{end}}}"
        return rule

    def _apply_multicells(self, table_format):
        # Applying multicells
        for slice_i, slice_j in self.multicells:
            if isinstance(slice_j, slice):
                start_j, stop_j, step = slice_j.indices(self.shape[1])
            else:
                start_j, stop_j = slice_j, slice_j+1
            if isinstance(slice_i, slice):
                start_i, stop_i, step = slice_i.indices(self.shape[1])
            else:
                start_i, stop_i = slice_i, slice_i+1

            table_format[start_i, slice(start_j, stop_j-1)] = ''
            cell_shape = table_format[slice_i, slice_j].shape

            if isinstance(slice_i, int):
                self.data[start_i, start_j] = f"\multicolumn{{{cell_shape[0]}}}{{{self.alignment[start_j]}}}{{{self.data[start_i, start_j]}}}"
            else:
                self.data[start_i, start_j] = f"\multirow{{{cell_shape[0]}}}{{*}}{{{self.data[start_i, start_j]}}}"

            if isinstance(slice_j, slice) and isinstance(slice_i, slice):
                self.data[start_i, start_j] = f"\multicolumn{{{cell_shape[1]}}}{{{self.alignment[start_j]}}}{{{self.data[start_i, start_j]}}}"

        return table_format

    def _build(self):
        row, col = self.data.shape
        self.head += f"{{{''.join(self.alignment)}}}\n\\toprule"
        self.tail = '\\bottomrule\n' + self.tail

        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, float):
                    entry = f'{{value:{self.float_format}}}'.format(value=value)
                else:
                    entry = str(value)
                self.data[i,j] = entry

        for i, j, highlight in self.highlights:
            if highlight == 'bold':
                command = "\\textbf{{{0}}}"
            elif highlight == 'italic':
                command = "\\textit{{{0}}}"
            self.data[i,j] = command.format(self.data[i,j])

        table_format = np.array([[' & ']*(self.shape[1]-1) + ['\\\\']]*self.shape[0], dtype=str)
        table_format = self._apply_multicells(table_format)
        for i, (row, row_format) in enumerate(zip(self.data, table_format)):
            self.body.append(''.join(item for pair in zip(row, row_format) for item in pair))
            if i in self.rules:
                rule = self._build_rule(*self.rules[i])
                self.body.append(rule)

        super()._build()


if __name__ == "__main__":
    doc = Document('Test', 'article', '12pt')

    sec = doc.new_environment('section', 'Testing tables')
    sec.label = 'tables_test'
    sec.add_text("This section tests tables.")

    col = 4
    row = 4
    data = np.array([[np.random.rand() for i in range(j,j+col)] for j in range(1, col*row, col)])

    table = sec.new_table(shape=(row+1, col+1), alignment='c', float_format='.2f')
    table[1:,1:] = data
    table[0,1:] = 'Title'
    table[1:,0] = 'Types'
    table[2:4,2:4] = 'test'
    table.add_rule(0, 1, trim_left=True, trim_right='1em')
    table.label = 'test'
    table.caption = 'test'

    table.highlight_best(1, (1,5), 'low', 'bold')
    table.highlight_best(4, (1,5), 'low', 'bold')
    table.highlight_best((1,5), 1, 'high', 'italic')
    table.highlight_best((1,5), 4, 'high', 'italic')

    doc.build()
    # print(doc.body)
