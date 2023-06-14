#file: ensemblestats.py
import sys
import numpy as np
from pathlib import Path 

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action/"
sys.path.append(path2sds)
from sdmplotting.datsrc import *
from sdmplotting.pltsrc import *
from sdmplotting.datsrc.sdprops import *

exp = "n256"
expdir = "/conc1e7_res25/"
 
runids = range(0,15,1)
timerange = [0, 14400]
cloudmasst0 = 900 # time to use to define initial cloud mass for t10 time

basepath = "/work/mh1126/m300950/prescribed2dflow/"+expdir
path2ensemble = basepath+"/"+exp+"/"
gridfile = basepath+"/../build/share/"+expdir+"/dimlessGBxbounds.dat"

npzdir = path2ensemble+"/ensemb/"
savenpz = True

### ------------------------ helper funcs -------------------------- ###
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

### -------------- save npz files for ensemble stats --------------- ###
zarrs, setuptxt = get_zarrbasedirs(path2ensemble, runids)
make_paths([npzdir])

### setup, superdroplet properties and grid
setup = pysetuptxt.setuptxt2dict(setuptxt, nattrs=3, isprint=False)
gbxs = pysetuptxt.get_gridboxes(None, gridfile, setup, isprint=False)

### Get Ensemble Data From Datasets (and save to npz files)
ensemble.EnsembleMassMoments(zarrs=zarrs, setup=setup, gbxs=gbxs,
                              npzdir=npzdir, savenpz=savenpz,
                              timerange=timerange)

ensemble.EnsembleRaindropMassMoments(zarrs=zarrs, setup=setup, gbxs=gbxs,
                                npzdir=npzdir, savenpz=savenpz, 
                                timerange=timerange)        
               
ensemble.EnsembleSurfPrecip(zarrs=zarrs, setup=setup, gbxs=gbxs,
                            npzdir=npzdir, savenpz=savenpz,
                            timerange=timerange)

ensemble.EnsembleRainTimes(zarrs=zarrs, setup=setup, gbxs=gbxs,
                           npzdir=npzdir, savenpz=savenpz,
                           t0=cloudmasst0)     
            
# ensemble.EnsemblePrecipEstimateFromSDs(zarrs=zarrs, gbxs=gbxs,
#                                        npzdir=npzdir, savenpz=savenpz, 
#                                        timerange=timerange)

# rainrlim = 40 # rlim for defining raindrops as r >= rlim
# ensemble.EnsembleRaindropMassMomsFromSDs(zarrs=zarrs, setup=setup, gbxs=gbxs,
#                                      npzdir=npzdir, savenpz=savenpz, 
#                                      timerange=timerange, rlim=rainrlim)                       
### ---------------------------------------------------------------- ###



### -------------- load ensemble stats From npz files -------------- ###
# massmoms = ensemble.EnsembleMassMoments(npzdir=nnpzdir, fromnpz=True).get_massmoms()                     
# rainmassmoms = ensemble.EnsembleRainMassMoments(npzdir=nnpzdir, fromnpz=True).get_massmoms()
# raintimes = ensemble.EnsembleRainTimes(npzdir=npzdir, fromnpz=True).get_raintimes()                     
# precip = ensemble.EnsembleSurfPrecip(npzdir=nnpzdir, fromnpz=True).get_precip()
# precipestimate = ensemble.EnsemblePrecipEstimateFromSDs(npzdir=nnpzdir, fromnpz=True).get_precip_estimate()
# rainmassmoms2 = ensemble.EnsembleRainMassMomsFromSDs(npzdir=nnpzdir, fromnpz=True).get_massmoms()                     
### ---------------------------------------------------------------- ###