from collections import OrderedDict
import os


class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename):
        self.filename = filename + '.tex'

    def save(self, tex):
        with open(self.filename, 'w', encoding='utf8') as file:
            file.write(tex)

    def compile(self):
        os.system(f"pdflatex {self.filename}")


class Environment:
    def __init__(self, env_name):
        self.env_name = env_name
        self.body = [] # List of Environments
        self.env_options = ()

    def add_text(self, text):
        self.body.append(text)

    def new_environment(self, env_name, *options):
        env = Environment(env_name)
        env.env_options = options
        self.body.append(env)
        return env

    def __repr__(self):
        return f'Environment {self.env_name}'

    def build(self):
        for i in range(len(self.body)):
            line = self.body[i]
            if isinstance(line, Environment):
                line.build()
                self.body[i] = line.body
        first_line = f'\\begin{{{self.env_name}}}'
        if self.env_options:
            first_line += f"{{{','.join(self.env_options)}}}"
        self.body = [first_line] + self.body + [f'\\end{{{self.env_name}}}']
        self.body = '\n'.join(self.body)


class Document(Environment):
    """
    Tex document class.
    """
    def __init__(self, filename, doc_type, *options, **kwoptions):
        super().__init__('document')
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

    def add_package(self, package, *options, **kwoptions):
        options = f"[{','.join(options)}]" if options else ''
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = options

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
        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            self.header.append(f"\\usepackage{options}{{{package}}}")
        self.header = '\n'.join(self.header)

        super().build()
        self.file.save(self.header + '\n' + self.body)
        self.file.compile()


if __name__ == "__main__":
    d = Document('Tata', 'article', '12pt')
    print(d.body)

    sec1 = d.new_environment('section', 'Yoyo')
    sec1.add_text("""This is section 1.""")

    d.build()
    print(d.body)
