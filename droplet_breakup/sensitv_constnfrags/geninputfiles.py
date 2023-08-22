# File: buildexp.py
# build CLEO in work directory and create 
# gridbox and thermodynamic data files 
# and superdroplet initial conditions 

import numpy as np
from src import *

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/droplet_breakup/build/"
constsfile = path2CLEO+"/libs/claras_SDconstants.hpp"
executable = "runbreakup"

nsupers = 8192
nfrags = 256.0
runnums = [0]
configtemplate = "./configtemplate.txt"
path2out = path2build+"../constnfrags/"

genSDs = False 
genGBxsthermo = False 
plotfigs = False 
initfigspath = path2build+"bin/"

for runn in runnums:
  ### --- generate configuration file(s) --- ###
  fs = configfile_for_nfragsX(path2build, path2out, configtemplate,
                              nsupers, nfrags, runn)

if genSDs:
  rspan                = [2e-7, 2e-3]                 # min and max range of radii to sample [m]
  radiigen = iSDs.SampleDryradiiGen(rspan, True)   # radii are sampled from rspan [m]

  reff                 = 7e-6                     # effective radius [m]
  nueff                = 0.08                     # effective variance 
  rdist1 = rprobs.ClouddropsHansenGamma(reff, nueff)
  nrain                = 3000                         # raindrop concentration [m^-3]
  qrain                = 0.9                          # rainwater content [g/m^3]
  dvol                 = 8e-4                         # mean volume diameter [m]
  rdist2 = rprobs.RaindropsGeoffroyGamma(nrain, qrain, dvol)
  numconc = 75e6 # [m^3]
  distribs = [rdist1, rdist2]
  scalefacs = [2750, 1]
  radiiprobdist = rprobs.CombinedRadiiProbDistribs(distribs, scalefacs)

  coord3gen            = None                        # do not generate superdroplet coords
  coord1gen            = None                        
  coord2gen            = None                        

### --- 0-D domain --- ###
if genGBxsthermo:
  zgrid = np.array([0, 100])  # array of zhalf coords [m]
  xgrid = np.array([0, 100])  # array of xhalf coords [m]
  ygrid = np.array([0, 100])  # array of yhalf coords [m]
  cgrid.write_gridboxboundaries_binary(fs["gridfile"],
                                      zgrid, xgrid, ygrid, constsfile)
  rgrid.print_domain_info(constsfile, fs["gridfile"])
        
  ### --- Constant, Uniform Thermodynamics --- ###
  tdyng = thermogen.ConstUniformThermo(100000.0, 273.15, None,
                                      0.0, 0.0, 0.0,
                                      0.0, relh=95.0,
                                      constsfile=constsfile)
  cthermo.write_thermodynamics_binary(fs["thermofiles"], tdyng,
                                      fs["configfile"], constsfile,
                                      fs["gridfile"])
  if plotfigs:
        ### --- plot and save figure for GBxs --- ###
        rgrid.plot_gridboxboundaries(constsfile, fs["gridfile"],
                              initfigspath, True)

if genSDs:
  for runn in runnums:
    ### --- Initial SD Conditions --- ###
    configfile = get_configfile_name(nsupers, nfrags, runn, path2build) 
    initSDsfile = get_initSDsfile_name(nsupers, runn, path2build)
    gridfile = get_gridfile_name(path2build)

    initattrsgen = iSDs.InitManyAttrsGen(radiigen, radiiprobdist,
                                        coord3gen, coord1gen, coord2gen)
    csupers.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                        configfile, constsfile,
                                        gridfile, nsupers, numconc)
    rsupers.print_initSDs_infos(initSDsfile, configfile,
                                constsfile, gridfile)
    if plotfigs:
      ### --- plot and save figure for initial SDs --- ###
      rsupers.plot_initGBxsdistribs(configfile, constsfile, 
                                  initSDsfile, gridfile,
                                  initfigspath, True, "all",
                                  endname="_"+str(runn))
                                     