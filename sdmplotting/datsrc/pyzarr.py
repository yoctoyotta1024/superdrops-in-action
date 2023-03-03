### functions involved in handling zarr dataset and
### txt files from SDM model output ###

import numpy as np
import xarray as xr
import awkward as ak
import random
from . import thermoeqns
from sys import maxsize

class Sddata:
  
  def __init__(self, dataset):
    ds = get_rawdataset(dataset) 
    self.totnsupers = ds["raggedcount"].values
  
    self.sdindex = ak.unflatten(ds["sdindex"].values, self.totnsupers)
    self.eps = ak.unflatten(ds["eps"].values, self.totnsupers)
    self.radius = ak.unflatten(ds["radius"].values, self.totnsupers)
    self.m_sol = ak.unflatten(ds["m_sol"].values, self.totnsupers)
    self.coord3 = ak.unflatten(ds["coord3"].values, self.totnsupers)

    self.radius_units = ds["radius"].units # probably microns ie. 'micro m'
    self.m_sol_units = ds["m_sol"].units # probably gramms
    self.coord3_units = ds["coord3"].units # probably meters

  def __getitem__(self, key):
    if key == "sdindex":
      return self.sdindex
    elif key == "eps":
      return self.eps
    elif key == "radius":
      return self.radius
    elif key == "m_sol":
      return self.m_sol
    elif key == "coord3":
      return self.coord3
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

class Thermodata:

  def __init__(self, dataset, setup):
    ds = get_rawdataset(dataset) 
    
    self.press = ds["press"].values
    self.temp = ds["temp"].values
    self.qvap = ds["qvap"].values
    self.qcond = ds["qcond"].values
    
    self.theta = self.get_potential_temp(setup) 

    self.press_units = ds["press"].units # probably hecta pascals
    self.temp_units = ds["temp"].units # probably kelvin
    self.theta_units = ds["temp"].units # probably kelvin

  def __getitem__(self, key):
    if key == "press":
      return self.press
    elif key == "temp":
      return self.temp
    elif key == "qvap":
      return self.qvap
    elif key == "qcond":
      return self.qcond
    elif key == "theta":
      return self.theta
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

  def get_potential_temp(self, setup):

    press = self.press*100 # convert from hPa to Pa
    theta = thermoeqns.dry_pot_temp(self.temp, press, self.qvap, setup)        # parcel potential temp
  
    return theta

def dims_from_setup(var, setup):
  """ return constant to multipy non-dimensional 
  data to convert to SI units """

  dims = {
    "time": setup["TIME0"],
    "press": setup["P0"],
    "temp": setup["TEMP0"],

    "radius": setup["R0"],
    "m_sol": setup["RHO0"] * (setup["R0"]**3),
    "coord3": setup["COORD0"],

    "qcond": 1.0,
    "qvap": 1.0,
    "id": 1,
    "eps": 1,
  }
  
  return dims[var]

def remove_undefined_values(data, dtype):

  if dtype == "uint64":
    data = data[data != maxsize*2+1]
  
  elif dtype == "float64":
    data = data[True != np.isnan(data)]

  return data

def get_rawdataset(dataset):

  return xr.open_dataset(dataset, engine="zarr", consolidated=False)

def get_sddata(dataset):
  ''' returns superdroplets' attributes data in a dictionary.
  Each attribute is a key and the value is a list of lists where
  each (inner) list is all superdroplets at a given output time,
  ie. [ [time1], [time2], [time3] ]'''

  sddata = Sddata(dataset)

  return sddata

def get_thermodata(dataset, setup):
  ''' returns a thermodynamic data in a dictionary. The value under 
  each key is the thermodynamics data in a 2D array 
  with dimensions [time, gridbox]. E.g. thermo["qvap"][:,0] gives the 
  timeseries of qvap for the 0th gridbox. thermo["qvap][0] gives 
  the qvap of all gridboxes at the 0th output time '''

  thermo = Thermodata(dataset, setup)

  return thermo


def get_time(dataset):

  ds = xr.open_dataset(dataset, engine="zarr", consolidated=False)
  
  return ds["time"].values


def extract_superdroplet_attr(sddata, id, attr):
  '''selects attribute from sddata belonging
  to superdroplet with identitiy 'sdindex'
  at every output time '''

  idx = np.where(sddata.sdindex==id) # index of superdrop in data lists

  return sddata[attr][idx]

def superdroplet_attr_for_ndrops(sddata, attr, ndrops2sample, minid, maxid):
  ''' returns 2D array with dimensions [time, SD]
  containing attribute data over time for 'ndrops'
  randomly selected from superdrops with id in
  range [minid, maxid] '''

  population = list(range(minid, maxid, 1))
  sampled_ids = random.sample(population, ndrops2sample)
  
  attrs = []
  for id in sampled_ids: 
    attrs.append(extract_superdroplet_attr(sddata, id, attr))
  
  return np.asarray(attrs).T


def select_from_attr(attrdata, time, times2sel):
  '''selects attribute at given times
   (for all superdroplets in sddata)'''

  selected_attr = [] # list containing an attribute at selected times
  for t in times2sel:
    ind = np.argmin(abs(time-t))
    selected_attr.append(attrdata[ind]) 
  
  return selected_attr

def select_manytimes_from_sddata(sddata, time, times2sel, attrs2sel):
  '''selects attributes at given times from
  sddata (for all superdroplets in sddata)'''

  selected_data = {} # dict containting selected attributes at selected times
  
  for attr in attrs2sel:
    
    selattr_data = select_from_attr(sddata[attr], time, times2sel)
    
    selected_data[attr] = selattr_data
  
  return selected_data

def select_1time_from_sddata(sddata, time, t2sel, attrs2sel):
  '''selects attributes at given times from
  sddata (for all superdroplets in sddata)'''

  selected_data = {} # dict containting selected attributes at selected times
  
  for attr in attrs2sel:

    ind = np.argmin(abs(time-t2sel))
    selattr_data = sddata[attr][ind] 

    selected_data[attr] = selattr_data
  
  return selected_data


