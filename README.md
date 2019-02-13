# Py2TeX: The Python to LaTeX converter

Did you ever feel overwhelmed by the cumbersomeness of LaTeX to produce quality tables and figures? Fear no more, Py2TeX is here! Produce perfect tables automatically and easily, create figures and plots that integrates seamlessly into your tex file, or even write your complete article directly from Python! All that effortlessly (or almost) with Py2TeX. (Plots and figures to come)

## Prerequisites

The package makes use of numpy and assumes a distribution of LaTeX that uses ``pdflatex`` is installed on your computer. Some LaTeX packages are used, such as ``booktabs``, ``tikz``, ``pgfplots`` and ``pgfplotstable``. Your LaTeX distribution should inform you if such package needs to be installed.

## Installation

To install the package on your session, simply clone the repository with

    git clone https://github.com/jsleb333/py2tex.git

then run the command

    pip install .

to make the module known to Python and to be able to import it in any Python shell.

## Examples

### Create a simple document

The following example shows how to create a document with a single section and some text.
```python
from py2tex import Document

doc = Document(filename='simple_document_example', filepath='./examples/simple document example', doc_type='article', options=('12pt',))
doc.set_margins(top='3cm', bottom='3cm', margins='2cm')
sec = doc.new_section('Spam and Egg', label='spam_egg')
sec.add_text('The Monty Python slays the Spam and eats the Egg.')

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
```

![Simple document result](https://github.com/jsleb333/py2tex/blob/master/examples/simple%20document%20example/simple_document_example.jpg)

### Create a table from a numpy array

This example shows how to generate automatically a table from data taken directly from a numpy array. The module allows to add merged cells easily, to add rules where you want and even to highlight the best value automatically inside a specified area! To ease these operations, the the square brackets ('getitem') operator have been repurposed to select an area of the table instead of returning the actual values contained in the table. Once an area is selected, use the 'multicell', 'add_rule' or 'highlight_best' methods. To get the actual values inside the table, one can use the 'data' attribute of the table.
```python
from py2tex import Document, Table, build
import numpy as np

doc = Document(filename='table_from_numpy_array_example', filepath='examples/table from numpy array example', doc_type='article', options=('12pt',))

sec = doc.new_section('Testing tables from numpy array')
sec.add_text("This section tests tables from numpy array.")

col, row = 6, 4
data = np.random.rand(row, col)

table = sec.new(Table(shape=(row+2, col+1), alignment='c', float_format='.2f'))
# Set a caption if desired
table.caption = 'Table from numpy array'
# Set entries with a slice directly from a numpy array!
table[2:,1:] = data

# Set a columns title as a multicell with custom parameters
table[0,1:4].multicell('Title1', h_align='c')
table[0,4:].multicell('Title2', h_align='c')
# Set subtitles as easily
table[1,1:] = [f'Col{i+1}' for i in range(col)]
# Set a subtitle on two lines if it is too long
table[1,-1:].divide_cell(shape=(2,1), alignment='c')[:] = [['Longer'],['Title']]

# Or simply create a new subtable as an entry
subtable = Table(shape=(2,1), as_float_env=False, bottom_rule=False, top_rule=False)
subtable[:,0] = ['From', 'Numpy']

# Chain multiple methods on the same area for easy combinations of operations
table[2:,0].multicell(subtable, v_align='*', v_shift='0pt').highlight('italic')
# Set multicell areas with a slice too
table[3:5,2:4] = 'Array' # The value is stored in the top left cell (here it would be cell (2,2))

# Add rules where you want, as you want
table[1,1:4].add_rule(trim_left=True, trim_right='.3em')
table[1,4:].add_rule(trim_left='.3em', trim_right=True)

# Automatically highlight the best value(s) inside the specified slice, ignoring text
for row in range(2,6):
    table[row,4:].highlight_best('low', 'italic') # Best per row, for the last 3 columns
# Highlights equal or near equal values too!
table[5,1] = 1.0
table[5,2] = 0.996
table[5].highlight_best('high', 'bold') # Whole row 4

tex = doc.build()
print(tex)
```
![Table from numpy result](https://github.com/jsleb333/py2tex/blob/master/examples/table%20from%20numpy%20array%20example/table_from_numpy_array_example.jpg)



### Create an unsupported environment
```python
from py2tex import Document, TexEnvironment

doc = Document(filename='unsupported_env_example', doc_type='article', filepath='examples/unsupported env example', options=('12pt',))

sec = doc.new_section('Unsupported env')
sec.add_text("This section shows how to create unsupported env if needed.")

sec.add_package('amsmath') # Add needed packages in any TexEnvironment, at any level
align = sec.new(TexEnvironment('align', label='align_label'))
align.add_text(r"""e^{i\pi} &= \cos \pi + i \sin \pi\\
         &= -1""") # Use raw strings to alleviate tex writing

tex = doc.build()
print(tex)
```
![Unsupported env result](https://github.com/jsleb333/py2tex/blob/master/examples/unsupported%20env%20example/unsupported_env_example.jpg)



## How it works

This LaTeX wrapper is based on the TexEnvironment class. Each such environment possesses a body attribute consisting in a list of strings and of other TexEnvironments. The 'build' method then converts every TexEnvironment to a tex string recursively. This step makes sure every environment is properly between a '\begin{env}' and a '\end{env}'. Converting the document to a string only at the end allows to do operation in the order desired, hence providing flexibility. The 'build' method can be called on any TexEnvironment, return the tex string representation of the environment. However, only the Document class 'build' method will also compile it to an actual pdf.
