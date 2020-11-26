import numpy as np
from numpy.lib.arraysetops import isin

from python2latex import Color


class LinearColorMap:
    """
    A colormap is a function which takes as input a float between 0 and 1, and outputs a color.

    This implementation takes as input a sequence of 2 or more colors and interpolates linearly the colors in between. Note that the color model (AKA color space) chosen will influence the result.

    Beware that the human eye does not perceive all colors equally. As an example, the perceived brightness of a color is not the average of the 'rgb' channels. Furthermore, varying the hue in the 'hsb' color model while keeping the saturation and the brightness fixed will generate colors with varying perceived brightness. For this reason, we suggest working in the JCh axes of the CIECAM02 color model, where J is the lightness (similar to brightness), C the chroma (similar to saturation) and h the hue. This color model is designed to change the perceived properties of the colors linearly with J, C and h. The Python 'colorspacious' package provides the tool to convert rgb colors to JCh colors and vice versa.

    When designing color maps to communicate information, bear in mind that some people are colorblind. Try to avoid green with red. If you want to use these two colors at the same time, use them with different brightness. It is also a good idea to try to have different *perceived* brightness across all the color map, which will help everyone differenciate the colors, even when printed in shades of gray.
    """
    def __init__(self,
                 color_anchors=[(0.5, 1, 0.5), (1.07, 0.7, 1)],
                 anchor_pos=None,
                 color_model='hsb',
                 color_transform=None):
        self.color_anchors = color_anchors
        self.anchor_pos = anchor_pos or np.linspace(0, 1, len(color_anchors))
        self.color_model = color_model
        self.color_transform = color_transform or (lambda x: x)

    def _interp_between_colors(self, frac, color_start, color_end):
        color = [self._lin_interp(frac, c1, c2) for c1, c2 in zip(color_start, color_end)]

        if self.color_model == 'RGB':
            color = [int(c) for c in color]

        if self.color_model == 'hsb':
            color[0] %= 1

        if self.color_model == 'Hsb':
            color[0] %= 360

        if self.color_model == 'JCh':
            color[2] %= 360

        return tuple(color)

    def _lin_interp(self, frac, scalar_1, scalar_2):
        return scalar_1*(1-frac) + scalar_2*frac

    def __call__(self, scalar):
        idx_color_start, idx_color_end = 0, 1
        while scalar > self.anchor_pos[idx_color_end]:
            idx_color_start += 1
            idx_color_end += 1

        interval_width = self.anchor_pos[idx_color_end] - self.anchor_pos[idx_color_start]
        interp_frac = (scalar - self.anchor_pos[idx_color_start])/interval_width

        interp_color = self._interp_between_colors(interp_frac,
                                                   self.color_anchors[idx_color_start],
                                                   self.color_anchors[idx_color_end])
        if self.color_transform is not None:
            interp_color = self.color_transform(interp_color)

        return interp_color


class Palette:
    def __init__(self,
                 colors,
                 color_model='hsb',
                 n_colors=None,
                 color_names=None,
                 color_transform=None):
        """
        Args:
            colors (Union[Iterable, Callable]): Colors used to generate the color palette. If is an iterable, should be a sequence of valid color specifications as explained in the documentation of the Color class. If a callable, the callable should be a color map (i.e. takes as input a scalar and outputs a color in the correct color model in the form of a tuple).

            color_model (str): Color model of the colors. See the Color class documentation.

            n_colors (Union[int, None]): Number of colors to sample from colors if it is a callable. If colors is a sequence, n_colors is ignored.

            color_names (Union[Iterable[str], None]): If colors is a sequence, one can provide the names of the colors to be used in the TeX file. Must be the same length as colors.

            color_transform (Union[Callable, None]): Transformation to be applied on the color before the Color object is created. For example, can be used to convert JCh colors from a color map to rgb or hsb colors.
        """
        self.colors = colors
        self.color_model = color_model
        self.n_colors = n_colors
        self.color_names = color_names
        self.color_transform = color_transform or (lambda x: x)

    def __iter__(self):
        if callable(self.colors):
            color_names = self.color_names or ['' for _ in range(self.n_colors)]
            for frac, color_name in zip(np.linspace(0, 1, self.n_colors), color_names):
                yield Color(*self.color_transform(self.colors(frac)),
                            color_name=color_name,
                            color_model=self.color_model)
        else:
            color_names = self.color_names or ['' for _ in range(len(self.colors))]
            for color, color_name in zip(self.colors, color_names):
                yield Color(*self.color_transform(color),
                            color_name=color_name,
                            color_model=self.color_model)


class DynamicPalette:
    def __init__(self,
                 color_map,
                 color_model='hsb',
                 color_transform=None,
                 cmap_range=lambda n_colors: (1/(n_colors+1), 1-1/(n_colors+1)),
                 max_n_colors=100_000):
        """
        Args:
            color_map (Callable): Color map used to generate the color palette (i.e. takes as input a scalar and outputs a color in the correct color model).

            color_model (str): Color model of the colors. See the Color class documentation.

            color_transform (Union[Callable, None]): Transformation to be applied on the color before the Color object is created. For example, can be used to convert JCh colors from a color map to rgb colors.

            cmap_range (Tuple[Union[Callable, float]]): Range of the color map used. If a tuple of floats, the colors will be sampled from the color map in the interval [buffer[0], buffer[1]]. The range can be dynamic if it is a callable which takes as input the number of colors and outputs a tuple of floats.

            max_n_colors (int): Upper bound on the number of generated colors to avoid infinite iteration.
        """
        self.color_map = color_map
        self.color_model = color_model
        self.color_transform = color_transform or (lambda x: x)
        if not callable(cmap_range):
            old_cmap_range = (cmap_range[0], cmap_range[1])
            cmap_range = lambda n_colors: old_cmap_range
        self.cmap_range = cmap_range
        self.n_colors = 0
        self.tex_colors = []
        self.max_n_colors = max_n_colors


    def __iter__(self):
        self.n_colors = 0
        self.tex_colors = []

        while self.n_colors < self.max_n_colors:
            self.n_colors += 1
            start, stop = self.cmap_range(self.n_colors)
            color_specs = [self.color_transform(self.color_map(frac)) for frac in np.linspace(start, stop, self.n_colors)]

            # Update old colors
            for tex_color, color_spec in zip(self.tex_colors, color_specs):
                tex_color.color_spec = color_spec

            new_color = Color(*color_specs[-1], color_model=self.color_model)
            self.tex_colors.append(new_color)

            yield new_color
