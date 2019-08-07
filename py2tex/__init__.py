try:
    from tex_base import *
    from tex_environment import TexEnvironment
    from document import Document, Section, Subsection
    from floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
    from table import Table
    from plot import Plot
<<<<<<< HEAD
    from tikzpicture import *
=======
    from color import Color
>>>>>>> dev
except:
    from .tex_base import *
    from .tex_environment import TexEnvironment
    from .document import Document, Section, Subsection
    from .floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
    from .table import Table
    from .plot import Plot
<<<<<<< HEAD
    from .tikzpicture import *
=======
    from .color import Color
>>>>>>> dev
