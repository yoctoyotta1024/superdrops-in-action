# file: pysetuptxt.py

import numpy as np
import sys

from .importpySD import ImportpySD
ImportpySD()
import pySD.gbxboundariesbinary_src.read_gbxboundaries as rgrid
from pySD.cxx2py import *

from .pyzarr import GridBoxes

def setuptxt2dict(setuptxt, nattrs=3, isprint=True):

  setup = read_configtxt_into_floats(setuptxt, False)[0]
  setup.update(read_cpp_into_floats(setuptxt, False)[0])
  setup.update(derive_more_floats(setup, False))
 
  setup["numSDattrs"] = setup["SDnspace"] + nattrs         
  setup["ntime"] = round(setup["T_END"]/setup["OBSTSTEP"])+1

  if isprint:
    print_dict_statement(setuptxt, "setup", setup)

  return setup 

def gridinfo_fromgridfile(gridfile, COORD0, isprint=True):

  gbxbounds, ndims =  rgrid.read_dimless_gbxboundaries_binary(gridfile,
                                                                COORD0=COORD0,
                                                                return_ndims=True,
                                                                isprint=isprint) 
  zhalf, xhalf, yhalf = rgrid.halfcoords_from_gbxbounds(gbxbounds,
                                                        isprint=isprint)
  domainvol, gbxvols, ngrid = rgrid.domaininfo(gbxbounds, isprint=isprint)
 
  grid = {
    "ngrid": ngrid, # number of gridboxes 
    "ndims": np.flip(ndims), # dimensions (no. gridboxes in [y,x,z] direction)
    "domainvol": domainvol,
    "domainarea": domainvol / (np.amax(zhalf) - np.amin(zhalf)), # x-y plane horizontal area
    "gbxvols": gbxvols, # list of vols of each gbx 
    
    "zhalf": zhalf, # half cell coords (boundaries)
    "zfull": rgrid.fullcell(zhalf), # full cell coords (centres)
    
    "xhalf": xhalf, # half cell coords (boundaries)
    "xfull": rgrid.fullcell(xhalf), # full cell coords (centres)
    
    "yhalf": yhalf, # half cell coords (boundaries)
    "yfull":  rgrid.fullcell(yhalf), # full cell coords (centres)
  }

  return grid

def get_gridboxes(dataset, gridfile, setup, isprint=True):

  grid = gridinfo_fromgridfile(gridfile, setup["COORD0"], isprint=isprint)
  
  return GridBoxes(dataset, grid, setup["ntime"])

def get_setup_gridinfo(setuptxt, gridfile, nattrs=3, isprint=True):
  ''' nattrs is number of attributes of SDs
   excluding spatial ones (eps, radius, m_sol) '''
  
  setup = setuptxt2dict(setuptxt, nattrs=nattrs, isprint=isprint)
  grid = gridinfo_fromgridfile(gridfile, setup["COORD0"], isprint=isprint)
  
  return setup, grid


