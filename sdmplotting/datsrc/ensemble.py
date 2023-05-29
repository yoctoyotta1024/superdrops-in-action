import numpy as np
import awkward as ak
from pathlib import Path 

from . import pyzarr
from .sdprops import CommonSuperdropProperties

def data_in_timerange(data, time, timerange):

  bools = np.where(time >= timerange[0], time <= timerange[1], False)
  
  return [d[bools] for d in data]

def statsdict_from_npzfile(statsdict, get_npzfile): 
    
    for key in list(statsdict.keys()):
      npzfile = get_npzfile(key)
      file = np.load(npzfile)

      statsdict[key] = EnsembStats(file, fromnpz=True)  

    return statsdict

def save_npz(statsdict, get_npzfile, printstr=""):

  for key, stats in statsdict.items(): 
      
    npzfile = get_npzfile(key)
    np.savez(npzfile, mean=stats.mean, stderr=stats.stderr,
                      q1=stats.q1, q3=stats.q3)
    
    print(printstr+" ensemble stats saved in "+npzfile)

class EnsembStats:

  def __init__(self, data, axis=0, fromnpz=False):

    if fromnpz:
      self.mean = data["mean"]
      self.stderr = data["stderr"]
      self.q1 = data["q1"] 
      self.q3 = data["q3"]
    else:
      n = np.shape(data)[0]
      self.mean = np.mean(data, axis=axis) # avg over ensemble runs (and y dim)
      self.stderr = np.std(data, axis=axis) / np.sqrt(n-1) # standard error of ensemble mean
      self.q1 = np.quantile(data, 0.25, axis=axis)
      self.q3 = np.quantile(data, 0.75, axis=axis)
    
class EnsembleMassMoments:

  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False,
                timerange=[0, np.inf]):
    ''' return average statistics for an ensemble
    of datasets for the mass moments (averaged over 
    y dimension too)'''

    self.npzdir = npzdir
    Path(self.npzdir).mkdir(exist_ok=True) 

    self.MassMoms = {
    "nsupers":  None,
    "mom0": None,
    "mom1": None,
    "mom2": None
    }

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    
    if fromnpz:
        self.MassMoms = self.ensemb_massmoms_from_npzfile()
      
    else: 
        self.MassMoms = self.ensemb_massmoms_from_zarrs(zarrs, setup,
                                                       gbxs, timerange)
        if savenpz:
          self.save_ensemb_massmoms_npzfile()

  def get_massmoms(self):

    return self.MassMoms

  def massmom_npzfile(self, key):

    return self.npzdir+"/ensemb"+key+".npz"
  
  def save_ensemb_massmoms_npzfile(self):

    save_npz(self.MassMoms, self.massmom_npzfile, "Mass moments")

  def ensemb_massmoms_from_npzfile(self): 

    MassMoms = statsdict_from_npzfile(self.MassMoms,
                                      self.massmom_npzfile) 
    return MassMoms

  def massmoms_fromzarr(self, zarr, setup, gbxs):

    ntime, ndims = setup["ntime"], gbxs["ndims"]

    zarrkeys = {"nsupers":  "nsupers",
                "mom0": "massmoment0",
                "mom1": "massmoment1",
                "mom2": "massmoment2"
                }

    nsupers = pyzarr.massmom_fromzarr(zarr, ntime, ndims, zarrkeys["nsupers"])
    mom0 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, zarrkeys["mom0"])
    mom1 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, zarrkeys["mom1"])
    mom2 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, zarrkeys["mom2"])
  
    return [nsupers, mom0, mom1, mom2]

  def ensemb_massmoms_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    ensemble_nsupers, ensemble_mom0, ensemble_mom1, ensemble_mom2 = [], [], [], []
    for zarr in zarrs:
      data = self.massmoms_fromzarr(zarr, setup, gbxs)
      time = pyzarr.get_rawdataset(zarr)["time"].values

      nsupers, mom0, mom1, mom2 = data_in_timerange(data, time, timerange)

      ensemble_nsupers.append(nsupers) 
      ensemble_mom0.append(mom0) 
      ensemble_mom1.append(mom1) 
      ensemble_mom2.append(mom2) 

    MassMoms = {"nsupers": EnsembStats(ensemble_nsupers, axis=(0,2)), # stats avg over time and y dims
                "mom0":  EnsembStats(ensemble_mom0, axis=(0,2)),
                "mom1":  EnsembStats(ensemble_mom1, axis=(0,2)),
                "mom2":  EnsembStats(ensemble_mom2, axis=(0,2))
                } 

    return MassMoms

