#!/bin/bash
#SBATCH --job-name=adiabatic
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=30G
#SBATCH --time=00:30:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=./build/bin/adiabatic_out.%j.out
#SBATCH --error=./build/bin/adiabatic_err.%j.out

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
module load gcc/11.2.0-gcc-11.2.0
source activate /work/mh1126/m300950/condaenvs/superdropsenv
path2CLEO=${HOME}/CLEO/
path2action=${HOME}/superdrops_in_action/
path2build=${HOME}/superdrops_in_action/validations/adiabaticparcel/build/
configfile=${HOME}/superdrops_in_action/validations/adiabaticparcel/condconfig.txt
python=python
gxx="g++"
gcc="gcc"

# path2CLEO=${HOME}/Documents/b1_springsummer2023/CLEO/
# #path2build=${HOME}/superdrops_in_action/validations/adiabaticparcel/build/                 ### TODO: correct path for my home dir
# #configfile=${HOME}/superdrops_in_action/validations/adiabaticparcel/condconfig.txt       ### TODO: correct path for my home dir
# python=${HOME}/opt/anaconda3/envs/superdropsV2/bin/python
# gxx="g++-13"
# gcc="gcc-13"
# ---------------------------------------------------- ###

### build CLEO using cmake (with openMP thread parallelism through Kokkos)
kokkosflags="-DKokkos_ARCH_NATIVE=ON -DKokkos_ENABLE_SERIAL=ON -DKokkos_ENABLE_OPENMP=ON"  # openMP parallelism enabled
CXX=${gxx} CC=${gcc} cmake -S ${path2CLEO} -B ${path2build} ${kokkosflags}

### ensure these directories exist (it's a good idea for later use)
mkdir ${path2build}bin
mkdir ${path2build}share

# ### generate input files
${python} condtest.py ${path2CLEO} ${path2action} ${configfile}