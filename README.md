# Python2LaTeX: The Python to LaTeX converter

Did you ever feel overwhelmed by the cumbersomeness of LaTeX to produce quality tables and figures? Fear no more, Python2LaTeX is here! Produce perfect tables automatically and easily, create figures and plots that integrates seamlessly into your tex file, or even write your complete article directly from Python! All that effortlessly (or almost) with Python2LaTeX.

## Prerequisites

The package makes use of numpy and assumes a distribution of LaTeX that uses ``pdflatex`` is installed on your computer. Some LaTeX packages are used, such as ``booktabs``, ``tikz``, ``pgfplots`` and ``pgfplotstable``. Your LaTeX distribution should inform you if such package needs to be installed.

## Installation

To install the package, simply run in your terminal the command

    pip install python2latex

## Examples

### Create a simple document

The following example shows how to create a document with a single section and some text.
```python
from python2latex import Document

doc = Document(filename='simple_document_example', filepath='./examples/simple document example', doc_type='article', options=('12pt',))
doc.set_margins(top='3cm', bottom='3cm', margins='2cm')
sec = doc.new_section('Spam and Egg', label='spam_egg')
sec.add_text('The Monty Python slays the Spam and eats the Egg.')

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
```

<details>
<summary>
<i> Click to unfold result </i>
</summary>
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/simple%20document%20example/simple_document_example.jpg" alt="Simple document">
</p>
</details>


### Create a table from a numpy array

This example shows how to generate automatically a table from data taken directly from a numpy array. The module allows to add merged cells easily, to add rules where you want and even to highlight the best value automatically inside a specified area and more! To ease these operations, the the square brackets ('getitem') operator have been repurposed to select an area of the table instead of returning the actual values contained in the table. Once an area is selected, use the 'format_spec', 'add_rule', 'multicell', 'apply_command', 'highlight_best' or 'divide_cell' methods or properties. To get the actual values inside the table, one can use the 'data' attribute of the table. See the examples for extensive coverage of possibilities. Here is a simple, working example to give a preview of the usage.
```python
from python2latex import Document, Table
import numpy as np

# Create the document of type standalone
doc = Document(filename='simple_table_from_numpy_array_example', filepath='examples/table examples', doc_type='standalone', border='10pt')

# Create the data
col, row = 4, 4
data = np.random.rand(row, col)

# Create the table and add it to the document at the same time
table = doc.new(Table(shape=(row+2, col+1), as_float_env=False)) # No float environment in standalone documents

# Set entries with a slice directly from a numpy array!
table[2:,1:] = data

# Set a columns title as a multicell with a simple slice assignment
table[0,1:] = 'Col title'
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
```
_Result:_
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/table%20examples/simple_table_from_numpy_array_example.jpg" alt="Table from numpy result">
</p>



### Create a simple plot
You can plot curves as easily as with `matplotlib.pyplot.plot` with the `Plot` environement that compiles it directly into pdf! This is a wrapper around the `pgfplots` and `pgfplotstable` LaTeX packages.
```python
from python2latex import Document, Plot
import numpy as np

# Document type 'standalone' will only show the plot, but does not support all tex environments.
filepath = './examples/plot examples/simple plot example/'
filename = 'simple_plot_example'
doc = Document(filename, doc_type='standalone', filepath=filepath)

# Create the data
X = np.linspace(0,2*np.pi,100)
Y1 = np.sin(X)
Y2 = np.cos(X)

# Create a plot
plot = doc.new(Plot(X, Y1, X, Y2, plot_path=filepath, as_float_env=False))

tex = doc.build()
```
_Result:_
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/plot%20examples/simple%20plot%20example/simple_plot_example.jpg" alt="Simple plot result">
</p>



### Create a more complex plot
You can make more complex plots with the options shown in this example.
```python
from python2latex import Document, Plot
import numpy as np

# Create the document
filepath = './examples/plot examples/more complex plot example/'
filename = 'more_complex_plot_example'
doc = Document(filename, doc_type='article', filepath=filepath)
sec = doc.new_section('More complex plot')
sec.add_text('This section shows how to make a more complex plot integrated directly into a tex file.')

# Create the data
X = np.linspace(0,2*np.pi,100)
Y1 = np.sin(X)
Y2 = np.cos(X)

# Create a plot
plot = sec.new(Plot(plot_name=filename, plot_path=filepath))
plot.caption = 'More complex plot'

plot.add_plot(X, Y1, 'blue', 'dashed', legend='sine') # Add colors and legend to the plot
plot.add_plot(X, Y2, 'orange', line_width='3pt', legend='cosine')
plot.legend_position = 'south east' # Place the legend where you want

# Add a label to each axis
plot.x_label = 'Radians'
plot.y_label = 'Projection'

# Choose the limits of the axis
plot.x_min = 0
plot.y_min = -1

# Choose the positions of the ticks on the axes
plot.x_ticks = np.linspace(0,2*np.pi,5)
plot.y_ticks = np.linspace(-1,1,9)
# Choose the displayed text for the ticks
plot.x_ticks_labels = r'0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'

# Use the tex environment 'axis' keyword options to use unimplemented features if needed.
plot.axis.kwoptions['y tick label style'] = '{/pgf/number format/fixed zerofill}' # This makes all numbers with the same number of 0 (fills if necessary).

tex = doc.build()
```
<details>
<summary>
<i> Click to unfold result </i>
</summary>
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/plot%20examples/more%20complex%20plot%20example/more_complex_plot_example.jpg" alt="More complex plot result">
</p>
</details>

