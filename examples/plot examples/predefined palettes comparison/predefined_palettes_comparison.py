from python2latex.document import Section
from python2latex.tex_base import TexObject, build
from python2latex import Document, TexEnvironment
from python2latex import Plot, Palette, LinearColorMap, predefined_cmaps, predefined_palettes
from python2latex.utils import JCh2rgb, rgb2JCh, hsb2JCh, JCh2hsb
import numpy as np
from matplotlib.colors import hsv_to_rgb


class Node(TexObject):
    def __init__(self, pos, text='', fill=None, minimum_width='.9cm', minimum_height='.9cm'):
        super().__init__(self)
        self.pos = pos
        self.text = text
        self.fill = fill or 'none'
        self.minimum_width = minimum_width
        self.minimum_height = minimum_height

    def build(self):
        return f'\\node[fill={build(self.fill, self)}, minimum width={self.minimum_width}, minimum height={self.minimum_height}] at {self.pos} {{{self.text}}};'


def plot_palette(doc, cmap, palette):
    # Create plots to compare the cmaps
    plot = doc.new(Plot(plot_path=filepath,
                        plot_name=filename+'_color',
                        lines='3pt',
                        height='6cm',
                        ))

    n_colors = 25
    interp_param = np.linspace(0, 1, n_colors+1)
    h_start = cmap.color_anchors[0][2]
    h_end = cmap.color_anchors[-1][2]

    def unfold_hue(h):
        if (h_start-0.001 <= h <= h_end+0.001) or (h_end-0.001 <= h <= h_start+0.001):
            return h
        else:
            return (h - h_start + 0.01) % 360 + h_start - 0.01

    for i, JCh_color in zip(range(n_colors), palette):
        # Plot the hue(h)-lightness(J) space
        J1, C1, h1 = cmap(interp_param[i])
        J2, C2, h2 = cmap(interp_param[i+1])
        plot.add_plot([unfold_hue(h1), unfold_hue(h2)], [J1, J2], color=JCh_color, line_cap='round')

    plot.x_label = 'Hue angle $h$'
    plot.y_label = 'Lightness $J$'


    for n_colors in [2, 3, 4, 5, 6, 9]:
        doc += f'{n_colors} colors: \\hspace{{10pt}}'
        tikzpicture = doc.new(TexEnvironment('tikzpicture'))
        for i, color in zip(range(n_colors), palette):
            tikzpicture += Node((i,0), fill=color)
        doc += '\n'



if __name__ == "__main__":
    # Create document
    filepath = './examples/plot examples/predefined palettes comparison/'
    filename = 'predefined_palettes_comparison'
    doc = Document(filename, doc_type='article', filepath=filepath)

    # plot_palette(doc, predefined_cmaps['aurore'], predefined_palettes['aurore'])

    # Let us create a color map in the JCh color model, which parametrizes the colors according to human perception of colors instead of actual physical properties of light.
    # Choose the color anchors of the color map defined in the JCh color space
    color1_hsb = [.4, .99, .35]
    color1_JCh = hsb2JCh(color1_hsb, False)
    color2_hsb = [1.3, .99, .9]
    color2_JCh = hsb2JCh(color2_hsb, False)

    color1_JCh = [28, 50, 200.1]
    color2_JCh = [50, 74, 380]
    color3_JCh = [80, 97, 470]
    print(color1_JCh, color2_JCh, color3_JCh)

    # Add full hue circle for color interpolation
    # color2_JCh[2] += 360

    cmap = LinearColorMap(color_anchors=[color1_JCh, color2_JCh, color3_JCh],
                          anchor_pos=[0,.55,1],
                          color_model='JCh')
    pal = Palette(cmap,
                  color_model='rgb',
                  cmap_range=lambda n_colors: (1/(2*n_colors**.8),1-1/(2*n_colors+1)),
                  color_transform=JCh2rgb)
    plot_palette(doc, cmap, pal)

    tex = doc.build()
