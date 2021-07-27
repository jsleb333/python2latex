# Basics must be loaded first
from .tex_base import *
from .tex_environment import *

# Other features
from .document import Document, Section, Subsection
from .color import *
from .colormap import *
from .floating_environment import FloatingFigure, FloatingTable, FloatingEnvironmentMixin
from .plot import Plot, LinePlot, MatrixPlot
from .template import Template
from .table import Table, Tabular
