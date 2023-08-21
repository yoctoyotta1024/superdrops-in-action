# File: buildexp.py
# build CLEO in work directory and create 
# gridbox and thermodynamic data files 
# and superdroplet initial conditions 

from src import *

path2CLEO = "/home/m/m300950/CLEO/"
path2build = "/work/mh1126/m300950/droplet_breakup/build/"
executable = "runbreakup"

cmd = "./build_compile.sh "+path2CLEO+" "+path2build+" "+executable
echo_and_sys(cmd)