### functions involved in handling zarr dataset and
### txt files from SDM model output ###

import numpy as np
import xarray as xr
import awkward as ak
import random
from . import thermoeqns
from sys import maxsize

def get_rawdataset(dataset):

  print("opening: ", dataset)
  return xr.open_dataset(dataset, engine="zarr", consolidated=False)

def tryopen(ds, totnsupers, var):
  try:
    return raggedvar_fromzarr(ds, totnsupers, var) 
  except:
    return ak.Array([])
  
def tryunits(ds, var):
  try:
    return ds[var].units
  except:
    return ""

def raggedvar_fromzarr(ds, raggedcount, var):
  ''' returns ragged ak.Array dims [time, ragged]
  for a variable "var" in zarr ds '''

  return ak.unflatten(ds[var].values, raggedcount)

def var4d_fromzarr(ds, ntime, ndims, key):
  '''' returns 4D variable with dims
  [time, y, x, z] from zarr dataset "ds" '''
  
  reshape = [ntime] + list(np.flip(ndims))

  np.reshape(ds[key].values, reshape) 

def var3d_fromzarr(ds, ndims, key):
  '''' returns 3D variable with dims
  [y, x, z] from zarr dataset "ds" '''
  
  reshape = np.flip(ndims)

  np.reshape(ds[key].values, reshape) 

def massmom_fromzarr(dataset, ntime, ndims, massmom):
  '''' opens zarr dataset "ds" and returns 
  4D mass moment "massmom" from it '''

  ds = get_rawdataset(dataset) 

  return var4d_fromzarr(ds, ntime, ndims, massmom) 

def thermovar_fromzarr(dataset, ntime, ndims, thermovar):
  '''' opens zarr dataset "ds" and returns 4D
  thermodynamic variable "thermovar" from it '''

  ds = get_rawdataset(dataset) 

  return var4d_fromzarr(ds, ntime, ndims, thermovar)  

def get_sddata(dataset):
  ''' returns superdroplets' attributes data in a dictionary.
  Each attribute is a key and the value is a list of lists where
  each (inner) list is all superdroplets at a given output time,
  ie. [ [time1], [time2], [time3] ]'''

  return Sddata(dataset)

def get_thermodata(dataset, setup, ndims):
  ''' returns a thermodynamic data in a dictionary. The value under 
  each key is the thermodynamics data in a 2D array 
  with dimensions [time, gridbox]. E.g. thermo["qvap"][:,0] gives the 
  timeseries of qvap for the 0th gridbox. thermo["qvap][0] gives 
  the qvap of all gridboxes at the 0th output time '''

  return Thermodata(dataset, setup, ndims)

def get_time(dataset):

  return Time(dataset)

class Sddata:
  
  def __init__(self, dataset):
    
    ds = get_rawdataset(dataset)
     
    self.totnsupers = ds["raggedcount"].values

    self.sdindex = tryopen(ds, self.totnsupers, "sdindex")
    self.sd_gbxindex = tryopen(ds, self.totnsupers, "sd_gbxindex")
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
    if key == "totnsupers":
      return self.totnsupers
    elif key == "sdindex":
      return self.sdindex
    elif key == "sd_gbxindex":
      return self.sd_gbxindex
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
    ntime = setup["ntime"]
    
    self.nsupers =  var4d_fromzarr(ds, ntime, ndims, "nsupers")               # number of superdroplets in gbxs over time
    self.mom0 = var4d_fromzarr(ds, ntime, ndims, "massmoment0")               # number of droplets in gbxs over time
    self.mom1 = var4d_fromzarr(ds, ntime, ndims, "massmoment1")               # total mass of droplets in gbxs over time
    self.mom2 = var4d_fromzarr(ds, ntime, ndims, "massmoment2")               # 2nd mass moment of droplets (~reflectivity)
    self.effmass = self.mom2 / self.mom1                                             # Effective Radius of droplets

    self.mom1_units = ds["massmoment1"].units                                       # probably grams
    self.mom2_units = ds["massmoment2"].units                                       # probably grams^2
    self.effmass_units = ds["massmoment2"].units + "/" + ds["massmoment1"].units    # probably grams

  def __getitem__(self, key):
    if key == "nsupers":
      return self.nsupers
    elif key == "mom0":
      return self.mom0
    elif key == "mom1":
      return self.mom1
    elif key == "mom2":
      return self.mom2
    elif key == "effmass":
      return self.effmass
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

