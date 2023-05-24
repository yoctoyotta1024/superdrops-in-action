import os
import sys
import numpy as np
from pathlib import Path 

path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO)

from pySD.gbxboundariesbinary_src import create_gbxboundaries as  cgrid
from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from pySD.thermobinary_src import thermogen
from pySD.thermobinary_src import create_thermodynamics as cthermo
from pySD.thermobinary_src import read_thermodynamics as rthermo
from pySD.initsuperdropsbinary_src import initattributes as iSDs
from pySD.initsuperdropsbinary_src import radiiprobdistribs as rprobs 
from pySD.initsuperdropsbinary_src import create_initsuperdrops as csupers 
from pySD.initsuperdropsbinary_src import read_initsuperdrops as rsupers 
from pySD import editconfigfile 

from ensemblerun_src import *

isgenbinaries = True # create gridbox bounadires, thermodynamics and SD binaries
isfigures = [True, True]

runids = range(0,10,1) # numbers of for initial SD conditions
experimentids = { # number of SDs per GBx initially (in gbxs with SDs)
   "n64" : 64,
}

### ---------------------------------------------------------------- ###
### paths and filenames for inputs and outputs
currentdir = "/home/m/m300950/superdrops_in_action/prescribed2dflow/conv1/"
path2build = "/work/mh1126/m300950/prescribed2dflow/conv1/build/"
binariespath = path2build+"/share/"

constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
gridfile =  binariespath+"/dimlessGBxbounds.dat" # note this should match config.txt
thermofiles =  binariespath+"/dimless.dat" # note this should match config.txt
configfile = currentdir+"/convconfig.txt"
bashfile = currentdir+"/runexp.sh"

savefigpath = currentdir
binpath = path2build+"../bin/"
tempdir = currentdir+"/temp/"

### input parameters for gridbox boundaries
zgrid                = [0, 1500, 20]
xgrid                = [0, 1500, 20]
ygrid                = np.asarray([0, 20])

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
numconc              = np.sum(scalefacs)*100*15/2
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
  cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, ygrid, constsfile)

  thermodyngen = thermogen.ConstHydrostaticAdiabat(configfile, constsfile, PRESS0, 
                                          THETA, qvapmethod, sratios, Zbase,
                                          qcond, WMAX, Zlength, Xlength,
                                          VVEL, moistlayer)  
  cthermo.write_thermodynamics_binary(thermofiles, thermodyngen, configfile,
                                        constsfile, gridfile)
  
  
  ### plot initial conditions / setup
  if isfigures[0]:
      if isfigures[1]:
          Path(savefigpath).mkdir(exist_ok=True) 
      
      rgrid.print_domain_info(constsfile, gridfile)
      rgrid.plot_gridboxboundaries(constsfile, gridfile, savefigpath, isfigures[1])
      
      rthermo.plot_thermodynamics(constsfile, configfile, gridfile,
                                  thermofiles, savefigpath, isfigures[1])


for exp, npergbx in experimentids.items():

  nsupers = iSDs.nsupers_at_domain_base(gridfile, constsfile, npergbx, zlim)
  initattrsgen = iSDs.InitManyAttrsGen(radiigen, radiiprobdist,
                                        coord3gen, coord1gen, coord2gen)
  
  for runn in runids: 
    initSDsfile = initSDsfilename(binariespath, exp, runn) 
    print("experiment: ", exp, "nSDs/GBx init:", npergbx,
          "run: ",runn , " initSDsfile:", initSDsfile)
    
    csupers.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                        configfile, constsfile,
                                        gridfile, nsupers, numconc)

    if isfigures[0]:
      if isfigures[1]:
        savefigpath_exp = savefigpath+"/"+exp+"/"
        Path(savefigpath_exp).mkdir(exist_ok=True) 
        savefigstem = savefigpath_exp+"/run"+str(runn)+"_"
      rsupers.plot_initGBxsdistribs(configfile, constsfile,
                                    initSDsfile, gridfile,
                                    savefigstem, isfigures[1], 0)

### run model for each s_ratios experiment
print("--- compiling runCLEO ---\nin "+path2build)
os.chdir(path2build)
os.system("make -j 16")
os.chdir(currentdir)

for exp, npergbx in experimentids.items():
  
  ### where to output data
  binpath_exp = binpath+"/"+exp+"/"  
  Path(binpath_exp).mkdir(exist_ok=True)   
  
  ### edit nSDsvec in config given npergbx of experiment
  edit_confignSDsvec(configfile, zgrid, xgrid, zlim, npergbx)

  ### copy config to temporary file for each run of experiment
  print("\n- copying config to temporary file -")  
  for runn in runids:  
    initSDsfile = initSDsfilename(binariespath, exp, runn) 
    tempconfigfile = configfiles_for_exprunX(exp, runn, binpath_exp,
                                              gridfile, initSDsfile,
                                              thermofiles, configfile,
                                              tempdir)
     
    print("config file copied to: "+tempconfigfile)

  ### run all runs of experiment
  print("\n- executing runCLEO via sbatch -")  
  edit_bash_script(bashfile, path2build, tempdir,
                   tempdir, constsfile, exp)
  runsstr = " ".join([str(n) for n in list(runids)])

  print("experiment: "+exp+" for runs "+runsstr)
  echo_and_sys("sbatch "+bashfile+" "+runsstr)
  print("-----------------------")
### ---------------------------------------------------------------- ###