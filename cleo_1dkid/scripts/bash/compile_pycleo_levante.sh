#!/bin/bash
#SBATCH --job-name=compile_pycleo
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=10G
#SBATCH --time=00:10:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bm1183
#SBATCH --output=./compile_pycleo_out.%j.out
#SBATCH --error=./compile_pycleo_err.%j.out

set -e
source /etc/profile
module purge
spack unload --all

### ------------------ input parameters ---------------- ###
### ----- You need to edit these lines to specify ------ ###
### ----- your build configuration and executables ----- ###
### ---------------------------------------------------- ###
# generic input parameters
### _NOTE_: best to use absolute paths here
path2source="$1/cleo_deps"                 # source directory, $1 is path to cleo_1dkid/
path2build=$2                              # build directory
make_clean=${3:-false}                     # == "true" or otherwise false
executables=${4:-"pycleo"}                 # list of executables to compile

# CLEO (openmp with gcc compiler) extra build parameters
cleo_build_flags=${5:-"-DCLEO_COUPLED_DYNAMICS="numpy" \
  -DCLEO_PYTHON=/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python"} # CLEO_BUILD_FLAGS

# Necessary Levante packages
levante_gcc="gcc/11.2.0-gcc-11.2.0" # bcn7mbu # module load
levante_gcc_openmpi="openmpi/4.1.2-gcc-11.2.0" # module load
### ---------------------------------------------------- ###

### ------------------ check arguments ----------------- ###
if [[ "${path2source}" == "" || "${path2build}" == "" ]]
then
  echo "Please provide absolute path to source and build directories"
  exit 1
fi

if [ "${path2source}" == "${path2build}" ]
then
    echo "Bad inputs: build directory cannot match source"
    exit 1
fi
### ---------------------------------------------------- ###

### ---- set relevant packages and compiler settings --- ###
module load ${levante_gcc} ${levante_gcc_openmpi} # for CLEO

levante_gxx_compiler="$(command -v mpic++)"
levante_gcc_compiler="$(command -v mpicc)"
cxx_flags="-Werror -Wall -Wextra -pedantic -Wno-unused-parameter -O3 -mfma" # for CLEO
### ---------------------------------------------------- ###

### ----------------- set CLEO flags ------------------- ###
CLEO_BUILD_FLAGS="${cleo_build_flags}"
CLEO_KOKKOS_BASIC_FLAGS="-DKokkos_ARCH_NATIVE=ON -DKokkos_ENABLE_SERIAL=ON"
CLEO_KOKKOS_HOST_FLAGS="-DKokkos_ENABLE_OPENMP=ON"
CLEO_KOKKOS_DEVICE_FLAGS=""
### ---------------------------------------------------- ###

### -------------------- build bindings ---------------- ###
echo "### --------------- Build Inputs -------------- ###"
echo "source directory=${path2source}"
echo "build directory=${path2build}"
echo "CMAKE_CXX_COMPILER=${levante_gxx_compiler}"
echo "CMAKE_C_COMPILER=${levante_gcc_compiler}"
echo "CMAKE_CXX_FLAGS="${cxx_flags}""

echo "CLEO_BUILD_FLAGS=${CLEO_BUILD_FLAGS}"
echo "CLEO_KOKKOS_FLAGS=${CLEO_KOKKOS_BASIC_FLAGS}\
  ${CLEO_KOKKOS_HOST_FLAGS} ${CLEO_KOKKOS_DEVICE_FLAGS}"
echo "### ------------------------------------------- ###"

cmake -DCMAKE_CXX_COMPILER=${levante_gxx_compiler} \
    -DCMAKE_C_COMPILER=${levante_gcc_compiler} \
    -DCMAKE_CXX_FLAGS="${cxx_flags}" \
    -S ${path2source} -B ${path2build} \
    ${CLEO_KOKKOS_BASIC_FLAGS} ${CLEO_KOKKOS_HOST_FLAGS} ${CLEO_KOKKOS_DEVICE_FLAGS} \
    ${CLEO_BUILD_FLAGS}
### ---------------------------------------------------- ###

### ------------------ compile bindings ---------------- ###
cmd="cd ${path2build}"
echo ${cmd}
eval ${cmd}

if [ "${make_clean}" == "true" ]
then
  cmd="make clean"
  echo ${cmd}
  eval ${cmd}
fi

cmd="make -j 32 ${executables}"
echo ${cmd}
eval ${cmd}
### ---------------------------------------------------- ###
