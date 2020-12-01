from colorspacious import cspace_converter
JCh2rgb = cspace_converter('JCh', 'sRGB1')

import numpy as np
from python2latex import Document, Plot, LinearColorMap, Palette

# Create the document
filepath = './examples/plot examples/custom colors and line labels example/'
filename = 'custom_colors_and_line_labels_example'
doc = Document(filename, doc_type='article', filepath=filepath)

# Create color map in JCh space, in which each parameter is linear with human perception
cmap = LinearColorMap(color_anchors=[(20, 45, 135), (81, 99, 495)],
                      color_model='JCh',
                      color_transform=lambda color: np.clip(JCh2rgb(color), 0, 1))

# Create a dynamical palette which generates as many colors as needed from the cmap. Note that by default, the range of color used expands with the number of colors.
palette = Palette(colors=cmap,
                  color_model='rgb')

pal = Palette(colors=cmap, n_colors=2)

# Create the data
X = np.linspace(-1, 1, 50)
Y = lambda c: np.exp(X*c) + c

# Let us compare the different color palettes generated for different number of line plots
for n_colors in [2, 3, 5, 10]:
    # Create a plot
    plot = doc.new(Plot(plot_name=filename + f'n_colors={n_colors}',
                        plot_path=filepath,
                        width='\\textwidth',
                        height='.21\\paperheight',
                        palette=palette,
                        ))

    for c in np.linspace(.5, 1.5, n_colors):
        plot.add_plot(X, Y(c), label=f'\\footnotesize $c={c:.3f}$') # Add labels (default is at end of line plot)

    plot.x_min = -1
    plot.x_max = 1.3

    doc += '\n'

tex = doc.build()
