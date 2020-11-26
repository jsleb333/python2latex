import os
import shutil
from inspect import cleandoc

from python2latex.color import Color
from python2latex.colormap import LinearColorMap, Palette, DynamicPalette


def areclose(tuple1, tuple2):
    return all(abs(c-a) <= 10e-10 for c, a in zip(tuple1, tuple2))

class TestLinearColorMap:
    def test_lin_interp(self):
        cmap = LinearColorMap('rbg')
        assert cmap._lin_interp(.5, 1, 2) == 1.5
        assert cmap._lin_interp(.2, 20, 10) == 18
        assert cmap._lin_interp(.5, 0, .8) == .4
        assert cmap._lin_interp(.5, .75, 1.25) == 1
        assert cmap._lin_interp(.1, -.25, .25) == -.2
        assert cmap._lin_interp(.1, 25, 125) == 35
        assert cmap._lin_interp(.5, 280, 160) == 220

    def test_interp_between_colors_model_rgb(self):
        cmap = LinearColorMap(color_model='rgb')
        color_start = (.1,.2,.3)
        color_end = (.5,.6,.7)
        assert cmap._interp_between_colors(.5, color_start, color_end) == (.3,.4,.5)

    def test_interp_between_colors_model_RGB(self):
        cmap = LinearColorMap(color_model='RGB')
        color_start = (1,2,3)
        color_end = (10,11,12)
        assert cmap._interp_between_colors(.25, color_start, color_end) == (3,4,5)

    def test_interp_between_colors_model_hsb(self):
        cmap = LinearColorMap(color_model='hsb')
        color_start = (.1,.2,.3)
        color_end = (.5,.6,.7)
        assert areclose(cmap._interp_between_colors(.25, color_start, color_end), (.2,.3,.4))
        color_end = (1.7,.6,.7)
        assert areclose(cmap._interp_between_colors(.75, color_start, color_end), (.3,.5,.6))

    def test_interp_between_colors_model_Hsb(self):
        cmap = LinearColorMap(color_model='Hsb')
        color_start = (36,.2,.3)
        color_end = (180,.6,.7)
        assert areclose(cmap._interp_between_colors(.25, color_start, color_end), (72,.3,.4))
        color_end = (612,.6,.7)
        assert areclose(cmap._interp_between_colors(.75, color_start, color_end), (108,.5,.6))

    def test_interp_between_colors_model_JCh(self):
        cmap = LinearColorMap(color_model='JCh')
        color_start = (.2,.3,36)
        color_end = (.6,.7,180)
        assert areclose(cmap._interp_between_colors(.25, color_start, color_end), (.3,.4,72))
        color_end = (.6,.7,612)
        assert areclose(cmap._interp_between_colors(.75, color_start, color_end), (.5,.6,108))

    def test_2_anchors(self):
        c_start, c_stop = (0,0,0), (1,1,1)
        cmap = LinearColorMap(color_anchors=[c_start, c_stop])
        assert cmap(.25) == (.25, .25, .25)

    def test_3_anchors_no_positions(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        cmap = LinearColorMap(color_anchors=[c_start, c_mid, c_stop])
        assert cmap(.5) == c_mid
        assert cmap(.25) == (.15,.15,.15)

    def test_3_anchors_with_positions(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        cmap = LinearColorMap(color_anchors=[c_start, c_mid, c_stop],
                              anchor_pos=[0,.75,1])
        assert cmap(.75) == c_mid
        assert areclose(cmap(.5), (.2,.2,.2))

    def test_color_transform(self):
        c_start, c_stop = (0,0,0), (1,1,1)
        transform = lambda c: (c[0], c[1]/2, c[2]+100)
        cmap = LinearColorMap(color_anchors=[c_start, c_stop],
                              color_transform=transform)
        assert areclose(cmap(.5), (.5, .25, 100.5))


class TestPalette:
    def test_color_from_list(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        colors = [c_start, c_mid, c_stop]

        palette = Palette(colors)
        for i, color in enumerate(palette):
            assert color.color_spec == colors[i]
            assert color.color_model == 'hsb'

        palette = Palette(colors, color_model='rgb')
        for i, color in enumerate(palette):
            assert color.color_spec == colors[i]
            assert color.color_model == 'rgb'

    def test_color_from_iterable_with_names(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        colors = [c_start, c_mid, c_stop]
        names = ['mycolor1', 'col2', 'col3']
        palette = Palette((c for c in colors), color_names=names)

        for i, color in enumerate(palette):
            assert color.color_spec == colors[i]
            assert color.color_name == names[i]

    def test_color_transform(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        colors = [c_start, c_mid, c_stop]
        transform = lambda c: (c[0], c[1]/2, c[2]+100)

        palette = Palette(colors, color_transform=transform)
        palette = Palette(colors, color_transform=transform)
        for i, color in enumerate(palette):
            assert color.color_spec == transform(colors[i])
            assert color.color_model == 'hsb'

    def test_color_from_cmap(self):
        c_start, c_mid, c_stop = (0,0,0), (.3,.3,.3), (1,1,1)
        color_anchors = [c_start, c_mid, c_stop]
        cmap = LinearColorMap(color_anchors=color_anchors, color_model='rgb')

        palette = Palette(cmap, n_colors=3, color_model='rgb')
        for i, color in enumerate(palette):
            assert color.color_spec == color_anchors[i]

        palette = Palette(cmap, n_colors=5, color_model='rgb')
        for color, answer in zip(palette, (c_start, (.15,.15,.15), c_mid, (.65,.65,.65), c_stop)):
            assert color.color_spec == answer

