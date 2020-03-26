from inspect import cleandoc

from pytest import fixture

from python2latex.table import *


@fixture
def three_by_three_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:, :] = [[j * n_cols + i + 1 for i in range(n_cols)] for j in range(n_rows)]
    return table


class TestRule:
    def test_build_rule(self):
        rules = [(0, 10, ''), (1, 2, 'r'), (3, 4, 'l'), (5, 6, 'l{3pt}r{4pt}')]
        expected_values = [
            r'\cmidrule{1-10}', r'\cmidrule(r){2-2}', r'\cmidrule(l){4-4}', r'\cmidrule(l{3pt}r{4pt}){6-6}'
        ]
        for rule, expected_value in zip(rules, expected_values):
            assert expected_value == Rule(*rule).build()


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

    def test_add_rule_default(self):
        self.row_area.add_rule()
        self.small_area.add_rule()
        assert self.table.rules == {1: [Rule(0, 3, ''), Rule(1, 3, '')]}

    def test_add_rule_above(self):
        self.row_area.add_rule('above')
        assert self.table.rules == {0: [Rule(0, 3, '')]}

    def test_add_rule_trimmed(self):
        self.row_area.add_rule(trim_left=True)
        self.small_area.add_rule(trim_right=True)
        self.one_cell_area.add_rule(trim_left='1pt', trim_right='2pt')
        assert self.table.rules == {1: [Rule(0, 3, 'l'), Rule(1, 3, 'r')], 0: [Rule(0, 1, 'r{2pt}l{1pt}')]}

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

    def test_highlight(self):
        pass

    def test_highlight_best(self):
        pass

    def test_divide_cell(self):
        pass


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


def test_table_with_multirow():
    pass


def test_table_with_highlight():
    pass


def test_table_with_highlight_best():
    pass


def test_table_with_highlight_best_with_equalities():
    pass


def test_table_with_divide_cell():
    pass


def test_table_with_other_float_format():
    pass
