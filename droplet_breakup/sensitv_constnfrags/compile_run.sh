#!/bin/bash
#SBATCH --job-name=runBUexp
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=30G
#SBATCH --time=00:30:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=/work/mh1126/m300950/breakup/build/tmp/runBUexp_out.%j.out
#SBATCH --error=/work/mh1126/m300950/breakup/build/tmp/runBUexp_err.%j.out

### ------------- PLEASE NOTE: this script assumes you ------------- ###
### ------------- have already built CLEO in path2build ------------ ### 
### -------------------  directory using cmake  -------------------- ###

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
module load python3/2022.01-gcc-11.2.0
source activate /work/mh1126/m300950/condaenvs/cleoenv 
path2CLEO=${1}
path2build=${2}
executable=${3}
configfile=${4}
### ---------------------------------------------------- ###

### ------------------- compile_run.sh ----------------- ###
### ensure these directories exist (it's a good idea for later use)
mkdir ${path2build}bin
mkdir ${path2build}share
mkdir ${path2build}tmp

### compile CLEO in ./build directory
cd ${path2build} && pwd 
make -j 16

### run CLEO
export OMP_PROC_BIND=spread
export OMP_PLACES=threads
runcmd="${path2build}/src/${executable} ${configfile} ${path2CLEO}libs/claras_SDconstants.hpp"
echo ${runcmd}
${runcmd}
### ---------------------------------------------------- ###