import os
import sys
import numpy as np
import matplotlib.pyplot as plt

#### DON'T FORGET TO CHANGE SDM PROCESS IN main.cpp TO 
# JUST COLLISIONS USING GOLVINS KERNEL ####

abspath = "/Users/yoctoyotta1024/Documents/autumnwinter2022_23/" +\
    "clara-bayley-superdroplets/"
sys.path.append(abspath+"/superdroplet_model/")
sys.path.append(abspath+"plottingscripts/")
sys.path.append(abspath+"validations/")
from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from src.handlesrc import *
from src_validationplots.golovin_figure import golovin_validation_figure

############### INPUTS ##################
# path and filenames for creating SD
# initial conditions and for running model
binpath = abspath+"validations/shima_2009/bin/"
constsfile = abspath+"superdroplet_model/src/include/claras_SDconstants.hpp"
configfile = abspath+"validations/shima_2009/golovinconfig.txt"
initSDsfile = binpath+"golovin_dimlessSDsinit.dat"
gridfile = binpath+"golovin_dimlessGBxboundaries.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, False]

# settings for 0D Model (no superdroplet or grid coordinates)
coord_params = ["false"]
zgrid = np.asarray([100, 0])
xgrid = np.asarray([0, 100]) 
ygrid = np.asarray([0, 100])

# settings for distirbution from exponential in droplet volume
volexpr0             = 30.531e-6                   # peak of volume exponential distribution [m]
numconc              = 2**(23)                     # total no. conc of real droplets [m^-3]
rspan                = [1e-8, 9e-5]                # max and min range of radii to sample [m]
randomr              = True                        # sample radii range randomly or not

samplevol = read_gbxboundaries.calc_domainvol(zgrid, xgrid, ygrid)
radiiprobdist = radiiprobdistribs.VolExponential(volexpr0, rspan)
radiigen = initattributes.SampleDryradiiGen(rspan, randomr) # radii are sampled from rspan [m]
coord3gen            = None                        # do not generate superdroplet coord3s

# path and file names for plotting results
setupfile = binpath+"golovinsetup.txt"
dataset = binpath+"golovinsol.zarr"

# ### 1. create files with initial SDs conditions and gridbox boundaries            
initattrs = initattributes.InitAttributes(radiigen, radiiprobdist,
                                          coord3gen, numconc, samplevol)
create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrs, 
                                                  configfile, constsfile)

create_gbxboundaries.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
                                                    ygrid, constsfile)
read_gbxboundaries.print_domain_info(constsfile, gridfile)

if isfigures[0]:
    read_gbxboundaries.plot_gridboxboundaries(constsfile, gridfile, 
                                        binpath, isfigures[1])
    read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
                                          samplevol, binpath, isfigures[1])
plt.close()

# 2. run model
os.chdir(abspath+"superdroplet_model/build")
os.system("pwd")
os.system("make clean && make")
os.chdir(binpath)
os.system("rm -rf "+dataset)
os.system(abspath+'superdroplet_model/build/src/coupledmodel ' +
          configfile+' '+constsfile)

# 3. load results
# read in constants and intial setup from setup .txt file
setup, grid = pysetuptxt.get_setup_grid(setupfile, gridfile)
SDprops = commonsuperdropproperties.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                                              setup["MR_SOL"], setup["IONIC"])
sddata = pyzarr.get_sddata(dataset)
time = pyzarr.get_time(dataset)

# 3. plot results
tplt = [0, 1200, 2400, 3600]
smoothsig = 0.62*(setup["nsupers"]**(-1/5)) # 0.2 factor for guassian smoothing
plotwitherr = True

fig, ax = golovin_validation_figure(plotwitherr, time,
                         sddata, tplt, grid["domainvol"], SDprops,
                            numconc, volexpr0, smoothsig)

savename = "/golovin_validation.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()            