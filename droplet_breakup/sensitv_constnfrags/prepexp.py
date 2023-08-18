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
from pySD.thermobinary_src import read_thermodynamics as rthermo
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
  
  configfile = "tmp/config_nsupers"+nsd+"_nfrags"+fgs+".txt"
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
runn = 0
configtemplate = "./configtemplate.txt"
path2out = path2build+"../constnfrags/"

gen_initSDs = True

fs = configfile_for_nfragsX(path2build, path2out, configtemplate,
                                   nsupers, nfrags, runn)

zgrid = [0, 100, 100]      # evenly spaced zhalf coords [zmin, zmax, zdelta] [m]
xgrid = [0, 100, 100]     # evenly spaced xhalf coords [m]
ygrid = np.array([0, 100])  # array of yhalf coords [m]

savefigpath = path2build+"bin/"
cgrid.write_gridboxboundaries_binary(fs["gridfile"],
                                     zgrid, xgrid, ygrid, constsfile)
rgrid.print_domain_info(constsfile, fs["gridfile"])
rgrid.plot_gridboxboundaries(constsfile, fs["gridfile"], savefigpath, True)