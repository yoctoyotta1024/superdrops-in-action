# for 128 SD randomly distirbuted in < 750m of domain, vary initial
# supersaturation profile (sbelow and sabove) to see effect on rain
# distribution and initiation time. e.g. higher supersaturation above
# zbase (sabove) means faster condnsational growth and therefore rain
# formation sonner in updraught whereas lower supersaturation -> slower
# condenstinal growth -> later rain onset and in downdraught

import os
import sys
import numpy as np
from pathlib import Path 
import time 

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

isgenSDsGBxs = True # create gridbox bounadires and SD binaries
isgenThermo  = True  # create thermodynamics files
isfigures = [True, True]

runids = range(0,1,1) # numbers of for initial SD conditions
sratios_experiments = { # s_ratio [below, above] Zbase and in moistlayer for each experiment
   "ss1p0_1p001_1p005_V2" : [1.0, 1.001, 1.005],
}

### ---------------------------------------------------------------- ###
### paths and filenames for inputs and outputs
currentdir = "/home/m/m300950/superdrops_in_action/prescribed2dflow/ssvar/"
path2build = "/work/mh1126/m300950/prescribed2dflow/ssvar/build/"
binariespath = path2build+"/share/"

constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
gridfile =  binariespath+"/dimlessGBxbounds.dat" # note this should match config.txt
configfile = currentdir+"/ssvarconfig.txt"

savefigpath = currentdir
binpath = path2build+"../bin/"
tempdir = currentdir+"/temp/"

### input parameters for gridbox boundaries
zgrid                = [0, 1500, 50]
xgrid                = [0, 1500, 50]
ygrid                = np.asarray([0, 20])

### input parameters for superdroplets
zlim                 = 400
npergbx              = 256

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
Zbase                = 650       # [m]
moistlayer = {
                 "z1": 650, # [m]
                 "z2": 750, # [m]
                 "x1": 0,   # [m]
                 "x2": 750, # [m]
}
### ---------------------------------------------------------------- ###
def edit_bash_script(bashfile, path2build, tempdir, configdir,
                     constsfile, expid):
  
  os.system("cp "+bashfile+" "+bashfile[:-3]+"_backup.sh")

  with open(bashfile, "r") as f:
    lines = f.readlines()
  
  for l in range(len(lines)):
    if "#SBATCH --job-name=" in lines[l]:
      lines[l] = "#SBATCH --job-name="+expid+"\n"
    if "#SBATCH --output=" in lines[l]:
      lines[l] = "#SBATCH --output="+tempdir+"/ssvarexp_"+\
                    expid+"_out.%j.out"+"\n"
    if "#SBATCH --error=" in lines[l]:
      lines[l] = "#SBATCH --error="+tempdir+"/ssvarexp_"+\
                    expid+"_err.%j.out"+"\n"
    if "path2build=" in lines[l]:
      lines[l] = "path2build="+path2build+"\n"                
    if "configdir=" in lines[l]:
      lines[l] = "configdir="+configdir+"\n"
    if "experimentid=" in lines[l]:
      lines[l] = "experimentid="+"/"+exp+"\n"
    if "constsfile=" in lines[l]:
      lines[l] = "constsfile="+constsfile+"\n"
  
  f = open(bashfile, "w")
  f.close()
  with open(bashfile, "a") as f:
    f.writelines(lines)

def echo_and_sys(cmd):
  os.system("echo "+cmd)
  os.system(cmd)

def configfiles_forexperiment_runX(exp, runn, binariespath, binpath_exp,
                                   gridfile, thermo_filenames,
                                   configfile, tempdir):
  
  initSDs_filename = binariespath+"/run"+str(runn)+"_dimlessSDsinit.dat"
  setuptxt = binpath_exp+"run"+str(runn)+"setup.txt"                 
  zarrbasedir = binpath_exp+"run"+str(runn)+"SDMdata.zarr"  

  print(" --- exp "+exp+" run "+str(runn)+" ---")
  print("gridfile:", gridfile)
  print("thermofiles:", thermo_filenames[:-4]+"_[XXX].dat")
  print("initSDs:", initSDs_filename)
  print("output to: "+setuptxt+"\n           "+zarrbasedir)

  ### modify config file ###
  configparams2edit = {
    "initSDs_filename" : initSDs_filename,
    "grid_filename" : gridfile,
    "setuptxt" : setuptxt,
    "zarrbasedir" : zarrbasedir,
    "press_filename" : thermo_filenames[:-4]+"_press.dat", 
    "temp_filename" : thermo_filenames[:-4]+"_temp.dat",
    "qvap_filename" : thermo_filenames[:-4]+"_qvap.dat",
    "qcond_filename" : thermo_filenames[:-4]+"_qcond.dat",
    "wvel_filename" : thermo_filenames[:-4]+"_wvel.dat",
    "uvel_filename" : thermo_filenames[:-4]+"_uvel.dat",
    "vvel_filename" : thermo_filenames[:-4]+"_vvel.dat",
    }
  
  editconfigfile.edit_config_params(configfile, configparams2edit)
  tempconfigfile = tempdir+"/"+exp+"_run"+str(runn)+"_config.txt" # n.b. this must match bash script
  echo_and_sys("cp "+configfile+" "+tempconfigfile)

  return tempconfigfile
