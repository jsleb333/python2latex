from inspect import cleandoc

from pytest import fixture

from python2latex.table import *
from python2latex.tex_base import bold, italic


@fixture
def three_by_three_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    return table

@fixture
def three_by_three_tabular():
    n_rows, n_cols = 3, 3
    table = Tabular((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    return table


class TestTable:
    def test_getitem(self, three_by_three_table):
        assert isinstance(three_by_three_table[:, :], SelectedArea)

    def test_setitem(self, three_by_three_table):
        three_by_three_table[0, 0] = 10
        three_by_three_table[1] = 'Spam'
        three_by_three_table[2, 1:2] = 'Egg'
        assert three_by_three_table.data[0, 0] == 10
        assert three_by_three_table.data[1, 0] == 'Spam'
        assert three_by_three_table.data[2, 1] == 'Egg'


class TestTabular:
    def test_getitem(self, three_by_three_tabular):
        assert isinstance(three_by_three_tabular[:, :], SelectedArea)

    def test_setitem(self, three_by_three_tabular):
        three_by_three_tabular[0, 0] = 10
        three_by_three_tabular[1] = 'Spam'
        three_by_three_tabular[2, 1:2] = 'Egg'
        assert three_by_three_tabular.data[0, 0] == 10
        assert three_by_three_tabular.data[1, 0] == 'Spam'
        assert three_by_three_tabular.data[2, 1] == 'Egg'

    def test_apply_command(self, three_by_three_tabular):
        three_by_three_tabular[0:2,1:3].apply_command(bold)
        three_by_three_tabular[0:2,1:3].apply_command(lambda content: content + ' test')
        assert three_by_three_tabular._apply_commands(0, 1, '2') == r"\textbf{2} test"

    def test_format_number_default_float(self, three_by_three_tabular):
        assert three_by_three_tabular._format_number(0, 0, .1) == '0.10'

    def test_format_number_default_int(self, three_by_three_tabular):
        assert three_by_three_tabular._format_number(0, 0, 100) == '100'

    def test_format_number_custom_format_spec(self, three_by_three_tabular):
        three_by_three_tabular[0, 0].format_spec('.3f')
        assert three_by_three_tabular._format_number(0, 0, .1) == '0.100'
        three_by_three_tabular[0, 1].format_spec('.3e')
        assert three_by_three_tabular._format_number(0, 1, 12345.0) == '1.234e+04'

    def test_format_number_decimal_separator(self, three_by_three_tabular):
        three_by_three_tabular.decimal_separator = ','
        assert three_by_three_tabular._format_number(0, 0, .1) == '0,10'

    def test_apply_multicells_multicolumn(self, three_by_three_tabular):
        three_by_three_tabular[0, 0:2].multicell('content')
        tex_array_format = np.array([[' & ']*2 + [r'\\']]*3)
        tex_array = np.full_like(three_by_three_tabular.data, '', dtype=object)

        for i, row in enumerate(three_by_three_tabular.data):
            for j, content in enumerate(row):
                tex_array[i, j] = str(content)

        three_by_three_tabular._apply_multicells(tex_array, tex_array_format)

        assert isinstance(tex_array[0, 0], multicolumn)
        assert tex_array_format[0, 0] == ''

    def test_apply_multicells_multirow(self, three_by_three_tabular):
        three_by_three_tabular[0:2, 0].multicell('content')
        tex_array_format = np.array([[' & ']*2 + [r'\\']]*3)
        tex_array = np.full_like(three_by_three_tabular.data, '', dtype=object)

        for i, row in enumerate(three_by_three_tabular.data):
            for j, content in enumerate(row):
                tex_array[i, j] = str(content)

        three_by_three_tabular._apply_multicells(tex_array, tex_array_format)

        assert isinstance(tex_array[0, 0], multirow)
        assert tex_array_format[0, 0] == ' & '


class TestSelectedArea:
    def setup(self):
        n_rows, n_cols = 3, 3
        self.table = Table((n_rows, n_cols))
        self.table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
        self.whole_table_area = self.table[:, :]
        self.row_area = self.table[1]
        self.col_area = self.table[:, 1]
        self.small_area = self.table[0:2, 1:3]
        self.one_cell_area = self.table[0, 0]

    def test_convert_idx_to_slice(self):
        indices = [
            (1, 2),
            (slice(None), 2),
            (slice(None), slice(None)),
            (1, slice(None)),
            (slice(1, 3)),
        ]
        expected_values = [
            (slice(1, 2), slice(2, 3)),
            (slice(None), slice(2, 3)),
            (slice(None), slice(None)),
            (slice(1, 2), slice(None)),
            (slice(1, 3), slice(None)),
        ]
        for idx, expected_value in zip(indices, expected_values):
            assert self.row_area._convert_idx_to_slice(idx) == expected_value

    def test_idx(self):
        assert self.whole_table_area.idx == ((0, 0), (3, 3))
        assert self.row_area.idx == ((1, 0), (2, 3))
        assert self.col_area.idx == ((0, 1), (3, 2))
        assert self.small_area.idx == ((0, 1), (2, 3))
        assert self.one_cell_area.idx == ((0, 0), (1, 1))

    def test_format_spec(self):
        self.one_cell_area.format_spec('3e')
        assert self.table.formats_spec[0, 0] == '3e'

    def test_add_rule_default(self):
        self.row_area.add_rule()
        self.small_area.add_rule()
        assert self.table.rules == {1: [midrule(), cmidrule(1, 3, '')]}

    def test_add_rule_above(self):
        self.row_area.add_rule('above')
        assert self.table.rules == {0: [midrule()]}

    def test_add_rule_trimmed(self):
        self.row_area.add_rule(trim_left=True)
        self.small_area.add_rule(trim_right=True)
        self.one_cell_area.add_rule(trim_left='1pt', trim_right='2pt')
        assert self.table.rules == {1: [cmidrule(0, 3, 'l'), cmidrule(1, 3, 'r')], 0: [cmidrule(0, 1, 'r{2pt}l{1pt}')]}

    def test_multicell_default(self):
        self.whole_table_area.multicell('whole table')
        for i, row in enumerate(self.table.data):
            for j, value in enumerate(row):
                if (i, j) == (0, 0):
                    assert value == 'whole table'
                else:
                    assert value == ''
        assert self.table.multicells == [((slice(None), slice(None)), '*', 'c', None)]

    def test_multicell_with_options(self):
        self.small_area.multicell('small', v_align='t', h_align='r', v_shift='2pt')
        for i, row in enumerate(self.table.data):
            for j, value in enumerate(row):
                if 0 <= i < 2 and 1 <= j < 3:
                    if (i, j) == (0, 1):
                        assert value == 'small'
                    else:
                        assert value == ''
        assert self.table.multicells == [((slice(0, 2), slice(1, 3)), 't', 'r', '2pt')]

    def test_apply_command_stores_commands(self):
        boldmath = lambda content: f'\\mathbf{{{content}}}'
        mathmode = lambda content: f'${content}$'
        self.small_area.apply_command(boldmath)
        self.small_area.apply_command(mathmode)
        assert self.table.commands[1, 2] == [boldmath, mathmode]

    def test_highlight_best_default(self):
        self.small_area.highlight_best()
        assert self.table.commands[1, 2] == [bold]

    def test_highlight_best_min_mode(self):
        self.small_area.highlight_best(mode='min')
        assert self.table.commands[0, 1] == [bold]

    def test_highlight_best_and_not_best(self):
        self.small_area.highlight_best(not_best=italic)
        assert self.table.commands[1, 2] == [bold]
        assert self.table.commands[0, 1] == [italic]
        assert self.table.commands[0, 2] == [italic]
        assert self.table.commands[1, 1] == [italic]

    def test_highlight_best_with_tolerance(self):
        self.small_area.highlight_best(atol=1)
        assert self.table.commands[1, 2] == [bold]
        assert self.table.commands[1, 1] == [bold]

    def test_divide_cell(self):
        self.table[0, 0].divide_cell((2, 1))
        assert isinstance(self.table.data[0, 0], Tabular)
        self.table.build()

    def test_divide_cell_carry_cell_format(self):
        self.table[0, 0].format_spec('e')
        self.table[0, 0].divide_cell((2, 1))
        assert (self.table.data[0, 0].formats_spec == np.array([['e', 'e']])).all()


class Testcmidrule:
    def test_build_cmidrule(self):
        rules = [(0, 10, ''), (1, 2, 'r'), (3, 4, 'l'), (5, 6, 'l{3pt}r{4pt}')]
        expected_values = [
            r'\cmidrule{1-10}', r'\cmidrule(r){2-2}', r'\cmidrule(l){4-4}', r'\cmidrule(l{3pt}r{4pt}){6-6}'
        ]
        for rule, expected_value in zip(rules, expected_values):
            assert expected_value == cmidrule(*rule).build()


class Testmulticolumn:
    def test_build_multicolumn(self):
        assert multicolumn(3, 'c', 'content').build() == r"\multicolumn{3}{c}{content}"


class Testmultirow:
    def test_build_multirow(self):
        assert multirow(3, '*', '1pt', 'content').build() == r"\multirow{3}{*}[1pt]{content}"


# General Table build tests
def test_standard_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        1 & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_non_floating_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), as_float_env=False)
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    assert table.build() == cleandoc(r'''
        \begin{tabular}{ccc}
        \toprule
        1 & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        ''')


