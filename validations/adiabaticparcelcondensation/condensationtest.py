import os
import sys
import numpy as np
import matplotlib.pyplot as plt

#### DON'T FORGET TO CHANGE SDM PROCESS IN main.cpp TO
# JUST CONDENSATION ####

#path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO) # for imports from pySD package

#apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/superdrops_in_action/"
apath = "/home/m/m300950/superdrops_in_action/"
sys.path.append(apath+"sdmplotting/")
sys.path.append(apath+"validations/")

from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from datsrc import *
from validsrc import individSDs, condensationcurves

############### INPUTS ##################
# path and filenames for creating SD initial conditions and for running model
binpath = apath+"validations/adiabaticparcelcondensation/bin/"
constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
configfile = apath+"validations/adiabaticparcelcondensation/condconfig.txt"
initSDsfile = binpath+"cond_dimlessSDsinit.dat"
gridfile = binpath+"cond_dimlessGBxboundaries.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, False]

# settings for 0D Model (no superdroplet or grid coordinates)
coord_params = ["false"]
zgrid = np.asarray([100, 0])
xgrid = np.asarray([0, 100]) 
ygrid = np.asarray([0, 100])

# settings for monodisperse droplet radii
numconc              = 0.05e9                        # [m^-3] total no. concentration of droplets
monor                = 0.1e-6                        
coord3gen            = None
radiigen  = initattributes.MonoAttrsGen(monor)       # all SDs have the same dryradius = monor [m]
radiiprobdist = radiiprobdistribs.DiracDelta(monor)  # monodisperse droplet radii probability distribution
samplevol = read_gbxboundaries.calc_domainvol(zgrid, xgrid, ygrid) # volume SD sample occupies (entire domain) [m^3]

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

### 2. compile and run model
os.chdir(path2CLEO+"build")
os.system("pwd")
os.system("make clean && make")
os.chdir(binpath)
os.system("rm -rf "+dataset)
os.system(path2CLEO+'build/src/coupledCVODECLEO ' + configfile+' '+constsfile)

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
                                              
minid, maxid = 0, setup["nsupers"] # sample drops to plot from whole range of SD ids
ndrops2plot = setup["nsupers"]
radii = pyzarr.superdroplet_attr_for_ndrops(sddata, "radius", ndrops2plot, minid, maxid) 
fig, ax = individSDs.individ_radiusgrowths_figure(time, radii)
savename = "cond_SDsradiigrowth.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()    

radius = pyzarr.extract_superdroplet_attr(sddata, 0, "radius")
eps = pyzarr.extract_superdroplet_attr(sddata, 0, "eps")
m_sol = pyzarr.extract_superdroplet_attr(sddata, 0, "m_sol")

numconc = np.sum(sddata["eps"][0])/grid["domainvol"]/1e6 # [/cm^3]

fig, axs = condensationcurves.condensation_validation_figure(time, eps, radius, m_sol,
                                                            thermo.temp, supersat, zprof, SDprops,
                                                            setup, numconc)
savename = "cond_validation.png"
fig.savefig(binpath+savename, dpi=400, 
            bbox_inches="tight", facecolor='w', format="png")
print("Figure .png saved as: "+binpath+savename)
plt.show()            

