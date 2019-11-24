import sys, os
import pytest
from inspect import cleandoc

from python2latex.template import Template

tex_test_file_content = cleandoc(
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
)
tex_test_filename = 'test_file_for_template'

def setup():
    with open(tex_test_filename + '.tex', 'w') as file:
        file.write(tex_test_file_content)

# def teardown():
#     os.remove(tex_test_filename)


class TestTemplate:
    def test_load_tex_file(self):
        template = Template(tex_test_filename)
        assert template._load_text() == tex_test_file_content.split('\n')

    def test_parse_tex_file(self):
        pass

