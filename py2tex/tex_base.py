import os
from subprocess import DEVNULL, STDOUT, check_call


def build(env):
    """
    Safely builds the environment by calling its method 'build' only if 'env' is not a string.
    """
    if isinstance(env, str):
        return env
    else:
        return env.build()


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
        """
        Add a package to the preamble. If the package had already been added, the old is removed.

        Args:
            package (str): The package name.
            options (tuple of str): Options to pass to the package in brackets.
            kwoptions (dict of str): Keyword options to pass to the package in brackets.
        """
        options = f"[{','.join(options)}]" if options else ''
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = options

    def add_text(self, text):
        """
        Add texts or really any tex commands as a string.

        Args:
            text (str): Text to add.
        """
        self.body.append(text)

    def new(self, env):
        """
        Appends a new environment to the environment then returns it.
        Args:
            env (TexEnvironment or subclasses): Environment to append to the current environment.

        Returns env.
        """
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
            tex.append(build(text_or_env))
            if isinstance(text_or_env, TexEnvironment):
                self.packages.update(text_or_env.packages)

        tex = [self.head] + tex + [self.tail]
        return '\n'.join(tex)

