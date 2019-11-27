import sys, os
import pytest
from inspect import cleandoc

from python2latex.template import Template
from python2latex.floating_environment import FloatingFigure

tex_test_file = {
    'text_file_for_new_template': cleandoc(
        r"""
        \documentclass[12pt]{article}
        \usepackage[margins=2cm]{geometry}
        \usepackage[french]{babel}
        \begin{document}
        \begin{section}{Section title}
        %! python2latex-anchor = figure1
        \end{section}
        \end{document}
        """
        ),
    'text_file_for_used_template': cleandoc(
        r"""
        \documentclass[12pt]{article}
        \usepackage[margins=2cm]{geometry}
        \usepackage[french]{babel}
        %! python2latex-preamble
        \usepackage{tikz}
        \begin{document}
        \begin{section}{Section title}
        %! python2latex-anchor = figure1
        something
        something
        %! python2latex-end-anchor = figure1
        \end{section}
        \end{document}
        """
        ),
}
filenames = list(tex_test_file.keys())
contents = list(tex_test_file.values())



class TestTemplate:
    def setup(self):
        for filename, filecontent in tex_test_file.items():
            with open(filename + '.tex', 'w') as file:
                file.write(filecontent)

    def teardown(self):
        for filename in tex_test_file:
            os.remove(filename + '.tex')

    def test_load_tex_file(self):
        template = Template(filenames[0])
        assert template._load_tex_file() == contents[0].split('\n')

    def test_split_preamble(self):
        preamble, doc = Template('test')._split_preamble(contents[0].split('\n'))
        assert preamble == ['\\documentclass[12pt]{article}',
                            '\\usepackage[margins=2cm]{geometry}',
                            '\\usepackage[french]{babel}']
        assert doc == [r'\begin{document}',
                       r'\begin{section}{Section title}',
                       r'%! python2latex-anchor = figure1',
                       r'\end{section}',
                       r'\end{document}']

    def test_insert_tex_at_anchors_for_new_template(self):
        template = Template(filenames[0])
        figure = FloatingFigure()
        template.anchors['figure1'] = figure

        tex = template._load_tex_file()
        preamble, doc = template._split_preamble(tex)
        template._insert_tex_at_anchors(doc)
        assert doc[3] is figure
        assert doc[4] == '%! python2latex-end-anchor = figure1'

    def test_insert_tex_at_anchors_for_used_template(self):
        template = Template(filenames[1])
        figure = FloatingFigure()
        template.anchors['figure1'] = figure

        tex = template._load_tex_file()
        preamble, doc = template._split_preamble(tex)
        template._insert_tex_at_anchors(doc)
        assert doc[3] is figure
        assert doc[4] == '%! python2latex-end-anchor = figure1'

    def test_update_preamble(self):
        template = Template(filenames[1])
        figure = FloatingFigure()
        figure.add_package('tikz')
        figure.add_package('babel', 'french')
        template.anchors['figure1'] = figure

        tex = template._load_tex_file()
        preamble, doc = template._split_preamble(tex)
        template._update_preamble(preamble)
        assert preamble[-2] == '%! python2latex-preamble'
        assert preamble[-1] == '\\usepackage{tikz}'
