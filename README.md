# Py2TeX: The Python to LaTeX converter

Did you ever feel overwhelmed by the cumbersomeness of LaTeX to produce quality tables and figures? Fear no more, Py2TeX is here! Produce perfect tables automatically and easily, create figures and plots that integrates seamlessly into your tex file, or even write your complete article directly from Python! All that effortlessly (or almost) with Py2TeX. (Plots and figures to come)

## Examples

### Create a simple document

The following example shows how to create a document with a single section and some text.
```python
from py2tex import Document

doc = Document(filename='Test', doc_type='article', options=('12pt',))
doc.set_margins(top='3cm', bottom='3cm', margins='2cm')
sec = doc.new_section('Spam and Egg', label='spam_egg')
sec.add_text('The mighty Python slays the Spam and eats the Egg.')

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
```

### Create a table from a numpy array

This example shows how to generate automatically a table from data taken directly from a numpy array. The module allows to add merged cells easily, to add rule easily and even to highlight the best value automatically inside a specified area!
```python
from py2tex import Document, Table
import numpy as np

doc = Document(filename='Test', doc_type='article', options=('12pt',))

sec = doc.new_section('Testing tables', label='tables_test')
sec.add_text("This section tests tables.")

col, row = 4, 4
data = np.random.rand(row, col)

table = sec.new(Table(shape=(row+1, col+1), alignment='c', float_format='.2f'))
table.caption = 'test' # Set a caption if desired
table[1:,1:] = data # Set entries with a slice

table[2:4,2:4] = 'test' # Set multicell areas with a slice too
table[0,1:].multicell('Title', h_align='c') # Set a multicell with custom parameters
table[1:,0].multicell('Types', v_align='*', v_shift='-2pt')

table[0,1:3].add_rule(trim_left=True, trim_right='.3em') # Add rules with parameters where you want
table[0,3:].add_rule(trim_left='.3em', trim_right=True)

table[1,1:].highlight_best('low', 'bold') # Automatically highlight the best value inside the specified slice
table[4,1:].highlight_best('low', 'bold')

tex = doc.build()
print(tex)
```
