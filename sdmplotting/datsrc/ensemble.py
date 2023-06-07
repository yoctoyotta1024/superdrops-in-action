#file: ensemble.py
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
        self.MassMoms = statsdict_from_npzfile(self.MassMoms, self.npzfile) 
    else: 
        self.MassMoms = self.ensemb_from_zarrs(zarrs, setup,
                                                       gbxs, timerange)
        if savenpz:
          Path(self.npzdir).mkdir(exist_ok=True) 
          save_npz(self.MassMoms, self.npzfile, "mass moments")

  def get_massmoms(self):
    return self.MassMoms

  def npzfile(self, key):
    return self.npzdir+"/ensemb"+key+".npz"

  def massmoms_fromzarr(self, zarr, setup, gbxs, timerange):

    keyconv = {
      "mom0": "massmom0",
      "mom1": "massmom1",
      "mom2": "massmom2"
    }

    ntime, ndims = setup["ntime"], gbxs["ndims"]
    time = pyzarr.get_rawdataset(zarr)["time"].values
    nsupers = pyzarr.massmom_fromzarr(zarr, ntime, ndims, "nsupers")
    mom0 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, keyconv["mom0"])
    mom1 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, keyconv["mom1"])
    mom2 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, keyconv["mom2"])
  
    data = [nsupers, mom0, mom1, mom2]
    data = data_in_timerange(data, time, timerange)

    return data

  def ensemb_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    ensemble_nsupers, ensemble_mom0, ensemble_mom1, ensemble_mom2 = [], [], [], []
    for zarr in zarrs:
      data = self.massmoms_fromzarr(zarr, setup, gbxs, timerange)
      ensemble_nsupers.append(data[0]) 
      ensemble_mom0.append(data[1]) 
      ensemble_mom1.append(data[2]) 
      ensemble_mom2.append(data[3]) 

    MassMoms = {"nsupers": EnsembStats(ensemble_nsupers, axis=(0,2)), # stats avg over time and y dims
                "mom0":  EnsembStats(ensemble_mom0, axis=(0,2)),
                "mom1":  EnsembStats(ensemble_mom1, axis=(0,2)),
                "mom2":  EnsembStats(ensemble_mom2, axis=(0,2))
                } 
    return MassMoms

class EnsembleRaindropMassMoments:
  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False,
                timerange=[0, np.inf]):
    ''' return average statistics for an ensemble
    of datasets for the mass moments (averaged over 
    y dimension too)'''

    self.npzdir = npzdir
    self.MassMoms = {
    "mom0": None,
    "mom1": None,
    }

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    if fromnpz:
        self.MassMoms = statsdict_from_npzfile(self.MassMoms, self.npzfile)
    else: 
        self.MassMoms = self.ensemb_from_zarrs(zarrs, setup,
                                                       gbxs, timerange)
        if savenpz:
          Path(self.npzdir).mkdir(exist_ok=True) 
          save_npz(self.MassMoms, self.npzfile, "raindrop mass moments")

  def get_massmoms(self):
    return self.MassMoms

  def npzfile(self, key):
    return self.npzdir+"/ensemb_raindrop"+key+".npz"

  def massmoms_fromzarr(self, zarr, setup, gbxs, timerange):

    ntime, ndims = setup["ntime"], gbxs["ndims"]
    time = pyzarr.get_rawdataset(zarr)["time"].values
    m0 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, "rainmom0")
    m1 = pyzarr.massmom_fromzarr(zarr, ntime, ndims, "rainmom1")
    mom0, mom1 = data_in_timerange([m0, m1], time, timerange)
  
    return [mom0, mom1]

  def ensemb_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    mom0s, mom1s = [], []
    for zarr in zarrs:
      data = self.massmoms_fromzarr(zarr, setup, gbxs, timerange) 
      mom0s.append(data[0]) 
      mom1s.append(data[1]) 

    MassMoms = {"mom0":  EnsembStats(mom0s, axis=(0,2)), # stats avg over time and y dims
                "mom1":  EnsembStats(mom1s, axis=(0,2)),
                } 
    return MassMoms

class EnsembleSurfPrecip:
  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False,
                timerange=[0, np.inf]):
    ''' return average statistics for an ensemble
    of datasets for the mass moments (averaged over 
    y dimension too)'''

    self.npzdir = npzdir
    self.Precip = {
    "rate":  None,
    "accum": None,
    "totrate": None,
    "totaccum": None
    }

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    if fromnpz:
      self.Precip = statsdict_from_npzfile(self.Precip, self.npzfile)
    else: 
      self.Precip = self.ensemb_from_zarrs(zarrs, setup, gbxs, timerange)
      if savenpz:
        Path(self.npzdir).mkdir(exist_ok=True) 
        save_npz(self.Precip, self.npzfile, "surf precip ") 

  def get_precip(self):
    return self.Precip

  def npzfile(self, key):
    return self.npzdir+"/ensemb_precip"+key+".npz"
  
  def precip_fromzarr(self, zarr, setup, gbxs, timerange):
    
    time = pyzarr.get_rawdataset(zarr)["time"].values
    spp = pyzarr.SurfPrecip(zarr, setup["ntime"], gbxs)
    data = [spp.rate, spp.accum, spp.totrate, spp.totaccum]
    data = data_in_timerange(data, time, timerange)

    return data

  def ensemb_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    rates, accums, totrates, totaccums = [], [], [], []
    for zarr in zarrs:
      data = self.precip_fromzarr(zarr, setup, gbxs, timerange)
      rates.append(data[0])
      accums.append(data[1])
      totrates.append(data[2])
      totaccums.append(data[3])

    Precip = {"rate": EnsembStats(rates, axis=(0,2)), # stats avg over time and y dims 
              "accum": EnsembStats(accums, axis=(0,2)),
              "totrate": EnsembStats(totrates, axis=(0)),
              "totaccum": EnsembStats(totaccums, axis=(0))
              }

    return Precip

