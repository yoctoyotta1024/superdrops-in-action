#!/bin/bash
#SBATCH --job-name=n64
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=30G
#SBATCH --time=00:30:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=/home/m/m300950/superdrops_in_action/prescribed2dflow/conv1//temp//ssvarexp_n64_out.%j.out
#SBATCH --error=/home/m/m300950/superdrops_in_action/prescribed2dflow/conv1//temp//ssvarexp_n64_err.%j.out

path2build=/work/mh1126/m300950/prescribed2dflow/conv1/build/
configdir=/home/m/m300950/superdrops_in_action/prescribed2dflow/conv1//temp/
experimentid=/n64
constsfile=/home/m/m300950/CLEO/libs/claras_SDconstants.hpp

module load gcc
export OMP_PROC_BIND=spread
export OMP_PLACES=threads
export OMP_PROC_BIND=true

for run in "$@" 
do
  configfile=${configdir}/${experimentid}_run${run}_config.txt
  execute="${path2build}src/runCLEO ${configfile} ${constsfile}"
  echo ${execute}
  # ${execute}
done