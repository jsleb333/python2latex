

class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename):
        self.filename = filename


class Environment:
    def __init__(self, env_name):
        self.env_name = env_name
        self.body = []

    def add_text(self, text):
        self.body.append(text)

    def build_environment(self):
        for line in self.body:
            if isinstance(line, Environment):
                line.build_environment()
        self.env = [f'\\begin{self.env_name}'] + self.body + [f'\\end{self.env_name}']
        self.env = '\n'.join(self.env)


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

        self.doc = ["\documentclass{options}{{{doc_type}}}".format(options=options, doc_type=doc_type)]

        self.packages = {'inputenc':'utf8',
                         'geometry':''}
        self.set_margins('2.5cm')

        self.body = [] # List of Environments

    def set_margins(self, margins, top=None, bottom=None):
        self.margins = {'top':margins,
                         'bottom':margins,
                         'margins':margins}
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom

        self.packages['geometry'] = ','.join(key+'='+value for key, value in self.margins.items())

    def new_environment(self, env_name):
        env = Environment(env_name)
        self.body.append(env)
        return env

    def build_document(self):
        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            pack = f"\\usepackage{options}{{{package}}}"
            self.doc.append(pack)

        self.doc.append("\\begin{{document}}")

        self.doc.append("\end{{document}}")

        self.file.file = '\n'.join(self.doc)



if __name__ == "__main__":
    d = Document('Tata', 'article', '12pt')
    print(d.doc)
    d.build_document()
    print(d.file.file)
