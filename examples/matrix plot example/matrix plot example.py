from python2latex import Document, Plot, Color
import numpy as np

# Create the document
filepath = './examples/matrix plot example'
filename = 'matrix_plot_example'
doc = Document(filename, doc_type='article', filepath=filepath)
sec = doc.new_section('Matrix plot AKA Heatmap AKA Colormap')
sec.add_text('This section shows how to make a matrix plot integrated directly into a tex file.')

# Create the data
X = np.linspace(-np.pi, np.pi, 21)
Y = np.linspace(-np.pi, np.pi, 21)

# Create a plot
plot = sec.new(Plot(plot_name=filename, plot_path=filepath, grid=False, lines=False))
plot.caption = 'Matrix plot of a gaussian'

XX, YY = np.meshgrid(X, Y)
print(np.max(np.exp(-(XX**2+YY**2)/(2*np.pi))))
plot.add_matrix_plot(X, Y, np.exp(-(XX**2+YY**2)/(2*np.pi)))

# Add a label to each axis
plot.x_label = 'X axis'
plot.y_label = 'Y axis'

# Choose the positions of the ticks on the axes
plot.x_ticks = np.linspace(-np.pi, np.pi, 5)
plot.y_ticks = np.linspace(-np.pi, np.pi, 5)
# Choose the displayed text for the ticks
plot.x_ticks_labels = r'$-\pi$', r'$-\frac{\pi}{2}$', r'0', r'$\frac{\pi}{2}$', r'$\pi$'
plot.y_ticks_labels = r'$\pi$', r'$\frac{\pi}{2}$', r'0', r'$-\frac{\pi}{2}$', r'$-\pi$'


tex = doc.build()
