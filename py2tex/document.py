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

    def compile_to_pdf(self):
        os.system(f"pdflatex {self.filename}")


class TexEnvironment:
    def __init__(self, env_name, *parameters, options=None, parent_doc=None):
        self.env_name = env_name
        self.body = [] # List of Environments or texts
        self.head = '\\begin{{{env_name}}}'.format(env_name=env_name)
        self.tail = '\\end{{{env_name}}}'.format(env_name=env_name)
        if parameters:
            self.head += f"{{{','.join(parameters)}}}"
        if options:
            self.head += f"[{options}]"
        self.parent_doc = parent_doc

    def add_text(self, text):
        self.body.append(text)

    def new_environment(self, env_name, *parameters, options=None):
        env = TexEnvironment(env_name, *parameters, options=None, parent_doc=self.parent_doc)
        self.body.append(env)
        return env

    def new_table(self, *parameters, position='h!'):
        table = Table(*parameters, position, parent_doc=self.parent_doc)
        self.body.append(table)
        return table

    def __repr__(self):
        return f'TexEnvironment {self.env_name}'

    def build(self):
        for i in range(len(self.body)):
            line = self.body[i]
            if isinstance(line, TexEnvironment):
                line.build()
                self.body[i] = line.body
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
        self.parent_doc = self

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
        self.file.compile_to_pdf()


class Table(TexEnvironment):
    """

    """
    def __init__(self, position='h!', **kwargs):
        """
        Args:

        """
        super().__init__('table', options=position, **kwargs)
        self.parent_doc.add_package('booktabs')
        self.head += '\n\centering'
        self.table = [[]]
        self.body = [self.table]

    def __getitem__(self, i):
        pass

    def __setitem__(self, i):
        pass

    def build_table(self):
        table = TexEnvironment('tabular', '\\textwidth', '')

    def build(self):
        self.build_table()
        self.body[0] = self.table
        self.body[0] = ''
        super().build()


if __name__ == "__main__":
    d = Document('Tata', 'article', '12pt')
    print(d.parent_doc)

    sec1 = d.new_environment('section', 'Koko')
    sec1.add_text("""This is section 100.""")
    print(sec1.parent_doc)

    table1 = sec1.new_table()
    print(table1.parent_doc)

    d.build()
    print(d.body)