class EnsemblePrecipEstimateFromSDs:
  def __init__(self, zarrs=[], gbxs="", npzdir="",
                savenpz=False, fromnpz=False, 
                timerange=[0, np.inf]):
    ''' return average statistics for an ensemble
    of datasets for the total rate of mass
    loss from domain [mm/hr] '''

    self.npzdir = npzdir
    self.PrecipEstimate = {"totrate":  None, # [mm/hr]
                            "totaccum":  None} # [mm]

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    if fromnpz:
      self.PrecipEstimate = statsdict_from_npzfile(self.PrecipEstimate,
                                                   self.npzfile)
    else: 
      self.PrecipEstimate = self.ensemb_ppestimate_from_zarrs(zarrs, gbxs,
                                                              timerange)
      if savenpz:
        Path(self.npzdir).mkdir(exist_ok=True) 
        save_npz(self.PrecipEstimate, self.npzfile,
                  printstr="precip estimate")

  def get_precip_estimate(self):
    return self.PrecipEstimate
   
  def npzfile(self, key):
    return self.npzdir+"/ensemb_precip_estimate_"+key+".npz"
   
  def ensemb_ppestimate_from_zarrs(self, zarrs, gbxs, timerange):
      
    rates, accums = [], []
    for zarr in zarrs:
      data = pyzarr.surfaceprecip_estimate(zarr, gbxs)
      time = pyzarr.get_rawdataset(zarr)["time"].values
      rate, accum = data_in_timerange(data, time, timerange)

      rates.append(rate) # [mm/hr]
      accums.append(accum) # [mm]
    
    PrecipEstimate = {"totrate": EnsembStats(rates, axis=0), 
                      "totaccum":  EnsembStats(accums, axis=0)} 
    return PrecipEstimate

class EnsembleRaindropMassMomsFromSDs:
  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False,
                timerange=[0, np.inf], rlim=40):
    ''' return average statistics for an ensemble
    of datasets for the mass moments (averaged over 
    y dimension too) of raindrops (r > rlim)'''

    self.npzdir = npzdir
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
        self.MassMoms = statsdict_from_npzfile(self.MassMoms, self.npzfile) 
    else: 
        self.MassMoms = self.ensemb_massmoms_from_zarrs(zarrs, setup,
                                                        gbxs, timerange)
        if savenpz:
          Path(self.npzdir).mkdir(exist_ok=True) 
          save_npz(self.MassMoms, self.npzfile, "raindrop mass moments")

  def get_massmoms(self):
    return self.MassMoms

  def npzfile(self, key):
    return self.npzdir+"/ensemb_raindropfromSDs"+key+".npz"

  def raindropsum(self, data, reshape):
    sumrain = np.reshape(ak.sum(data, axis=1), reshape)
    return ak.to_numpy(sumrain, allow_missing=False)

  def calc_raindropmassmoms(self, eps, radius, m_sol, SDprops, ntime, ndims):
    '''calulate mass moments from superdroplets 
    for raindrops, ie. only including superdrops with r >= rlim '''
    reshape = [np.uint64(ntime)]+[np.uint64(n) for n in ndims]
    
    israin = radius >= self.rlim # ak array True for raindrops
    eps = ak.where(israin, eps, 0.0)
    mass = SDprops.mass(ak.where(israin, radius, 0.0),
                        ak.where(israin, m_sol, 0.0))

    nsupers = self.raindropsum(israin, reshape) 
    mom0 = self.raindropsum(eps, reshape)  
    mom1 = self.raindropsum(eps*mass, reshape)  
    mom2 = self.raindropsum(eps*mass*mass, reshape)  
    
    return [nsupers, mom0, mom1, mom2]

  def raindropmassmoms_fromzarr(self, zarr, setup, gbxs, timerange):
    ntime, ndims = setup["ntime"], gbxs["ndims"]
    SDprops = CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                    setup["MR_SOL"], setup["IONIC"])
    
    ds = pyzarr.get_rawdataset(zarr)
    nsupers_raggedcount = np.uint64(ds["nsupers"].values).flatten()
    radius = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "radius")
    eps = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "eps")
    m_sol = pyzarr.raggedvar_fromzarr(ds, nsupers_raggedcount, "m_sol")
   
    massmoms = self.calc_raindropmassmoms(eps, radius, m_sol,
                                      SDprops, ntime, ndims)
    
    time = pyzarr.get_rawdataset(zarr)["time"].values
    massmoms = data_in_timerange(massmoms, time, timerange)
    
    return massmoms

  def ensemb_massmoms_from_zarrs(self, zarrs, setup, gbxs, timerange):
      
    ensemble_nsupers, ensemble_mom0 = [], []
    ensemble_mom1, ensemble_mom2 = [], []
    for zarr in zarrs:
      data = self.raindropmassmoms_fromzarr(zarr, setup, gbxs, timerange)
      ensemble_nsupers.append(data[0]) 
      ensemble_mom0.append(data[1]) 
      ensemble_mom1.append(data[2]) 
      ensemble_mom2.append(data[3]) 

    MassMoms = {"nsupers": EnsembStats(ensemble_nsupers, axis=(0,2)), # stats avg over time and y dims
                "mom0":  EnsembStats(ensemble_mom0, axis=(0,2)),
                "mom1":  EnsembStats(ensemble_mom1, axis=(0,2)),
                "mom2":  EnsembStats(ensemble_mom2, axis=(0,2))
                } 
    return MassMoms