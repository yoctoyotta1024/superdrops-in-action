# script creates the data and
# plots the same plots as in Figure 5 of
# "On the CCN (de)activation nonlinearities"
# S. Arabas and S. Shima 2017 to check radius
# growth due to condensation is correct

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

#### DON'T FORGET TO CHANGE SDM PROCESS IN main.cpp TO JUST CONDENSATION ####

path2CLEO = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/CLEO/"
sys.path.append(path2CLEO) # for imports from pySD package

apath = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/superdrops_in_action/"
sys.path.append(apath+"sdmplotting")
sys.path.append(apath+"validations/")

from pySD.gbxboundariesbinary_src import create_gbxboundaries, read_gbxboundaries
from pySD.initsuperdropsbinary_src import *
from pySD import editconfigfile 
from datsrc import *
from validsrc import condensationcurves

############### INPUTS ##################
# path and filenames for creating SD
# initial conditions and for running model
binpath = apath+"validations/arabas_shima_2017/bin/"
constsfile = path2CLEO+"src/claras_SDconstants.hpp"
configfile = apath+"validations/arabas_shima_2017/arabasconfig.txt"
initSDsfile = binpath+"arabas_dimlessSDinit.dat"
gridfile = binpath+"arabas_dimlessGBxbounds.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, False]

# settings for 0D Model (no superdroplet or grid coordinates)
coord_params = ["false"]
zgrid = np.asarray([100, 0])
xgrid = np.asarray([0, 100]) 
ygrid = np.asarray([0, 100])

# settings for monodisperse droplet radii
numconcs              = [50e6, 500e6, 500e6]                        # [m^-3] total no. concentration of droplets
monors                = [0.1e-6, 0.1e-6, 0.05e-6]                
coord3gen             = None
samplevol = read_gbxboundaries.calc_domainvol(zgrid, xgrid, ygrid)  # volume SD sample occupies (entire domain) [m^3]

# setup parameters
params1 = {
    "W_AVG": 1,
    "T_HALF": 150,
    "TEND": 300,
    "OUT_TSTEP": 1,
    "lwdth": 2,
}
params2 = {
    "W_AVG": 0.5,
    "T_HALF": 300,
    "TEND": 600,
    "OUT_TSTEP": 1,
    "lwdth": 1,
}
params3 = {
    "W_AVG": 0.002,
    "T_HALF": 75000,
    "TEND": 150000,
    "OUT_TSTEP": 3,
    "lwdth": 0.5,
}

paramslist = [params1, params2, params3]

def displacement(time, w_avg, thalf):
    '''displacement z given velocity, w, is sinusoidal 
    profile: w = w_avg * pi/2 * np.sin(np.pi * t/thalf)
    where wmax = pi/2*w_avg and tauhalf = thalf/pi.'''
    
    zmax = w_avg / 2 * thalf
    z = zmax * ( 1 - np.cos(np.pi * time / thalf) )
    return z

# ### 1. compile model
os.chdir(path2CLEO+"/build")
os.system("pwd")
os.system("make clean && make")
os.chdir(binpath)
for run_num in range(len(monors)*len(paramslist)):
    dataset = binpath+"arabassol"+str(run_num)+".zarr"
    os.system("rm -rf "+dataset)

# 2a. create file with gridbox boundaries
create_gbxboundaries.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, 
                                                     ygrid, constsfile)
read_gbxboundaries.print_domain_info(constsfile, gridfile)
if isfigures[0]:
    read_gbxboundaries.plot_gridboxboundaries(constsfile, gridfile, 
                                              binpath, isfigures[1])
plt.close()

runnum = 0
for i in range(len(monors)):

    # 2b. create file with initial SDs conditions
    monor, numconc = monors[i], numconcs[i]
    radiigen  = initattributes.MonoAttrsGen(monor)       # all SDs have the same dryradius = monor [m]
    radiiprobdist = radiiprobdistribs.DiracDelta(monor)  # monodisperse droplet radii probability distribution

    initattrs = initattributes.InitAttributes(radiigen, radiiprobdist, 
                                            coord3gen, numconc, samplevol)
    create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrs, 
                                                  configfile, constsfile)

    if isfigures[0]:
        read_initsuperdrops.plot_initdistribs(configfile, constsfile, initSDsfile,
                                          samplevol, binpath, isfigures[1])
        plt.close()
    
    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(5, 16))
    for params in paramslist:

        zarrbasedir = "arabassol"+str(runnum)+".zarr"
        os.system("rm -rf "+binpath+zarrbasedir)
        params["zarrbasedir"] = "arabassol"+str(runnum)+".zarr"

        # 3. edit relevant setup file parameters
        editconfigfile.edit_config_params(configfile, params)

        # 4. run model
        os.chdir(binpath)
        os.system(path2CLEO+'/build/src/coupledmodel ' +
                  configfile+' '+constsfile)

        # 5. load results
        setupfile = binpath+"arabassetup.txt"
        dataset = binpath+"arabassol"+str(runnum)+".zarr"

        # read in constants and intial setup from setup .txt file
        setup, grid = pysetuptxt.get_setup_grid(setupfile, gridfile) 
        SDprops = commonsuperdropproperties.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                                              setup["MR_SOL"], setup["IONIC"])
        thermo = pyzarr.get_thermodata(dataset, setup)
        time = pyzarr.get_time(dataset)
        sddata = pyzarr.get_sddata(dataset)
        zprof = displacement(time, setup["W_AVG"], setup["T_HALF"])
       
        radius = pyzarr.extract_superdroplet_attr(sddata, 0, "radius")
        eps = pyzarr.extract_superdroplet_attr(sddata, 0, "eps")
        m_sol = pyzarr.extract_superdroplet_attr(sddata, 0, "m_sol")

        numconc = np.sum(sddata["eps"][0])/grid["domainvol"]/1e6 # [/cm^3]

        # relative humidty and supersaturation
        press = thermo.press*100 #convert from hPa to Pa
        relh, supersat = thermoeqns.relative_humidity(press, thermo.temp, 
                                              thermo.qvap, setup["Mr_ratio"])
                                              
        # 5. plot results
        wlab = "<w> = {:.1f}".format(float(setup["W_AVG"])*100)+"cm s$^{-1}$"
        axs = condensationcurves.condensation_validation_subplots(axs, time, radius,
                                                                  supersat, zprof,
                                                                  lwdth=params["lwdth"],
                                                                  lab=wlab)

        runnum += 1

    condensationcurves.plot_kohlercurve_with_criticalpoints(axs[1], radius, m_sol[0],
                                        thermo.temp[0], SDprops.IONIC, SDprops.MR_SOL)

    textlab = "N = "+str(numconc)+"cm$^{-3}$\n" +\
              "r$_{dry}$ = "+"{:.2g}\u03BCm\n".format(radius[0])
    axs[0].legend(loc="lower right", fontsize=10)
    axs[1].legend(loc="upper left")
    axs[0].text(0.03, 0.85, textlab, transform=axs[0].transAxes)

    axs[0].set_xlim([-1, 1])
    for ax in axs[1:]:
        ax.set_xlim([0.125, 10])
        ax.set_xscale("log")
    axs[0].set_ylim([0, 150])
    axs[1].set_ylim([-1, 1])
    axs[2].set_ylim([5, 75])

    fig.tight_layout()

    savename = "/arabas_shima_condensation_"+str(i)+".png"
    fig.savefig(binpath+savename, dpi=400, 
                bbox_inches="tight", facecolor='w', format="png")
    print("Figure .png saved as: "+binpath+savename)
    plt.show()      