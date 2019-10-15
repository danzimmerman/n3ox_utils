# -*- coding: utf-8 -*-

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import numpy as np
import cycler
import string

plot_colors = ['#000000', '#0072bd', '#d95319', '#edb120', '#7e2f8e',
               '#77ac30', '#4dbeee', '#a2142f', '#adbc01', '#2302cd',
               '#ff4d3b', '#836dff', '#c16f66', '#7dd1b1', '#e5e840',
               '#2f637c', '#6d1e1e', '#6d777c', '#4b5e21', '#39215e',
               '#917151', '#91517a', '#516591']


def init_pyplot_defaults(plt):
    '''
    Initializes defaults for 
    matplotlib.pyplot instance
    '''
    color_cycle = cycler.cycler('color', plot_colors)
    plt.rcParams.update({'figure.figsize': (15.0, 9.0),
                         'font.size': 16,
                         'lines.linewidth': 2,
                         'lines.markersize': 10.0,
                         'axes.prop_cycle': color_cycle,
                         'savefig.dpi': 300,
                         # 'image.cmap':'PuOr_r',
                         })
    return plt


def init_gridspec_fig(plt, nrows=1, ncols=2, figsize=(15, 9), **gsopts):
    '''
    Initializes a Matplotlib gridspec figure with 
    nrows rows and ncols columns and returns a 
    figure object.

    Requires a matplotlib.pyplot module instance as the first argument

    The figure object has axes
    fig.axa, fig.axb, etc and the gridspec object is fig.gs

    Accepts gridspec kwarg options.
    '''
    fig = plt.figure(figsize=figsize)
    fig.gs = gridspec.GridSpec(ncols=ncols, nrows=nrows, figure=fig, **gsopts)
    fig.ncols = int(ncols)
    fig.nrows = int(nrows)

    for i in range(0, fig.nrows):
        for j in range(0, fig.ncols):
            fig.add_subplot(fig.gs[i, j])

    for ax, letter in zip(fig.axes, string.ascii_lowercase):
        setattr(fig, 'ax'+letter, ax)

    return fig


def init_ARRL_polar_fig(plt, rtickdB=None, **figopts):
    '''
    Initializes a Matplotlib figure with a polar-projection
    subplot and sets radial dB divisions suitable for an 
    ARRL-style polar antenna plot.

    Returns a Matplotlib figure fig with one axis, fig.axa
    '''
    if not 'figsize' in figopts.keys():
        figopts.update({'figsize': (15, 15)})

    if not rtickdB:
        rtickdB = np.array(
            [0.0, -5.0, -10.0, -15.0, -20.0, -30.0, -40.0, -50.0])
    rtickV = 10.0**(rtickdB/20.0)

    fig = plt.figure(**figopts)

    # --- compute radial ticks and their text labels, omit labels under -40dB ---
    fig.rticklocs = ARRL_scaleV(rtickV)
    fig.rticklabels = [f'{dBval:.0f}dB' if dBval > -
                       40.0 else '' for dBval in rtickdB]

    # --- create a polar axis ---
    fig.axa = fig.add_subplot(111, projection='polar')
    fig.patch.set_alpha(0.0)
    maxr = 1.01
    minr = ARRL_scaleV(1e-5)
    fig.axa.set_rlim(minr, maxr)
    fig.axa.set_yticks(fig.rticklocs)
    fig.axa.set_yticklabels(fig.rticklabels)
    fig.axa.set_rlabel_position(90)

    return fig


def add_ARRL_polar_plot(thdata, powerdata, ax=None, **plotopts):
    '''
    Scales powerdata to voltage units, applies ARRL scaling, and 
    plot on polar axes ax against angle thdata.

    Plot on an axis set up by init_ARRL_polar_fig()
    '''
    normpower = powerdata/np.max(powerdata)
    nvdata = np.sqrt(normpower)
    rdata = ARRL_scaleV(nvdata)
    ax.plot(thdata, rdata, **plotopts)


def ARRL_scaleV(voltdata):
    '''
    Applies ARRL radial scaling function to
    data in normalized voltage units.
    '''
    return 0.89**(-10*np.log10(voltdata))
