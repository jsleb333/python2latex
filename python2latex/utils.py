import sys
import os
import subprocess
import numpy as np
from colorspacious import cspace_converter, cspace_convert
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv


def open_file_with_default_program(filename, filepath):
    cwd = os.getcwd()
    try:
        os.chdir(filepath)
        if sys.platform.startswith('linux'):
            open_command = 'xdg-open'
            subprocess.run([open_command, filename + ".pdf"])
        else:
            open_command = 'start'
            subprocess.run([open_command, filename + ".pdf"], shell=True)
    finally:
        os.chdir(cwd)


def gamma_decompress(rgb):
    """
    Make pixel values perceptually linear.
    """
    rgb_lin = ((rgb + 0.055) / 1.055) ** 2.4
    i_low = np.where(rgb <= .04045)
    rgb_lin[i_low] = rgb[i_low] / 12.92
    return rgb_lin


def gamma_compress(gray_lin):
    """
    Make pixel values display-ready.
    """
    if gray_lin <= .0031308:
        return 12.92 * gray_lin
    else:
        return 1.055 * gray_lin ** (1 / 2.4) - 0.055


def rgb2gray_linear(rgb):
    """
    Convert *linear* RGB values to *linear* grayscale values.
    """
    return 0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]


def rgb2gray(rgb):
    return gamma_compress(rgb2gray_linear(gamma_decompress(np.array(rgb))))


def JCh2rgb(JCh):
    J, C, h = JCh
    return np.clip(cspace_convert((J, C, h%360), 'JCh', 'sRGB1'), 0, 1)

def rgb2JCh(rgb):
    return cspace_convert(rgb, 'sRGB1', 'JCh')


def JCh2hsb(JCh, restrict_hue_domain=True):
    J, C, h = JCh
    hue = h % 360
    hsb = rgb_to_hsv(JCh2rgb((J, C, hue)))
    if not restrict_hue_domain:
        hsb[0] += (h - hue)/360
    return hsb

def hsb2JCh(hsb, restrict_hue_domain=True):
    h, s, b = hsb
    hue = h % 1
    JCh = rgb2JCh(hsv_to_rgb((hue, s, b)))
    if not restrict_hue_domain:
        JCh[2] += (h - hue)*360
    return JCh