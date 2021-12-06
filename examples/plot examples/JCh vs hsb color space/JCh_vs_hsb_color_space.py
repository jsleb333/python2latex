from python2latex import Document, Plot, Color, Palette, LinearColorMap
from python2latex.utils import rgb2gray
import numpy as np
from colorspacious import cspace_converter, cspace_convert
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
"""
In this example, we explore color maps and palettes.

A color map is understood as a function taking as input a scalar between 0 and 1 and outputs and color in some format. The class LinearColorMap takes as input a sequence of colors and interpolates linearly the colors in-between to yield a color map.

A palette is simply a collection of colors. python2latex defines a Palette object that handles the boilerplating related to the creation of Color objects from a sequence of colors or from a color map. The Palette object modifies dynamically the colors generated according to the number of colors needed so that colors never repeat, as opposed to a standard palette which loops back to the beginning when colors are exhausted.
"""
# First create a conversion function
JCh2rgb = lambda color: np.clip(cspace_convert(color, 'JCh', 'sRGB1'), 0, 1)
rgb2JCh = cspace_converter('sRGB1', 'JCh')

# Create document
filepath = './examples/plot examples/JCh vs hsb color space/'
filename = 'JCh_vs_hsb_color_space'
doc = Document(filename, doc_type='article', filepath=filepath)

# Let us create a color map in the JCh color model, which parametrizes the colors according to human perception of colors instead of actual physical properties of light.
# Choose the color anchors of the color map defined in the JCh color space
color1_hsb = [.31, .9, .3]
color1_JCh = rgb2JCh(hsv_to_rgb(color1_hsb))
color2_hsb = [.31, .9, 1] # Same color with different brightness
color2_JCh = rgb2JCh(hsv_to_rgb(color2_hsb))

# Add full hue circle for color interpolation
color2_hsb[0] += 1
color2_JCh[2] += 360

# Create the color maps
cmap_JCh = LinearColorMap(color_anchors=[color1_JCh, color2_JCh],
                          color_model='JCh')
cmap_hsb = LinearColorMap(color_anchors=[color1_hsb, color2_hsb],
                          color_model='hsb')

n_colors = 50
palette_JCh = Palette(
    cmap_JCh,
    color_model='rgb',
    cmap_range=(0,1),
    n_colors=n_colors,
    color_transform=JCh2rgb
)
palette_JCh_lightness = Palette(
    cmap_JCh,
    color_model='gray',
    cmap_range=(0,1),
    n_colors=n_colors,
    color_transform=lambda color: (color[0]/100,)
)
palette_JCh_gray = Palette(
    cmap_JCh,
    color_model='gray',
    cmap_range=(0,1),
    n_colors=n_colors,
    color_transform=lambda color: (rgb2gray(JCh2rgb(color)),)
)

palette_hsb = Palette(
    cmap_hsb,
    color_model='hsb',
    cmap_range=(0,1),
    n_colors=n_colors
)
palette_hsb_lightness = Palette(
    cmap_hsb,
    color_model='gray',
    cmap_range=(0,1),
    n_colors=n_colors,
    color_transform=lambda color: (rgb2JCh(hsv_to_rgb(color))[0]/100,)
)
palette_hsb_gray = Palette(
    cmap_hsb,
    color_model='gray',
    cmap_range=(0,1),
    n_colors=n_colors,
    color_transform=lambda color: (rgb2gray(hsv_to_rgb(color)),)
)

# Create plots to compare the cmaps
plot_color = doc.new(Plot(plot_path=filepath,
                          plot_name=filename+'_color',
                          lines='3pt',
                          height='6cm',
                          ))
plot_lightness = doc.new(Plot(plot_path=filepath,
                              plot_name=filename+'_lightness',
                              lines='3pt',
                              height='6cm',
                              ))
plot_gray = doc.new(Plot(plot_path=filepath,
                         plot_name=filename+'_gray',
                         lines='3pt',
                         height='6cm',
                         ))

def unfold_hue(h):
    """Adds 360 degrees of hue when the hue value is less than the starting value to make sure the plots are continuous."""
    h_start = color1_JCh[2] - 1/(10*n_colors) # The negative term is for numerical precision
    return (h - h_start)%360 + h_start

interp_param = np.linspace(0, 1, n_colors+1)
for i, (JCh_color, JCh_lightness, JCh_gray,
        hsb_color, hsb_lightness, hsb_gray) in enumerate(zip(palette_JCh,
                                                             palette_JCh_lightness,
                                                             palette_JCh_gray,
                                                             palette_hsb,
                                                             palette_hsb_lightness,
                                                             palette_hsb_gray,
                                                             )):
    # Plot JCh linear interpolation in the hue(h)-lightness(J) space
    J1, C1, h1 = cmap_JCh(interp_param[i])
    J2, C2, h2 = cmap_JCh(interp_param[i+1])
    plot_color.add_plot([unfold_hue(h1), unfold_hue(h2)], [J1, J2], color=JCh_color, line_cap='round')
    # Plot the same in gray levels, first using the lightness parameter J, then using the rgb2gray functions correcting the gamma compression used in the rgb space.
    plot_lightness.add_plot([unfold_hue(h1), unfold_hue(h2)], [J1, J2], color=JCh_lightness, line_cap='round')

    gray1 = rgb2gray(JCh2rgb((J1, C1, h1)))
    gray2 = rgb2gray(JCh2rgb((J2, C2, h2)))
    plot_gray.add_plot([unfold_hue(h1), unfold_hue(h2)], [gray1, gray2], color=JCh_gray, line_cap='round')

    # Plot the hsb linear interpolation in h-J space
    J1, C1, h1 = rgb2JCh(hsv_to_rgb(cmap_hsb(interp_param[i])))
    J2, C2, h2 = rgb2JCh(hsv_to_rgb(cmap_hsb(interp_param[i+1])))
    plot_color.add_plot([unfold_hue(h1), unfold_hue(h2)], [J1, J2], color=hsb_color, line_cap='round')
    # Plot the same in gray levels, first using the lightness parameter J, then using the rgb2gray functions correcting the gamma compression used in the rgb space.
    gray_level = Color(JCh_color.color_spec[0], color_model='gray')
    plot_lightness.add_plot([unfold_hue(h1), unfold_hue(h2)], [J1, J2], color=hsb_lightness, line_cap='round')

    gray1 = rgb2gray(JCh2rgb((J1, C1, h1)))
    gray2 = rgb2gray(JCh2rgb((J2, C2, h2)))
    plot_gray.add_plot([unfold_hue(h1), unfold_hue(h2)], [gray1, gray2], color=hsb_gray, line_cap='round')

for plot in [plot_color, plot_lightness, plot_gray]:
    plot.axis += r'\node at (120,480) {Linear interp. in JCh space};'
    plot.axis += r'\node at (280,140) {Linear interp. in HSV space};'

    plot.x_label = 'Hue angle $h$'
    plot.y_label = 'Lightness $J$'

plot_gray.y_label = 'Gray level'

doc += """Comparison of linear interpolation of colors in \\texttt{JCh} and \\texttt{hsb} spaces. The starting and the ending colors have the same hue and saturation, and only vary in brightness.
The top figure illustrates a linear color interpolation in the JCh and hsb space plotted on the hue h and lightness J axes.
The middle figure uses the lightness J axis to plot the same figure in gray level, while the last figure plots both interpolation using a conventional rgb to gray levels that consider gamma compression.

One can see that in the \\texttt{JCh}, the lightness J correlates linearly with human perception of brightness.
On the other hand, linear variations in the \\texttt{hsb} space is not linear with the human perception of brightness."""

tex = doc.build()
