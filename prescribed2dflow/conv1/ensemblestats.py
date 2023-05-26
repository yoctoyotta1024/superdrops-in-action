import sys
import numpy as np
from pathlib import Path 

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action/"
sys.path.append(path2sds)
from sdmplotting.datsrc import *
from sdmplotting.pltsrc import *
from sdmplotting.datsrc.sdprops import *

exp = "n64"
runids = range(0,10,1)
timerange = [0, 14400]

basepath = "/work/mh1126/m300950/prescribed2dflow/conv1/"
path2ensemble = basepath+"/bin/"+exp+"/"
gridfile = basepath+"/build/share/dimlessGBxbounds.dat"

npzdir = path2ensemble+"/ensemb/"
savenpz = True
savefigpath = path2sds+"prescribed2dflow/conv1/"+exp+"/ensemb/"

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
make_paths([npzdir, savefigpath])

### setup, superdroplet properties and grid
setup = pysetuptxt.setuptxt2dict(setuptxt, nattrs=3, isprint=False)
gbxs = pysetuptxt.get_gridboxes(None, gridfile, setup, isprint=False)
SDprops = CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                    setup["MR_SOL"], setup["IONIC"])

### Get Ensemble Data From Datasets (and save to npz files)
ensemble.EnsembleMassMoments(zarrs=zarrs, setup=setup, gbxs=gbxs,
                              npzdir=npzdir, savenpz=savenpz,
                              timerange=timerange)

ensemble.EnsemblePrecip(zarrs=zarrs, setup=setup, gbxs=gbxs,
                          npzdir=npzdir, savenpz=savenpz, 
                          timerange=timerange)
### ---------------------------------------------------------------- ###



### -------------- load ensemble stats From npz files -------------- ###
# mmmoms = ensemble.EnsembleMassMoments(npzdir=npzdir, fromnpz=True).get_massmoms()                     
# precip = ensemble.EnsemblePrecip(npzdir=npzdir, fromnpz=True).get_precip()
### ---------------------------------------------------------------- ###