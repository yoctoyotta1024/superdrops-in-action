# File: buildexp.py
# build CLEO in work directory and create 
# gridbox and thermodynamic data files 
# and superdroplet initial conditions 

import os
import sys
import numpy as np

path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO)

from pySD import editconfigfile 
from pySD.gbxboundariesbinary_src import create_gbxboundaries as  cgrid
from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid
from pySD.thermobinary_src import thermogen
from pySD.thermobinary_src import create_thermodynamics as cthermo
from pySD.initsuperdropsbinary_src import initattributes as iSDs
from pySD.initsuperdropsbinary_src import radiiprobdistribs as rprobs 
from pySD.initsuperdropsbinary_src import create_initsuperdrops as csupers 
from pySD.initsuperdropsbinary_src import read_initsuperdrops as rsupers 

def print_filenames(nsd, nfrags, runn, path2build, configfile, gridfile,
                    thermofiles, initSDsfile, setuptxt, zarrbasedir):
  
  print(" --- nsupers "+nsd+", nfrags "+str(nfrags)+", run "+runn+" ---")
  print("build:     ", path2build)
  print("config:     ", "build/"+configfile)
  print("gridfile:   ", "build/"+gridfile)
  print("thermofiles:", "build/"+thermofiles[:-4]+"_[XXX].dat")
  print("initSDs:    ",  "build/"+initSDsfile)
  print("output to:  "+setuptxt+"\n            "+zarrbasedir)
  print(" ---------------------------------------" )

def configparams2edit_dict(initSDsfile, gridfile, setuptxt, zarrbasedir,
                           thermofiles, nSDsvec, nfrags):
  
  configparams2edit = {
    "initSDs_filename" : initSDsfile,
    "grid_filename" : gridfile,

    "setuptxt" : setuptxt,
    "zarrbasedir" : zarrbasedir,
    
    "press_filename" : thermofiles[:-4]+"_press.dat", 
    "temp_filename" : thermofiles[:-4]+"_temp.dat",
    "qvap_filename" : thermofiles[:-4]+"_qvap.dat",
    "qcond_filename" : thermofiles[:-4]+"_qcond.dat",
    "wvel_filename" : thermofiles[:-4]+"_wvel.dat",
    "uvel_filename" : thermofiles[:-4]+"_uvel.dat",
    "vvel_filename" : thermofiles[:-4]+"_vvel.dat",

    "nSDsvec" : nSDsvec,
    "nfrags" : nfrags
    }
  
  return configparams2edit
  
def configfile_for_nfragsX(path2build, path2out, configtemplate,
                           nSDsvec, nfrags, runn):
  
  fgs = str(nfrags).replace(".", "p")
  nsd = str(nSDsvec)
  runn = str(runn)
  
  configfile = "tmp/config_nsupers"+nsd+"_nfrags"+fgs+"_"+runn+".txt"
  gridfile = "share/dimlessGBxboundaries.dat" 
  initSDsfile = "share/dimlessSDsinit_nsupers"+nsd+"_"+runn+".dat"
  thermofiles = "share/dimlessthermo.dat"
  setuptxt = path2out+"setup_nsupers"+nsd+"_nfrags"+fgs+".txt"   
  zarrbasedir = path2out+"SDMdata_nsupers"+nsd+"_nfrags"+fgs+"_"+runn+".zarr"  

  print_filenames(nsd, nfrags, runn, path2build, configfile, gridfile,
                    thermofiles, initSDsfile, setuptxt, zarrbasedir) 
  
  ### parameters to modify in config file ###
  fs = {
    "configfile" : path2build+configfile,
    "gridfile" : path2build+gridfile,
    "initSDsfile" : path2build+initSDsfile,
    "thermofiles" : path2build+thermofiles
  }

  params = configparams2edit_dict(fs["initSDsfile"], fs["gridfile"],
                                  setuptxt, zarrbasedir,
                                  fs["thermofiles"], nSDsvec, nfrags)
   
  ### create and modify config file based on template ### 
  os.system("cp "+configtemplate+" "+fs["configfile"])
  editconfigfile.edit_config_params(fs["configfile"], params)

  return fs

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/breakup/build/"
constsfile = path2CLEO+"/libs/claras_SDconstants.hpp"
executable = "runbreakup"

nsupers = 2048
nfrags = 5.2
runnums = [0, 1]
configtemplate = "./configtemplate.txt"
path2out = path2build+"../constnfrags/"

genSDs = True # generate inital SD conditions
plotfigs = True
initfigspath = path2build+"bin/"

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
  scalefacs = [10000, 1]
  radiiprobdist = rprobs.CombinedRadiiProbDistribs(distribs, scalefacs)

  coord3gen            = None                        # do not generate superdroplet coords
  coord1gen            = None                        
  coord2gen            = None                        


for runn in runnums:
  ### --- generate configuration file --- ###
  fs = configfile_for_nfragsX(path2build, path2out, configtemplate,
                              nsupers, nfrags, runn)

### --- 0-D domain --- ###
zgrid = np.array([0, 100])  # array of zhalf coords [m]
xgrid = np.array([0, 100])  # array of xhalf coords [m]
ygrid = np.array([0, 100])  # array of yhalf coords [m]
cgrid.write_gridboxboundaries_binary(fs["gridfile"],
                                     zgrid, xgrid, ygrid, constsfile)
rgrid.print_domain_info(constsfile, fs["gridfile"])
if plotfigs:
      ### --- plot and save figure for GBxs --- ###
      rgrid.plot_gridboxboundaries(constsfile, fs["gridfile"],
                             initfigspath, True)
      
### --- Constant, Uniform Thermodynamics --- ###
tdyng = thermogen.ConstUniformThermo(100000.0, 273.15, None,
                                     0.0, 0.0, 0.0,
                                     0.0, relh=95.0,
                                     constsfile=constsfile)
cthermo.write_thermodynamics_binary(fs["thermofiles"], tdyng,
                                    fs["configfile"], constsfile,
                                    fs["gridfile"])

for runn in runnums:
  ### --- generate configuration file --- ###
  fs = configfile_for_nfragsX(path2build, path2out, configtemplate,
                              nsupers, nfrags, runn)

  if genSDs:
    ### --- Initial SD Conditions --- ###
    initattrsgen = iSDs.InitManyAttrsGen(radiigen, radiiprobdist,
                                        coord3gen, coord1gen, coord2gen)
    csupers.write_initsuperdrops_binary(fs["initSDsfile"], initattrsgen, 
                                        fs["configfile"], constsfile,
                                        fs["gridfile"], nsupers, numconc)
    rsupers.print_initSDs_infos(fs["initSDsfile"], fs["configfile"],
                                constsfile, 
                                fs["gridfile"])

    if plotfigs:
      ### --- plot and save figure for initial SDs --- ###
      rsupers.plot_initGBxsdistribs(fs["configfile"], constsfile, 
                                  fs["initSDsfile"], fs["gridfile"],
                                  initfigspath, True, "all",
                                  endname="_"+str(runn))
                                     