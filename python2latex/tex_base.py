import os
from subprocess import DEVNULL, STDOUT, check_call


def build(obj, parent=None):
    """
    Safely builds the object by calling its method 'build' only if 'obj' is not a string. If a parent is passed, all packages and preamble lines needed to the object will be added to the packages and preamble of the parent.
    """
    if isinstance(obj, TexObject):
        built_obj = obj.build()
        if parent:
            for package_name, package in obj.packages.items():
                parent.add_package(package_name, *package.options, **package.kwoptions)
            for line in obj.preamble:
                parent.add_to_preamble(line)
        return built_obj
    else:
        return str(obj)


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
        # os.chdir(self.filepath)
        check_call(['pdflatex', '-halt-on-error',
                    '--output-directory', self.filepath,
                    self.filepath + '/' + self.filename],
                   stdout=DEVNULL, stderr=STDOUT)


class TexObject:
    """
    Implements an abstract Tex object.
    Provides a 'add_package' method to add packages needed for this object.
    Inherited classes should redefine the 'build' method.
    """
    def __init__(self, obj_name):
        """
        Args:
            obj_name (str): Name of the object.
        """
        self.name = obj_name

        self.packages = {}
        self.preamble = []

    def add_package(self, package, *options, **kwoptions):
        """
        Add a package to the preamble. If the package had already been added, the options are updated.

        Args:
            package (str): The package name.
            options (tuple of str): Options to pass to the package in brackets.
            kwoptions (dict of str): Keyword options to pass to the package in brackets.
        """
        if not package in self.packages:
            self.packages[package] = Package(package, *options, **kwoptions)
        else:
            options = set(options) | set(self.packages[package].options)
            self.packages[package].options = tuple(options)
            self.packages[package].kwoptions.update(kwoptions)

    def add_to_preamble(self, tex_object_or_string):
        self.preamble.append(tex_object_or_string)

    def build_preamble(self):
        packages = self.build_packages()
        preamble = set(build(line, self) for line in self.preamble)
        preamble = '\n'.join([packages] + list(preamble))

        return preamble

    def build_packages(self):
        return '\n'.join([build(package, self) for package in self.packages.values()])

    def __repr__(self):
        class_name = self.__name__ if '__name__' in self.__dict__ else self.__class__.__name__
        return f'{class_name} {self.name}'

    def __str__(self):
        return self.build()

    def build(self):
        """
        Builds the object. Should return a valid LaTeX string.
        """
        return ''


class TexCommand(TexObject):
    def __init__(self, command, *parameters, options=list(), options_pos='second', **kwoptions):
        r"""
        Args:
            command (str): Name of the command that will be rendered as '\command'.
            parameters: Parameters of the command, appended inside curly braces {}.
            options (str or list of str): Options to pass to the command, appended inside brackets [].
            options_pos (str, either 'first', 'second' or 'last'): Position of the options with respect to the parameters.
            kwoptions (dict of str): Keyword options to pass to the command, appended inside the same brackets as options.
        """
        super().__init__(command)
        self.command = command
        self.options = list(options) if isinstance(options, (tuple, list)) else [options]
        self.parameters = list(parameters)
        self.kwoptions = kwoptions
        self.options_pos = options_pos

    def build(self):
        command = f'\\{self.command}'
        options = ''

        if self.options or self.kwoptions:
            kwoptions = ', '.join('='.join((build(key, self).replace('_', ' '), build(value, self))) for key, value in self.kwoptions.items())
            options = ', '.join([build(opt, self) for opt in self.options])
            if kwoptions and options:
                options += ', '
            options = f'[{options}{kwoptions}]'
        if self.parameters:
            parameters = f"{{{'}{'.join([build(param, self) for param in self.parameters])}}}"

        if self.options_pos == 'first':
            command += options
            if self.parameters:
                command += f"{{{'}{'.join([build(param, self) for param in self.parameters])}}}"
        if self.options_pos == 'second':
            if self.parameters:
                command += f'{{{build(self.parameters[0], self)}}}'
            command += options
            if len(self.parameters) > 1:
                command += f"{{{'}{'.join([build(param, self) for param in self.parameters[1:]])}}}"
        elif self.options_pos == 'last':
            if self.parameters:
                command += f"{{{'}{'.join([build(param, self) for param in self.parameters])}}}"
            command += options

        return command


class Package(TexCommand):
    """
    'usepackage' tex command wrapper.
    """
    def __init__(self, package_name, *options, **kwoptions):
        super().__init__('usepackage', package_name, options=options, options_pos='first', **kwoptions)


class bold(TexCommand):
    r"""
    Applies \textbf{...} command on text.
    """
    def __init__(self, text):
        """
        Args:
            text (str): Text to print in bold.
        """
        super().__init__('textbf', text)


class italic(TexCommand):
    r"""
    Applies \textit{...} command on text.
    """
    def __init__(self, text):
        """
        Args:
            text (str): Text to print in italic.
        """
        super().__init__('textit', text)