class EnsemblePrecip:

  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False, 
                timerange=[0, np.inf]):
    ''' return average statistics for an ensemble
    of datasets for the total rate of mass
    loss from domain [mm/hr] '''

    self.npzdir = npzdir
    Path(self.npzdir).mkdir(exist_ok=True) 
    
    self.Precip = {"rate":  None, # [mm/hr]
                  "accum":  None} # [mm]

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    
    if fromnpz:
      self.Precip = self.ensemb_precip_from_npzfiles()
    
    else: 
      self.Precip = self.ensemb_precip_from_zarrs(zarrs, gbxs,
                                                  timerange)
      if savenpz:
        self.save_ensemb_precip_npzfiles()

  def get_precip(self):

      return self.Precip
   
  def precip_npzfile(self, key):

    return self.npzdir+"/ensemb_precip"+key+".npz"
  
  def save_ensemb_precip_npzfiles(self):
    
    save_npz(self.Precip, self.precip_npzfile, printstr="precip")
    
  def ensemb_precip_from_npzfiles(self): 

    Precip = statsdict_from_npzfile(self.Precip,
                                         self.precip_npzfile)
    return Precip
  
  def ensemb_precip_from_zarrs(self, zarrs, gbxs, timerange):
      
    rates, accums = [], []
    for zarr in zarrs:
      data = pyzarr.surfaceprecip_fromdataset(zarr, gbxs)
      time = pyzarr.get_rawdataset(zarr)["time"].values
      rate, accum = data_in_timerange(data, time, timerange)

      rates.append(rate) # [mm/hr]
      accums.append(accum) # [mm]
    
    Precip = {"rate": EnsembStats(rates, axis=0), 
              "accum":  EnsembStats(accums, axis=0)} 
    
    return Precip

import numpy as np
from pathlib import Path 

from . import pyzarr

def data_in_timerange(data, time, timerange):

  bools = np.where(time >= timerange[0], time <= timerange[1], False)
  
  return [d[bools] for d in data]

def statsdict_from_npzfile(statsdict, get_npzfile): 
    
    for key in list(statsdict.keys()):
      npzfile = get_npzfile(key)
      file = np.load(npzfile)

      statsdict[key] = EnsembStats(file, fromnpz=True)  

    return statsdict

def save_npz(statsdict, get_npzfile, printstr=""):

  for key, stats in statsdict.items(): 
      
    npzfile = get_npzfile(key)
    np.savez(npzfile, mean=stats.mean, stderr=stats.stderr,
                      q1=stats.q1, q3=stats.q3)
    
    print(printstr+" ensemble stats saved in "+npzfile)

class EnsembStats:

  def __init__(self, data, axis=0, fromnpz=False):

    if fromnpz:
      self.mean = data["mean"]
      self.stderr = data["stderr"]
      self.q1 = data["q1"] 
      self.q3 = data["q3"]
    else:
      n = np.shape(data)[0]
      self.mean = np.mean(data, axis=axis) # avg over ensemble runs (and y dim)
      self.stderr = np.std(data, axis=axis) / np.sqrt(n-1) # standard error of ensemble mean
      self.q1 = np.quantile(data, 0.25, axis=axis)
      self.q3 = np.quantile(data, 0.75, axis=axis)
    
