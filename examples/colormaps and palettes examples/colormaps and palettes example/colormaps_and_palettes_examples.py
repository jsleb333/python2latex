from colorspacious.ciecam02 import NegativeAError
from python2latex import Document, Plot, Palette, Palette, LinearColorMap
from python2latex.utils import rgb2gray
import numpy as np
from colorspacious import cspace_converter
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
"""
In this example, we explore color maps and palettes.

A color map is understood as a function taking as input a scalar between 0 and 1 and outputs and color in some format. The class LinearColorMap takes as input a sequence of colors and interpolates linearly the colors in-between to yield a color map.

A palette is simply a collection of colors. python2latex defines a Palette object that handles the boilerplating related to the creation of Color objects from a sequence of colors or from a color map. The Palette object modifies dynamically the colors generated according to the number of colors needed so that colors never repeat, as opposed to a standard palette which loops back to the beginning when colors are exhausted.
"""
# First create a conversion function
JCh2rgb = cspace_converter('JCh', 'sRGB1')
rgb2JCh = cspace_converter('sRGB1', 'JCh')

# Document type 'standalone' will only show the plot, but does not support all tex environments.
filepath = './examples/plot examples/colormaps and palettes example/'
filename = 'colormaps_and_palettes_example'
doc = Document(filename, doc_type='article', filepath=filepath)

# Let us create a color map in the JCh color model, which parametrizes the colors according to human perception of colors instead of actual physical properties of light.
# Choose the color anchors of the color map defined in the JCh color space
color1 = rgb2JCh(hsv_to_rgb((.3, .9, .3)))
color2 = rgb2JCh(hsv_to_rgb((.29, .9, 1)))
color2 = (color2[0], color2[1], color2[2]+360)
print(color1, color2)
# color1 = (20, 30, 200)
# color2 = (70, 60, 480)
# Create the color map
cmap = LinearColorMap(color_anchors=[color1, color2],
                      color_model='JCh',
                      color_transform=JCh2rgb)

n_colors = 75
palette_JCh = Palette(cmap, color_model='rgb', n_colors=n_colors)

# Create a plot to illustrate the cmap
plot = doc.new(Plot(plot_path=filepath,
                    plot_name=filename,
                    lines='3pt',
                    palette=palette_JCh))
hue = np.linspace(color1[2], color2[2], n_colors+1)
lightness = np.linspace(color1[0], color2[0], n_colors+1)
for i in range(n_colors):
    plot.add_plot(hue[i:i+2], lightness[i:i+2], line_cap='round')

# Same plot but in gray level with human perceived brightness
palette_gray = Palette(cmap, color_model='gray', n_colors=n_colors, color_transform=lambda color: (rgb2gray(color),))
plot.axis.color_iterator = iter(palette_gray)
for i in range(n_colors):
    plot.add_plot(hue[i:i+2]+20, lightness[i:i+2], line_cap='round')

plot.axis += r'\node at (120,500) {Linear interp. in JCh space};'

# Same plot but using a linear cmap in the hsb color model rather than in the JCh
hsb_1 = np.clip(rgb_to_hsv(np.clip(JCh2rgb(color1),0,1)),0,1)
hsb_2 = np.clip(rgb_to_hsv(np.clip(JCh2rgb(color2),0,1)),0,1)
hsb_2 = (hsb_2[0]+1, hsb_2[1], hsb_2[2])
hsb_cmap = LinearColorMap(color_anchors=[hsb_1, hsb_2],
                          color_model='hsb')
palette_hsb = Palette(hsb_cmap, color_model='hsb', n_colors=n_colors)
colors = [c for c in palette_hsb]
plot.axis.color_iterator = iter(palette_hsb)

def shift_hue(h):
    return (h-color1[2]+.001)%360+color1[2]

for i in range(n_colors-1):
    J1, C1, h1 = rgb2JCh(hsv_to_rgb(colors[i].color_spec))
    J2, C2, h2 = rgb2JCh(hsv_to_rgb(colors[i+1].color_spec))
    plot.add_plot([shift_hue(h1), shift_hue(h2)], [J1, J2], line_cap='round')

plot.axis += r'\node at (280,170) {Linear interp. in HSV space};'

plot.x_label = 'Hue angle $h$'
plot.y_label = 'Lightness $J$'

plot.caption = 'Comparison of linear interpolation of colors in JCh space and HSV space. The starting and the ending colors have the same hue and the same saturation and only vary in value/brightness. One can see that the HSV space is not perceptually linear in lightness, while the JCh space is, as shown by the gray conversion of the colors (shifted on the hue axis for comparison).'

tex = doc.build()
