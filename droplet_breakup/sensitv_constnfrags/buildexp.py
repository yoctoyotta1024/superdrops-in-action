# File: buildexp.py
# build CLEO in work directory and create 
# gridbox and thermodynamic data files 
# and superdroplet initial conditions 

import os

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/breakup/build/"
executable = "runbreakup"

def echo_and_sys(cmd):
  os.system("echo "+cmd)
  os.system(cmd)

cmd = "./build_compile.sh "+path2CLEO+" "+path2build+" "+executable
echo_and_sys(cmd)

# configfile=${HOME}/CLEO/src/config/config.txt