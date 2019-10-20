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

'''
This module is a collection of PyNEC helper utilities, mostly to provide a 
named-variable interface to the most common PyNEC things I use.
'''
import ipywidgets
from IPython.display import display
import urllib


def pack_gn_card_args(gn_card_params):
    '''
    Takes a dictionary of named parameters and returns
    a list of arguments for the .gn_card() method of
    a PyNEC NEC context.

    See http://tmolteno.github.io/necpp/classnec__context.html#a124bb06c25d9aa47305ae75b53becb59

    ground_type: 
      perfect, free_space, real_SN, or real_refl

      for perfectly conducting, free space, Sommerfeld/Norton 
      or finite reflection-coefficient ground types.

    rad_wire_count:
      Number of radials in the ground screen approx, or
      none for no ground screen

    epsilon:
      relative dielectric constant

    sigma:
      conductivity in mhos/meter

    Additional parameters for different radial/cliff scenarios:

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
    gpr = gn_card_params
    args = [0]*8
    gt = {'perfect': 1, 'free_space': -1,
          'real_SN': 2, 'real_refl': 0}

    args[0] = gt[gpr['ground_type']]  # I1 ground_type
    args[1] = gpr['rad_wire_count']  # I2 rad_wire_count
    args[2] = gpr['epsilon']  # F1 tmp1
    args[3] = gpr['sigma']  # F2 tmp2

    if gpr['rad_wire_count'] > 0:
        args[4] = gpr['screen_radius'] # F3 tmp3
        args[5] = gpr['screen_wire_radius'] #F4 tmp4

    if 'cliff_boundary_distance' in gpr.keys():
        if gpr['rad_wire_count'] > 0:
            raise UserWarning(
                'rad_wire_count>0 but cliff_distance is specified! Set rad_wire_count to zero for two-medium cliff.')
        args[4] = gpr['medium_two_epsilon'] #F3 tmp3
        args[5] = gpr['medium_two_sigma'] #F4 tmp4
        args[6] = gpr['cliff_boundary_distance'] #F5 tmp5
        args[7] = gpr['cliff_drop_distance'] #F6 tmp6

    return args


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
        self.wire_cellwidths = ['5%']*2+['10%']*6+['8%']*3

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

        self.taperbutton = ipywidgets.ToggleButton(description='Show Taper Params',
                                                   value=False,
                                                   button_style='info',
                                                   tooltip='Show/hide tapered wire rdel and rrad.')

        self.taperbutton.observe(self.taperbutton_handler)
        self.wires = []

        self.controls = ipywidgets.HBox([self.wirebutton, self.delbutton, self.taperbutton],
                                        layout=self.hb_layout)
        self.frame = ipywidgets.VBox([self.controls],
                                     layout=self.frame_layout)  # the "frame" is a collection of rows
        self.nwires = 0
        self.add_wire_row()
        # self.show() # this doesn't always work, so let's make it manual for now

    def import_EZNEC_wires_from_URL(self, ezurl):
        '''
        Uses urllib to open a wire description output from EZNEC.

        Parses the units line and converts to meters.
        '''
        # --- Check the file for units line and select number of header lines ---

        with urllib.request.urlopen(ezurl) as urf:
            bytesdata = urf.readlines()

        desc = [line.decode('UTF-8') for line in bytesdata]
        self.EZNEC_import = desc
        EZNEC_in_line = [line.count('EZNEC') for line in desc]
        NH = EZNEC_in_line.index(True)+8
        if not NH == 8:
            uestr = 'Found units line {0} as first line. Not yet implemented.'
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
        self.EZNEC_xformers = [int]+[float]*6 + [lambda num: float(num)/2000]
        self.EZNEC_xformers += [int, float, lambda num: float(num)/1000]

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
