from py2tex import Document, Table
import numpy as np

doc = Document(filename='table_from_numpy_array_example', filepath='examples/table from numpy array example', doc_type='article', options=('12pt',))

sec = doc.new_section('Testing tables from numpy array')
sec.add_text("This section tests tables from numpy array.")

col, row = 4, 4
data = np.random.rand(row, col)

table = sec.new(Table(shape=(row+1, col+1), alignment='c', float_format='.2f'))
# Set a caption if desired
table.caption = 'Table from numpy array'
# Set entries with a slice directly from a numpy array!
table[1:,1:] = data

# Set multicell areas with a slice too
table[2:4,2:4] = 'Array' # The value is stored in the top left cell (here it would be cell (2,2))
# Set a multicell with custom parameters
table[0,1:].multicell('From', h_align='c')
# Chain multiple methods on the same area for easy combinations of operations
table[1:,0].multicell('Numpy', v_align='*', v_shift='10pt').highlight('italic')

# Add rules where you want, as you want
table[0,1:3].add_rule(trim_left=True, trim_right='.3em')
table[0,3:].add_rule(trim_left='.3em', trim_right=True)

# Automatically highlight the best value(s) inside the specified slice, ignoring text
table[1].highlight_best('low', 'bold') # Whole row 1
# Highlights equal or near equal values too!
table[4,1] = 1.0
table[4,2] = 0.996
table[4].highlight_best('high', 'bold') # Whole row 4

tex = doc.build()
print(tex)
