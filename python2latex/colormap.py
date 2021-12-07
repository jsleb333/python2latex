import numpy as np
import sys

from python2latex import Color
from python2latex.utils import JCh2rgb


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
        """
        Creates a linear color map from a sequence of key color anchors.

        Args:
            color_anchors (Sequence[tuple], optional):
                Sequence of colors used as key points to interpolate colors in-between. Colors should be a sequence of floats or int representing the colors in the appropriate color model. If using a cyclic variable such as the hue, one can use larger or smaller values than the standard range of accepted values to get different color maps (e.g. in hsb, one can start at blue (h=0.5) and end at orange (h=0.1) without passing by green by adding 1 to the hue of the end color (h=1.1)). Cyclic variable are outputed after the modulo is taken.
            anchor_pos (Sequence[float], optional):
                Positions of the color anchors relative to one another on the interval [0,1]. By default, colors are evenly spaced on the interval (e.g. if there are 4 color anchors, the positions will be [0, .33, .66, 1]). Should has the same length as 'color_anchors' and must be in increasing order.
            color_model (str, optional):
                Color model (AKA color space) of the colors. Accepted models are 'RGB', 'rgb', 'hsb', 'Hsb' and 'JCh'. Defaults to 'hsb'. The hue being cyclic, the output color is taken modulo the periodicity. Other color model can be used using the 'rgb' model (which is just a basic linear interpolation) and apply further transformation at the end using the 'color_transform' argument.
            color_transform (Callable[[tuple], tuple], optional):
                Callable that takes an interpolated color as input and outputs a transformed color. Useful for unsupported color models.
        """
        self.color_anchors = color_anchors
        self.anchor_pos = anchor_pos or np.linspace(0, 1, len(color_anchors))
        self.color_model = color_model
        self.color_transform = color_transform or (lambda x: x)

    def interpolate_between_colors(self, frac, color_start, color_end, cyclic=True):
        color = [self._lin_interp(frac, c1, c2) for c1, c2 in zip(color_start, color_end)]

        if self.color_model == 'RGB':
            color = [int(c) for c in color]

        if cyclic:
            if self.color_model == 'hsb':
                color[0] %= 1

            if self.color_model == 'Hsb':
                color[0] %= 360

            if self.color_model == 'JCh':
                color[2] %= 360

        return tuple(color)

    def _lin_interp(self, frac, scalar_1, scalar_2):
        return scalar_1*(1-frac) + scalar_2*frac

    def __call__(self, scalar: float, cyclic: bool = True):
        idx_color_start, idx_color_end = 0, 1
        while scalar > self.anchor_pos[idx_color_end]:
            idx_color_start += 1
            idx_color_end += 1

        interval_width = self.anchor_pos[idx_color_end] - self.anchor_pos[idx_color_start]
        interp_frac = (scalar - self.anchor_pos[idx_color_start])/interval_width

        interp_color = self.interpolate_between_colors(
            interp_frac,
            self.color_anchors[idx_color_start],
            self.color_anchors[idx_color_end],
            cyclic
        )
        if self.color_transform is not None:
            interp_color = self.color_transform(interp_color)

        return interp_color


