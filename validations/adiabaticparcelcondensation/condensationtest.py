# Script creates the data and
# plots a plot similar to Figure 5 of
# "On the CCN (de)activation nonlinearities"
# S. Arabas and S. Shima 2017 to show
# example of cusp birfucation

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# To create build dir:
# CXX=[compiler choice] cmake -S [path2CLEO] -B ./build 
# e.g. CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build
# or CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build -DKokkos_ENABLE_OPENMP=ON -DKokkos_ARCH_NATIVE=ON

# path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
# apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/superdrops_in_action/"
path2CLEO = "/home/m/m300950/CLEO/"
apath = "/home/m/m300950/superdrops_in_action/"

sys.path.append(path2CLEO) # for imports from pySD package
sys.path.append(apath+"sdmplotting/")
sys.path.append(apath+"validations/")

from pySD.gbxboundariesbinary_src import create_gbxboundaries as cgrid
from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from pySD.initsuperdropsbinary_src import *
from datsrc import *
from validsrc import individSDs
from validsrc import condensationcurves as ccs

############### INPUTS ##################
# path and filenames for creating SD initial conditions and for running model
buildpath = apath+"validations/adiabaticparcelcondensation/build/"
binpath = buildpath+"bin/"
constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
configfile = apath+"validations/adiabaticparcelcondensation/condconfig.txt"
initSDsfile = binpath+"cond_dimlessSDsinit.dat"
gridfile = binpath+"cond_dimlessGBxboundaries.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, True]

# settings for 0D Model (no superdroplet or grid coordinates)
nsupers = {0: 1}
coord_params = ["false"]
zgrid = np.asarray([0, 100])
xgrid = np.asarray([0, 100]) 
ygrid = np.asarray([0, 100])

# settings for monodisperse droplet radii
numconc              = 0.5e9                        # [m^-3] total no. concentration of droplets
monor                = 0.025e-6                        
radiigen  = initattributes.MonoAttrsGen(monor)       # all SDs have the same dryradius = monor [m]
radiiprobdist = radiiprobdistribs.DiracDelta(monor)  # monodisperse droplet radii probability distribution
samplevol = rgrid.calc_domainvol(zgrid, xgrid, ygrid) # volume SD sample occupies (entire domain) [m^3]
coord3gen            = None                        # do not generate superdroplet coords
coord1gen            = None                        
coord2gen            = None   

# path and file names for plotting results
setupfile = binpath+"condsetup.txt"
dataset = binpath+"condsol.zarr"

def displacement(time, w_avg, thalf):
    '''displacement z given velocity, w, is sinusoidal 
    profile: w = w_avg * pi/2 * np.sin(np.pi * t/thalf)
    where wmax = pi/2*w_avg and tauhalf = thalf/pi.'''
    
    zmax = w_avg / 2 * thalf
    z = zmax * ( 1 - np.cos(np.pi * time / thalf) )
    return z

# ### 1. create files with initial SDs conditions and gridbox boundaries
Path(binpath).mkdir(parents=True, exist_ok=True) 
os.system("rm "+gridfile)
os.system("rm "+initSDsfile)            
cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
                                                     ygrid, constsfile)
rgrid.print_domain_info(constsfile, gridfile)

initattrsgen = initattributes.InitManyAttrsGen(radiigen, radiiprobdist,
                                               coord3gen, coord1gen, coord2gen)
create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                                  configfile, constsfile,
                                                  gridfile, nsupers, numconc)


if isfigures[0]:
    rgrid.plot_gridboxboundaries(constsfile, gridfile, 
                                              binpath, isfigures[1])
    read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
                                          gridfile, binpath, isfigures[1])
plt.close()

### 2. compile and run model
Path(buildpath).mkdir(exist_ok=True) 
os.chdir(buildpath)
os.system('pwd')
os.system('rm -rf '+dataset)
os.system("make clean && make -j 16 cond0D")
os.system(buildpath+'src/cond0D ' + configfile+' '+constsfile)

# 3. load and plot results
# read in constants and intial setup from setup .txt file
setup, grid = pysetuptxt.get_setup_grid(setupfile, gridfile)
SDprops = sdprops.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                             setup["MR_SOL"], setup["IONIC"])
thermo = pyzarr.get_thermodata(dataset, setup, grid["ndims"])
time = pyzarr.get_time(dataset).secs
sddata = pyzarr.get_sddata(dataset)
zprof = displacement(time, setup["W_AVG"], setup["T_HALF"])

# relative humidty and supersaturation
press = thermo.press*100 #convert from hPa to Pa
relh, supersat = thermoeqns.relative_humidity(press, thermo.temp, 
                                              thermo.qvap, setup["Mr_ratio"])
                                              
minid, maxid = 0, setup["totnsupers0"] # sample drops to plot from whole range of SD ids
ndrops2plot = setup["totnsupers0"]
radii = pyzarr.attrtimeseries_for_superdropssample(sddata, "radius", ndrops2plot, minid, maxid) 
fig, ax = individSDs.individ_radiusgrowths_figure(time, radii)
savename = "cond_SDsradiigrowth.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()    

radius = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "radius")
eps = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "eps")
m_sol = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "m_sol")

numconc = np.sum(sddata["eps"][0])/grid["domainvol"]/1e6 # [/cm^3]

fig, axs = ccs.condensation_validation_figure(time, eps, radius, m_sol,
                                                thermo.temp.flatten(),
                                                supersat.flatten(), zprof, SDprops,
                                                setup, numconc)
savename = "cond_validation.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()            