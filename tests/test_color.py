from inspect import cleandoc

from python2latex import Document
from python2latex.color import *


class TestColor:
    def teardown_method(self, mtd):
        Color.color_count = 0

    def test_init(self):
        color = Color(3, 4, 5, color_name='spam')
        assert color.build() == 'spam'
        assert color.build_preamble() == '\n\\definecolor{spam}{rgb}{3,4,5}'

    def test_without_color_name(self):
        color = Color(3, 4, 5)
        assert color.build() == 'color1'
        color2 = Color(3, 4, 6)
        assert color2.build() == 'color2'

    def test_preamble_appears_in_document(self):
        doc = Document('test')
        color = Color(1, 2, 3)
        command = TexCommand('somecommand', 'param', options=[color])
        doc += command
        assert doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \definecolor{color1}{rgb}{1,2,3}
            \begin{document}
            \somecommand{param}[color1]
            \end{document}''')



class TestTextColor:
    def teardown_method(self, mtd):
        Color.color_count = 0

    def test_build(self):
        colored_text = textcolor('red', 'hello')
        assert colored_text.build() == '\\textcolor{red}{hello}'
        assert colored_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

        colored_text = textcolor(Color(1, 0, 0), 'hello')
        assert colored_text.build() == '\\textcolor{color1}{hello}'
        assert colored_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{color1}{rgb}{1,0,0}''')

        colored_text = textcolor(Color(1, 0, 0, color_name='my_color'), 'hello')
        assert colored_text.build() == '\\textcolor{my_color}{hello}'
        assert colored_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}''')

    def test_preamble_appears_in_document(self):
        doc = Document('test')
        colored_text = textcolor(Color(1, 0, 0, color_name='my_color'), 'hello')
        doc += colored_text
        assert doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}
            \begin{document}
            \textcolor{my_color}{hello}
            \end{document}''')

    def test_predefined_colors(self):
        colored_text = textred('hello')
        assert colored_text.build() == '\\textcolor{red}{hello}'
        assert colored_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

        colored_text = textOliveGreen('hello')
        assert colored_text.build() == '\\textcolor{OliveGreen}{hello}'
        assert colored_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

    def test_textcolor_callable(self):
        my_color_callable = textcolor_callable(Color(1, 0, 0, color_name='my_color'))
        colored_text = my_color_callable('hello')
        assert colored_text.build() == '\\textcolor{my_color}{hello}'
        assert colored_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}''')