def test_captioned_labeled_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), label='my_label')
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table.caption = 'My caption'
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \caption{My caption}
        \label{table:my_label}
        \vspace{6pt}
        \begin{tabular}{ccc}
        \toprule
        1 & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_no_rule_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False)
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    assert table.build() == cleandoc(r'''
        \begin{tabular}{ccc}
        1 & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \end{tabular}
        ''')


def test_different_alignments_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False, alignment='r')
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table.alignment[1:] = ['l', 'p{3cm}']
    assert table.build() == cleandoc(r'''
        \begin{tabular}{rlp{3cm}}
        1 & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \end{tabular}
        ''')


def test_with_midrules_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False)
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table[0].add_rule(trim_left=True)
    table[1, 1:].add_rule('above', trim_right=True)
    table[2, 1:2].add_rule(trim_left='1pt', trim_right='2pt')
    assert table.build() == cleandoc(r'''
        \begin{tabular}{ccc}
        1 & 2 & 3\\
        \cmidrule(l){1-3}
        \cmidrule(r){2-3}
        4 & 5 & 6\\
        7 & 8 & 9\\
        \cmidrule(r{2pt}l{1pt}){2-2}
        \end{tabular}
        ''')


def test_table_with_int_format():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), int_format='.0e')
    table[:, :] = np.array([[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)])*1000
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        1e+03 & 2e+03 & 3e+03\\
        4e+03 & 5e+03 & 6e+03\\
        7e+03 & 8e+03 & 9e+03\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_float_format():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols), float_format='.1f')
    table[:, :] = np.array([[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)])/10
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        0.1 & 0.2 & 0.3\\
        0.4 & 0.5 & 0.6\\
        0.7 & 0.8 & 0.9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_ints_and_floats():
    n_rows, n_cols = 2, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[.1,.2,.3],[4,5,6]]
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        0.10 & 0.20 & 0.30\\
        4 & 5 & 6\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_int_and_float_formats_changed():
    n_rows, n_cols = 2, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[.1,.2,.3],[4,5,6]]
    table[0,0].format_spec('.3f')
    table[1,0:2].format_spec('.0e')
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        0.100 & 0.20 & 0.30\\
        4e+00 & 5e+00 & 6\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_divide_cell():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table[0, 0].divide_cell((2, 1))[:] = [['long'], ['title']]
    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        \begin{tabular}{c}
        long\\
        title\\
        \end{tabular} & 2 & 3\\
        4 & 5 & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_multicells():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table[0:2, 0:2].multicell('content', v_shift='2pt')

    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        \multicolumn{2}{c}{\multirow{2}{*}[2pt]{content}} & 3\\
         &  & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')


def test_table_with_highlight_best():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    table[0:2, 0:2].highlight_best(not_best=italic, atol=1)

    assert table.build() == cleandoc(r'''
        \begin{table}[h!]
        \centering
        \begin{tabular}{ccc}
        \toprule
        \textit{1} & \textit{2} & 3\\
        \textbf{4} & \textbf{5} & 6\\
        7 & 8 & 9\\
        \bottomrule
        \end{tabular}
        \end{table}
        ''')
