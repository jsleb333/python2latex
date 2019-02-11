try:
    from document import Document, TexEnvironment
    from table import Table
except:
    from .document import Document, TexEnvironment
    from .table import Table
