from py2tex import Document, Plot
import numpy as np

# Document type 'standalone' will only show the plot, but does not support all tex environments.
filepath = './examples/simple plot example/'
filename = 'simple_plot_example'
doc = Document(filename, doc_type='standalone', filepath=filepath)

# Create the data
X = np.linspace(0,2*np.pi,100)
Y1 = np.sin(X)
Y2 = np.cos(X)

# Create a plot
plot = doc.new(Plot(X, Y1, X, Y2, plot_path=filepath, as_float_env=False))

tex = doc.build()
