import os
from subprocess import DEVNULL, STDOUT, check_call

import numpy as np


class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename):
        self.filename = filename + '.tex'

    def save(self, tex):
        with open(self.filename, 'w', encoding='utf8') as file:
            file.write(tex)

    def _compile_to_pdf(self):
        check_call(['pdflatex', self.filename], stdout=DEVNULL, stderr=STDOUT)


class TexEnvironment:
    def __init__(self, env_name, *parameters, options=None, label_pos='top'):
        """
        Args:
            env_name (str): Name of the environment.
            parameters (tuple of str): Parameters of the environment, appended inside curly braces {}.
            options (tuple of str): Options to pass to the environment, appended inside brackets [].
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the environment.
        """
        self.env_name = env_name
        self.body = [] # List of Environments or texts
        self.head = '\\begin{{{env_name}}}'.format(env_name=env_name)
        self.tail = '\\end{{{env_name}}}'.format(env_name=env_name)
        if parameters:
            self.head += f"{{{','.join(parameters)}}}"
        if options:
            self.head += f"[{options}]"
        self.packages = {}
        self.label_pos = label_pos
        self.label = ''

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

    def _build(self):
        label = f"\label{{{self.env_name}:{self.label}}}"
        if self.label:
            if self.label_pos == 'top':
                self.head += '\n' + label
            else:
                self.tail = label + '\n' + self.tail

        for i in range(len(self.body)):
            text_or_env = self.body[i]
            if isinstance(text_or_env, TexEnvironment):
                text_or_env._build()
                self.body[i] = text_or_env.body
                self.packages.update(text_or_env.packages)
        first_line = f'\\begin{{{self.env_name}}}'

        self.body = [self.head] + self.body + [self.tail]
        self.body = '\n'.join(self.body)


class Document(TexEnvironment):
    """
    Tex document class.
    """
    def __init__(self, filename, doc_type, *options, **kwoptions):
        super().__init__('document')
        self.head = '\\begin{document}'
        self.tail = '\\end{document}'
        self.filename = filename
        self.file = TexFile(filename)

        options = list(options)
        for key, value in kwoptions.items():
            options.append(f"{key}={value}")
        options = '[' + ','.join(options) + ']'

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

    def build(self):
        super()._build()

        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            self.header.append(f"\\usepackage{options}{{{package}}}")
        self.header = '\n'.join(self.header)

        self.file.save(self.header + '\n' + self.body)
        self.file._compile_to_pdf()
