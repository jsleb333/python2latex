import os
import shutil
from inspect import cleandoc

from python2latex.color import Color
from python2latex.colormap import LinearColorMap, Palette, DynamicPalette


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
        assert cmap._interp_between_colors(.25, color_start, color_end) == (.2,.30000000000000004,.39999999999999997)

        color_end = (1.7,.6,.7)
        for c, a in zip(cmap._interp_between_colors(.75, color_start, color_end), (.3,.5,.6)):
            assert abs(c-a) <= 10e-10

    def test_interp_between_colors_model_Hsb(self):
        cmap = LinearColorMap(color_model='Hsb')
        color_start = (36,.2,.3)
        color_end = (180,.6,.7)
        assert cmap._interp_between_colors(.25, color_start, color_end) == (72,.30000000000000004,.39999999999999997)

        color_end = (612,.6,.7)
        for c, a in zip(cmap._interp_between_colors(.75, color_start, color_end), (108,.5,.6)):
            assert abs(c-a) <= 10e-10

    def test_interp_between_colors_model_JCh(self):
        cmap = LinearColorMap(color_model='JCh')
        color_start = (.2,.3,36)
        color_end = (.6,.7,180)
        assert cmap._interp_between_colors(.25, color_start, color_end) == (.30000000000000004,.39999999999999997,72)

        color_end = (.6,.7,612)
        for c, a in zip(cmap._interp_between_colors(.75, color_start, color_end), (.5,.6,108)):
            assert abs(c-a) <= 10e-10

    def test_call(self):
        pass