# -*- coding: utf-8 -*-

# NEC-2 Card/Code References

# Here are some references I'm consulting while working with PyNEC. I haven't done NEC decks before, only EZNEC, so I'm learning as I go.
# http://www.antentop.org/w4rnl.001/necdeck.html
# https://www.nec2.org/part_3/cards/
# http://tmolteno.github.io/necpp/classnec__context.html#pub-methods
# http://tmolteno.github.io/necpp/libnecpp_8h.html

'''
This module is a collection of PyNEC helper utilities, mostly to provide a 
named-variable interface to the most common PyNEC things I use.
'''
import ipywidgets
from IPython.display import display
import urllib.request as urlrq
import numpy as np


def pack_ex_card_args(**kwargs):
    '''
    Takes named excitation parameters as keyword args and returns
    an ordered list of arguments for the .ex_card() method of 
    a PyNEC NEC context.

    See http://tmolteno.github.io/necpp/classnec__context.html#ae3bc2cfa92d14dfa02028ca88fbfad19
    and https://www.nec2.org/part_3/cards/ex.html

    Common arguments to all excitation types:

    excitation_type:
      voltage
      linear_wave
      r_circ_wave
      l_circ_wave
      current
      voltage_disc (current-slope-discontinuity voltage source)

    Arguments for voltage or voltage_disc (category A):

    source_tag: 
      integer tag for the excited wire
    source_seg: 
      integer tag for the excited segment on the wire
    ereal:
      real part of the voltage
    eimag:
      imaginary part of the voltage

    Wave and current excitations (category B & C) not yet implemented.

    '''
    # --- dict of integer flags ---
    exints = {'voltage': 0, 'linear_wave': 1,
              'r_circ_wave': 2, 'l_circ_wave': 3,
              'current': 4, 'voltage_disc': 5}

    volt_exs = [key for key in exints.keys() if key.count('voltage')]
    wave_exs = [key for key in exints.keys() if key.count('wave')]
    curr_exs = [key for key in exints.keys() if key.count('current')]

    # --- Check for invalid arguments ---
    # TODO: collect all valid keys and throw errors if any are missing

    excat = None  # category A, B, C to harmonize with PyNEC and NEC-2 docs
    extype = kwargs['excitation_type']
    if extype in volt_exs:
        excat = 'A'
    elif extype in wave_exs:
        excat = 'B'
    elif extype in curr_exs:
        excat = 'C'
    else:
        emsg = ('Invalid excitation_type {0}. '
                'Supply one of {1}')
        evals0 = extype
        evals1 = ', '.join(exints.keys())
        raise UserWarning(emsg.format(evals0, evals1))

    # --- Pack and return the argument list ---
    args = [0]*10  # might need to be 11 if all are working
    if excat == 'A':
        args[0] = exints[extype]  # I1
        args[1] = kwargs['source_tag']  # I2
        args[2] = kwargs['source_seg']  # I3
        args[3] = 0  # I4 Admit/Imped print, skip
        args[4] = kwargs['ereal']  # F1
        args[5] = kwargs['eimag']  # F2
        args[6] = 0  # F3 normalization for I4
        # F4-F7 remaining three args are zero for voltage sources

    else:
        emsg = ('Excitation categories B and C not '
                'yet implemented (Excitation types {0})')
        evals0 = ', '.join(wave_exs + curr_exs)
        raise NotImplementedError(emsg.format(evals0))

    return args


