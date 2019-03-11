import pytest
from pytest import fixture
from inspect import cleandoc

from py2tex import Table


@fixture
def three_by_three_table():
    n_rows, n_cols = 3, 3
    table = Table((n_rows, n_cols))
    table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
    return table


class TestTable:
    def setup(self):
        pass

    def test__build_rule(self):
        rules = [(0, 10, ''),
                 (1, 2, 'r'),
                 (3, 4, 'l'),
                 (5, 6, 'l{3pt}r{4pt}')]
        expected_values = [r'\cmidrule{1-10}',
                    r'\cmidrule(r){2-2}',
                    r'\cmidrule(l){4-4}',
                    r'\cmidrule(l{3pt}r{4pt}){6-6}']
        for rule, expected_value in zip(rules, expected_values):
            assert expected_value == Table()._build_rule(*rule)

    def test_standard_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols))
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
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

    def test_non_floating_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols), as_float_env=False)
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
        assert table.build() == cleandoc(r'''
            \begin{tabular}{ccc}
            \toprule
            1 & 2 & 3\\
            4 & 5 & 6\\
            7 & 8 & 9\\
            \bottomrule
            \end{tabular}
            ''')

    def test_captioned_labeled_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols), label='my_label')
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
        table.caption = 'My caption'
        assert table.build() == cleandoc(r'''
            \begin{table}[h!]
            \centering
            \caption{My caption}
            \label{table:my_label}
            \begin{tabular}{ccc}
            \toprule
            1 & 2 & 3\\
            4 & 5 & 6\\
            7 & 8 & 9\\
            \bottomrule
            \end{tabular}
            \end{table}
            ''')

    def test_no_rule_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False)
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
        assert table.build() == cleandoc(r'''
            \begin{tabular}{ccc}
            1 & 2 & 3\\
            4 & 5 & 6\\
            7 & 8 & 9\\
            \end{tabular}
            ''')

    def test_different_alignments_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False, alignment='r')
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
        table.alignment[1:] = ['l', 'p{3cm}']
        assert table.build() == cleandoc(r'''
            \begin{tabular}{rlp{3cm}}
            1 & 2 & 3\\
            4 & 5 & 6\\
            7 & 8 & 9\\
            \end{tabular}
            ''')

    def test_with_midrules_table(self):
        n_rows, n_cols = 3, 3
        table = Table((n_rows, n_cols), as_float_env=False, top_rule=False, bottom_rule=False)
        table[:,:] = [[j*n_cols + i+1 for i in range(n_cols)] for j in range(n_rows)]
        table[0].add_rule(trim_left=True)
        table[1,1:].add_rule('above', trim_right=True)
        table[2,1:2].add_rule(trim_left='1pt', trim_right='2pt')
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

    def test_table_with_multirow(self):
        pass
