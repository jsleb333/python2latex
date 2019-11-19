from python2latex import Document, Plot, Color
import numpy as np

# Create the document
filepath = './examples/more complex matrix plot example'
filename = 'more_complex_matrix_plot_example'
doc = Document(filename, doc_type='article', filepath=filepath)
sec = doc.new_section('More complex matrix plot')
sec.add_text('This section shows how to make a more complex matrix plot integrated directly into a tex file.')

# Adding necessary library to preamble for colormaps
doc.add_to_preamble(r'\usepgfplotslibrary{colorbrewer}')
doc.add_to_preamble(r'\pgfplotsset{compat=1.15, colormap/Blues-3}')

# Create the data
X = np.array([0.05, 0.1, 0.2])
Y = np.array([1.5, 2.0, 3.0, 4.0])
Z = np.random.random((3,4))

# Create a plot
plot = sec.new(Plot(plot_name=filename, plot_path=filepath,
                    grid=False, lines=False,
                    enlargelimits='false',
                    width=r'.6\textwidth', height=r'.8\textwidth'
                    ))
plot.caption = 'Matrix plot of some random numbers as probabilities'
plot.add_matrix_plot(range(len(X)), range(len(Y)), Z) # Dummy values for x and y so that the region are all the same size, even though the values of X and Y are not linear.

# Adding more complex custom options to the axis (see PGFPlots documentation)
plot.axis.options += (
    r'nodes near coords={\pgfmathprintnumber\pgfplotspointmeta\,\%}',
    r'every node near coord/.append style={xshift=0pt,yshift=-7pt, black, font=\footnotesize}',
    )

# Add a label to each axis
plot.x_label = 'X axis'
plot.y_label = 'Y axis'

# Choose the positions of the ticks on the axes
plot.x_ticks = list(range(3))
plot.y_ticks = list(range(4))
# Choose the displayed text for the ticks
plot.x_ticks_labels = [str(x) for x in X]
plot.y_ticks_labels = [str(y) for y in Y]

tex = doc.build()
