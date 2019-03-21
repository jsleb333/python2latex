import os
from subprocess import DEVNULL, STDOUT, check_call
from functools import wraps


def build(obj):
    """
    Safely builds the object by calling its method 'build' only if 'obj' is not a string.
    """
    if isinstance(obj, TexObject):
        return obj.build()
    else:
        return obj


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
        check_call(['pdflatex', '-halt-on-error', self.filename], stdout=DEVNULL, stderr=STDOUT)


class TexObject:
    """
    Implements an abstract Tex object.

    Allows recursive use of Tex objects inside others.
    Add LaTeX packages needed for this object with 'add_package'.
    """
    def __init__(self, obj_name):
        """
        Args:
            obj_name (str): Name of the object.
        """
        self.name = obj_name
        self.body = []

        self.packages = {}

    def add_package(self, package, *options, **kwoptions):
        """
        Add a package to the preamble. If the package had already been added, the old is removed.

        Args:
            package (str): The package name.
            options (tuple of str): Options to pass to the package in brackets.
            kwoptions (dict of str): Keyword options to pass to the package in brackets.
        """
        kwoptions.update({o:'' for o in options})
        self.packages[package] = kwoptions

    def __repr__(self):
        class_name = self.__name__ if '__name__' in self.__dict__ else self.__class__.__name__
        return f'{class_name} {self.name}'

    def add_text(self, text):
        """
        Adds text (or a tex command) as a string or another TexObject to be appended.

        Args:
            text (str): Text to add.
        """
        self.append(text)

    def append(self, text):
        """
        Adds text (or a tex command) as a string or another TexObject to be appended.

        Args:
            text (str): Text to add.
        """
        self.body.append(text)

    def __iadd__(self, other):
        self.append(other)
        return self

    def build(self):
        """
        Builds recursively the objects of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        tex = []
        for text_or_obj in self.body:
            tex.append(build(text_or_obj))
            if isinstance(text_or_obj, TexObject):
                self.packages.update(text_or_obj.packages)

        return '\n'.join(tex)


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

    def __str__(self):
        return self.build()

    def build(self):
        command = f'\\{self.command}'
        options = ''

        if self.options or self.kwoptions:
            kwoptions = ', '.join('='.join((k, str(v))) for k, v in self.kwoptions.items())
            options = ', '.join(self.options)
            if kwoptions and options:
                options += ', '
            options = f'[{options}{kwoptions}]'
        if self.parameters:
            parameters = f"{{{'}{'.join(self.parameters)}}}"

        if self.options_pos == 'first':
            command += options
            if self.parameters:
                command += f"{{{'}{'.join(self.parameters)}}}"
        if self.options_pos == 'second':
            if self.parameters:
                command += f'{{{self.parameters[0]}}}'
            command += options
            if len(self.parameters) > 1:
                command += f"{{{'}{'.join(self.parameters[1:])}}}"
        elif self.options_pos == 'last':
            if self.parameters:
                command += f"{{{'}{'.join(self.parameters)}}}"
            command += options

        body = super().build()
        return '\n'.join([command, body] if body else [command])


class TexEnvironment(TexObject):
    r"""
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
            options (str or tuple of str): Options to pass to the environment, appended inside brackets [].
            label (str): Label of the environment if needed.
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the object. If 'top', will be at the end of the head, else if 'bottom', will be at the top of the tail.
        """
        super().__init__(env_name)
        self.head = TexCommand('begin', env_name, *parameters, options=options, **kwoptions)
        self.tail = TexCommand('end', env_name)

        self.parameters = self.head.parameters
        self.options = self.head.options
        self.kwoptions = self.head.kwoptions

        self.label_pos = label_pos
        self.label = label

    def new(self, obj):
        """
        Appends a new object to the current object then returns it.
        Args:
            obj (TexObject or subclasses): object to append to the current object.

        Returns obj.
        """
        self.body.append(obj)
        return obj

    def __contains__(self, value):
        return value in self.body

    def bind(self, *clss):
        """
        Binds the classes so that any new instances will automatically be appended to the body of the current environment. Note that the binded classes are new classes and the original classes are left unchanged.

        Usage example:
        >>> from py2tex import Document, Section
        >>> doc = Document('Title')
        >>> section = doc.bind(Section)
        >>> sec1 = section('Section 1')
        >>> sec1.append("All sections created with ``section'' will automatically be appended to the doc")
        >>> sec2 = section('Section 2')
        >>> sec2.append("sec2 is also automatically appended to the doc!")
        >>> doc.build()

        Args:
            clss (tuple of uninstanciated classes): Classes to bind to the current environment.

        Returns a binded class or a tuple of binded classes.
        """
        binded_clss = tuple(self._bind(cls) for cls in clss)
        return binded_clss[0] if len(binded_clss) == 1 else binded_clss

    def _bind(self, cls_to_bind):
        class BindedCls(cls_to_bind):
            @wraps(cls_to_bind.__new__)
            def __new__(cls, *args, **kwargs):
                instance = cls_to_bind.__new__(cls)
                self.append(instance)
                return instance
        BindedCls.__name__ = 'Binded' + cls_to_bind.__name__
        BindedCls.__qualname__ = 'Binded' + cls_to_bind.__qualname__
        BindedCls.__doc__ = f"\tThis is a {cls_to_bind.__name__} object binded to {repr(self)}. Each time an instance is created, it is appended to the body of {repr(self)}. Everything else is identical.\n\n" + str(cls_to_bind.__doc__)
        return BindedCls

    def build(self):
        """
        Builds recursively the environments of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        body = super().build()
        head = self.head.build()
        tail = self.tail.build()
        if self.label:
            label = f"\n\\label{{{self.name}:{self.label}}}"
            if self.label_pos == 'top':
                head += label
            else:
                body += label

        return '\n'.join([part for part in [head, body, tail] if part])