def pack_gn_card_args(**kwargs):
    '''
    Takes named ground plane parameters as keyword args and returns
    a list of arguments for the .gn_card() method of
    a PyNEC NEC context.

    See http://tmolteno.github.io/necpp/classnec__context.html#a124bb06c25d9aa47305ae75b53becb59

    Common arguments to all ground types: 

    ground_type: 
      perfect, free_space, real_SN, or real_refl

      for perfectly conducting, free space, Sommerfeld/Norton 
      or finite reflection-coefficient ground types.

    rad_wire_count:
      Number of radials in the ground screen approx, or
      0 for no ground screen.

    epsilon:
      relative dielectric constant

    sigma:
      conductivity in mhos/meter

    Additional arguments for different radial/cliff scenarios:

    if rad_wire_count > 0:
      screen_radius: radial screen R in meters
      screen_wire_radius: radial wire radius, meterss

    if rad_wire_count == 0:
     cliff_boundary_distance: radial or linear distance for 
       two-medium cliff breakpoint (radial or positive X distance)

     cliff_drop_distance: 
       distance of medium 2 surface below medium 1

     medium_two_epsilon, 
     medium_two_sigma:
       dielectric constant and conductivity of the 
       second medium at the bottom of the cliff

       RP card specifies whether the cliff geometry is circular or linear
    '''

    args = [0]*8
    gt = {'perfect': 1, 'free_space': -1,
          'real_SN': 2, 'real_refl': 0}

    basic_kwargs = ['ground_type', 'rad_wire_count',
                    'epsilon', 'sigma']
    radial_kwargs = ['screen_radius',
                     'screen_wire_radius']
    cliff_kwargs = ['medium_two_epsilon', 'medium_two_sigma',
                    'cliff_boundary_distance', 'cliff_drop_distance']

    all_valid_kwargs = basic_kwargs + radial_kwargs + cliff_kwargs

    # --- Check for invalid/illegal keyword arguments ----
    illegal_kwargs = [arg for arg in kwargs.keys() if not
                      arg in all_valid_kwargs]

    if len(illegal_kwargs) > 0:
        emsg = ('Invalid argument(s) {0}. '
                'Valid args: {1}')
        evals0 = ', '.join(illegal_kwargs)
        evals1 = ', '.join(all_valid_kwargs)
        raise UserWarning(emsg.format(evals0, evals1))

    # --- Check for basic arguments ---
    missing_args = [arg for arg in basic_kwargs
                    if not arg in kwargs.keys()]
    if len(missing_args) > 0:
        emsg = ('Arguments {0} are required for all ground types, '
                'but {1} were missing. See documentation.')
        evals0 = ', '.join(basic_kwargs)
        evals1 = ', '.join(missing_args)
        raise UserWarning(emsg.format(evals0, evals1))

    # --- Check directly for valid ground type ---

    if not kwargs['ground_type'] in gt.keys():
        emsg = ('Invalid ground_type {0}. '
                'Supply one of {1}')
        evals0 = kwargs['ground_type']
        evals1 = ', '.join(gt.keys())
        raise UserWarning(emsg.format(evals0, evals1))
    # TODO: more validity checking

    args[0] = gt[kwargs['ground_type']]  # I1 ground_type
    args[1] = kwargs['rad_wire_count']  # I2 rad_wire_count
    args[2] = kwargs['epsilon']  # F1 tmp1
    args[3] = kwargs['sigma']  # F2 tmp2

    if kwargs['rad_wire_count'] > 0:
        args[4] = kwargs['screen_radius']  # F3 tmp3
        args[5] = kwargs['screen_wire_radius']  # F4 tmp4

    if 'cliff_boundary_distance' in kwargs.keys():
        if kwargs['rad_wire_count'] > 0:
            raise UserWarning(
                'rad_wire_count>0 but cliff_distance is specified! Set rad_wire_count to zero for two-medium cliff.')
        args[4] = kwargs['medium_two_epsilon']  # F3 tmp3
        args[5] = kwargs['medium_two_sigma']  # F4 tmp4
        args[6] = kwargs['cliff_boundary_distance']  # F5 tmp5
        args[7] = kwargs['cliff_drop_distance']  # F6 tmp6

    return args


