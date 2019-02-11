from py2tex import Document, Table
import numpy as np

doc = Document(filename='table_from_numpy_array_example', filepath='examples/table from numpy array example', doc_type='article', options=('12pt',))

sec = doc.new_section('Testing tables from numpy array')
sec.add_text("This section tests tables from numpy array.")

col, row = 4, 4
data = np.random.rand(row, col)

table = sec.new(Table(shape=(row+1, col+1), alignment='c', float_format='.2f'))
table.caption = 'Table from numpy array' # Set a caption if desired
table[1:,1:] = data # Set entries with a slice directly from a numpy array!

table[2:4,2:4] = 'Array' # Set multicell areas with a slice too. The value is contained in the top left cell (here it would be cell (2,2))
table[0,1:].multicell('From', h_align='c') # Set a multicell with custom parameters
table[1:,0].multicell('Numpy', v_align='*', v_shift='-2pt')

table[0,1:3].add_rule(trim_left=True, trim_right='.3em') # Add rules with parameters where you want
table[0,3:].add_rule(trim_left='.3em', trim_right=True)

table[1,1:].highlight_best('low', 'bold') # Automatically highlight the best value inside the specified slice
table[4,1:].highlight_best('low', 'bold')

tex = doc.build()
print(tex)
