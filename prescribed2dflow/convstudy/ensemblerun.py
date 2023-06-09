import os
import sys
import numpy as np
from pathlib import Path 

path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO)

from pySD.initsuperdropsbinary_src import initattributes as iSDs
from pySD.initsuperdropsbinary_src import radiiprobdistribs as rprobs 

from ensemblerun_src import *

isgenbinaries = True # create gridbox boundaries, thermodynamics binaries
isgenSDbinaries = True # create SD binaries
isfigures = [True, True]

runids = range(0, 15, 1) # numbers of for initial SD conditions
expdir = "/conc1e7_res25/"
experimentids = { # number of SDs per GBx initially (in gbxs with SDs)
   "n2": 2,
}
sumbit_individruns = False # submit each run of an experiment as seperate SLURM job

### ---------------------------------------------------------------- ###
### paths and filenames for inputs and outputs
currentdir = "/home/m/m300950/superdrops_in_action/prescribed2dflow/convstudy/"
path2build = "/work/mh1126/m300950/prescribed2dflow/build/"
# path2build = "/work/mh1126/m300950/prescribed2dflow//build/"
binariespath = path2build+"/share/"+expdir+"/"

constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
gridfile =  binariespath+"/dimlessGBxbounds.dat" # note this should match config.txt
thermofiles =  binariespath+"/dimless.dat" # note this should match config.txt
configfile = currentdir+"/convconfig.txt"

savefigpath = currentdir+"/"+expdir+"/"
binpath = path2build+"../"+expdir+"/"
tempdir = currentdir+"/temp/"

### input parameters for gridbox boundaries
zgrid                = [0, 1500, 25]
xgrid                = [0, 1500, 25]
ygrid                = np.asarray([0, 25])

### input parameters for superdroplets
zlim                 = 400

coord3gen            = iSDs.SampleCoordGen(True) 
coord1gen            = iSDs.SampleCoordGen(True) 
coord2gen            = None                        

rspan                = [3e-9, 3e-6]                
randomr              = True                        
radiigen             = iSDs.SampleDryradiiGen(rspan, randomr) 
geomeans             = [0.02e-6, 0.15e-6]               
geosigs              = [1.4, 1.6]                    
scalefacs            = [6e6, 4e6]
numconc              = np.sum(scalefacs)
radiiprobdist        = rprobs.LnNormal(geomeans, geosigs, scalefacs)

### input parameters for thermodynamic profiles
PRESS0               = 101500    # [Pa]
THETA                = 289       # [K]
qcond                = 0.0       # [Kg/Kg]
WMAX                 = 0.6       # [m/s]
VVEL                 = None      # [m/s]
Zlength              = 1500      # [m]
Xlength              = 1500      # [m]
qvapmethod           = "sratio"
sratios              = [1.0, 1.001]
Zbase                = 650       # [m]
moistlayer = {
                 "z1": 650, # [m]
                 "z2": 750, # [m]
                 "x1": 0,   # [m]
                 "x2": 750, # [m]
           "mlsratio": 1.005
}
### ---------------------------------------------------------------- ###

make_essentialpaths(path2CLEO, path2build, binariespath, binpath, tempdir)

# write initial conditions / setup binaries
if isgenbinaries:
  gen_gridboxboundaries_binary(gridfile, constsfile, zgrid, xgrid, ygrid, 
                                  isfigures, savefigpath)

  gen_thermodynamics_binaries(thermofiles, configfile, constsfile,
                                gridfile, PRESS0, THETA, qvapmethod,
                                sratios, Zbase, qcond, WMAX,
                                Zlength, Xlength, VVEL, moistlayer,
                                isfigures, savefigpath)

if isgenSDbinaries:
  for exp, npergbx in experimentids.items():
    gen_initSDs_for_ensembleruns(binariespath, gridfile, configfile,
                                 constsfile, exp, runids, npergbx,
                                 zlim, radiigen, radiiprobdist, 
                                 coord3gen, coord1gen, coord2gen,
                                 numconc, isfigures, savefigpath)

### run model for each s_ratios experiment
print("--- compiling runCLEO ---\nin "+path2build)
os.chdir(path2build)
os.system("make -j 16")
os.chdir(currentdir)

for exp, npergbx in experimentids.items():
  binpath_exp = binpath+"/"+exp+"/"  
  Path(binpath_exp).mkdir(exist_ok=True)   
  
  ### edit nSDsvec in config given npergbx of experiment
  edit_confignSDsvec(configfile, zgrid, xgrid, zlim, npergbx)
  
  ### copy config to a temporary file for each run
  temporary_configfile_copy(tempdir, exp, runids, binpath_exp, 
                              binariespath, gridfile, thermofiles,
                              configfile)
  
  if sumbit_individruns:
    bashfile = currentdir+"/runexp1run.sh"
    submit_runs_individually(bashfile, path2build, tempdir, constsfile,
                             exp, runids)
  else:
    bashfile = currentdir+"/runexp.sh"
    submit_allruns1job(bashfile, path2build, tempdir, constsfile,
                       exp, runids)
### ---------------------------------------------------------------- ###