### Create a simple matrix plot AKA heatmap
You can also make heatmaps in a similar fashion as a plot.
```python
from python2latex import Document, Plot
import numpy as np

# Create the document
filepath = './examples/plot examples/simple matrix plot example'
filename = 'simple_matrix_plot_example'
doc = Document(filename, doc_type='standalone', filepath=filepath, border='1cm')

# Create the data
X = np.linspace(-3, 3, 11)
Y = np.linspace(-3, 3, 21)

# Create a plot
plot = doc.new(Plot(plot_name=filename, plot_path=filepath, as_float_env=False,
                    grid=False, lines=False,
                    enlargelimits='false',
                    width=r'.5\textwidth', height=r'.5\textwidth'))

XX, YY = np.meshgrid(X, Y)
Z = np.exp(-(XX**2+YY**2)/6).T # Transpose is necessary because numpy puts the x dimension along columns and y dimension along rows, which is the opposite of a standard graph.
plot.add_matrix_plot(X, Y, Z)

# Adding titles and labels
plot.x_label = 'X axis'
plot.y_label = 'Y axis'
plot.title = 'Some title'

tex = doc.build()
```
_Result:_
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/plot%20examples/simple%20matrix%20plot%20example/simple_matrix_plot_example.jpg" alt="Simple matrix plot result">
</p>

Be sure to check our more complex matrix plot example too!


### Templating
If you do not want to write your whole document in python2latex, you can use our simple templating engine to insert parts of tex code directly inside your file.
Simply write the command `%! python2latex-anchor = anchor_name_here` and the script will automatically insert the commands below it.

See our example folder for a simple usage example of the Template class.


### Create an unsupported environment
If some environment is not currently supported, you can create one from the TexEnvironment base class.
```python
from python2latex import Document, TexEnvironment

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
<details>
<summary>
<i> Click to unfold result </i>
</summary>
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/unsupported%20env%20example/unsupported_env_example.jpg" alt="Unsupported environment result">
</p>
</details>


### Binding objects to environments
To alleviate syntax, it is possible to bind TexObject classes to an instance of a TexEnvironment. This creates an alternative class that automatically append any new instance of the class to the environment.
```python
from python2latex import Document, Section, Subsection, TexEnvironment

doc = Document(filename='binding_objects_to_environments_example', filepath='./examples/binding objects to environments example', doc_type='article', options=('12pt',))
section = doc.bind(Section) # section is now a new class that creates Section instances that are automatically appended to 'doc'

sec1 = section('Section 1', label='sec1') # Equivalent to: sec1 = doc.new(Section('Section 1', label='sec1'))
sec1.add_text("All sections created with ``section'' will be automatically appended to the document body!")

subsection, texEnv = sec1.bind(Subsection, TexEnvironment) # 'bind' supports multiple classes in the same call
eq1 = texEnv('equation')
eq1.add_text(r'e^{i\pi} = -1')

eq2 = texEnv('equation')
eq2 += r'\sum_{n=1}^{\infty} n = -\frac{1}{12}' # The += operator calls is the same as 'add_text'

sub1 = subsection('Subsection 1 of section 1')
sub1 += 'Text of subsection 1 of section 1.'

sec2 = section('Section 2', label='sec2')
sec2 += "sec2 is also appended to the document after sec1."

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
```
<details>
<summary>
<i> Click to unfold result </i>
</summary>
<p>
<img src="https://github.com/jsleb333/python2latex/blob/master/examples/binding%20objects%20to%20environments%20example/binding_objects_to_environments_example.jpg" alt="Binding objects to environments result">
</p>
</details>


## How it works

This LaTeX wrapper is based on the TexEnvironment class. Each such environment possesses a body attribute consisting in a list of strings and of other TexEnvironments. The 'build' method then converts every TexEnvironment to a tex string recursively. This step makes sure every environment is properly between a '\begin{env}' and a '\end{env}'. Converting the document to a string only at the end allows to do operation in the order desired, hence providing flexibility. The 'build' method can be called on any TexEnvironment, return the tex string representation of the environment. However, only the Document class 'build' method will also compile it to an actual pdf.
