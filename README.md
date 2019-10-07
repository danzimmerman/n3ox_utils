# `n3ox_utils` 

## N3OX Python Utilities

This is a personal package of Python utilities for antennas and transmission lines by N3OX.

## Contents
 * `nfanim`: Near-field animations using 
 [`PyNEC`](https://github.com/tmolteno/python-necpp/tree/master/PyNEC) NEC-2++ simulations.
 
 * `tlcalc`: Lossy transmission line calculations.

 * `pynec_helpers`: Wire input GUI and other helper utilities for working with [`PyNEC`](https://github.com/tmolteno/python-necpp/tree/master/PyNEC)

 ## PyNEC Helpers

 ### Wire Input Widget

This is a GUI wire entry tool using [`ipywidgets`](https://ipywidgets.readthedocs.io/en/latest/)

Wire coordinates and segmentation are entered manually, and calling the WireInput's `return_wire_dicts()` method returns a list of dicts that
can be unpacked into PyNEC's `PyNEC.c_geometry.wire()` method. 


 ![WireInput Screenshot showing GUI wire input interface](/docimages/WireInput_Screenshot.png?raw=true)