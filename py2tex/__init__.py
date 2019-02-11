try:
    from document import Document, TexEnvironment
    from table import Table
except ModuleNotFoundError:
    from .document import Document, TexEnvironment
    from .table import Table