def pack_ld_card_args(**kwargs):
    '''
    Takes named load parameters as keyword args and returns
    a list of arguments for the .ld_card() method of
    a PyNEC NEC context.

    See http://tmolteno.github.io/necpp/classnec__context.html#a8e3690b43a90a9b947ffda3727732017


    Required arguments for all load types include 
    load_type:
      none, series_RLC_lump, parallel_RLC_lump, 
      series_dist, parallel_dist, load_Z,
      wire_conductivity

    load_tag: 
      the wire to load

    load_seg_start: 
      the starting segment for the loading

    load_seg_end: 
      the ending segment for the loading

    Other arguments depending on load type 
    R, L, C : 
      resistance, inductance, and capacitance 
      for lumped loads 

    R, X: 
      resistance and reactance for load_Z

    R_per_meter, L_per_meter, C_per_meter:
      resistance, inductance, and capacitance per meter for
      distributed loads

    wire_sigma:
      conductivity in mhos/meter for wire conductivity

    If load_tag and Load_seg_start are zero, the load will
    apply to all wires. 

    If load_seg_start and load_seg_end are zero
    with non-zero load_tag, the entire wire will be loaded.

    '''
    thisfunc = 'pack_ld_card_args()'
    args = [0]*7
    load_types = {'none': -1,
                  'series_RLC_lump': 0,
                  'parallel_RLC_lump': 1,
                  'series_dist': 2,
                  'parallel_dist': 3,
                  'load_Z': 4,
                  'wire_conductivity': 5}
    ltstr = ', '.join(load_types.keys())

    if not 'load_type' in kwargs.keys():
        emsg = f'Specify keyword load_type with a value from {ltstr}'
        raise UserWarning(emsg)

    loadtype = kwargs['load_type']
    if not loadtype in load_types:
        emsg = f'Invalid load_type {loadtype} for {thisfunc}. Specify one of {ltstr}'
        raise UserWarning(emsg)

    if not (loadtype == 'none'):
        reqd_keys = ['load_tag', 'load_seg_start']
        _check_kwarg_keys(thisfunc, reqd_keys,
                          kwargs, 'keyword arguments')

    if ('load_seg_start' in kwargs.keys()) and (not ('load_seg_end' in kwargs.keys())):
        kwargs['load_seg_end'] = kwargs['load_seg_start']

    rlc_idx = [4, 5, 6]
    # --- Check distributed loads and assign to positional args ---
    if loadtype in ['series_dist', 'parallel_dist']:
        possible_args = ['R_per_meter', 'L_per_meter', 'C_per_meter']

    # --- Check lumped loads and assign to positional args
    elif loadtype in ['series_RLC_lump', 'parallel_RLC_lump']:
        possible_args = ['R', 'L', 'C']

    # --- Check wire conductivity ---
    elif loadtype == 'wire_conductivity':
        possible_args = ['wire_sigma']

    elif loadtype == 'load_Z':
        possible_args = ['R', 'X']

    elif loadtype == 'none':
        possible_args = []

    _check_minimum_keys(thisfunc, possible_args,
                        kwargs, f'for load type {loadtype}')
    # --- populate args[4], args[5], and args[6] with appropriate values
    # --- based on possible_args logic above
    for ldargkey, ix in zip(possible_args, rlc_idx):
        if ldargkey in kwargs.keys():
            args[ix] = float(kwargs[ldargkey])

    if loadtype == 'none':
        args[0] = load_types[loadtype]
    else:
        args[0] = load_types[loadtype]
        args[1] = kwargs['load_tag']
        args[2] = kwargs['load_seg_start']
        args[3] = kwargs['load_seg_end']

    return args

def pack_nearfield_card_args(coord_system=None, **kwargs):
    '''
    Takes named load parameters as keyword args and returns
    a list of arguments for the .ne_card() and .nh_card() methods of
    a PyNEC NEC context.

    https://www.nec2.org/part_3/cards/ne.html

    coord_system: 
      'rectangular' or 'spherical' 

    Specify number of points, starting coordinates, and step increments: 

    if rectangular: 
        nx, ny, nz, x0, y0, z0, delx, dely, delz
    if spherical:
        nr, nphi, ntheta, r0, phi0, theta0, delr, delphi, deltheta
    '''
    thisfunc = 'pack_nearfield_card_args()'
    allowed_csys = ['rectangular', 'spherical']

    if coord_system not in allowed_csys:
        emsg = f'{thisfunc} requires coord_system from {allowed_csys}, not {coord_system}'
        raise UserWarning(emsg)

    if coord_system == 'rectangular':
        nfargs = ['nx', 'ny', 'nz', 'x0', 'y0', 'z0', 'delx', 'dely', 'delz']
        nf_flag = 0
    elif coord_system == 'spherical':
        nfargs = ['nr', 'nphi', 'ntheta', 'r0', 'phi0', 'theta0', 'delr','delphi','deltheta']
        nf_flag = 1

    _check_kwarg_keys(thisfunc, nfargs, kwargs, f'arguments for {coord_system} coordinates')
    
    args = [nf_flag]+[kwargs[var] for var in nfargs]
    return args


