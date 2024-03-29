# Script creates the data and
# plots the same plots as in Figure 5 of
# "On the CCN (de)activation nonlinearities"
# S. Arabas and S. Shima 2017 to check
# radius growth/shrinking due to
# condensation/evaporation is correct

# To create build dir:
# CXX=[compiler choice] cmake -S [path2CLEO] -B ./build
# e.g. CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build
# or CXX=g++-13 CC=gcc-13 cmake -S ../../../CLEO/ -B ./build -DKokkos_ENABLE_OPENMP=ON -DKokkos_ARCH_NATIVE=ON

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

path2CLEO = sys.argv[1]
path2action = sys.argv[2]
configfile = sys.argv[3]
path2valids = sys.argv[2]+"validations/"

sys.path.append(path2CLEO)                           # for imports from pySD package
sys.path.append(path2action+"sdmplotting/")
sys.path.append(path2valids)

from pySD import editconfigfile
from pySD.initsuperdropsbinary_src import *
from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from pySD.gbxboundariesbinary_src import create_gbxboundaries as cgrid
from datsrc import *
from validsrc import condensationcurves as ccs

############### INPUTS ##################
# path and filenames for creating SD
# initial conditions and for running model
constsfile = path2CLEO+"libs/claras_SDconstants.hpp"
buildpath = path2valids+"arabas_shima_2017/build/"
binpath = buildpath+"bin/"
initSDsfile = binpath+"arabas_dimlessSDsinit.dat"
gridfile = binpath+"arabas_dimlessGBxboundaries.dat"

# booleans for [making, showing] initialisation figures
isfigures = [True, False]

# settings for 0D Model (no superdroplet or grid coordinates)
nsupers = {0: 32}
coord_params = ["false"]
zgrid = np.asarray([0, 100])
xgrid = np.asarray([0, 100])
ygrid = np.asarray([0, 100])

# settings for monodisperse droplet radii
# [m^-3] total no. concentration of droplets
numconcs = [500e6, 500e6, 50e6]
monors = [0.05e-6, 0.1e-6, 0.1e-6]
coord3gen = None                        # do not generate superdroplet coords
coord1gen = None
coord2gen = None
# volume SD sample occupies (entire domain) [m^3]
samplevol = rgrid.calc_domainvol(zgrid, xgrid, ygrid)

# setup parameters
params1 = {
    "W_AVG": 1,
    "T_HALF": 150,
    "T_END": 300,
    "COUPLTSTEP": 1,
    "OBSTSTEP": 2,
    "lwdth": 2,
}

params2 = {
    "W_AVG": 0.5,
    "T_HALF": 300,
    "T_END": 600,
    "COUPLTSTEP": 1,
    "OBSTSTEP": 2,
    "lwdth": 1,
}
params3 = {
    "W_AVG": 0.002,
    "T_HALF": 75000,
    "T_END": 150000,
    "COUPLTSTEP": 3,
    "OBSTSTEP": 750,
    "lwdth": 0.5,
}

paramslist = [params1, params2, params3]


def displacement(time, w_avg, thalf):
    '''displacement z given velocity, w, is sinusoidal 
    profile: w = w_avg * pi/2 * np.sin(np.pi * t/thalf)
    where wmax = pi/2*w_avg and tauhalf = thalf/pi.'''

    zmax = w_avg / 2 * thalf
    z = zmax * (1 - np.cos(np.pi * time / thalf))
    return z


# ### 1. compile model
Path(buildpath).mkdir(exist_ok=True)
os.chdir(buildpath)
os.system("pwd")
for run_num in range(len(monors)*len(paramslist)):
    dataset = binpath+"arabassol"+str(run_num)+".zarr"
    os.system("rm -rf "+dataset)
os.system("make clean && make -j 16 adiabatic0D")

# 2a. create file with gridbox boundaries
Path(binpath).mkdir(parents=True, exist_ok=True)
os.system("rm "+gridfile)
cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid,
                                     ygrid, constsfile)
rgrid.print_domain_info(constsfile, gridfile)
if isfigures[0]:
    rgrid.plot_gridboxboundaries(constsfile, gridfile,
                                 binpath, isfigures[1])
plt.close()

runnum = 0
for i in range(len(monors)):

    # 2b. create file with initial SDs conditions
    monor, numconc = monors[i], numconcs[i]
    # all SDs have the same dryradius = monor [m]
    radiigen = initattributes.MonoAttrsGen(monor)
    # monodisperse droplet radii probability distribution
    radiiprobdist = radiiprobdistribs.DiracDelta(monor)

    initattrsgen = initattributes.InitManyAttrsGen(radiigen, radiiprobdist,
                                                   coord3gen, coord1gen, coord2gen)
    os.system("rm "+initSDsfile)
    create_initsuperdrops.write_initsuperdrops_binary(initSDsfile, initattrsgen,
                                                      configfile, constsfile,
                                                      gridfile, nsupers, numconc)

    if isfigures[0]:
        read_initsuperdrops.plot_initGBxsdistribs(configfile, constsfile, initSDsfile,
                                              gridfile, binpath, isfigures[1], "all")
        plt.close()

    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(5, 16))
    for params in paramslist:

        zarrbasedir = binpath+"arabassol"+str(runnum)+".zarr"
        os.system("rm -rf "+binpath+zarrbasedir)
        params["zarrbasedir"] = binpath+"arabassol"+str(runnum)+".zarr"

        # 3. edit relevant setup file parameters
        editconfigfile.edit_config_params(configfile, params)

        # 4. run model
        os.system(buildpath+'src/adiabatic0D ' +
                  configfile+' '+constsfile)

        # 5. load results
        setupfile = binpath+"arabassetup.txt"
        dataset = binpath+"arabassol"+str(runnum)+".zarr"

        # read in constants and intial setup from setup .txt file
        setup, grid = pysetuptxt.get_setup_gridinfo(setupfile, gridfile)
        SDprops = sdprops.CommonSuperdropProperties(setup["RHO_L"], setup["RHO_SOL"],
                                                    setup["MR_SOL"], setup["IONIC"])
        thermo = pyzarr.get_thermodata(dataset, setup, grid["ndims"])
        time = pyzarr.get_time(dataset).secs
        sddata = pyzarr.get_sddata(dataset)
        zprof = displacement(time, setup["W_AVG"], setup["T_HALF"])

        radius = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "radius")
        eps = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "eps")
        m_sol = pyzarr.attrtimeseries_for_1superdrop(sddata, 0, "m_sol")

        numconc = np.sum(sddata["eps"][0])/grid["domainvol"]/1e6  # [/cm^3]

        # relative humidty and supersaturation
        press = thermo.press*100  # convert from hPa to Pa
        relh, supersat = thermoeqns.relative_humidity(press, thermo.temp,
                                                      thermo.qvap, setup["Mr_ratio"])

        # 5. plot results
        wlab = "<w> = {:.1f}".format(float(setup["W_AVG"])*100)+"cm s$^{-1}$"
        axs = ccs.condensation_validation_subplots(axs, time, radius,
                                                   supersat.flatten(),
                                                   zprof,
                                                   lwdth=params["lwdth"],
                                                   lab=wlab)

        runnum += 1

    ccs.plot_kohlercurve_with_criticalpoints(axs[1], radius, m_sol[0],
                                             thermo.temp.flatten()[0],
                                             SDprops.IONIC, SDprops.MR_SOL)

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

    savename = "arabas_shima_condensation_"+str(i)+".png"
    fig.savefig(binpath+savename, dpi=400,
                bbox_inches="tight", facecolor='w', format="png")
    print("Figure .png saved as: "+binpath+savename)
    plt.show()