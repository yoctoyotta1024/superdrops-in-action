import numpy as np
import sys

path_in2pySD = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
#path_in2pySD = "/home/m/m300950/CLEO/"
sys.path.append(path_in2pySD)

from pySD.gbxboundariesbinary_src.read_gbxboundaries import read_dimless_gbxboundaries_binary
from pySD.gbxboundariesbinary_src.read_gbxboundaries import halfcoords_from_gbxbounds, domaininfo

def print_dict_statement(filename, dict):

  print("\n---- floats in dict from "+filename+" -----")
  for c in dict:
    print(c, "=", dict[c])
  print("---------------------------------------------\n")
  
def remove_excess_line(line):
  """ removes white spaces and 
  and comments from a line """
  
  line = line.strip()
  line = line.replace(" ", "")
  if "#" in line:
    line = line[:line.find("#")] 
    

  return line

def line_with_assignment(line):
  """ find all the lines in a file 
  which have form [...] = [...] ;
  ie. lines which assign variables. return
  list of these lines truncatd at ; """

  line = line.replace(" ", "")
  if "double" in line or "int" in line: 
    ind1 = line.find("=")
    ind2 = line.find(";")
    if ind2 != -1 and ind1 != -1 and line[0] != "/":
      goodline = line[:ind2+1]
      return goodline
    
  else:
    return False

def where_typename_ends(line):
  """finds index where c++ name for 
  variable type ends for a const double, 
  double, int or const int. """

  if line[:3] == "int": x=3
  elif line[:6] == "double": x=6
  elif line[:11] == "constdouble": x=11
  elif line[:8] == "constint": x=8
  elif line[:15] == "constexprdouble": x=15
  elif line[:12] == "constexprint": x=12
  else:
    raise Exception ("variable type not correctly understood or read."+\
      "It should be a (const) int or (const) double.")
        
  return x

def read_cppconsts_into_floats(filename):
  """returns dictionary of value: float from 
  (const) doubles and (const) ints
  assigned in a c++ file. Also creates
  dictionary of notfloats for values that
  couldn't be converted"""

  floats = {}
  notfloats = {}
  with open(filename) as file:
      rlines=[]
      filelines = file.readlines()
      for line in filelines:
        goodline = line_with_assignment(line)
        if goodline:
          rlines.append(goodline)
      
      for line in rlines:
        x = where_typename_ends(line)
        name =  line[x:line.find("=")]
        value =  line[line.find("=")+1 : line.find(";")]
        
        try: 
          floats[name] = float(value)
        except ValueError:
          notfloats[name] = value

  return floats

def derive_more_floats(CONSTS):
  '''return MCONSTS dictionary containing
    some derived key,values from values in
    CONSTS dictionary'''
   
  MCONSTS = {
    "COORD0"     : CONSTS["TIME0"]*CONSTS["W0"], # characteristic coordinate grid scale [m]
    "RGAS_DRY"   : CONSTS["RGAS_UNIV"]/CONSTS["MR_DRY"], # specific gas constant for dry air [J/Kg/K]  
    "RGAS_V"     : CONSTS["RGAS_UNIV"]/CONSTS["MR_WATER"], #specific gas constant for water [J/Kg/K]
    "CP0"        : CONSTS["CP_DRY"], # characteristic Heat capacity [J/Kg/K]
    "MR0"        : CONSTS["MR_DRY"], # characteristic molecular molar mass [Kg/mol]
    "Mr_ratio"   : CONSTS["MR_WATER"]/CONSTS["MR_DRY"],
  }
  MCONSTS["RHO0"]       = CONSTS["P0"]/(MCONSTS["RGAS_DRY"]*CONSTS["TEMP0"]) # characteristic density [Kg/m^3]
  MCONSTS["Rho_sol"]    =  CONSTS["RHO_SOL"]/MCONSTS["RHO0"]     # dimensionless solute density []

  return MCONSTS

def read_configparams_into_floats(filename):
  """returns dictionary of value: float from 
  values assigned in a config .txt file. 
  Also creates dictionary of notfloats 
  for values that couldn't be converted. """

  floats = {}
  notfloats = {}
  with open(filename) as file:
    rlines=[]
    filelines = file.readlines()
    for line in filelines:
      if line[0] != "#" and line[0] != "/" and "=" in line:
        goodline = remove_excess_line(line)
        rlines.append(goodline)
    
    for line in rlines:
      ind = line.find("=")
      name =  line[:ind]
      value =  line[ind+1:]
      
      try: 
        floats[name] = float(value)
      except ValueError:
        notfloats[name] = value

  try:
    floats["totnsupers0"] = int(floats["nSDsvec"])            # initial total no. of superdrops 
  except:
    pass
  try:
    floats["SDnspace"] = int(floats["SDnspace"])              # no spatial coords to SDs
  except:
    pass

  return floats

def setuptxt2dict(setuptxt, nattrs=3, ngrid=0, printinfo=True):

  setup = read_configparams_into_floats(setuptxt)
  setup.update(read_cppconsts_into_floats(setuptxt))
  setup.update(derive_more_floats(setup))
 
  setup["numSDattrs"] = setup["SDnspace"] + nattrs         
  setup["ngrid"] = ngrid

  if printinfo:
    print_dict_statement(setuptxt, setup)

  return setup 

def get_grid(gridfile, SDnspace, COORD0):

  if SDnspace > 1:
      raise ValueError("SDnspace > 1 but no Python function to read in griddata")

  gbxbounds =  read_dimless_gbxboundaries_binary(gridfile, COORD0) 
  zhalf, xhalf, yhalf = halfcoords_from_gbxbounds(gbxbounds)
  domainvol, gbxvols, ngrid = domaininfo(gbxbounds)
 
  if SDnspace == 0:
    zhalf = np.array([0, 0])
  
  zfull = (zhalf[1:] + zhalf[:-1])/2
  
  grid = {
    "ngrid": ngrid, # number of gridboxes 
    "zhalf": zhalf, # half cell coords (boundaries)
    "zfull": zfull, # full cell coords (centres)
    "domainvol": domainvol,
    "gbxvols": gbxvols
  }

  return grid

def get_setup_grid(setuptxt, gridfile, printinfo=True):

  nattrs = 3 # number of attributes of SDs excluding spatial ones (eps, radius, m_sol)
  setup = setuptxt2dict(setuptxt, nattrs=nattrs, ngrid=0, printinfo=printinfo)
  grid = get_grid(gridfile, setup["SDnspace"], setup["COORD0"])
  
  setup["ngrid"] = grid["ngrid"]

  return setup, grid

