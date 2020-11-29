from python2latex import Document, Plot, Color
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

nice_blue = Color(.07, .22, .29, color_name='nice_blue')
nice_orange = Color(.85, .33, .28, color_name='nice_orange')

plot.add_plot(X, Y1, nice_blue, 'dashed', legend='sine') # Add colors and legend to the plot
line_plot = plot.add_plot(X, Y2, line_width='3pt', legend='cosine')
line_plot.options += (nice_orange,) # Add options to the line plot object after creation if desired.
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

# The 'axis' TeX environment can be accessed via the axis attribute. Options can be passed to the environment using the 'options' and 'kwoptions' attributes to customize unimplemented features if needed.
plot.axis.kwoptions['y tick label style'] = '{/pgf/number format/fixed zerofill}' # This makes all numbers with the same number of 0 (fills if necessary).

tex = doc.build()
