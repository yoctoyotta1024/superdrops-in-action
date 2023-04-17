import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# To create build dir:
# CXX=/opt/homebrew/bin/g++-12 cmake -S [path2CLEO] -B ./build 
# e.g. CXX=/opt/homebrew/bin/g++-12 cmake -S ../../../CLEO/ -B ./build

path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/superdrops_in_action/"
#path2CLEO = "/home/m/m300950/CLEO/"
#apath = "/home/m/m300950/superdrops_in_action/"

sys.path.append(path2CLEO) # for imports from pySD package
sys.path.append(apath+"sdmplotting/")
sys.path.append(apath+"validations/")

from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from datsrc import *
from validsrc.golovin_figure import golovin_validation_figure

############### INPUTS ##################
# path and filenames for creating SD
# initial conditions and for running model
buildpath = apath+"validations/shima_2009/build/"
binpath = buildpath+"bin/"
constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
configfile = apath+"validations/shima_2009/golovinconfig.txt"
initSDsfile = binpath+"golovin_dimlessSDsinit.dat"
gridfile = binpath+"golovin_dimlessGBxboundaries.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, True]

# settings for 0D Model (no superdroplet or grid coordinates)
nsupers = {0: 2048}
coord_params = ["false"]
zgrid = np.asarray([0, 100])
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
coord3gen            = None                        # do not generate superdroplet coords
coord1gen            = None                        
coord2gen            = None                        

# path and file names for plotting results
setupfile = binpath+"golovinsetup.txt"
dataset = binpath+"golovinsol.zarr"

# ### 1. create files with initial SDs conditions and gridbox boundaries
Path(binpath).mkdir(parents=True, exist_ok=True)             
create_gbxboundaries.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
                                                    ygrid, constsfile)
read_gbxboundaries.print_domain_info(constsfile, gridfile)

initattrsgen = initattributes.InitManyAttrsGen(radiigen, radiiprobdist,
                                               coord3gen, coord1gen, coord2gen)
create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                                  configfile, constsfile,
                                                  gridfile, nsupers, numconc)

if isfigures[0]:
    read_gbxboundaries.plot_gridboxboundaries(constsfile, gridfile, 
                                        binpath, isfigures[1])
    read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
                                          gridfile, binpath, isfigures[1])
plt.close()

### 2. compile and the run model
Path(buildpath).mkdir(exist_ok=True) 
os.chdir(buildpath)
os.system('pwd')
os.system("make clean && make golcolls0D")
os.system('rm -rf '+dataset)
os.system(buildpath+'/src/golcolls0D ' + configfile+' '+constsfile)

# 3. load results
# read in constants and intial setup from setup .txt file
setup, grid = pysetuptxt.get_setup_grid(setupfile, gridfile)
SDprops = commonsuperdropproperties.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                                              setup["MR_SOL"], setup["IONIC"])
sddata = pyzarr.get_sddata(dataset)
time = pyzarr.get_time(dataset)

# 3. plot results
tplt = [0, 1200, 2400, 3600]
smoothsig = 0.62*(setup["totnsupers0"]**(-1/5)) # 0.2 factor for guassian smoothing
plotwitherr = True

fig, ax = golovin_validation_figure(plotwitherr, time,
                         sddata, tplt, grid["domainvol"], SDprops,
                            numconc, volexpr0, smoothsig)

savename = "golovin_validation.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()            