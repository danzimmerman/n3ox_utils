# -*- coding: utf-8 -*-

# Copyright (c) 2019 Daniel S. Zimmerman, N3OX

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import numpy as np
import PyNEC
import json
import matplotlib.pyplot as mplt
import n3ox_utils.plot_tools as pltools
import colorcet as cc


class CartesianFieldAnimation(object):
    '''
    Class to generate animated movies of one period of a complex
    amplitude field defined on a cartesian grid.
    '''

    def __init__(self, X, Y, fieldamp,
                 nframes=100, pyplot_plt=None, scalefunc=None):
        '''
        Initializes an animation object with 

         X, Y: Cartesian coordinates as from np.meshgrid()

         fieldamp: Complex amplitude field from PyNEC
                  simulation.

         nframes: Number of phase frames to compute.

         pyplot_plt: optional, configured matplotlib.pyplot instance
         If this is not passed in, self.plt will be initialized
         using pyplot defaults from n3ox_utils.plot_tools

         scalefunc: optional, function to scale the real part of the field.

        '''
        # --- default to unscaled ---
        if scalefunc:
            self.scalefunc = scalefunc
        else:
            self.scalefunc = lambda x: x

        self.X = X
        self.Y = Y
        self.A = fieldamp
        self.nf = nframes
        self.phase = np.linspace(0, 2*np.pi, self.nf)
        self.Ff = self.A[:, :, np.newaxis]*np.exp(-1j*self.phase)
        self.sCf = self.scalefunc(self.Ff.real/np.max(np.abs(self.Ff)))
        self.clims = [np.min(self.sCf), np.max(self.sCf)]

        if not pyplot_plt:
            self.plt = mplt
            pltools.init_pyplot_defaults(self.plt)
        else:
            self.plt = pyplot_plt

    def plot_preview_frames(self, framelist=None, **pcolor_options):
        '''
        Plots a grid of pcolor preview frames matching the frame list. 

        Returns a figure object containing axes
         fig.axa
         fig.axb

         etc.

         Accepts matplotlib.pyplot plt.pcolor kwarg options.

         If cmap argument is passed in after required keyword args, 
         the plot will use a matplotlib colormap.

         Otherwise, a colormap from https://colorcet.pyviz.org/
         matching colorcet_cmap_name will be used, defaulting to 'bky'.

        '''

        if not 'cmap' in pcolor_options.keys():
            print(f'Using colorcet cmap "bky"')
            pcolor_options.update({'cmap': cc.cm['bky']})
        else:

            cmname = pcolor_options['cmap']
            try:
                pcolor_options.update({'cmap': cc.cm[cmname]})
                print(f'Using colorcet colormap "{cmname}"')
            except:
                print(f'Trying "{cmname}" as a matplotlib colormap name.')

        nplots = len(framelist)
        # --- compute a figure size that matches the plots' aspect ratios ---

        width = 15.0
        ncols = 5
        nrows = int(np.ceil(nplots/ncols))
        Xsize = np.max(self.X)-np.min(self.X)
        Ysize = np.max(self.Y)-np.min(self.Y)
        height = Ysize/Xsize * width

        # --- initialize a gridspec figure using n3ox_utils.plot_tools ---
        fig = pltools.init_gridspec_fig(self.plt,
                                        nrows=nrows,
                                        ncols=ncols,
                                        figsize=(width, height))
        # --- plot frames ---
        for fnum, ax in zip(framelist, fig.axes):
            p = ax.pcolor(self.X, self.Y,
                          self.sCf[:, :, fnum],
                          **pcolor_options)
            ax.axis('equal')
            ax.axis('off')
            p.set_clim(self.clims)

        return fig

    def save_anim(self, nframes):
        '''

        '''
        print('save_anim() not implemented yet')
        pass