class Palette:
    """
    We define a Palette as an iterable that yields colors. In this implementation, it yields python2latex Color object ready to be used anywhere.

    This Palette has three modes:
        1. (Default) From a color map, produce dynamically evenly spaced colors from a color map as needed (at each iteration, recomputes all the colors).
        2. From a color map, produce exactly n_colors evenly spaced colors from a color map.
        3. From an iterable of tuples representing colors, produce python2latex Color objects.
    """
    def __init__(self,
                 colors=LinearColorMap(),
                 color_model='hsb',
                 n_colors=None,
                 color_names=None,
                 cmap_range=lambda n_colors: (1/(2*n_colors), 1-1/(2*n_colors)),
                 color_transform=None,
                 max_n_colors=10_000):
        """
        The default behavior of this palette is to create dynamically evenly spaced colors from a color map as needed. One can change this behavior by specifying a fixed number of colors, or by passing an iterable of colors instead of a color map.

        Args:
            colors (Union[Iterable, Callable]):
                Colors used to generate the color palette. If is an iterable, should be a sequence of valid color specifications as explained in the documentation of the Color class. If a callable, the callable should be a color map (i.e. takes as input a scalar and outputs a color in the correct color model in the form of a tuple).
            color_model (str):
                Color model of the colors. See the Color class documentation.
            n_colors (Union[int, None]):
                Number of colors to sample from colors if it is a callable. If colors is a sequence, n_colors is ignored.
            color_names (Union[Iterable[str], None]):
                If colors is a sequence, one can provide the names of the colors to be used in the TeX file. Must be the same length as colors.
            cmap_range (Union[Tuple[float], Callable[[int], Tuple]]):
                Range of the color map used. Ignored if 'colors' is an iterable. If is a tuple of floats, the colors will be sampled from the color map in the interval [cmap_range[0], cmap_range[1]]. The range can be dynamic if it is a callable which takes as input the number of colors and outputs a tuple of floats. The default is dynamic and is designed to spread colors equally in hue space (given that the color maps covers 360 of hue).
            color_transform (Union[Callable, None]):
                Transformation to be applied on the color before the Color object is created. For example, can be used to convert JCh colors from a color map to rgb or hsb colors.
            max_n_colors (int):
                Upper bound on the number of generated colors to avoid infinite iteration when generating dynamically the palette from a color map.
        """
        self.colors = colors
        self.color_model = color_model
        self.n_colors = n_colors
        self.color_names = color_names
        if not callable(cmap_range):
            old_cmap_range = (cmap_range[0], cmap_range[1])
            cmap_range = lambda n_colors: old_cmap_range
        self.cmap_range = cmap_range
        self.color_transform = color_transform or (lambda x: x)
        self.max_n_colors = max_n_colors

        self.tex_colors = []
        if not (callable(self.colors) and self.n_colors is None): # Not a dynamic palette
            self._init_colors()

    def _init_colors(self):
        if callable(self.colors): # Create iterable from color map if needed
            if self.n_colors is not None:
                start, stop = self.cmap_range(self.n_colors)
                colors = [self.colors(frac) for frac in np.linspace(start, stop, self.n_colors)]
            else:
                raise ValueError('Variable n_colors must be set when colors is a color map.')
        else:
            colors = self.colors

        color_names = self.color_names or ('' for _ in colors)
        for color, name in zip(colors, color_names):
            self.tex_colors.append(Color(*self.color_transform(color),
                                            color_name=name,
                                            color_model=self.color_model))

    def __getitem__(self, idx):
        return self.tex_colors[idx]

    def _iter_dynamic(self):
        n_colors = 0
        self.tex_colors = []

        while n_colors < self.max_n_colors:
            n_colors += 1
            start, stop = self.cmap_range(n_colors)
            color_specs = [self.color_transform(self.colors(frac)) for frac in np.linspace(start, stop, n_colors)]

            # Update old colors
            for tex_color, color_spec in zip(self.tex_colors, color_specs):
                tex_color.color_spec = color_spec

            new_color = Color(*color_specs[-1], color_model=self.color_model)
            self.tex_colors.append(new_color)

            yield new_color

    def __iter__(self):
        if callable(self.colors) and self.n_colors is None: # Dynamic palette
            yield from self._iter_dynamic()
        else: # Static palette
            yield from self.tex_colors

    def __len__(self):
        return len(self.tex_colors)


class aube_cmap(LinearColorMap):
    def __init__(self):
        super().__init__(color_anchors=[(26.2, 46.5, 235.2), (71.7, 58.5, 450.1)],
                         color_model='JCh')

class aurore_cmap(LinearColorMap):
    def __init__(self):
        super().__init__(color_anchors=[(14.6, 50.9, 317.0), (83.5, 73.8, 107.3)],
                         color_model='JCh')

class holi_cmap(LinearColorMap):
    def __init__(self):
        super().__init__(color_anchors=[(10, 60, 190),
                                        (35, 74, 350),
                                        (67, 130, 475),
                                        (70, 20, 560)],
                         anchor_pos=[0,.29,.55,1],
                         color_model='JCh')


class aube(Palette):
    def __init__(self, n_colors=None):
        super().__init__(aube_cmap(),
                         color_model='rgb',
                         n_colors=n_colors,
                         cmap_range=lambda n_colors: (0, 1-1/(2*n_colors+2)),
                         color_transform=JCh2rgb)

class aurore(Palette):
    def __init__(self, n_colors=None):
        super().__init__(aurore_cmap(),
                         color_model='rgb',
                         n_colors=n_colors,
                         cmap_range=lambda n_colors: (1/(3*n_colors), 1-1/(3*n_colors)),
                         color_transform=JCh2rgb)

class holi(Palette):
    def __init__(self, n_colors=None):
        super().__init__(holi_cmap(),
                         color_model='rgb',
                         n_colors=n_colors,
                         cmap_range=lambda n_colors: (1/(n_colors+4),1-1/(n_colors**.3+.7)),
                         color_transform=JCh2rgb)



PREDEFINED_CMAPS = {
    'aube': aube_cmap(),
    'aurore': aurore_cmap(),
    'holi': holi_cmap(),
}

class _PredefinedPalettes:
    def __getitem__(self, palette_name):
        for cmap_name in PREDEFINED_CMAPS.keys():
            if palette_name.startswith(cmap_name):
                remainder = palette_name[len(cmap_name):]
                if remainder == '':
                    remainder = None
                else:
                    remainder = int(remainder)
                return getattr(sys.modules[__name__], cmap_name)(remainder)

PREDEFINED_PALETTES = _PredefinedPalettes()

default_palette = holi()
