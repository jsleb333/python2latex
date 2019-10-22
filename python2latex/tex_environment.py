from functools import wraps
from python2latex import TexObject, TexCommand, build


class begin(TexCommand):
    """
    'begin' tex command wrapper.
    """
    def __init__(self, environment, *parameters, options=list(), options_pos='second', **kwoptions):
        return super().__init__('begin', environment, *parameters, options=options, options_pos=options_pos, **kwoptions)


class end(TexCommand):
    """
    'end' tex command wrapper.
    """
    def __init__(self, environment):
        return super().__init__('end', environment)


class Label(TexCommand):
    """
    'label' tex command wrapper.
    """
    def __init__(self, label, prefix=None):
        self.label = label
        self.prefix = prefix
        return super().__init__('label')

    def build(self):
        prefix = f'{self.prefix}:' if self.prefix else ''
        if self.label:
            self.parameters = (prefix + self.label,)
            return super().build()
        else:
            return ''


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
        self.head = begin(env_name, *parameters, options=options, **kwoptions)
        self.tail = end(env_name)
        self.body = []

        self.parameters = self.head.parameters
        self.options = self.head.options
        self.kwoptions = self.head.kwoptions

        self.label_pos = label_pos
        self._label = Label(label, env_name)
        self.label = self._label.label

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
        >>> from python2latex import Document, Section
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
        tex = [self.head]

        if self.label_pos == 'top':
            tex.append(self._label)

        tex.append(self.build_body())

        if self.label_pos == 'bottom':
            tex.append(self._label)

        tex.append(self.tail)

        tex = [build(part, self) for part in tex]
        return '\n'.join([part for part in tex if part])

    def build_body(self):
        return '\n'.join([build(line, self) for line in self.body])
