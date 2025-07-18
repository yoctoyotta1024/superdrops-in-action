#!/bin/bash
#SBATCH --job-name=inputfiles
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=940M
#SBATCH --time=00:05:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bm1183
#SBATCH --output=./build/bin/inputfiles_out.%j.out
#SBATCH --error=./build/bin/inputfiles_err.%j.out

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
path2CLEO=${HOME}/CLEO
path2scripts=/home/m/m300950/superdrops-in-action/cleo_1dkid/libs/cleo_sdm/initconds
condaenv=/work/bm1183/m300950/bin/envs/superdrops-in-action
python=${condaenv}/bin/python
### ---------------------------------------------------- ###

configfile=$1
path2build=$2

if [[ "${configfile}" == "" || "${path2build}" == "" ]]
then
  echo "Please specify config file and path2build"
else

  echo "config file: ${configfile}"
  echo "path to build directory: ${path2build}"

  ### --------------- create gbx boundaries -------------- ###
  echo "${python} create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${configfile}"
  ${python} ${path2scripts}/create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${configfile}
  ### ---------------------------------------------------- ###

  ### -------- create superdrop initial conditions ------- ###
  echo "${python} create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${configfile}"
  ${python} ${path2scripts}/create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${configfile}
  ### ---------------------------------------------------- ###

fi
