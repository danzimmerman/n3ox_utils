#test_pynec_helpers.py

import n3ox_utils.pynec_helpers as pnh
import pytest

def test_url_import():
    wireurl = 'http://n3ox.net/files/ezwires/N3OX_flex_wires.txt'
    wireinput = pnh.WireInput()
    wireinput.import_EZNEC_wires_from_URL(wireurl)
    wd = wireinput.return_wire_dicts()
    assert wd[0]['zw2'] == pytest.approx(1.9304)
    
