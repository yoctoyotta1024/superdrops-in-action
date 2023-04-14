import numpy as np
import awkward as ak

######## common functions for accessing superdroplet attributes  ########

class CommonSuperdropProperties():
    '''Contains attributes common to all superdroplets and functions
    for calculating derived ones'''

    def __init__(self, RHO_L, RHO_SOL, MR_SOL, IONIC):
        '''Common attributes shared by superdroplets'''
        
        # density of liquid in droplets (=density of water at 300K) [Kg/m^3]
        self.RHO_L = RHO_L

        # droplet solute properties
        # density of (dry) solute [Kg/m^3]
        self.RHO_SOL = RHO_SOL
        self.MR_SOL = MR_SOL                             # Mr of solute [g/mol]
        # degree ionic dissociation (van't Hoff factor)
        self.IONIC = IONIC

        self.print_properties()

    def print_properties(self):
        print("\n---- Superdrop Properties -----")
        print("RHO_L =", self.RHO_L, "Kg/m^3")
        print("RHO_SOL =", self.RHO_SOL, "Kg/m^3")
        print("MR_SOL =", self.MR_SOL, "Kg/mol")
        print("IONIC =", self.IONIC)
        print("-------------------------------\n")

    def rhoeff(self, r, m_sol):
        ''' calculates effective density [g m^-3] of 
      droplet such that mass_droplet, m = 4/3*pi*r^3 * rhoeff
      taking into account mass of liquid and mass of
      solute assuming solute occupies volume it
      would given its (dry) density, RHO_SOL. '''

        m_sol = m_sol/1000 # convert from grams to Kg
        r = r/1e6 # convert microns to m

        solfactor = 3*m_sol/(4.0*np.pi*(r**3))
        rhoeff = self.RHO_L + solfactor*(1-self.RHO_L/self.RHO_SOL)

        return rhoeff * 1000 #[g/m^3]

    def vol(self, r):
        ''' volume of droplet [m^3] '''

        r = r/1e6 # convert microns to m

        return 4.0/3.0 * np.pi * r**3

    def mass(self, r, m_sol):
        ''' total mass of droplet (water + (dry) areosol) [g],
         m =  4/3*pi*rho_l**3 + m_sol(1-rho_l/rho_sol) 
        ie. m = 4/3*pi*rhoeff*R**3 '''

        m_sol = m_sol/1000 # convert from grams to Kg
        r = r/1e6 # convert microns to m

        msoleff = m_sol*(1-self.RHO_L/self.RHO_SOL) # effect of solute on mass
        m = msoleff + 4/3.0*np.pi*(r**3)*self.RHO_L

        return m * 1000 # [g]

    def m_water(self, r, m_sol):
        ''' mass of only water in droplet [g]'''

        m_sol = m_sol/1000 # convert m_sol from grams to Kg
        r = r/1e6 # convert microns to m

        v_sol = m_sol/self.RHO_SOL
        v_w = 4/3.0*np.pi*(r**3) - v_sol

        return self.RHO_L*v_w * 1000 #[g]

    def masstimeseries(self, radii, m_sols):
        ''' call mass function for each r, m_sol pair '''

        masses = []
        for r,m_sol in zip(radii, m_sols):
            ms = self.mass(np.asarray(r), np.asarray(m_sol))
            masses.append(ms)
        
        return masses # [g]