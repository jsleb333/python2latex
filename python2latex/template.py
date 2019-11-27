import subprocess, os, sys

from python2latex import TexFile, TexEnvironment, TexCommand, build

"""
TODO:
    - Document syntax for anchors
    - Parsing of packages, library and colors in preamble
"""


class Template:
    """
    Class that allows to insert TeX commands inside an already existing tex file and then compile it. Useful to make figures and tables with python2latex and insert them into your project without needing to copy and paste.
    """
    def __init__(self, filename, filepath='.'):
        """
        Args:
            filename (str): Name of the file without extension.
            filepath (str): Path where the files will be saved and compiled to pdf.
        """
        self.file = TexFile(filename, filepath)

        self.anchors = {}

    def _load_tex_file(self):
        """
        Returns the loaded tex file as a list of strings.
        """
        with open(self.file.path, 'r', encoding='utf8') as file:
            return [line.strip() for line in file]

    def _split_preamble(self, text):
        """
        Returns the preamble and the rest of the document.
        """
        for i, line in enumerate(text):
            if r'\begin{document}' in line:
                begin_document_line = i
                break
        return text[:begin_document_line], text[begin_document_line:]

    def _insert_tex_at_anchors(self, doc):
        anchors_position = {}
        for i, line in enumerate(doc):
            if line.startswith('%! python2latex-anchor'):
                _, anchor_name = line.replace(' ', '').split('=')
                anchors_position[anchor_name] = (i, None)

            if line.startswith('%! python2latex-end-anchor'):
                anchors_position[anchor_name] = (anchors_position[anchor_name][0], i)

        for anchor_name, (start, end) in anchors_position.items():
            if end:
                del doc[start+1:end+1]
            doc.insert(start+1, self.anchors[anchor_name])
            doc.insert(start+2, f'%! python2latex-end-anchor = {anchor_name}')

    def render(self):
        tex = self._load_tex_file()
        preamble, doc = self._split_preamble(tex)
        self._insert_tex_at_anchors(doc)
        self._update_preamble()
        self._save_file_to_disk()
        self._compile_to_pdf()
        self._show_output()
