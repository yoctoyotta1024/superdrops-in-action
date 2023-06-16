#!/bin/bash
#SBATCH --job-name=n1024_run6
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --mem=30G
#SBATCH --time=08:00:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=mh1126
#SBATCH --output=/home/m/m300950/superdrops_in_action/prescribed2dflow/convstudy//temp//n1024_run6_out.%j.out
#SBATCH --error=/home/m/m300950/superdrops_in_action/prescribed2dflow/convstudy//temp//n1024_run6_err.%j.out

path2build=/work/mh1126/m300950/prescribed2dflow/build/
configdir=/home/m/m300950/superdrops_in_action/prescribed2dflow/convstudy//temp/
experimentid=/n1024
constsfile=/home/m/m300950/CLEO/libs/claras_SDconstants.hpp

module load gcc
export OMP_PROC_BIND=spread
export OMP_PLACES=threads
export OMP_PROC_BIND=true

configfile=${configdir}/${experimentid}_run${@}_config.txt
execute="${path2build}src/runCLEO ${configfile} ${constsfile}"
echo ${execute}
${execute}