# File: runexp.py
# compile and run experiment using
# prebuilt CLEO, config file and 
# input binaries

from src import *

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/droplet_breakup/build/"
executable = "runbreakup"

nsupers = 8192
nfrags = 512.0
runnums = [0]

for runn in runnums:
  configfile = get_configfile_name(nsupers, nfrags, runn, path2build)
  cmd = "./compile_run.sh "+path2CLEO+" "+path2build+" "+executable+" "+configfile
  echo_and_sys(cmd)