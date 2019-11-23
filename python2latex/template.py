import subprocess, os, sys

from python2latex import TexFile, TexEnvironment, TexCommand, build


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
        self.filename = filename
        self.filepath = filepath

        self.anchors = {}

    def render(self):
        self._load_text()
        self._parse_text()
        self._insert_tex()
        self._update_preamble()
        self._save_file_to_disk()
        self._compile_to_pdf()
        self._show_output()
