from py2tex import TexFile, TexEnvironment


class Document(TexEnvironment):
    """
    Tex document class.
    Has a body, a header and a dict of packages updated recursively with other TexEnvironment nested inside the body.
    The 'build' method writes all text to a .tex file and compiles it to pdf.
    """
    def __init__(self, filename, filepath='.', doc_type='article', options=(), **kwoptions):
        """
        Args:
            filename (str): Name of the file without extension.
            filepath (str): Path where the files will be saved and compiled to pdf.
            doc_type (str): Any document type LaTeX supports, like 'article', 'standalone', etc.
            options (tuple of str): Any options that goes between brackets. See template further.
            kwoptions (keyword options of the document type): Options should be strings. The dict is converted to string when building to tex. See template below.

        The doc_type, options and kwoptions arguments will be compiled in the following way:
            \documentclass[*options*, *kwoptions*]{doc_type}
        """
        super().__init__('document')
        self.filename = filename
        self.file = TexFile(filename, filepath)

        options = list(options)
        for key, value in kwoptions.items():
            options.append(f"{key}={value}")
        options = '[' + ', '.join(options) + ']'

        self.header = [f"\documentclass{options}{{{doc_type}}}"]

        self.packages = {'inputenc':'utf8',
                         'geometry':''}
        self.set_margins('2.5cm')

    def __repr__(self):
        return f'Document {self.filename}'

    def set_margins(self, margins='2.5cm', top=None, bottom=None, left=None, right=None):
        """
        Sets margins of the document. Default is 2.5cm on all sides.

        Args:
            margins (str): Default value for all sides.
            top, bottom, left, right (str, any valid LaTeX length): Overrides the 'margins' argument with the specified length.
        """
        self.margins = {'top':margins,
                         'bottom':margins,
                         'left':margins,
                         'right':margins}
        if top: self.margins['top'] = top
        if bottom: self.margins['bottom'] = bottom
        if left: self.margins['left'] = left
        if right: self.margins['right'] = right

        self.packages['geometry'] = ','.join(key+'='+value for key, value in self.margins.items())

    def new_section(self, name, label=''):
        """
        Create a new LaTeX section.

        Args:
            name (str): Name of the section.
            label (str): Label of the section to refer to.
        """
        return self.new(Section(name, label=label))

    def build(self, save_to_disk=True, compile_to_pdf=True):
        tex = super().build()

        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            self.header.append(f"\\usepackage{options}{{{package}}}")
        self.header = '\n'.join(self.header)

        tex = self.header + '\n' + tex
        if save_to_disk:
            self.file.save(tex)

        if compile_to_pdf:
            self.file.save(tex)
            self.file._compile_to_pdf()
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
