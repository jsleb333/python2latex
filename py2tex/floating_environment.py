from py2tex import TexEnvironment


class _FloatingEnvironment(TexEnvironment):
    """
    LaTeX floating environment.
    """
    def __init__(self, env_name, position='h!', label='', label_pos='bottom', centered=True, **kwargs):
        """
        Args:
            position (str, combination of 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility.
            label (str): Label of the environment if needed.
            label_pos (str, either 'top' or 'bottom'): Position of the label inside the object. If 'top', will be at the end of the head, else if 'bottom', will be at the top of the tail.
        """
        super().__init__(env_name=env_name, options=position, label=label, label_pos=label_pos)
        if centered:
            self.head.append(r'\centering')


class FloatingFigure(_FloatingEnvironment):
    """
    LaTeX floating figure environment.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('figure', *args, **kwargs)


class FloatingTable(_FloatingEnvironment):
    """
    LaTeX floating table environment.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            See _FloatingEnvironment arguments.
        """
        super().__init__('table', *args, **kwargs)
