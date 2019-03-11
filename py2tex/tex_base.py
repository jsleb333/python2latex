import os
from subprocess import DEVNULL, STDOUT, check_call


def build(obj):
    """
    Safely builds the object by calling its method 'build' only if 'obj' is not a string.
    """
    if isinstance(obj, TexEnvironment):
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
    Implements a basic Tex object.

    Allows recursive use of Tex objects inside others.
    Add new objects with the method 'new' and add standard text with 'add_text'.
    Add LaTeX packages needed for this object with 'add_package'.
    """
    def __init__(self, obj_name, head=None, tail=None, label='', label_pos='top'):
        """
        Args:
            obj_name (str): Name of the object.
            head (str or list of str or None): Tex text that will appear above the body. If a list, each item in the list must be a valid LaTeX line.
            tail (str or list of str or None): Tex text that will appear below the body. If a list, each item in the list must be a valid LaTeX line.
            label (str): Label of the object if needed.
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the object. If 'top', will be at the end of the head, else if 'bottom', will be at the top of the tail.
        """
        self.name = obj_name
        self.body = [] # List of objects or texts
        self.head = [head] if isinstance(head, str) else (head or [])
        self.tail = [tail] if isinstance(tail, str) else (tail or [])

        self.packages = {}
        self.label_pos = label_pos
        self.label = label

    def add_package(self, package, *options, **kwoptions):
        """
        Add a package to the preamble. If the package had already been added, the old is removed.

        Args:
            package (str): The package name.
            options (tuple of str): Options to pass to the package in brackets.
            kwoptions (dict of str): Keyword options to pass to the package in brackets.
        """
        options = list(options)
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = f"[{', '.join(options)}]" if options else ''

    def add_text(self, text):
        """
        Add texts or really any tex commands as a string.

        Args:
            text (str): Text to add.
        """
        self.body.append(text)

    def new(self, obj):
        """
        Appends a new object to the current object then returns it.
        Args:
            obj (TexObject or subclasses): object to append to the current object.

        Returns obj.
        """
        self.body.append(obj)
        return obj

    def __repr__(self):
        class_name = self.__name__ if '__name__' in self.__dict__ else self.__class__.__name__
        return f'{class_name} {self.name}'

    def build(self, head=None, tail=None):
        """
        Builds recursively the objects of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        tex = []
        label = f"\\label{{{self.name}:{self.label}}}"
        head = head or list(self.head)
        tail = tail or list(self.tail)
        if self.label:
            if self.label_pos == 'top':
                head.append(label)
            else:
                tail.insert(0, label)

        for text_or_obj in self.body:
            tex.append(build(text_or_obj))
            if isinstance(text_or_obj, TexObject):
                self.packages.update(text_or_obj.packages)

        tex = head + tex + tail
        return '\n'.join(tex)


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
        super().__init__(env_name,
                         head=[rf'\begin{{{env_name}}}'], tail=[rf'\end{{{env_name}}}'],
                         label=label, label_pos=label_pos)
        self.parameters = parameters
        self.options = options if isinstance(options, tuple) else (options,)
        self.kwoptions = kwoptions

    def build(self):
        """
        Builds recursively the environments of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        head = list(self.head)
        if self.options or self.kwoptions:
            kwoptions = ', '.join('='.join((k, str(v))) for k, v in self.kwoptions.items())
            options = ', '.join(self.options)
            if kwoptions and options:
                options += ', '
            head[0] += f"[{options + kwoptions}]"
        if self.parameters:
            head[0] += f"{{{', '.join(self.parameters)}}}"

        return super().build(head)

