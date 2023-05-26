import numpy as np
from pathlib import Path 

from . import pyzarr

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
                savenpz=False, fromnpz=False):
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
        self.MassMoms = self.ensemb_massmom_from_npzfile()
      
    else: 
      for key in list(self.MassMoms.keys()):
        self.MassMoms[key] = self.ensemb_massmom_from_zarrs(zarrs, setup,
                                                            gbxs, key)
        if savenpz:
          self.save_ensemb_massmom_npzfile(key)

  def get_massmoms(self):

    return self.MassMoms

  def massmom_npzfile(self, key):

    Path(self.npzdir).mkdir(exist_ok=True) 

    return self.npzdir+"/ensemb"+key+".npz"
  
  def ensemb_massmom_from_zarrs(self, zarrs, setup, gbxs, key):
      
      zarrkeys = {"nsupers":  "nsupers",
                  "mom0": "massmoment0",
                  "mom1": "massmoment1",
                  "mom2": "massmoment2"
                  }
      
      ensembledata = []
      for zarr in zarrs:
        data1run = pyzarr.massmom_fromzarr(zarr, setup["ntime"],
                                           gbxs["ndims"], zarrkeys[key])
        ensembledata.append(data1run)
      stats = EnsembStats(ensembledata, axis=(0,2)) # stats avg over time and y dims
      
      return stats

  def save_ensemb_massmom_npzfile(self, key):
    
    npzfile = self.massmom_npzfile(key)
    stats = self.MassMoms[key]

    np.savez(npzfile, mean=stats.mean, stderr=stats.stderr,
                      q1=stats.q1, q3=stats.q3)
    print("mass momement "+key+" ensemble stats saved in "+npzfile)
  
  def ensemb_massmom_from_npzfile(self): 
    
    for key in list(self.MassMoms.keys()):
      npzfile = self.massmom_npzfile(key)
      file = np.load(npzfile)

      self.MassMoms[key] = EnsembStats(file, fromnpz=True)  
    
    return self.MassMoms
  
class EnsemblePrecip:

  def __init__(self, zarrs=[], setup="", gbxs="", npzdir="",
                savenpz=False, fromnpz=False):
    ''' return average statistics for an ensemble
    of datasets for the total rate of mass
    loss from domain [mm/hr] '''

    self.npzdir = npzdir

    self.Precip = {"rate":  None, # [mm/hr]
                  "accum":  None} # [mm]

    if savenpz and fromnpz:
      err = "cannot save and load data from npzfile in same instance"
      raise ValueError(err)
    
    if fromnpz:
      self.Precip = self.ensemb_precip_from_npzfiles()
    
    else: 
      self.Precip = self.ensemb_precip_from_zarrs(zarrs, gbxs)
      if savenpz:
        self.save_ensemb_precip_npzfiles()

  def get_precip(self):

      return self.Precip
   
  def precip_npzfile(self, key):

    Path(self.npzdir).mkdir(exist_ok=True) 

    return self.npzdir+"/ensemb_precip"+key+".npz"
  
  def ensemb_precip_from_zarrs(self, zarrs, gbxs):
      
    rates, accums = [], []
    for zarr in zarrs:
      rate, accum = pyzarr.surfaceprecip_fromdataset(zarr, gbxs)
      
      rates.append(rate) # [mm/hr]
      accums.append(accum) # [mm]
    
    Precip = {"rate": EnsembStats(rates, axis=0), 
              "accum":  EnsembStats(accums, axis=0)} 
    
    return Precip

  def save_ensemb_precip_npzfiles(self):

    for key, stats in self.Precip.items(): 
      
      npzfile = self.precip_npzfile(key)
      np.savez(npzfile, mean=stats.mean, stderr=stats.stderr,
                        q1=stats.q1, q3=stats.q3)
      print("precip "+key+" ensemble stats saved in "+npzfile)
    
  def ensemb_precip_from_npzfiles(self): 
    
    for key in list(self.Precip.keys()):
      npzfile = self.precip_npzfile(key)
      file = np.load(npzfile)

      self.Precip[key] = EnsembStats(file, fromnpz=True)  

    return self.Precip