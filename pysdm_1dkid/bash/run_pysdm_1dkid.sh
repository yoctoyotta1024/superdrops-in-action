#!/bin/bash
#SBATCH --job-name=pysdm_kid
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --time=08:00:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bm1183
#SBATCH --output=./pysdm_kid_out.%j.out
#SBATCH --error=./pysdm_kid_err.%j.out

### ------------------ Input Parameters ---------------- ###
### ------ You MUST edit these lines to set your ------- ###
### ---- build type, directories, the executable(s) ---- ###
### -------- to compile, and your python script -------- ###
### ---------------------------------------------------- ###
### check settings in configfile specified below too(!)
python="/work/bm1183/m300950/bin/envs/clouds/bin/python"
pythonlibs="/work/bm1183/m300950/bin/envs/clouds/lib/python3.13/site-packages/"

runscript="/home/m/m300950/superdrops-in-action/pysdm_1dkid/scripts/run_pysdm_1dkid.py"
config_filename="/home/m/m300950/superdrops-in-action/pysdm_1dkid/share/config.yaml"
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###

### ---- set relevant packages and runtime settings ---- ###
# (optional) prepend to python path to make import searches faster
export PYTHONPATH=${pythonlibs}:${path2cleopythonbindings}:${path2cleo1dkid}:${PYTHONPATH}
### ---------------------------------------------------- ###

echo "${python} ${runscript} --config_filename=${config_filename}"
${python} ${runscript} --config_filename=${config_filename}
