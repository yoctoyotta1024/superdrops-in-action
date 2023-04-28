### functions involved in handling zarr dataset and
### txt files from SDM model output ###

import numpy as np
import xarray as xr
import awkward as ak
import random
from . import thermoeqns
from sys import maxsize

def tryopen(ds, totnsupers, var):
  try:
    return ak.unflatten(ds[var].values, totnsupers)
  except:
    return None

def tryunits(ds, var):
  try:
    return ds[var].units
  except:
    return None

class Sddata:
  
  def __init__(self, dataset):
    ds = get_rawdataset(dataset) 
    self.totnsupers = ds["raggedcount"].values
  
    self.sdindex = tryopen(ds, self.totnsupers, "sdindex")
    self.eps = tryopen(ds, self.totnsupers, "eps")
    self.radius = tryopen(ds, self.totnsupers, "radius")
    self.m_sol = tryopen(ds, self.totnsupers, "m_sol")

    self.coord3 = tryopen(ds, self.totnsupers, "coord3")
    self.coord1 = tryopen(ds, self.totnsupers, "coord1")
    self.coord2 = tryopen(ds, self.totnsupers, "coord2")

    self.radius_units = tryunits(ds, "radius") # probably microns ie. 'micro m'
    self.m_sol_units = tryunits(ds, "m_sol") # probably gramms
    self.coord3_units = tryunits(ds, "coord3") # probably meters
    self.coord1_units = tryunits(ds, "coord1") # probably meters
    self.coord2_units = tryunits(ds, "coord2") # probably meters

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
    elif key == "coord1":
      return self.coord1
    elif key == "coord2":
      return self.coord2
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

class MassMoments:
  def __init__(self, dataset, setup, ndims):
    ds = get_rawdataset(dataset) 
    
    reshape = [setup["ntime"]] + list(np.flip(ndims))
    
    self.mom0 = np.reshape(ds["massmoment0"].values, reshape) # number of droplets in gbxs over time
    self.mom1 = np.reshape(ds["massmoment1"].values, reshape) # total mass of droplets in gbxs over time
    self.mom2 = np.reshape(ds["massmoment2"].values, reshape) # 2nd mass moment of droplets (~reflectivity)

    self.mom1_units = ds["massmoment1"].units # probably grams
    self.mom2_units = ds["massmoment2"].units # probably grams^2


class Thermodata:

  def __init__(self, dataset, setup, ndims):
    ds = get_rawdataset(dataset) 
    
    reshape = [setup["ntime"]] + list(np.flip(ndims))
    
    self.press = np.reshape(ds["press"].values, reshape)
    self.temp = np.reshape(ds["temp"].values, reshape)
    self.qvap = np.reshape(ds["qvap"].values, reshape)
    self.qcond = np.reshape(ds["qcond"].values, reshape) #dims [t, y, x, z]
    
    self.theta = self.get_potential_temp(setup) 

    self.press_units = ds["press"].units # probably hecto pascals
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
  
  def meanytime(self, var):
    ''' mean of thermo variable over
    time and y dimeensions '''      
        
    return np.mean(var, axis=(0,1))

  def meanxyz(self, var):
    ''' mean of thermo variable over
    (x,y,z) dimensions '''      
        
    return np.mean(var, axis=(1,2,3))

  def meanxytime(self, var):
    ''' mean of thermo variable over
    (x,y,z) dimensions '''      
        
    return np.mean(var, axis=(0,1,2))
   
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

def get_rawdataset(dataset):

  return xr.open_dataset(dataset, engine="zarr", consolidated=False)

def get_sddata(dataset):
  ''' returns superdroplets' attributes data in a dictionary.
  Each attribute is a key and the value is a list of lists where
  each (inner) list is all superdroplets at a given output time,
  ie. [ [time1], [time2], [time3] ]'''

  sddata = Sddata(dataset)

  return sddata

def get_thermodata(dataset, setup, ndims):
  ''' returns a thermodynamic data in a dictionary. The value under 
  each key is the thermodynamics data in a 2D array 
  with dimensions [time, gridbox]. E.g. thermo["qvap"][:,0] gives the 
  timeseries of qvap for the 0th gridbox. thermo["qvap][0] gives 
  the qvap of all gridboxes at the 0th output time '''

  thermo = Thermodata(dataset, setup, ndims)

  return thermo

def get_time(dataset):

  ds = xr.open_dataset(dataset, engine="zarr", consolidated=False)
  
  return ds["time"].values

def extract_1superdroplet_attr_timeseries(sddata, id, attr):
  '''selects attribute from sddata belonging
  to superdroplet with identitiy 'sdindex'
  at every output time '''

  bools = ak.Array(sddata.sdindex==id) # True/False id is found in sdindex at each time
  
  attr_timeseries = sddata[attr][bools]
  num = ak.num(attr_timeseries) # at each time, number of positions where id is found (should be 0 or 1)
  
  if any(num[num!=1]):
    errmsg = "attr_timeseries has times when more"+\
      " than one position in sddata has sdindex==id. num should be"+\
    " list of either 1 or 0 (id found in sdindex at given time or not)"
    raise ValueError(errmsg)
    
  attr_timeseries = np.where(num!=0, attr_timeseries, ak.Array([[np.nan]])) # replace empty positions with nan
  
  return ak.flatten(attr_timeseries, axis=1)

def attr_timeseries_for_nsuperdrops_sample(sddata, attr,
                                           ndrops2sample=0,
                                           minid=0, maxid=0,
                                           ids=[]):
  ''' returns 2D array with dimensions [time, SD]
  containing attribute data over time for 'ndrops'
  randomly selected from superdrops with id in
  range [minid, maxid] '''

  if ids == []:
    population = list(range(minid, maxid, 1))
    sampled_ids = random.sample(population, ndrops2sample)
  else:
    sampled_ids = ids

  ndrops_attr = []
  for id in sampled_ids: 
    attr_timeseries = extract_1superdroplet_attr_timeseries(sddata, id, attr)
    ndrops_attr.append(attr_timeseries)
  
  return np.asarray(ndrops_attr).T

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


