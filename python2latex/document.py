import os

from python2latex import TexFile, TexEnvironment, TexCommand, build
from python2latex.utils import open_file_with_default_program


class Document(TexEnvironment):
    """
    Tex document class.
    Has a body, a preamble and a dict of packages updated recursively with other TexEnvironment nested inside the body.
    The 'build' method writes all text to a .tex file and compiles it to pdf.
    """
    def __init__(self, filename, filepath='.', doc_type='article', options=(), **kwoptions):
        r"""
        Args:
            filename (str): Name of the file without extension.
            filepath (str): Path where the files will be saved and compiled to pdf.
            doc_type (str): Any document type LaTeX supports, like 'article', 'standalone', etc.
            options (Union[Tuple[str], str, TexObject]): Any options that goes between brackets. See template further.
            kwoptions (keyword options of the document type): Options should be strings. The dict is converted to string
            when building to tex. See template below.

        The doc_type, options and kwoptions arguments will be compiled in the following way:
            \documentclass[*options, **kwoptions]{doc_type}
        """
        super().__init__('document')
        self.filename = filename
        self.filepath = filepath
        self.file = TexFile(filename, filepath)

        self.doc_class = TexCommand('documentclass',
                                    doc_type,
                                    options=options,
                                    options_pos='first',
                                    **kwoptions)

        self.add_package('inputenc', 'utf8')
        self.set_margins('2.5cm')

    def __repr__(self):
        return f'Document {self.filename}'

    def set_margins(self, margins='2.5cm', top=None, bottom=None, left=None, right=None):
        """
        Sets margins of the document. Default is 2.5cm on all sides.

        Args:
            margins (str): Default value for all sides.
            top, bottom, left, right (str, any valid LaTeX length): Overrides the 'margins' argument with the specified
            length.
        """
        top = top or margins
        bottom = bottom or margins
        left = left or margins
        right = right or margins

        self.add_package('geometry', top=top, bottom=bottom, left=left, right=right)

    def new_section(self, name, label=''):
        """
        Create a new LaTeX section.

        Args:
            name (str): Name of the section.
            label (str): Label of the section to refer to.
        """
        return self.new(Section(name, label=label))

    def build(self,
              save_to_disk=True,
              compile_to_pdf=True,
              show_pdf=True,
              delete_files=list(),
              build_from_dir='cwd'):
        r"""
        Builds the document to a tex file and optionally compiles it into tex and show the output pdf in the default pdf reader of the system.

        Args:
            save_to_disk (bool):
                If True, the built tex will be save to disk automatically. Else, one can recover the tex string from the return of the current method.
            compile_to_pdf (bool):
                If True, automatically call pdflatex to compile the generated tex file to pdf. Only used if 'save_to_disk' is True.
            show_pdf (bool):
                If True, the default pdf reader will be called to show the compiled pdf. This may not work well with non-read-only pdf viewer such as Acrobat Reader or Foxit Reader. Only used if 'save_to_disk' and 'compile_to_pdf' are True.
            delete_files (Union[str, Iterable[str]]):
                Extensions of the files to delete after compilation. By default no files saved on disk are deleted. Valid extensions are 'tex', 'aux', 'log' and 'pdf'. 'all' is also accepted and will delete everything except the pdf.
            build_from_dir (str, either 'source' or 'cwd'):
                Directory to build from. With the 'source' option, pdflatex will be called from the directory containing the TeX file, like this:
                    ~/some/path/to/tex_file> pdflatex './filename.tex'
                With the 'cwd' option, pdflatex will be called from the current working directory, like this:
                    ~/some/path/to/cwd> pdflatex 'filepath/filename.tex'
                This can be important if you include content in the TeX file, such as with the command \input{<path_to_some_file>}, where 'path_to_some_file' should be relative to the directory where pdflatex is called.

        Returns:
            The tex string of the file.
        """
        tex = super().build()

        tex = build(self.doc_class) + '\n' + self.build_preamble() + '\n' + tex
        if save_to_disk:
            self.file.save(tex)

            if compile_to_pdf:
                self.file.compile_to_pdf(build_from_dir=build_from_dir)

                if show_pdf:
                    open_file_with_default_program(self.filename, self.filepath)

                if isinstance(delete_files, str):
                    if delete_files == 'all':
                        delete_files = ['tex', 'aux', 'log']
                    else:
                        delete_files = [delete_files]

                for ext in delete_files:
                    if ext in ['tex', 'aux', 'log', 'pdf']:
                        os.remove(f'{self.filepath}/{self.filename}.{ext}')

        return tex


class Section(TexEnvironment):
    """
    Implements a LaTeX section.
    """
    def __init__(self, name, label=''):
        """
        Args:
            name (str): Name of the section.
            label (str): Label of the section to refer to.
        """
        super().__init__('section', name, label=label)

    def new_subsection(self, name, label=''):
        """
        Args:
            name (str): Name of the subsection.
            label (str): Label of the subsection to refer to.
        """
        return self.new(Subsection(name, label=label))


class Subsection(TexEnvironment):
    """
    Implements a LaTeX subsection.
    """
    def __init__(self, name, label=''):
        """
        Args:
            name (str): Name of the subsection.
            label (str): Label of the subsection to refer to.
        """
        super().__init__('subsection', name, label=label)

    def new_subsubsection(self, name, label=''):
        """
        Args:
            name (str): Name of the subsubsection.
            label (str): Label of the subsubsection to refer to.
        """
        return self.new(TexEnvironment('subsubsection', name, label=label))
