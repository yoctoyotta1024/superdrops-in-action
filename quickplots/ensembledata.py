import sys
import numpy as np
from pathlib import Path 

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action/"
sys.path.append(path2sds)
from sdmplotting.datsrc import *
from sdmplotting.pltsrc import *
from sdmplotting.datsrc.commonsuperdropproperties import *

exp = "n64"
runids = range(0,2,1)
basepath = "/work/mh1126/m300950/prescribed2dflow/conv1/"
path2ensemble = basepath+"/bin/"+exp+"/"
gridfile = basepath+"/build/share/dimlessGBxbounds.dat"

npzdir = path2ensemble+"/ensemb/"
savenpz = True
savefigpath = path2sds+"prescribed2dflow/conv1/"+exp+"/ensemb/"
### ---------------------------------------------------------------- ###

def get_zarrbasedirs(ensemblepath, runids): 
    
  zarrs = []
  for runn in runids:
     zarrs.append(ensemblepath + "/run"+str(runn)+"SDMdata.zarr")
  setuptxt = ensemblepath + "/run0setup.txt"

  print("---\nensemble members:\n"+"\n    ".join(zarrs)+"\n---")
  return zarrs, setuptxt 

def make_paths(paths):
  
  for path in paths:
    Path(path).mkdir(exist_ok=True) 
  print("---\ncreated dirs: \n"+"\n    ".join(paths)+"\n---")

### ---------------------------------------------------------------- ###

zarrs, setuptxt = get_zarrbasedirs(path2ensemble, runids)
make_paths([npzdir, savefigpath])

# ### setup, superdroplet properties and grid
setup, grid = pysetuptxt.get_setup_grid(setuptxt, gridfile, printinfo=False)
SDprops = CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                    setup["MR_SOL"], setup["IONIC"])

class EnsembStats:

  def __init__(self, data, fromnpz=False):

    if fromnpz:
      self.mean = data["mean"]
      self.std = data["std"]
      self.q1 = data["q1"] 
      self.q3 = data["q3"]
    else:
      self.mean = np.mean(data, axis=(0,2)) # avg over ensemble runs and y dim
      self.std = np.std(data, axis=(0,2))
      self.q1 = np.quantile(data, 0.25, axis=(0,2))
      self.q3 = np.quantile(data, 0.75, axis=(0,2))
    
class EnsembleMassMoments:

  def __init__(self, zarrs=[], setup="", grid="", npzdir="",
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
    
    for key in list(self.MassMoms.keys()):
      if fromnpz:
        self.MassMoms[key] = self.ensemb_massmom_from_npzfile(key)
      
      else: 
        self.MassMoms[key] = self.ensemb_massmom_from_zarrs(zarrs, setup,
                                                            grid, key)
        if savenpz:
          self.save_ensemb_massmom_npzfile(key)

  def get_massmoms(self):

      return self.MassMoms

  def massmom_npzfile(self, key):

    Path(self.npzdir).mkdir(exist_ok=True) 

    return self.npzdir+"/ensemb"+key+".npz"
  
  def ensemb_massmom_from_zarrs(self, zarrs, setup, grid, key):
      
      ensembledata = []
      for zarr in zarrs:
        data1run = pyzarr.MassMoments(zarr, setup, grid["ndims"])[key]
        ensembledata.append(data1run)
      stats = EnsembStats(ensembledata) 
      
      return stats

  def ensemb_massmom_from_npzfile(self, key): 
    
    npzfile = self.massmom_npzfile(key)
    file = np.load(npzfile)

    return EnsembStats(file, fromnpz=True)  

  def save_ensemb_massmom_npzfile(self, key):
    
    npzfile = self.massmom_npzfile(key)
    stats = self.MassMoms[key]

    np.savez(npzfile, mean=stats.mean, std=stats.std,
                      q1=stats.q1, q3=stats.q3)
    print("mass momement "+key+" ensemble stats saved in "+npzfile)


### Get Ensemble Data From Datasets (and save to npz files)
mmmoms = EnsembleMassMoments(zarrs=zarrs, setup=setup, grid=grid,
                             npzdir=npzdir, savenpz=True).get_massmoms()
print(mmmoms["mom0"].mean.shape)

### Load Ensemble Data From npz files
mmmoms = EnsembleMassMoments(npzdir=npzdir, fromnpz=True).get_massmoms()                     
print(mmmoms["mom0"].mean.shape)

# ### Superdroplets' quantities
# sddata = pyzarr.Sddata(dataset)
# thermo = pyzarr.Thermodata(dataset, setup, grid["ndims"])


