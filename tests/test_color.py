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

    def test_color_models(self):
        colors = {
            'rgb': (.1, .2, .3),
            'cmy': (.1, .2, .3),
            'cmyk': (.1, .2, .3, .4),
            'hsb': (.1, .2, .3),
            'Hsb': (100, .2, .3),
            'tHsb': (100, .2, .3),
            'gray': (.1,),
            'RGB': (10, 20, 30),
            'HTML': ('2266FF',),
            'HSB': (80, 160, 240),
            'Gray': (10,),
            'wave': (500,),
        }
        for model, spec in colors.items():
            color = Color(*spec, color_name='spam', color_model=model)
            assert color.build() == 'spam'
            assert color.build_preamble() == f'\n\\definecolor{{spam}}{{{model}}}{{{",".join(map(str, spec))}}}'


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


class TestColorBox:
    def teardown_method(self, mtd):
        Color.color_count = 0

    def test_build(self):
        highlighted_text = colorbox('red', 'hello')
        assert highlighted_text.build() == '\\colorbox{red}{hello}'
        assert highlighted_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

        highlighted_text = colorbox(Color(1, 0, 0), 'hello')
        assert highlighted_text.build() == '\\colorbox{color1}{hello}'
        assert highlighted_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{color1}{rgb}{1,0,0}''')

        highlighted_text = colorbox(Color(1, 0, 0, color_name='my_color'), 'hello')
        assert highlighted_text.build() == '\\colorbox{my_color}{hello}'
        assert highlighted_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}''')

    def test_preamble_appears_in_document(self):
        doc = Document('test')
        highlighted_text = colorbox(Color(1, 0, 0, color_name='my_color'), 'hello')
        doc += highlighted_text
        assert doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}
            \begin{document}
            \colorbox{my_color}{hello}
            \end{document}''')

    def test_predefined_colors(self):
        highlighted_text = colorboxred('hello')
        assert highlighted_text.build() == '\\colorbox{red}{hello}'
        assert highlighted_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

        highlighted_text = colorboxOliveGreen('hello')
        assert highlighted_text.build() == '\\colorbox{OliveGreen}{hello}'
        assert highlighted_text.build_preamble() == '\\usepackage[dvipsnames]{xcolor}'

    def test_colorbox_callable(self):
        my_colorbox_callable = colorbox_callable(Color(1, 0, 0, color_name='my_color'))
        highlighted_text = my_colorbox_callable('hello')
        assert highlighted_text.build() == '\\colorbox{my_color}{hello}'
        assert highlighted_text.build_preamble() == cleandoc(r'''
            \usepackage[dvipsnames]{xcolor}
            \definecolor{my_color}{rgb}{1,0,0}''')
