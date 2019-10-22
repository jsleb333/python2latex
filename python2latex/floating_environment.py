import warnings
from python2latex import TexEnvironment, TexObject, TexCommand, build

class Caption(TexCommand):
    """
    Simple caption command.
    """
    def __init__(self, caption):
        """
        Args:
            caption (str): Caption of the environment.
        """
        super().__init__('caption', caption)


class _FloatingEnvironment(TexEnvironment):
    """
    LaTeX floating environment. This should be inherited.
    """
    def __init__(self, env_name, position='h!', label='', label_pos='bottom', caption='', centered=True):
        """
        Args:
            position (str, combination of 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility.
            label (str): Label of the environment if needed.
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the object. If 'top', will be at the end of the head, else if 'bottom', will be at the top of the tail.
            caption (str): Caption of the floating environment.
            centered (bool): Wheter to center or not the environment.
        """
        super().__init__(env_name=env_name, options=position, label=label, label_pos=label_pos)
        self.caption = caption
        self.centered = centered

    def build(self):
        """
        Builds recursively the environments of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        tex = [self.head]

        if self.centered:
            tex.append(r'\centering')

        if self.label_pos == 'top':
            if self.caption:
                tex.append(Caption(self.caption))
            tex.append(self._label)

        tex.append(self.build_body())

        if self.label_pos == 'bottom':
            if self.caption:
                tex.append(Caption(self.caption))
            tex.append(self._label)

        tex.append(self.tail)

        tex = [build(part) for part in tex]
        return '\n'.join([part for part in tex if part])


class FloatingFigure(_FloatingEnvironment):
    """
    LaTeX floating figure environment.
    """
    def __init__(self, *args, label_pos='bottom', **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('figure', *args, label_pos=label_pos, **kwargs)


class FloatingTable(_FloatingEnvironment):
    """
    LaTeX floating table environment.
    """
    def __init__(self, *args, label_pos='top', **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('table', *args, label_pos=label_pos, **kwargs)


class FloatingEnvironmentMixin:
    """
    Makes an environment optionally floatable.
    Should be inherited and a 'super_class' parameter should be included. 'super_class' should be a FloatingEnvironment class.

    Example:
    >>> class Table(FloatingEnvironmentMixin, super_class=FloatingTable):
    ...     pass

    See the Table and the Plot environments for complete examples.
    """
    def __init__(self, *args, as_float_env=True, centered=True, **kwargs):
        """
        Args:
            as_float_env (bool): Whether the environment will be floating or not.
            args and kwargs: Arguments and keyword arguments of super_class.
        """
        centered = False if not as_float_env else centered
        super().__init__(*args, centered=centered, **kwargs)
        self.as_float_env = as_float_env
        if not as_float_env:
            self.head = TexObject('')
            self.tail = TexObject('')
            self.options = ()

    def __init_subclass__(cls, super_class):
        cls.__bases__ += (super_class,)

    def build(self):
        if not self.as_float_env and self.caption:
            self.caption = '' # No caption outside of float env
            warnings.warn('Cannot produce caption outside floating environment!')
        return super().build()
