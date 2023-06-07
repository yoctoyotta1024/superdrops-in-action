import os
import sys
import numpy as np
from pathlib import Path 

path2CLEO = "/home/m/m300950/CLEO/"
sys.path.append(path2CLEO)

from pySD import editconfigfile 

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

def gen_gridboxboundaries_binary(gridfile, constsfile, zgrid, xgrid, ygrid,
                                   isfigures, savefigpath):
  
  from pySD.gbxboundariesbinary_src import create_gbxboundaries as  cgrid
  from pySD.gbxboundariesbinary_src import read_gbxboundaries as rgrid

  cgrid.write_gridboxboundaries_binary(gridfile, zgrid, xgrid, ygrid, constsfile)

  if isfigures[0]:
    if isfigures[1]:
        Path(savefigpath).mkdir(exist_ok=True) 
      
        rgrid.print_domain_info(constsfile, gridfile)
        rgrid.plot_gridboxboundaries(constsfile, gridfile, savefigpath, isfigures[1])

def gen_thermodynamics_binaries(thermofiles, configfile, constsfile,
                                gridfile, PRESS0, THETA, qvapmethod,
                                sratios, Zbase, qcond, WMAX,
                                Zlength, Xlength, VVEL, moistlayer,
                                isfigures, savefigpath):
  
  from pySD.thermobinary_src import thermogen
  from pySD.thermobinary_src import create_thermodynamics as cthermo
  from pySD.thermobinary_src import read_thermodynamics as rthermo

  thermodyngen = thermogen.ConstHydrostaticAdiabat(configfile, constsfile, PRESS0, 
                                          THETA, qvapmethod, sratios, Zbase,
                                          qcond, WMAX, Zlength, Xlength,
                                          VVEL, moistlayer)  
  cthermo.write_thermodynamics_binary(thermofiles, thermodyngen, configfile,
                                        constsfile, gridfile)
  
  if isfigures[0]:
      if isfigures[1]:
          Path(savefigpath).mkdir(exist_ok=True) 
      
      rthermo.plot_thermodynamics(constsfile, configfile, gridfile,
                                  thermofiles, savefigpath, isfigures[1])

def gen_initSDs_for_ensembleruns(binariespath, gridfile, configfile,
                                 constsfile, exp, runids, npergbx,
                                 zlim, radiigen, radiiprobdist, 
                                 coord3gen, coord1gen, coord2gen,
                                 numconc, isfigures, savefigpath):
    
    from pySD.initsuperdropsbinary_src import initattributes as iSDs
    from pySD.initsuperdropsbinary_src import create_initsuperdrops as csupers 
    from pySD.initsuperdropsbinary_src import read_initsuperdrops as rsupers                    
    
    nsupers = iSDs.nsupers_at_domain_base(gridfile, constsfile, npergbx, zlim)
    initattrsgen = iSDs.InitManyAttrsGen(radiigen, radiiprobdist,
                                          coord3gen, coord1gen, coord2gen)
    
    for runn in runids: 
      initSDsfile = initSDsfilename(binariespath, exp, runn) 
      print("experiment: ", exp, "nSDs/GBx init:", npergbx,
            "run: ",runn , " initSDsfile:", initSDsfile)
      
      csupers.write_initsuperdrops_binary(initSDsfile, initattrsgen, 
                                          configfile, constsfile,
                                          gridfile, nsupers, numconc)

      if isfigures[0]:
        if isfigures[1]:
          savefigpath_exp = savefigpath+"/"+exp+"/"
          Path(savefigpath_exp).mkdir(exist_ok=True) 
          savefigpath_exp = savefigpath_exp+"initSDdistribs/"
          Path(savefigpath_exp).mkdir(exist_ok=True) 
          
          savefigstem = savefigpath_exp+"/run"+str(runn)+"_"
        rsupers.plot_initGBxsdistribs(configfile, constsfile,
                                      initSDsfile, gridfile,
                                      savefigstem, isfigures[1], 0)

def temporary_configfile_copy(tempdir, exp, runids, binpath_exp, 
                              binariespath, gridfile, thermofiles,
                              configfile):

  ### copy config to temporary file for each run of experiment
  print("\n- copying config to temporary file -")  
  for runn in runids:  
    
    initSDsfile = initSDsfilename(binariespath, exp, runn) 
    tempconfigfile = configfiles_for_exprunX(exp, runn, binpath_exp,
                                              gridfile, initSDsfile,
                                              thermofiles, configfile,
                                              tempdir)
     
  print("config file copied to: "+tempconfigfile)

def edit_bash_script(bashfile, path2build, tempdir, configdir,
                     constsfile, expid, runid=""):
  
  os.system("cp "+bashfile+" "+bashfile[:-3]+"_backup.sh")

  with open(bashfile, "r") as f:
    lines = f.readlines()
  
  for l in range(len(lines)):
    if "#SBATCH --job-name=" in lines[l]:
      lines[l] = "#SBATCH --job-name="+expid+"_run"+runid+"\n"
    if "#SBATCH --output=" in lines[l]:
      lines[l] = "#SBATCH --output="+tempdir+"/"+expid+\
                  "_run"+runid+"_out.%j.out"+"\n"
    if "#SBATCH --error=" in lines[l]:
      lines[l] = "#SBATCH --error="+tempdir+"/"+expid+\
                  "_run"+runid+"_err.%j.out"+"\n"
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

def edit_confignSDsvec(configfile, zgrid, xgrid, zlim, npergbx):
  ''' modify nSDsvec in config file '''
    
  zs = np.arange(zgrid[2], zgrid[1]+zgrid[2], zgrid[2])
  nxs = len(np.arange(xgrid[2], xgrid[1]+xgrid[2], xgrid[2]))
  nSDsvec = npergbx * len(zs[zs<=zlim]) * nxs # total no. SDs initially in domain

  print("changing nSDsvec to ", nSDsvec, "in "+configfile)
  configparams2edit = {"nSDsvec" : nSDsvec}
  editconfigfile.edit_config_params(configfile, configparams2edit)

def submit_runs_individually(bashfile, path2build, tempdir,
                             constsfile, exp, runids):
  '''run all runs of experiment using
  seperate SLURM jobs for each run'''

  print("\n- executing runCLEO via sbatch -")  
  for runn in runids:
    runid = str(runn)
    edit_bash_script(bashfile, path2build, tempdir,
                    tempdir, constsfile, exp,
                    runid=runid)
    print("experiment: "+exp+" for run "+runid)
    echo_and_sys("sbatch "+bashfile+" "+runid)
  print("-----------------------")

def submit_allruns1job(bashfile, path2build, tempdir,
                        constsfile, exp, runids):
  ''' run all runs of experiment using single SLURM job '''

  print("\n- executing runCLEO via sbatch -")  
  edit_bash_script(bashfile, path2build, tempdir,
                  tempdir, constsfile, exp,
                  runid="many")
  runsstr = " ".join([str(n) for n in list(runids)])
  print("experiment: "+exp+" for runs "+runsstr)
  echo_and_sys("sbatch "+bashfile+" "+runsstr)
  print("-----------------------")