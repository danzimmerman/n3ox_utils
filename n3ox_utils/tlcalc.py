# -*- coding: utf-8 -*-

from scipy.constants import speed_of_light as C0
import numpy as np

class rlgcTL(object):
    '''
    Computes properties of an arbitrary
    transmission line specified with L,C parameters
    and k1, k2 model for R and G.

    See https://owenduffy.net/transmissionline/concept/mptl.htm

    R and G are computed as functions of frequency in MHz 

    '''

    def __init__(self, params=None):
        '''
        Defaults to RG-303 (Belden 84303) 50 ohm coax
        https://catalog.belden.com/techdata/EN/84303_techdata.pdf

        and k1, k2 taken from here:
        https://owenduffy.net/calc/tl/tllc.php#NoteModellingLoss

        '''
        if not params:
            params = {
                      'k1': 1.226e-5,
                      'k2': 5.226e-11,
                      'Rn': 50.0,
                      'Vf': 0.700,  # 69.5% in datasheet, but want to match owen's calculator
                      }

        for k, v in params.items():
            setattr(self, k, v)

        self.L = self.Rn/(C0*self.Vf)
        self.C = 1.0/(C0*self.Vf*self.Rn)

    def R(self, freq):
        '''
        Resistance proportional to square root of frequency.
        '''
        return 2*self.Rn/20*np.log(10)*self.k1*freq**0.5

    def G(self, freq):
        '''
        Shunt conductance proportional to frequency
        '''
        return (2.0/self.Rn)/20*np.log(10)*self.k2*freq

    def Xl(self, freq):
        '''
        Convenience function for j*\omega*L
        '''
        return 2.0*np.pi*freq*self.L

    def Bc(self, freq):
        '''
        Convenience function for susceptance j\omega C
        '''
        return 2.0*np.pi*freq*self.C

    def Z0(self, freq):
        '''
        Returns the line characteristic impedance as a function of frequency.
        This is actually frequency-dependent for real, lossy lines.

        Assumes frequency in Hz
        '''

        imp = self.R(freq) + 1j*self.Xl(freq)
        adm = self.G(freq) + 1j*self.Bc(freq)
        return np.sqrt(imp/adm)

    def gamma(self, freq):
        '''
        Returns the complex propagation constant as a function of frequency
        Frequency in Hz
        '''
        imp = self.R(freq) + 1j*self.Xl(freq)
        adm = self.G(freq) + 1j*self.Bc(freq)
        return np.sqrt(imp*adm)

    def Zin(self, freq, length, Zload):
        '''
        Returns the input impedance using the Telegrapher's equation
        and the stored parameters.

        Freq in Hz
        '''

        Z0e = self.Z0(freq)
        gme = self.gamma(freq)
        num = Zload+Z0e*np.tanh(gme*length)
        denom = Z0e+Zload*np.tanh(gme*length)

        return Z0e*num/denom
