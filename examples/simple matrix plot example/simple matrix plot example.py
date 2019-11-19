from python2latex import Document, Plot
import numpy as np

# Create the document
filepath = './examples/simple matrix plot example'
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
