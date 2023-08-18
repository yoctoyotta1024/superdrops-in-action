# File: runexp.py
# compile and run experiment using
# prebuilt CLEO, config file and 
# input binaries

import os

def echo_and_sys(cmd):
  os.system("echo "+cmd)
  os.system(cmd)

def get_configfile_name(path2build, nsupers, nfrags, runn):

  fgs = str(nfrags).replace(".", "p")
  nsd = str(nsupers)
  runn = str(runn)

  return path2build+"tmp/config_nsupers"+nsd+"_nfrags"+fgs+"_"+runn+".txt"

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/breakup/build/"
executable = "runbreakup"

nsupers = 2048
nfrags = 5.2
runnums = [0]

for runn in runnums:
  configfile = get_configfile_name(path2build, nsupers, nfrags, runn)
  cmd = "./compile_run.sh "+path2CLEO+" "+path2build+" "+executable+" "+configfile
  echo_and_sys(cmd)