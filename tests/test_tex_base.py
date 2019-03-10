import pytest

from py2tex.tex_base import TexObject


class TestTexObject:
    def setup(self):
        self.tex_obj = TexObject('DefaultTexObject')

    def test_init(self):
        assert self.tex_obj.name == 'DefaultTexObject'

    def test_add_text(self):
        self.tex_obj.add_text(r"This is raw \LaTeX")
        assert self.tex_obj.body == [r"This is raw \LaTeX"]

    def test_add_package_without_options(self):
        package_name = 'package'
        self.tex_obj.add_package(package_name)
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name] == ''

    def test_add_package_with_options(self):
        package_name = 'package'
        options = ('spam', 'egg')
        self.tex_obj.add_package(package_name, 'spam', 'egg', answer=42, question="We don't know")
        assert package_name in self.tex_obj.packages
        assert self.tex_obj.packages[package_name] == "[spam,egg,answer=42,question=We don't know]"

    def test_new(self):
        other_tex_obj = TexObject('Other')
        returned_object = self.tex_obj.new(other_tex_obj)
        assert returned_object is other_tex_obj
        assert self.tex_obj.body[0] is other_tex_obj

    def test_repr(self):
        assert repr(self.tex_obj) == 'TexObject DefaultTexObject'

    def test_build_empty(self):
        assert self.tex_obj.build() == ''

    def test_build_with_head_tail(self):
        tex_obj_with_head_tail = TexObject('obj_with_head_tail',
                                           head=[r'\begin{document}',r'\centering'],
                                           tail=r'\end{document}')
        assert tex_obj_with_head_tail.build() == '\\begin{document}\n\\centering\n\\end{document}'

    def test_build_with_label(self):
        tex_obj_label = TexObject('obj_with_label', head='head', tail='tail', label='some_label')
        tex_obj_label.add_text('some text')

        assert tex_obj_label.build() == 'head\n\\label{obj_with_label:some_label}\nsome text\ntail'
        tex_obj_label.label_pos = 'bottom'
        assert tex_obj_label.build() == 'head\nsome text\n\\label{obj_with_label:some_label}\ntail'
