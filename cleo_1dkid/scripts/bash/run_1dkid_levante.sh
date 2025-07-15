#!/bin/bash
#SBATCH --job-name=speedtest
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=20G
#SBATCH --time=00:60:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bm1183
#SBATCH --output=./kid_out.%j.out
#SBATCH --error=./kid_err.%j.out

### ------------------ Input Parameters ---------------- ###
### ------ You MUST edit these lines to set your ------- ###
### ---- build type, directories, the executable(s) ---- ###
### -------- to compile, and your python script -------- ###
### ---------------------------------------------------- ###
path2superdropsinaction="${HOME}/superdrops-in-action"
path2build=${HOME}/superdrops-in-action/build                    # build directory (should be absolute path)
python=/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###


### ------------------ check arguments ----------------- ###
if [[ "${path2build}" == "" ]]
then
  echo "Please provide absolute path to build directory"
  exit 1
fi
### ---------------------------------------------------- ###

# ensure these directories exist (it's a good idea for later use)
mkdir ${path2build}/bin && mkdir ${path2build}/bin/condevap_only && mkdir ${path2build}/bin/fullscheme
cd ${path2superdropsinaction} && pwd
${python} ./cleo_1dkid/scripts/run_cleo_1dkid_condevap_only.py
${python} ./cleo_1dkid/scripts/run_cleo_1dkid_fullscheme.py
### ---------------------------------------------------- ###
