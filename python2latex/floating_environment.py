import warnings

from python2latex import TexEnvironment, TexObject, TexCommand, build, Label


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
    def __init__(self,
                 env_name,
                 star_env=False,
                 position='h!',
                 label='',
                 caption='',
                 caption_pos='bottom',
                 caption_space='',
                 centered=True):
        """
        Args:
            position (str, combination of 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility.
            star_env (bool): Whether the environment should be starred or not.
            label (str): Label of the environment if needed.
            caption (str): Caption of the floating environment.
            caption_pos (str, either 'top' or 'bottom'): Position of the caption, either at the beginning (top) of the floating environment or at the end (bottom).
            caption_space (str, valid TeX length or empty str): Space between the caption and the object in the floating environment. Can be any valid TeX length. If empty string, no space is added.
            centered (bool): Whether to center the environment or not.
        """
        super().__init__(env_name=env_name,
                         star_env=star_env,
                         options=position,
                         label=label,
                         label_pos=None, # Label positioning is handled here instead of in TexEnvironment.
                         )
        self.caption = caption
        self.caption_pos = caption_pos
        self.caption_space = caption_space
        self.centered = centered

    def build(self):
        """
        Builds recursively the environments of the body and converts it to .tex.
        Returns the .tex string of the file.
        """
        if self.caption:
            caption = Caption(self.caption)
            space = TexCommand('vspace', self.caption_space) if self.caption_space else ''

            if self.caption_pos == 'top':
                self.body = [caption, self._label, space] + self.body

            if self.caption_pos == 'bottom':
                self.body += [space, caption, self._label]

        if self.centered:
            self.body = [r'\centering'] + self.body

        return super().build()


class FloatingFigure(_FloatingEnvironment):
    """
    LaTeX floating figure environment.
    """
    def __init__(self, *args, label_pos='bottom', **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('figure', *args, caption_pos=label_pos, **kwargs)


class FloatingTable(_FloatingEnvironment):
    """
    LaTeX floating table environment.
    """
    def __init__(self, *args, caption_pos='top', caption_space='5pt', **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('table', *args, caption_pos=caption_pos, caption_space=caption_space, **kwargs)


class FloatingEnvironmentMixin:
    """
    Makes an environment optionally floatable.
    Should be inherited and a 'super_class' parameter should be included. 'super_class' should be a FloatingEnvironment
    class.

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
        cls.__bases__ += (super_class, )

    def build(self):
        if not self.as_float_env and self.caption:
            self.caption = ''  # No caption outside of float env
            warnings.warn('Cannot produce caption outside floating environment!')
        return super().build()
