import os
from subprocess import DEVNULL, STDOUT, check_call

import numpy as np


class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename, filepath):
        self.filename = filename + '.tex'
        self.filepath = filepath

    def save(self, tex):
        os.makedirs(self.filepath, exist_ok=True)
        filename = os.path.join(self.filepath, self.filename)
        with open(filename, 'w', encoding='utf8') as file:
            file.write(tex)

    def _compile_to_pdf(self):
        os.chdir(self.filepath)
        check_call(['pdflatex', self.filename])#, stdout=DEVNULL, stderr=STDOUT)


class TexEnvironment:
    """
    Implements a basic TexEnvironment as
    \begin{env}
        ...
    \end{env}

    Allows recursive use of environment inside others.
    Add new environments with the method 'new' and add standard text with 'add_text'.
    Add LaTeX packages needed for this environment with 'add_package'.
    """
    def __init__(self, env_name, *parameters, options=(), label='', label_pos='top', **kwoptions):
        """
        Args:
            env_name (str): Name of the environment.
            parameters (tuple of str): Parameters of the environment, appended inside curly braces {}.
            options (tuple of str): Options to pass to the environment, appended inside brackets [].
            label (str): Label of the environment if needed.
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the environment.
        """
        self.env_name = env_name
        self.body = [] # List of Environments or texts
        self.head = '\\begin{{{env_name}}}'.format(env_name=env_name)
        self.tail = '\\end{{{env_name}}}'.format(env_name=env_name)

        self.parameters = parameters
        self.options = options if isinstance(options, tuple) else (options,)
        self.kwoptions = kwoptions
        self.packages = {}
        self.label_pos = label_pos
        self.label = label

    def add_package(self, package, *options, **kwoptions):
        options = f"[{','.join(options)}]" if options else ''
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = options

    def add_text(self, text):
        self.body.append(text)

    def new(self, env):
        self.body.append(env)
        return env

    def __repr__(self):
        return f'TexEnvironment {self.env_name}'

    def build(self):
        """
        Builds recursively the environments of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        if self.parameters:
            self.head += f"{{{', '.join(self.parameters)}}}"
        if self.options or self.kwoptions:
            kwoptions = ', '.join('='.join((k, str(v))) for k, v in self.kwoptions.items())
            options = ', '.join(self.options)
            if kwoptions and options:
                options += ', '
            self.head += f"[{options + kwoptions}]"

        tex = []
        label = f"\label{{{self.env_name}:{self.label}}}"
        if self.label:
            if self.label_pos == 'top':
                self.head += '\n' + label
            else:
                self.tail = label + '\n' + self.tail

        for text_or_env in self.body:
            if isinstance(text_or_env, TexEnvironment):
                built_env = text_or_env.build()
                tex.append(built_env)
                self.packages.update(text_or_env.packages)
            else:
                tex.append(text_or_env)

        tex = [self.head] + tex + [self.tail]
        return '\n'.join(tex)


class Document(TexEnvironment):
    """
    Tex document class.
    Has a body, a header and a dict of packages updated recursively with other TexEnvironment nested inside the body.
    The 'build' method writes all text to a .tex file and compiles it to pdf.
    """
<<<<<<< HEAD
    def __init__(self, filename, doc_type='article', filepath=os.getcwd(), options=(), **kwoptions):
=======
    def __init__(self, filename, doc_type='article', filepath='.', options=(), **kwoptions):
>>>>>>> master
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

    def set_margins(self, margins, top=None, bottom=None):
        self.margins = {'top':margins,
                         'bottom':margins,
                         'margin':margins}
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom

        self.packages['geometry'] = ','.join(key+'='+value for key, value in self.margins.items())

    def new_section(self, name, label=''):
        """
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