### ---------------------------------------------------------------- ###
if path2CLEO == path2build:
  raise ValueError("build directory cannot be CLEO")
else:
  Path(path2build).mkdir(exist_ok=True) 
  Path(binariespath).mkdir(exist_ok=True) 
  Path(binpath).mkdir(exist_ok=True) 
  Path(tempdir).mkdir(exist_ok=True) 

# write initial conditions / setup binaries
if isgenSDsGBxs:
  cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, ygrid, constsfile)

  nsupers = iSDs.nsupers_at_domain_base(gridfile, constsfile, npergbx, zlim)
  initattrsgen = iSDs.InitManyAttrsGen(radiigen, radiiprobdist,
                                        coord3gen, coord1gen, coord2gen)
  for n in runids: 
    initSDsfile = binariespath+"/run"+str(n)+"_dimlessSDsinit.dat" # note this should match config.txt
    csupers.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                        configfile, constsfile,
                                        gridfile, nsupers, numconc)

  ### plot initial conditions / setup
  if isfigures[0]:
      if isfigures[1]:
          Path(savefigpath).mkdir(exist_ok=True) 
      
      rgrid.print_domain_info(constsfile, gridfile)
      rgrid.plot_gridboxboundaries(constsfile, gridfile, savefigpath, isfigures[1])

      rsupers.plot_initGBxsdistribs(configfile, constsfile,
                                                     initSDsfile, gridfile,
                                                     savefigpath, isfigures[1], 0)

### generate thermodyanmics for each s_ratios experiment
if isgenThermo:
  for exp, sratios in sratios_experiments.items():
    thermopath = binariespath+"/"+exp+"/"
    
    Path(thermopath).mkdir(exist_ok=True) 
    thermofiles =  thermopath+"dimless.dat"
    moistlayer["mlsratio"] = sratios[2]
    thermodyngen = thermogen.ConstHydrostaticAdiabat(configfile, constsfile, PRESS0, 
                                          THETA, qvapmethod, sratios[0:2], Zbase,
                                          qcond, WMAX, Zlength, Xlength,
                                          VVEL, moistlayer)
    
    print("experiment: ", exp, "sratios:", sratios, "in thermofiles:", thermofiles)
    cthermo.write_thermodynamics_binary(thermofiles, thermodyngen, configfile,
                                        constsfile, gridfile)

### run model for each s_ratios experiment
print("--- compiling runCLEO ---\nin "+path2build)
os.chdir(path2build)
os.system("make -j 16")
os.chdir(currentdir)

for exp, sratios in sratios_experiments.items():
  
  ### names of initial condiitons / setup binarues
  thermo_filenames = binariespath+"/"+exp+"/dimless.dat"

  ### where to output data
  binpath_exp = binpath+"/"+exp+"/"  
  Path(binpath_exp).mkdir(exist_ok=True) 
    
  if isfigures[0]:
      savefigpath_exp = savefigpath+"/"+exp+"/"
      Path(savefigpath_exp).mkdir(exist_ok=True) 
      if isfigures[1]:
          Path(savefigpath).mkdir(exist_ok=True) 
      rthermo.plot_thermodynamics(constsfile, configfile, gridfile,
                                  thermo_filenames, savefigpath_exp,
                                  isfigures[1])
  
  print("\n- copying config to temp files -")  
  for runn in runids:  
    tempconfigfile = configfiles_forexperiment_runX(exp, runn, binariespath, binpath_exp,
                                   gridfile, thermo_filenames,
                                   configfile, tempdir)  
    print("config file copied to: "+tempconfigfile)

  print("\n- executing runCLEO via sbatch -")  
  bashfile = currentdir+"/ssvarrunexp.sh"
  edit_bash_script(bashfile, path2build, tempdir,
                    tempdir, constsfile, exp)
  runsstr = " ".join([str(n) for n in list(runids)])
  print("executing experiment: "+exp+" for runs "+runsstr)
  echo_and_sys("sbatch "+bashfile+" "+runsstr)

  print("-----------------------")
### ---------------------------------------------------------------- ###


