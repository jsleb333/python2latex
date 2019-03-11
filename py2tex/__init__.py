try:
    from tex_base import TexFile, TexObject, TexEnvironment, build
    from document import Document, Section, Subsection
    from floating_environment import FloatingFigure, FloatingTable
    from table import Table
    from plot import Plot
except:
    from .tex_base import TexFile, TexObject, TexEnvironment, build
    from .document import Document, Section, Subsection
    from .floating_environment import FloatingFigure, FloatingTable
    from .table import Table
    from .plot import Plot
