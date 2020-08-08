# `n3ox_utils` 

## N3OX Python Utilities

This is a personal package of Python utilities for antennas and transmission lines by N3OX. Work in progress.

## Contents
 * `nfanim`: Near-field animations using 
 [`PyNEC`](https://github.com/tmolteno/python-necpp/tree/master/PyNEC) NEC-2++ simulations.
 
 * `tlcalc`: Lossy transmission line calculations. 
 Implements the same transmission line calculations as [Owen Duffy's Transmission Line Calculator](https://owenduffy.net/transmissionline/concept/mptl.htm) for use in Jupyter notebooks and other Python scripts.

 * `plot_tools`
 General matplotlib pyplot setup as well as antenna pattern polar plotting in ARRL style.

From [this PDF](http://www.arrl.org/files/file/ARRL%20Handbook%20Supplemental%20Files/2018%20Edition/Radio%20Supplement.pdf)
 _The modified logarithmic grid used by the ARRL has a system of
concentric grid lines spaced according to the logarithm of 0.89 times
the value of the signal voltage._

 * `pynec_helpers`: Wire input GUI and other helper utilities for working with [`PyNEC`](https://github.com/tmolteno/python-necpp/tree/master/PyNEC)

 ## PyNEC Helpers

 ### Wire Input Widget

This is a GUI wire entry tool using [`ipywidgets`](https://ipywidgets.readthedocs.io/en/latest/)

Wire coordinates and segmentation are entered manually, and calling the WireInput's `return_wire_dicts()` method returns a list of dicts that
can be unpacked into PyNEC's `PyNEC.c_geometry.wire` method. 

 ![WireInput Screenshot showing GUI wire input interface](/docimages/WireInput_Screenshot.png?raw=true)