#!/bin/bash
#SBATCH --job-name=fvdvs
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=30G
#SBATCH --time=00:30:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=afvavout.%j.out
#SBATCH --error=/afcaay_err.%j.out

path2build=/work/mh11
configdir=/home/m/m300950/superdrops_i
experimentid=/L1_s
constsfile=/home/m/m30095

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