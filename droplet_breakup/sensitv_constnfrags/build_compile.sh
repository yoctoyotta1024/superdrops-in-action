#!/bin/bash
#SBATCH --job-name=compileCLEO
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=30G
#SBATCH --time=00:30:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=./build/bin/compileCLEO_out.%j.out
#SBATCH --error=./build/bin/compileCLEO_err.%j.out

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
module load gcc/11.2.0-gcc-11.2.0
module load python3/2022.01-gcc-11.2.0
source activate /work/mh1126/m300950/condaenvs/cleoenv 
path2CLEO=${1}
path2build=${2}
executable=${3}
python=python
gxx="g++"
gcc="gcc"
### ---------------------------------------------------- ###

### ------------------ build_compile.sh ---------------- ###
### build CLEO using cmake (with openMP thread parallelism through Kokkos)
kokkosflags="-DKokkos_ARCH_NATIVE=ON -DKokkos_ENABLE_SERIAL=ON -DKokkos_ENABLE_OPENMP=ON"  # openMP parallelism enabled
CXX=${gxx} CC=${gcc} cmake -S ${path2CLEO} -B ${path2build} ${kokkosflags}

### ensure these directories exist (it's a good idea for later use)
mkdir ${path2build}bin
mkdir ${path2build}share
mkdir ${path2build}tmp

### compile CLEO
cd ${path2build} && pwd 
make clean && make ${executable} -j 16
### ---------------------------------------------------- ###