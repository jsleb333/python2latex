# Basics must be loaded first
from .tex_base import *
from .tex_environment import TexEnvironment

# Other features
from .document import Document, Section, Subsection
from .color import Color
from .floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
from .plot import Plot, LinePlot, MatrixPlot
from .table import Table
