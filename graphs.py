import matplotlib as mpl
from colors import *

mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['text.color'] = text_color
mpl.rcParams['axes.labelcolor'] = text_color
mpl.rcParams['xtick.color'] = text_color
mpl.rcParams['ytick.color'] = text_color
mpl.rcParams['figure.facecolor'] = grey
mpl.rcParams['axes.facecolor'] = grey
mpl.rcParams['axes.edgecolor'] = text_color

class RegrMagic(object):
    def __init__(self, calc):
        self.x = 0
        self.calc = calc

    def __call__(self):
        self.x += 1
        return self.x, self.calc.dpm_by_name