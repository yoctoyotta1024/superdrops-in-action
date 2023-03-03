import os
import sys
import numpy as np

abspath = "/Users/yoctoyotta1024/Documents/autumnwinter2022_23/" +\
    "clara-bayley-superdroplets/"
sys.path.append(abspath+"/superdroplet_model/")
from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from pySD.editconfigfile import edit_config_params
from pySD import cxx2py

### ----------------- INPUTS ----------------- ###
# path and filenames for creating SD 
# initial conditions and for running model
binpath = abspath+"verticalresolution_experiment/bin/"
constsfile = abspath+"superdroplet_model/src/include/claras_SDconstants.hpp"
configfile = abspath+"verticalresolution_experiment/verticalresexp_config.txt"

# [plot, save] figures of initial conditions
isfigures = [True, True] 

# domain / gridbox and outputlabel settings
xgrid = np.asarray([0, 1000]) 
ygrid = np.asarray([0, 1000])
zgridlimits = [0, 1000] # [minz, maxz] [m] of domain
#resolutions = [1000, 500, 250, 125, 62.5, 31.25] # deltaz [m] of domain gridboxes
resolutions = [1000, 500, 250, 125] # deltaz [m] of domain gridboxes
run_nums = range(0, 15, 1) # experiment numbers to run
outputlabel = sys.argv[1] # label for output e.g. "condcoll" or "golovin"

# settings for sampling radii from exponential in volume distirbution
volexpr0             = 30.531e-6                   # peak of volume exponential distribution [m]
numconc              = 2**(23)                     # total no. conc of real droplets [m^-3]
rspan                = [1e-8, 9e-5]                # max and min range of radii to sample [m]
randomr              = True                        # sample radii range randomly or not

radiiprobdist = radiiprobdistribs.VolExponential(volexpr0, rspan)
radiigen = initattributes.SampleDryradiiGen(rspan, randomr) # radii are sampled from rspan [m]

# settings for randomly choosing initial SDs' coord3s in domain
coord3span           = zgridlimits                 # max and min range of coord3 to sample [m]                 
randomcoord3         = True                        # sample coord3 range randomly or not
coord3gen = initattributes.SampleCoord3Gen(coord3span, randomcoord3)
### ------------------------------------------ ###

### ----------- PREPARE EXPERIMENT ----------- ###

# # create initial SD conditions to use in all experiments
# for j in run_nums:
#   initSDsfile = binpath+"dimlessSDsinit_run"+str(j)+".dat"
  
#   samplevol = read_gbxboundaries.calc_domainvol(np.asarray(coord3span), xgrid, ygrid)
#   print("sample VOL:", samplevol)
#   initattrs = initattributes.InitAttributes(radiigen, radiiprobdist, 
#                                             coord3gen, numconc, samplevol)
#   create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrs, 
#                                                     configfile, constsfile)

#   if isfigures[0]:
#     read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
#                                           samplevol, binpath, isfigures[1])
    
# # create gridbox files to use in all experiments
# for i, res in enumerate(resolutions):
#   zgrid = zgridlimits+[res] # input settings for zgrid for given experiment
#   gridfile = binpath+"resexp"+str(i)+"_dimlessGBxbounds.dat"
 
#   create_gbxboundaries.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
#                                                        ygrid, constsfile)
#   read_gbxboundaries.print_domain_info(constsfile, gridfile)
  
#   if isfigures[0]:
#       read_gbxboundaries.plot_gridboxboundaries(constsfile, gridfile, 
#                                                 binpath, isfigures[1])

### ------------------------------------------ ###

# ## -------------- COMPILE MODEL ------------- ###

os.chdir(abspath+"superdroplet_model/build")
os.system("pwd")
os.system("make clean && make")

# ## ------------------------------------------ ###

### ------------- RUN EXPERIMENT ------------- ###

os.chdir(binpath)

for j in run_nums:
  
  initSDsfile = "dimlessSDsinit_run"+str(j)+".dat"
    
  for i, res in enumerate(resolutions):

    gridfile = "resexp"+str(i)+"_dimlessGBxbounds.dat"

    # modify where zarr file saves (relative to binpath)
    params2edit = {
    "initSDs_filename" : initSDsfile,
    "grid_filename" : gridfile,
    "setuptxt" : "resexp"+str(i)+"_setup.txt",
    "zarrbasedir" : outputlabel+"/resexp"+str(i)+"/"+outputlabel+"_run"+str(j)+".zarr",
    }
    edit_config_params(configfile, params2edit)

    # run model
    os.chdir(binpath)
    os.system(abspath+'superdroplet_model/build/src/coupledmodel ' +
                    configfile+' '+constsfile)

### ------------------------------------------ ###