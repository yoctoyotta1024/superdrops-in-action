# File: buexpsrc.py
# source file for functions used in
# breakup experiemnt including to
# build, compile, generate input binaries
# and run experiment ensembles

import os
import sys

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

def echo_and_sys(cmd):
  os.system("echo "+cmd)
  os.system(cmd)

def get_configfile_name(nsupers, nfrags, runn, path2build=None):

  fgs = str(nfrags).replace(".", "p")
  nsd = str(nsupers)
  runn = str(runn)

  configfile = "tmp/config_nsupers"+nsd+"_nfrags"+fgs+"_"+runn+".txt"
  if path2build:
    return path2build+configfile
  else:
    return configfile 

def get_initSDsfile_name(nsupers, runn, path2build=None):

  nsd = str(nsupers)
  runn = str(runn)

  initSDsfile = "share/dimlessSDsinit_nsupers"+nsd+"_"+runn+".dat"
  if path2build:
    return path2build+initSDsfile
  else:
    return initSDsfile

def get_gridfile_name(path2build=None):
  gridfile = "share/dimlessGBxboundaries.dat" 
  if path2build:
    return path2build+gridfile
  else:
    return gridfile


def get_thermofiles_name(path2build=None):
  thermofiles = "share/dimlessthermo.dat" 
  if path2build:
    return path2build+thermofiles
  else:
    return thermofiles
 
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

def configfile_for_nfragsX(path2build, path2out, configtemplate,
                           nSDsvec, nfrags, runn):
  
  fgs = str(nfrags).replace(".", "p")
  nsd = str(nSDsvec)
  runn = str(runn)
  
  configfile = get_configfile_name(nSDsvec, nfrags, runn) 
  gridfile = get_gridfile_name()
  initSDsfile = get_initSDsfile_name(nSDsvec, runn) 
  thermofiles = get_thermofiles_name() 
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