class Thermodata:

  def __init__(self, dataset, setup, ndims):
    
    ds = get_rawdataset(dataset)
    ntime = setup["ntime"]

    self.press = var4d_fromzarr(ds, ntime, ndims, "press")
    self.temp = var4d_fromzarr(ds, ntime, ndims, "temp")
    self.qvap = var4d_fromzarr(ds, ntime, ndims, "qvap")
    self.qcond = var4d_fromzarr(ds, ntime, ndims, "qcond") 
    
    self.theta = self.get_potential_temp(setup) 

    ds = get_rawdataset(dataset) 
    self.Mr_ratio = setup["Mr_ratio"]
    self.press_units = ds["press"].units # probably hecto pascals
    self.temp_units = ds["temp"].units # probably kelvin
    self.theta_units = ds["temp"].units # probably kelvin

  def get_vapourpressure(self):
    '''returns vapour and saturation pressure '''
    
    p_pascals = self.press*100 # convert from hPa to Pa
    pv = thermoeqns.vapour_pressure(p_pascals, self.qvap, self.Mr_ratio) / 100 # [hPa]
    psat = thermoeqns.saturation_pressure(self.temp) / 100 # [hPa]
   
    return pv, psat

  def get_relativehumidity(self):
    ''' returns relative humidty and supersaturation '''
    
    p_pascals = self.press*100 # convert from hPa to Pa
    relh, supersat = thermoeqns.relative_humidity(p_pascals, self.temp, 
                                                  self.qvap, self.Mr_ratio)
    return relh, supersat
  
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
    elif key == "relh":
      return self.get_relativehumidity()[0]
    elif key == "supersat":
      return self.get_relativehumidity()[1]
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

  def get_potential_temp(self, setup):

    press = self.press*100 # convert from hPa to Pa
    theta = thermoeqns.dry_pot_temp(self.temp, press, self.qvap, setup)        # parcel potential temp
  
    return theta

class Time:
  
  def __init__(self, dataset):
    
    ds = get_rawdataset(dataset) 
    
    self.secs = ds["time"].values
    self.mins = self.secs / 60
    self.hrs = self.secs / 60 / 60
  
  def __getitem__(self, key):
    if key == "secs":
      return self.secs
    elif key == "mins":
      return self.mins
    elif key == "hrs":
      return self.hrs
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

class GridBoxes:
  ''' grid setup, gridbox indexes and nsupers over time
  in each gridbox as well as 2D (z,x) meshgrids '''

  def __init__(self, dataset, grid):
    
    ds = get_rawdataset(dataset)
     
    self.grid = grid
    self.gbxindex = var3d_fromzarr(ds, grid["ndims"], "gbxindex")
    self.gbxindex = var4d_fromzarr(ds, grid["ndims"], "nsupers")

    self.xxh, self.zzh = np.meshgrid(self.grid["xhalf"],
                                     self.grid["zhalf"], indexing="ij") # dims [xdims, zdims] [m]
    
    self.xxf, self.zzf = np.meshgrid(self.grid["xfull"],
                                     self.grid["zfull"], indexing="ij") # dims [xdims, zdims] [m]

  def __getitem__(self, key):
    if key == "grid":
      return self.grid
    elif key == "gbxindex":
      return self.gbxindex
    if key == "xxhzzh":
      return self.xxh, self.zzh
    if key == "xxfzzf":
      return self.xxf, self.zzf
    else:
      err = "no known return provided for "+key+" key"
      raise ValueError(err)

class Raindrops:
  
  def __init__(self, sddata, rlim=40):
    ''' return data for (rain)drops with radii > rlim.
    Default minimum raindrops size is rlim=40microns'''
    
    israin = sddata.radius >= rlim # ak array True for raindrops
    self.totnsupersrain = ak.num(israin[israin==True])

    self.sdindex = sddata.sdindex[israin]
    self.sd_gbxindex = sddata.sd_gbxindex[israin] 
    self.eps = sddata.eps[israin] 
    self.radius = sddata.radius[israin] 
    self.m_sol = sddata.m_sol[israin] 

    if np.any(sddata.coord3):
      self.coord3 = sddata.coord3[israin] 
      if np.any(sddata.coord1):
        self.coord1 = sddata.coord1[israin] 
        if np.any(sddata.coord2):
          self.coord2 = sddata.coord2[israin] 

  def __getitem__(self, key):
    if key == "totnsupers_rain":
      return self.totnsupers_rain
    elif key == "sdindex":
      return self.sdindex
    elif key == "sd_gbxindex":
      return self.sd_gbxindex
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

def attrtimeseries_for_1superdrop(sddata, id, attr):
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

def attrtimeseries_for_superdropssample(sddata, attr,
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
    attr_timeseries = attrtimeseries_for_1superdrop(sddata, id, attr)
    ndrops_attr.append(attr_timeseries)
  
  return np.asarray(ndrops_attr).T

def attr_at_times(attrdata, time, times2sel):
  '''selects attribute at given times
   (for all superdroplets in sddata)'''

  selected_attr = [] # list containing an attribute at selected times
  for t in times2sel:
    ind = np.argmin(abs(time-t))
    selected_attr.append(attrdata[ind]) 
  
  return ak.Array(selected_attr)

def attrs_at_times(sddata, time, times2sel, attrs2sel):
  '''selects attributes at given times from
  sddata (for all superdroplets in sddata)'''

  selected_data = {} # dict containting selected attributes at selected times
  
  for attr in attrs2sel:
    
    selattr_data = attr_at_times(sddata[attr], time, times2sel)
    selected_data[attr] = selattr_data
  
  return selected_data