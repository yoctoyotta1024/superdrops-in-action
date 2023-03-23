import os
import sys
import numpy as np
import matplotlib.pyplot as plt

path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO) # for imports from pySD package

from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from pySD.editconfigfile import edit_config_params
from pySD import cxx2py

### ----------------- INPUTS ----------------- ###
# path and filenames for creating SD 
# initial conditions and for running model
# apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/"+\
#         "superdrops_in_action/verticalresolution_experiment/"
apath = "/home/m/m300950/superdrops_in_action/verticalresolution_experiment/"
binpath = apath+"binhighres/"
constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
configfile = apath+"verticalresexp_config.txt"

# [plot, save] figures of initial conditions
isfigures = [True, True] 

# domain / gridbox and outputlabel settings
run_nums = range(0, 5, 1) # experiment numbers to run
outputlabel = sys.argv[1] # label for output e.g. "condcoll" or "golovin"
xgrid = np.asarray([0, 1000]) 
ygrid = np.asarray([0, 1000])

# gridspacing = "UNI" # "UNI" (uniform) or "ICON" (non-uniform) grid spacing
# resolutions = [25, 50, 100, 250] # deltaz [m] of domain gridboxes for uniform grid spacing
# resexplabs = ["u25", "u50", "u100", "u250"]
gridspacing = "ICON" # "UNI" (uniform) or "ICON" (non-uniform) grid spacing
#resolutions = [0.25, 0.5, 1, 2] # scale factors for ICON grid resolution
resolutions = [4] # scale factors for ICON grid resolution
resexplabs = [str(res).replace(".", "p") for res in resolutions]

# settings for sampling radii from exponential in volume distirbution
volexpr0             = 30.531e-6                   # peak of volume exponential distribution [m]
numconc              = 2**(23)                     # total no. conc of real droplets [m^-3]
rspan                = [5e-9, 9e-5]                # max and min range of radii to sample [m]
#rspan                = [2e-9, 9.8e-5]                # max and min range of radii to sample [m]
randomr              = True                        # sample radii range randomly or not

radiiprobdist = radiiprobdistribs.VolExponential(volexpr0, rspan)
radiigen = initattributes.SampleDryradiiGen(rspan, randomr) # radii are sampled from rspan [m]

# settings for randomly choosing initial SDs' coord3s in domain
coord3span           = [500, 1500]                 # max and min range of coord3 to sample [m]                 
randomcoord3         = True                        # sample coord3 range randomly or not
coord3gen = initattributes.SampleCoord3Gen(coord3span, randomcoord3)
### ------------------------------------------ ###

def icon191levels_zgrid(scale_resolution, show_plot=False):

  icon191_zhalf = np.array([1523.668,
      1374.309,
      1229.543,
      1089.563,
      954.591,
      824.889,
      700.767,
      582.597,
      470.846,
      366.104,
      269.158,
      181.115,
      103.685,
      40,
      0])
  
  icon191_deltaz = icon191_zhalf[:-1] - icon191_zhalf[1:]
  
  if scale_resolution <= 0:
    raise ValueError("scale factor for resolution must be > 0")
  
  elif scale_resolution >= 1:
    deltaz = np.repeat(icon191_deltaz / scale_resolution, scale_resolution)
    zgrid = icon191_zhalf[0] - np.cumsum(deltaz)
    zgrid = np.insert(zgrid, 0, icon191_zhalf[0])
  
  elif scale_resolution < 1:
    a = int(1/scale_resolution)
    zgrid = (icon191_zhalf)[np.s_[::a]]
    if zgrid[-1] != 0:
      zgrid = np.append(zgrid, 0)
  
  zgrid = np.abs(np.around(zgrid, decimals=4))
   
  if show_plot:
    print("zgrid = ", zgrid)
    print("ngridboxes = ", len(zgrid))
    
    deltaz = zgrid[:-1] - zgrid[1:]
    plt.scatter(deltaz, zgrid[:-1], linestyle="--",
                color="k", marker="+")

    plt.plot(icon191_deltaz, icon191_zhalf[:-1], linestyle="-",
                color="r", label="ICON 191 levels", zorder=0)
    
    plt.xlabel("level thickness /m")
    plt.ylabel("level upper boundary /m")
    plt.ylim([0, np.amax(icon191_zhalf)])
    plt.legend(loc="upper left")
    plt.show()

  return zgrid


# ----------- PREPARE EXPERIMENT ----------- ###

# create initial SD conditions to use in all experiments
for j in run_nums:
  initSDsfile = binpath+"dimlessSDsinit_run"+str(j)+".dat"
  
  samplevol = read_gbxboundaries.calc_domainvol(np.asarray(coord3span), xgrid, ygrid)
  print("sample VOL:", samplevol)
  initattrs = initattributes.InitAttributes(radiigen, radiiprobdist, 
                                            coord3gen, numconc, samplevol)
  create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrs, 
                                                    configfile, constsfile)

  if isfigures[0]:
    read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
                                          samplevol, binpath, isfigures[1])
    
# create gridbox files to use in all experiments
for i, resexp in enumerate(resexplabs):
  
  if gridspacing == "ICON":
    zgrid = icon191levels_zgrid(resolutions[i], True)
  elif gridspacing == "UNI":
    zgridlimits = [0, 1500] # [zmin, zmax] of domain
    zgrid = zgridlimits+[resolutions[i]] # input settings for zgrid for given experiment
  else:
    raise ValueError("gridspacing can be either 'UNI' or 'ICON'")
  
  gridfile = binpath+"resexp"+resexp+"_dimlessGBxbounds.dat"
 
  create_gbxboundaries.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
                                                       ygrid, constsfile)
  read_gbxboundaries.print_domain_info(constsfile, gridfile)
  
  if isfigures[0]:
      read_gbxboundaries.plot_gridboxboundaries(constsfile, gridfile, 
                                                binpath, isfigures[1])

# # ------------------------------------------ ###

# ## -------------- COMPILE MODEL ------------- ###

os.chdir(path2CLEO+"build")
os.system("pwd")
os.system("make clean && make")

# ## ------------------------------------------ ###

### ------------- RUN EXPERIMENT ------------- ###

os.chdir(binpath)

for j in run_nums:
  
  initSDsfile = "dimlessSDsinit_run"+str(j)+".dat"
    
  for i, resexp in enumerate(resexplabs):
    gridfile = "resexp"+resexp+"_dimlessGBxbounds.dat"

    # modify where zarr file saves (relative to binpath)
    params2edit = {
    "initSDs_filename" : initSDsfile,
    "grid_filename" : gridfile,
    "setuptxt" : "resexp"+resexp+"_setup.txt",
    "zarrbasedir" : outputlabel+"/resexp"+resexp+"/"+\
                    outputlabel+"_run"+str(j)+".zarr",
    }
    edit_config_params(configfile, params2edit)

    # run model
    os.chdir(binpath)
    os.system(path2CLEO+'/build/src/coupledCVODECLEO ' +
               configfile+' '+constsfile)
### ------------------------------------------ ###
