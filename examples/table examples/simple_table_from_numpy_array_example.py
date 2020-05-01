from python2latex import Document, Table
import numpy as np

# Create the document of type standalone
doc = Document(filename='simple_table_from_numpy_array_example', filepath='examples/simple_table from numpy array example', doc_type='standalone', border='10pt')

# Create the data
col, row = 4, 4
data = np.random.rand(row, col)

# Create the table and add it to the document at the same time
table = doc.new(Table(shape=(row+2, col+1), as_float_env=False)) # No float environment in standalone documents

# Set entries with a slice directly from a numpy array!
table[2:,1:] = data

# Set a columns title as a multicell with custom parameters
table[0,1:].multicell('Col title', h_align='c')
# Set whole lines or columns in a single line with lists
table[1,1:] = [f'Col{i+1}' for i in range(col)]
table[2:,0] = [f'Row{i+1}' for i in range(row)]

# Add rules where you want
table[1,1:].add_rule()

# Automatically highlight the best value(s) inside the specified slice, ignoring text
for r in range(2,row+2):
    table[r].highlight_best('high', 'bold') # Best per row

tex = doc.build()
print(tex)