def _check_kwarg_keys(caller, required_keys, kwargs, where):
    '''
    Checks for required argument names in kwargs.keys()
    Raises an error including caller name of the form

    <caller> is missing <missing keys> in <where>
    <where> could be something like "arguments"
    '''
    missing_keys = [key for key in required_keys if not key in kwargs.keys()]

    if missing_keys:
        emsg = f'ERROR: {caller} is missing {missing_keys} in {where}'
        print(emsg)
        raise UserWarning(emsg)


def _check_minimum_keys(caller, possible_keys, kwargs, why):
    '''
    Checks to see at least one of the possible keys is present in kwargs.keys()

    Raises an error including caller name of the form
    <caller> needs at least one of <possible keys> <why>
    '''
    present_keys = [key for key in possible_keys if key in kwargs.keys()]
    if (not present_keys) and possible_keys:
        emsg = f'ERROR: {caller} needs at least one of {possible_keys} {why}'
        print(emsg)
        raise UserWarning(emsg)
    return present_keys


class WireInput(object):
    '''
    A Jupyter notebook wire input GUI for PyNEC

    https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Styling.html
    https://github.com/tmolteno/python-necpp/tree/master/PyNEC


    '''

    def __init__(self):
        '''
        Sets up the initial UI layout with labels and a single wire. 

        Defines list of wire arguments and units.
        '''

        # --- PyNEC/NEC-2 wire geometry arguments and labels ---

        self.out = None
        self.wireargs = ['tag_id', 'segment_count', 'xw1', 'yw1',
                         'zw1', 'xw2', 'yw2', 'zw2', 'rad', 'rdel', 'rrad']
        self.cellnames = ['delbutton'] + self.wireargs
        self.wire_units = ['', '']+['(m)']*9
        self.wire_cellwidths = ['5%']*2+['9.5%']*6+['7.5%']*3
        self.boxlayout = ipywidgets.Layout(width='8%')
        # --- GUI layout and styling ---
        self.frame_layout = ipywidgets.Layout(width='100%')
        self.hb_layout = ipywidgets.Layout()
        self.wire_cell_layouts = [ipywidgets.Layout(width=cellwidth)
                                  for cellwidth in self.wire_cellwidths]

        # --- Define the header cells for descriptions of wire input fields ---
        # --- ipywidgets fonts seem to be most easily handled with HTML styling ---
        head_style = '"text-align:center; font-weight:bold; font-size:135%;"'
        self.headercells = [ipywidgets.Label(
            layout=ipywidgets.Layout(width='2%'))]
        self.headercells += [ipywidgets.HTML(value=f'<div style={head_style}>{arg} {unit}</div>', layout=clay)
                             for arg, unit, clay in zip(self.wireargs,
                                                        self.wire_units,
                                                        self.wire_cell_layouts)]

        # --- Use some shortened names for headers ---
        self.headercells[1].value = self.headercells[1].value.replace(
            'tag_', '')
        self.headercells[2].value = self.headercells[2].value.replace(
            'segment_count', 'segs')

        self.header = ipywidgets.HBox(self.headercells, layout=self.hb_layout)

        # --- Set up interface buttons ---
        self.wirebutton = ipywidgets.Button(description='Add Wire',
                                            button_style='info',
                                            tooltip='Add a new row.')
        self.wirebutton.on_click(self.on_add_wire)

        self.delbutton = ipywidgets.Button(description='Delete All',
                                           button_style='danger',
                                           tooltip='CAUTION! No confirmations!')

        self.delbutton.on_click(self.on_del_all)

        self.taperbutton = ipywidgets.ToggleButton(description='Taper Params',
                                                   value=False,
                                                   button_style='info',
                                                   tooltip='Show/hide tapered wire rdel and rrad.')

        self.taperbutton.observe(self.taperbutton_handler)
        self.translatebutton = ipywidgets.Button(description='Translate Wires',
                                                 button_style='info',
                                                 tooltip='Select x, y, z and fill in magnitude.')

        self.translatebutton.on_click(self.on_translate_wires)
        self.translate_direction_selector = ipywidgets.ToggleButtons(options=['x', 'y', 'z'],
                                                                     value='z',
                                                                     button_style='info',
                                                                     )
        self.translate_direction_selector.style.button_width = '10%'
        self.translate_direction_selector.style.font_weight = 'bold'
        self.translation_amount_box = ipywidgets.FloatText(value=0.0,
                                                           tooltip='Translation amount.',
                                                           layout=self.boxlayout)
        self.wires = []

        self.controls = ipywidgets.HBox([self.wirebutton, self.delbutton,
                                         self.taperbutton, self.translatebutton,
                                         self.translation_amount_box, self.translate_direction_selector],
                                        layout=self.hb_layout)

        self.frame = ipywidgets.VBox([self.controls],
                                     layout=self.frame_layout)  # the "frame" is a collection of rows
        self.nwires = 0
        self.add_wire_row()
        # self.show() # this doesn't always work, so let's make it manual for now

    def get_EZNEC_wirestr(self, round=None):
        '''
        Writes out a string that can be imported into EZNEC.
        '''
        wirefields = [f'{c}w1' for c in 'xyz']+[f'{c}w2' for c in 'xyz']+['rad']
        row_fmt_str = ', '.join(['{'+f'{wf}:14.12f'+'}' for wf in wirefields])
        ezwstr = 'm m\n'
        wiredicts = self.return_wire_dicts()
        for wd in wiredicts:
            ezwstr += row_fmt_str.format(**wd)
            ezwstr += '\n'
        return ezwstr

    def import_EZNEC_wires_from_URL(self, ezurl, round=None):
        '''
        Uses urllib.request (as urlrq) to open a wire description output from EZNEC.

        Parses the units line and converts to meters.
        '''
        # --- Check the file for units line and select number of header lines ---

        with urlrq.urlopen(ezurl) as urf:
            bytesdata = urf.readlines()

        desc = [line.decode('UTF-8') for line in bytesdata]
        self.EZNEC_import = desc
        EZNEC_in_line = [line.count('EZNEC') for line in desc]
        NH = EZNEC_in_line.index(True)+8
        if not NH == 8:
            uestr = 'import_EZNEC_wires_from_URL() found units line "{0}" as first line. Not yet implemented.'
            raise NotImplementedError(uestr.format(desc[0]))

        pipesepdata = ['|'.join(line.split()).replace(',|', ',')  # EZNEC files have mix of variable spacing and comma seperated, replace with pipes
                       for line in desc[NH:]]
        wiredata = []
        # --- The wire coordinates are still comma separated, split those up too ---
        for entry in pipesepdata:
            # drop wire connectivity like W1E2, etc
            wire_line_temp = [d.split(',')
                              for d in entry.split('|') if not d.count('W')]
            wire_entry_unpacked = []
            for wdlist in wire_line_temp:  # unpack the wire coordinates and other data into individual entries in wdlist
                wire_entry_unpacked.extend(wdlist)
            wiredata.append(wire_entry_unpacked)

        self.EZNEC_entry_map = ['tag_id', 'xw1', 'yw1', 'zw1', 'xw2',
                                'yw2', 'zw2', 'rad', 'segment_count',
                                'dielc', 'dielthk']
        # --- TODO: change transformers based on wire units --- probably make a dict of transformers ---
        if round:
            floatfn = lambda x: np.round(float(x), decimals=round)
        else:
            floatfn = float
        self.EZNEC_xformers = [int]+[floatfn]*6 + [lambda num: floatfn(num)/2000]
        self.EZNEC_xformers += [int, floatfn, lambda num: floatfn(num)/1000]

        # --- Use transformations to build a wire dictionary from EZNEC input data ---
        wiredicts = []
        for wire_entry in wiredata:  # wiredata is a list of lists, one per wire
            wiredict = {key: xformer(value) for key, xformer, value in
                        zip(self.EZNEC_entry_map, self.EZNEC_xformers, wire_entry)}
            wiredicts.append(wiredict)

        self.EZNEC_wires = wiredicts
        # --- Delete existing wires and add new wires with imported data ---
        self.delete_all_wires()
        for wiredict in self.EZNEC_wires:
            row = self.add_wire_row()
            self.populate_row(row=row,
                              wiredict=wiredict)

        if self.out:
            self.refresh()  # refresh if .show() has been called, otherwise don't refresh

    def populate_row(self, row=None, wiredict=None):
        '''
        Iterates through children of a wire row returned from add_wire_row() 
        and fills in appropriate values from a dict of wires.

        Matches keys so extraneous keys (Dielectric properties from EZNEC, 
        for example) are ignored.

        Note that the "row" is a list of widgets, 
        but isn't contained in the row's HBox
        '''
        for k, v in wiredict.items():
            for box in row:
                if box.argid == k:
                    box.value = v

    def delete_all_wires(self):
        '''
        Sets the wire list to an empty list and self.nwires to 0
        '''
        self.wires = []
        self.nwires = 0

    def on_add_wire(self, button):
        '''
        Callback for the "Add Wire" button.
        '''
        self.add_wire_row()
        self.refresh()

    def on_del_wire(self, button):
        '''
        Deletes a wire input row from the GUI.
        Renumbers the wire tag_id's appropriately.
        '''
        self.wires.pop(button.tag_id-1)
        self.nwires -= 1
        for n, wire in enumerate(self.wires):
            tagix = self.cellnames.index('tag_id')

            wire.children[tagix].value = str(n+1)  # 1-indexed
            wire.children[0].tag_id = n+1  # this is the wire delete button

        self.refresh()

    def on_del_all(self, button):
        '''
        Deletes all the wires. No return, no safeties!
        '''
        self.delete_all_wires()
        self.refresh()

    def on_translate_wires(self, button):
        '''
        Translates all the wire coords in the GUI according to direction
        and amount in interface.
        '''
        amount = self.translation_amount_box.value
        directstr = self.translate_direction_selector.value
        self.translate_wires(amount, directstr)

    def translate_wires(self, amount, direction_string):
        '''
        External function to translate wires
        '''
        if not direction_string in ['x', 'y', 'z']:
            raise UserWarning("Invalid value for 'direction_string'. Valid directions are 'x', 'y', and 'z'")

        tags = [direction_string+'w1',direction_string+'w2']
        for wire in self.wires:
            for child in wire.children:
                if child.argid in tags:
                    child.value += amount

    def add_wire_row(self):
        '''
        Adds a wire input row to the GUI.
        '''
        self.nwires += 1
        tag_id = self.nwires
        row = [ipywidgets.IntText(layout=clay) if n < 2
               else ipywidgets.FloatText(layout=clay, step=None)
               for n, clay in enumerate(self.wire_cell_layouts)]

        for widget, wirearg in zip(row, self.wireargs):
            widget.argid = wirearg

        # --- add a wire delete button at the beginning of the row ---
        del_lay = ipywidgets.Layout(width='2%', border='1px solid black')
        delbutton = ipywidgets.Button(description='X',
                                      layout=del_lay,
                                      button_style='danger',
                                      font_weight='bold')
        delbutton.tag_id = tag_id
        delbutton.on_click(self.on_del_wire)
        delbutton.argid = None
        row = [delbutton] + row

        # --- fill in default values for new wires ---

        for n, c in enumerate(row):
            if c.argid == 'tag_id':
                c.value = tag_id
                c.disabled = True  # tag_id is read-only and handled in the background

            elif c.argid == 'segment_count':  # default to previous wire's segmentation, or 5 if no previous wire
                try:
                    c.value = self.wires[-1].children[n].value
                except:
                    c.value = 5

            elif c.argid == 'rad':  # default to one mm
                c.value = 0.001

            elif c.argid in ['rdel', 'rrad']:
                c.value = 1.0

            else:
                c.value = 0.000

        self.wires.append(ipywidgets.HBox(row, layout=self.hb_layout))
        return row

    def taperbutton_handler(self, change):
        '''
        Handles the wire taper toggle button.

        TODO: Consider properly handling the change dictionaries that the button
        emits instead of checking its current value.
        '''
        # print(change)

        if self.taperbutton.value == True:
            setval = 'visible'
        else:
            setval = 'hidden'

        for colname in ['rdel', 'rrad']:
            n = self.cellnames.index(colname)
            self.headercells[n].layout.visibility = setval
            for wire in self.wires:
                wire.children[n].layout.visibility = setval
                # default for rrad and rdel is 1.0
                wire.children[n].value = 1.0

        self.refresh()

    def refresh(self):
        '''
        Update the outermost VBox self.frame with added or deleted wires
        '''
        # this automatically re-displays changes, nothing else needed
        # possibly needs display_id = True in display?
        self.frame.children = [self.controls, self.header] + self.wires

    def show(self):
        '''
        Initialize and display the collection of widgets.
        '''

        self.frame.children = [self.controls, self.header] + self.wires

        for colname in ['rdel', 'rrad']:
            n = self.cellnames.index(colname)
            self.headercells[n].layout.visibility = 'hidden'
            for wire in self.wires:
                wire.children[n].layout.visibility = 'hidden'
                wire.children[n].layout.visibility = 'hidden'

        self.out = display(self.frame, display_id=True)

    def return_wire_dicts(self):
        '''
        Return the current wire params as a list of dicts
        suitable for ** unpacking into PyNEC wire geometry's 
        add_wire()
        '''
        wiredicts = []
        for wire in self.wires:
            wiredict = {child.argid: child.value
                        for child in wire.children if child.argid}
            wiredicts.append(wiredict)

        return wiredicts

