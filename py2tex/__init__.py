try:
    from tex_base import TexFile, TexCommand, TexObject, build
    from tex_environment import TexEnvironment
    from document import Document, Section, Subsection
    from floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
    from table import Table
    from plot import Plot
except:
    from .tex_base import TexFile, TexCommand, TexObject, build
    from .tex_environment import TexEnvironment
    from .document import Document, Section, Subsection
    from .floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
    from .table import Table
    from .plot import Plot
