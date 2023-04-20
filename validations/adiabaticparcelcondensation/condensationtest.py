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
from validsrc import individSDs, condensationcurves

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
nsupers = {0: 5}
coord_params = ["false"]
zgrid = np.asarray([0, 100])
xgrid = np.asarray([0, 100]) 
ygrid = np.asarray([0, 100])

# settings for monodisperse droplet radii
numconc              = 0.05e9                        # [m^-3] total no. concentration of droplets
monor                = 0.1e-6                        
radiigen  = initattributes.MonoAttrsGen(monor)       # all SDs have the same dryradius = monor [m]
radiiprobdist = radiiprobdistribs.DiracDelta(monor)  # monodisperse droplet radii probability distribution
samplevol = read_gbxboundaries.calc_domainvol(zgrid, xgrid, ygrid) # volume SD sample occupies (entire domain) [m^3]
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

### 2. compile and run model
Path(buildpath).mkdir(exist_ok=True) 
os.chdir(buildpath)
os.system('pwd')
os.system("make clean && make cond0D")
os.system('rm -rf '+dataset)
os.system(buildpath+'src/cond0D ' + configfile+' '+constsfile)

# 3. load and plot results
# read in constants and intial setup from setup .txt file
setup, grid = pysetuptxt.get_setup_grid(setupfile, gridfile)
SDprops = commonsuperdropproperties.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                                              setup["MR_SOL"], setup["IONIC"])
thermo = pyzarr.get_thermodata(dataset, setup)
time = pyzarr.get_time(dataset)
sddata = pyzarr.get_sddata(dataset)
zprof = displacement(time, setup["W_AVG"], setup["T_HALF"])

# relative humidty and supersaturation
press = thermo.press*100 #convert from hPa to Pa
relh, supersat = thermoeqns.relative_humidity(press, thermo.temp, 
                                              thermo.qvap, setup["Mr_ratio"])
                                              
minid, maxid = 0, setup["totnsupers0"] # sample drops to plot from whole range of SD ids
ndrops2plot = setup["totnsupers0"]
radii = pyzarr.attr_timeseries_for_nsuperdrops_sample(sddata, "radius", ndrops2plot, minid, maxid) 
fig, ax = individSDs.individ_radiusgrowths_figure(time, radii)
savename = "cond_SDsradiigrowth.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()    

radius = pyzarr.extract_1superdroplet_attr_timeseries(sddata, 0, "radius")
eps = pyzarr.extract_1superdroplet_attr_timeseries(sddata, 0, "eps")
m_sol = pyzarr.extract_1superdroplet_attr_timeseries(sddata, 0, "m_sol")

numconc = np.sum(sddata["eps"][0])/grid["domainvol"]/1e6 # [/cm^3]

fig, axs = condensationcurves.condensation_validation_figure(time, eps, radius, m_sol,
                                                            thermo.temp, supersat, zprof, SDprops,
                                                            setup, numconc)
savename = "cond_validation.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()            