# === Below we collect some functions for manipulating the geometry of wire dictionaries. ===


def rotate_wiredict(wd, thetadeg, axis, inplace=False):
    """
    Rotates a dictionary wd with points
    xw1, yw1, zw1 and xw2, yw2, zw2 
    about the specified axis 'x', 'y', or 'z'
    through an angle thetadeg in degrees.

    If inplace is set to False, a copy is returned.

    https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
    """
    theta = np.pi/180.0*thetadeg
    if axis == 'x':
        R = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    elif axis == 'y':
        R = np.array([[np.cos(theta), 0, np.sin(theta)],
                      [0, 1, 0],
                      [-np.sin(theta), 0, np.cos(theta)]])
    elif axis == 'z':
        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])

    if not inplace:
        wd = wd.copy()

    p1 = (wd['xw1'], wd['yw1'], wd['zw1'])
    p2 = (wd['xw2'], wd['yw2'], wd['zw2'])

    # @ is Python 3 shortcut for np.matmul()
    wd['xw1'], wd['yw1'], wd['zw1'] = R@p1
    wd['xw2'], wd['yw2'], wd['zw2'] = R@p2
    return wd


def translate_wiredict(wd, amount, axis, inplace=False):
    """
    Translates a dictionary wd with points
    xw1, yw1, zw1 and xw2, yw2, zw2 
    a distance 'amount' along the specified axis 'x', 'y', or 'z'
    """
    if not inplace:
        wd = wd.copy()

    if axis == 'x':
        wd['xw1'] += amount
        wd['xw2'] += amount
    elif axis == 'y':
        wd['yw1'] += amount
        wd['yw2'] += amount
    elif axis == 'z':
        wd['zw1'] += amount
        wd['zw2'] += amount

    return wd


def get_wire_points(wd):
    """
    Returns 
    p1 = (xw1, yw1, zw1)
    p2 = (xw2, yw2, zw2)

    from a wire dictionary
    """
    p1 = np.asarray([wd['xw1'], wd['yw1'], wd['zw1']])
    p2 = np.asarray([wd['xw2'], wd['yw2'], wd['zw2']])
    return p1, p2
