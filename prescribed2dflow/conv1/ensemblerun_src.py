import os
import sys
import numpy as np
from pathlib import Path 

path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO)

from pySD import editconfigfile 

def edit_bash_script(bashfile, path2build, tempdir, configdir,
                     constsfile, expid):
  
  os.system("cp "+bashfile+" "+bashfile[:-3]+"_backup.sh")

  with open(bashfile, "r") as f:
    lines = f.readlines()
  
  for l in range(len(lines)):
    if "#SBATCH --job-name=" in lines[l]:
      lines[l] = "#SBATCH --job-name="+expid+"\n"
    if "#SBATCH --output=" in lines[l]:
      lines[l] = "#SBATCH --output="+tempdir+"/exp_"+\
                    expid+"_out.%j.out"+"\n"
    if "#SBATCH --error=" in lines[l]:
      lines[l] = "#SBATCH --error="+tempdir+"/exp_"+\
                    expid+"_err.%j.out"+"\n"
    if "path2build=" in lines[l]:
      lines[l] = "path2build="+path2build+"\n"                
    if "configdir=" in lines[l]:
      lines[l] = "configdir="+configdir+"\n"
    if "experimentid=" in lines[l]:
      lines[l] = "experimentid="+"/"+expid+"\n"
    if "constsfile=" in lines[l]:
      lines[l] = "constsfile="+constsfile+"\n"
  
  f = open(bashfile, "w")
  f.close()
  with open(bashfile, "a") as f:
    f.writelines(lines)

def echo_and_sys(cmd):
  os.system("echo "+cmd)
  os.system(cmd)

def configfiles_for_exprunX(exp, runn, binpath_exp,
                            gridfile, initSDsfile, thermofiles,
                            configfile, tempdir):
  
  setuptxt = binpath_exp+"run"+str(runn)+"setup.txt"                 
  zarrbasedir = binpath_exp+"run"+str(runn)+"SDMdata.zarr"  

  print(" --- exp "+exp+" run "+str(runn)+" ---")
  print("gridfile:", gridfile)
  print("thermofiles:", thermofiles[:-4]+"_[XXX].dat")
  print("initSDs:", initSDsfile)
  print("output to: "+setuptxt+"\n           "+zarrbasedir)

  ### modify config file ###
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
    }
  
  editconfigfile.edit_config_params(configfile, configparams2edit)
  tempconfigfile = tempdir+"/"+exp+"_run"+str(runn)+"_config.txt" # n.b. this must match bash script
  echo_and_sys("cp "+configfile+" "+tempconfigfile)

  return tempconfigfile

def make_essentialpaths(path2CLEO, path2build, binariespath,
               binpath, tempdir):
  
  if path2CLEO == path2build:
    raise ValueError("build directory cannot be CLEO")
  else:
    Path(path2build).mkdir(exist_ok=True) 
    Path(binariespath).mkdir(exist_ok=True) 
    Path(binpath).mkdir(exist_ok=True) 
    Path(tempdir).mkdir(exist_ok=True) 

def initSDsfilename(binariespath, exp, runn):
  
  initSDspath = binariespath+"/"+exp+"/"
  Path(initSDspath).mkdir(exist_ok=True) 

  return initSDspath+"/dimlessSDsinit_run"+str(runn)+".dat"

def edit_confignSDsvec(configfile, zgrid, xgrid, zlim, npergbx):
  ''' modify nSDsvec in config file '''
    
  zs = np.arange(zgrid[2], zgrid[1]+zgrid[2], zgrid[2])
  nxs = len(np.arange(xgrid[2], xgrid[1]+xgrid[2], xgrid[2]))
  nSDsvec = npergbx * len(zs[zs<=zlim]) * nxs # total no. SDs initially in domain

  print("changing nSDsvec to ", nSDsvec, "in "+configfile)
  configparams2edit = {"nSDsvec" : nSDsvec}
  editconfigfile.edit_config_params(configfile, configparams2edit)
