try:
    from tex_base import TexFile, TexEnvironment, build
    from document import Document
    from table import Table
except:
    from .tex_base import TexFile, TexEnvironment, build
    from .document import Document
    from .table import Table
