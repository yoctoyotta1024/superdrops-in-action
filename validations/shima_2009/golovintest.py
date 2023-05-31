# Script creates the data and
# plots as in Shima et al. 2009
# to show comparision of 0D box model
# of collision-coalescence with
# Golovin's analytical solution

# To create build dir:
# CXX=[compiler choice] cmake -S [path2CLEO] -B ./build
# e.g. CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build
# or CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build -DKokkos_ENABLE_OPENMP=ON -DKokkos_ARCH_NATIVE=ON

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
# apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/superdrops_in_action/"
path2CLEO = "/home/m/m300950/CLEO/"
apath = "/home/m/m300950/superdrops_in_action/"

sys.path.append(path2CLEO)  # for imports from pySD package
sys.path.append(apath+"sdmplotting/")
sys.path.append(apath+"validations/")

from pySD.thermobinary_src import read_thermodynamics as rthermo
from pySD.thermobinary_src import create_thermodynamics as cthermo
from pySD.thermobinary_src.thermogen import ConstUniformThermo
from pySD.initsuperdropsbinary_src import *
from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from pySD.gbxboundariesbinary_src import create_gbxboundaries as cgrid
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
thermofile = binpath+"dimlessthermodynamics.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, True]

# settings for 0D Model (no superdroplet or grid coordinates
# and constant uniform thermodynamics)
nsupers = {0: 2048}
coord_params = ["false"]
zgrid = np.asarray([0, 100])
xgrid = np.asarray([0, 100])
ygrid = np.asarray([0, 100])
PRESS = 100000.0                        # initial pressure [Pa]
TEMP = 273.15                           # initial parcel temperature [T]
relh = 95.0                             # initial relative humidity (%)
qcond = 0.0                             # initial liquid water content []
WVEL, UVEL, VVEL = [None]*3            # don't create wind velocity files

# settings for distirbution from exponential in droplet volume
# peak of volume exponential distribution [m]
volexpr0 = 30.531e-6
numconc = 2**(23)                     # total no. conc of real droplets [m^-3]
rspan = [1e-8, 9e-5]                # max and min range of radii to sample [m]
randomr = True                        # sample radii range randomly or not

samplevol = rgrid.calc_domainvol(zgrid, xgrid, ygrid)
radiiprobdist = radiiprobdistribs.VolExponential(volexpr0, rspan)
radiigen = initattributes.SampleDryradiiGen(
    rspan, randomr)  # radii are sampled from rspan [m]
coord3gen = None                        # do not generate superdroplet coords
coord1gen = None
coord2gen = None

# path and file names for plotting results
setupfile = binpath+"golovinsetup.txt"
dataset = binpath+"golovinsol.zarr"

# ### 1. create files with initial SDs conditions and gridbox boundaries

Path(binpath).mkdir(parents=True, exist_ok=True)
os.system("rm "+gridfile)
os.system("rm "+initSDsfile)
cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid,
                                     ygrid, constsfile)
rgrid.print_domain_info(constsfile, gridfile)

thermogen = ConstUniformThermo(PRESS, TEMP, None, qcond,
                               WVEL, UVEL, VVEL, relh=relh,
                               constsfile=constsfile)
cthermo.write_thermodynamics_binary(thermofile, thermogen, configfile,
                                    constsfile, gridfile)

initattrsgen = initattributes.InitManyAttrsGen(radiigen, radiiprobdist,
                                               coord3gen, coord1gen, coord2gen)
create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrsgen,
                                                  configfile, constsfile,
                                                  gridfile, nsupers, numconc)

if isfigures[0]:
    rgrid.plot_gridboxboundaries(constsfile, gridfile,
                                 binpath, isfigures[1])
    rthermo.plot_thermodynamics(constsfile, configfile, gridfile,
                                thermofile, binpath, isfigures[1])
    read_initsuperdrops.plot_initGBxsdistribs(configfile, constsfile, initSDsfile,
                                              gridfile, binpath, isfigures[1], "all")
plt.close()

# 2. compile and the run model
Path(buildpath).mkdir(exist_ok=True)
os.chdir(buildpath)
os.system('pwd')
os.system('rm -rf '+dataset)
os.system("make clean && make -j 16 golcolls0D")
os.system(buildpath+'/src/golcolls0D ' + configfile+' '+constsfile)

# 3. load results
# read in constants and intial setup from setup .txt file
setup, grid = pysetuptxt.get_setup_gridinfo(setupfile, gridfile)
SDprops = sdprops.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                            setup["MR_SOL"], setup["IONIC"])
sddata = pyzarr.get_sddata(dataset)
time = pyzarr.get_time(dataset).secs

# 3. plot results
tplt = [0, 1200, 2400, 3600]
# 0.2 factor for guassian smoothing
smoothsig = 0.62*(setup["totnsupers0"]**(-1/5))
plotwitherr = True

fig, ax = golovin_validation_figure(plotwitherr, time,
                                    sddata, tplt, grid["domainvol"], SDprops,
                                    numconc, volexpr0, smoothsig)

savename = "golovin_validation.png"
fig.savefig(binpath+savename, dpi=400,
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()
