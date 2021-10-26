import os
import shutil
from inspect import cleandoc

from pytest import fixture

from python2latex import TexEnvironment, Document, Section, Subsection


@fixture
def default_doc():
    return Document('Default')


class TestDocument:
    def setup(self):
        pass

    def test_set_margins(self, default_doc):
        default_doc.set_margins(margins='3cm')
        assert default_doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=3cm, bottom=3cm, left=3cm, right=3cm]{geometry}
            \begin{document}
            \end{document}''')
        default_doc.set_margins(top='1cm', bottom='2cm', left='4cm', right='5cm')
        assert default_doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=1cm, bottom=2cm, left=4cm, right=5cm]{geometry}
            \begin{document}
            \end{document}''')

    def test_repr(self, default_doc):
        assert repr(default_doc) == 'Document Default'

    def test_new_section(self, default_doc):
        sec = default_doc.new_section('Section name')
        assert default_doc.body[0] is sec
        assert isinstance(sec, Section)

    def test_build_default(self, default_doc):
        assert default_doc.build(False, False, False) == cleandoc(r'''
            \documentclass{article}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \begin{document}
            \end{document}''')

    def test_build_with_options(self):
        doc = Document('With options', doc_type='standalone', options=['12pt', 'Spam'], egg=42)
        assert doc.build(False, False, False) == cleandoc(r'''\documentclass[12pt, Spam, egg=42]{standalone}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \begin{document}
            \end{document}''')

    def test_build_with_body_and_packages(self):
        doc = Document('With options', doc_type='standalone', options=['12pt', 'Spam'], egg=42)
        doc.add_package('tikz')
        sec = doc.new_section('Section', label='Section')
        sec.add_text('Hey')
        assert doc.build(False, False, False) == cleandoc(r'''\documentclass[12pt, Spam, egg=42]{standalone}
            \usepackage[utf8]{inputenc}
            \usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
            \usepackage{tikz}
            \begin{document}
            \begin{section}{Section}
            \label{section:Section}
            Hey
            \end{section}
            \end{document}''')

    def test_build_with_relative_path_from_cwd(self):
        filepath = './some_doc_path/'
        doc_name = 'Doc name'
        doc = Document(doc_name, filepath=filepath)
        doc += 'Some text'
        try:
            doc.build(show_pdf=False, build_from_dir='cwd')
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
        finally:
            if os.path.exists(filepath): shutil.rmtree(filepath)

    def test_build_with_relative_path_from_source(self):
        filepath = './some_doc_path/'
        doc_name = 'Doc name'
        doc = Document(doc_name, filepath=filepath)
        doc += 'Some text'
        try:
            doc.build(show_pdf=False, build_from_dir='source')
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
        finally:
            if os.path.exists(filepath): shutil.rmtree(filepath)

    def test_deletes_files_all(self):
        filepath = './some_doc_path/'
        doc_name = 'doc_name'
        doc = Document(doc_name, filepath=filepath)
        doc += 'Some text'
        try:
            doc.build(show_pdf=False, delete_files='all')
            assert not os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
        finally:
            if os.path.exists(filepath): shutil.rmtree(filepath)

    def test_deletes_files_aux(self):
        filepath = './some_doc_path/'
        doc_name = 'doc_name'
        doc = Document(doc_name, filepath=filepath)
        doc += 'Some text'
        try:
            doc.build(show_pdf=False, delete_files='aux')
            assert not os.path.exists(filepath + doc_name + '.aux')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.log')
        finally:
            if os.path.exists(filepath): shutil.rmtree(filepath)

    def test_deletes_files_aux_and_log(self):
        filepath = './some_doc_path/'
        doc_name = 'doc_name'
        doc = Document(doc_name, filepath=filepath)
        doc += 'Some text'
        try:
            doc.build(show_pdf=False, delete_files=['aux', 'log'])
            assert not os.path.exists(filepath + doc_name + '.aux')
            assert not os.path.exists(filepath + doc_name + '.log')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(filepath + doc_name + '.tex')
        finally:
            if os.path.exists(filepath): shutil.rmtree(filepath)

class TestSection:
    def test_new_subsection(self):
        sec = Section('Section name')
        sub = sec.new_subsection('Subsection name')
        assert sec.body[0] is sub
        assert isinstance(sub, Subsection)


class TestSubsection:
    def test_new_subsubsection(self):
        sub = Subsection('Section name')
        subsub = sub.new_subsubsection('Subsection name')
        assert sub.body[0] is subsub
        assert isinstance(subsub, TexEnvironment)