class EnsembleRainMassMoments:

  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False,
                timerange=[0, np.inf], rlim=40):
    ''' return average statistics for an ensemble
    of datasets for the mass moments (averaged over 
    y dimension too) of raindrops (r > rlim)'''

    self.npzdir = npzdir
    Path(self.npzdir).mkdir(exist_ok=True) 

    self.rlim = rlim
    self.MassMoms = {
    "nsupers":  None,
    "mom0": None,
    "mom1": None,
    "mom2": None
    }

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    
    if fromnpz:
        self.MassMoms = self.ensemb_massmoms_from_npzfile()
      
    else: 
        self.MassMoms = self.ensemb_massmoms_from_zarrs(zarrs, setup,
                                                       gbxs, timerange)
        if savenpz:
          self.save_ensemb_massmoms_npzfile()

  def get_massmoms(self):

    return self.MassMoms

  def rainmassmom_npzfile(self, key):

    return self.npzdir+"/ensemb_rain"+key+".npz"
  
  def save_ensemb_massmoms_npzfile(self):

    save_npz(self.MassMoms, self.rainmassmom_npzfile, "Rain mass moments")

  def ensemb_massmoms_from_npzfile(self): 

    MassMoms = statsdict_from_npzfile(self.MassMoms,
                                      self.rainmassmom_npzfile) 
    return MassMoms

  def calc_rainmassmoms(self, eps, radius, m_sol, SDprops, ntime, ndims):
    '''calulate mass moments from superdroplets 
    for raindrops, ie. only including superdrops with r >= rlim '''

    reshape = [np.uint64(ntime)]+[np.uint64(n) for n in ndims]

    israin = radius >= self.rlim # ak array True for raindrops
    
    eps = ak.where(israin, eps, 0.0)
    radius = ak.where(israin, radius, 0.0)
    m_sol = ak.where(israin, m_sol, 0.0)
    mass = SDprops.mass(radius, m_sol)

    nsupers = ak.to_numpy(np.reshape(ak.sum(israin, axis=1), reshape), allow_missing=False)
    mom0 = ak.to_numpy(np.reshape(ak.sum(eps, axis=1), reshape), allow_missing=False)
    mom1 = ak.to_numpy(np.reshape(ak.sum(eps*mass, axis=1), reshape), allow_missing=False)
    mom2 = ak.to_numpy(np.reshape(ak.sum(eps*mass*mass, axis=1), reshape), allow_missing=False)
    
    return [nsupers, mom0, mom1, mom2]

  def rainmassmoms_fromzarr(self, zarr, setup, gbxs):

    ntime, ndims = setup["ntime"], gbxs["ndims"]
    
    SDprops = CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                    setup["MR_SOL"], setup["IONIC"])

    ds = pyzarr.get_rawdataset(zarr)
    nsupers_raggedcount = np.uint64(ds["nsupers"].values).flatten()
    radius = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "radius")
    eps = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "eps")
    m_sol = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "m_sol")

    massmoms = self.calc_rainmassmoms(eps, radius, m_sol, SDprops, ntime, ndims)

    return massmoms

  def ensemb_massmoms_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    ensemble_nsupers, ensemble_mom0, ensemble_mom1, ensemble_mom2 = [], [], [], []
    for zarr in zarrs:
      data = self.rainmassmoms_fromzarr(zarr, setup, gbxs)
      time = pyzarr.get_rawdataset(zarr)["time"].values

      nsupers, mom0, mom1, mom2 = data_in_timerange(data, time, timerange)

      ensemble_nsupers.append(nsupers) 
      ensemble_mom0.append(mom0) 
      ensemble_mom1.append(mom1) 
      ensemble_mom2.append(mom2) 

    MassMoms = {"nsupers": EnsembStats(ensemble_nsupers, axis=(0,2)), # stats avg over time and y dims
                "mom0":  EnsembStats(ensemble_mom0, axis=(0,2)),
                "mom1":  EnsembStats(ensemble_mom1, axis=(0,2)),
                "mom2":  EnsembStats(ensemble_mom2, axis=(0,2))
                } 

    return MassMoms