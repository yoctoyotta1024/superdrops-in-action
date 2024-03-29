#!/bin/bash
#SBATCH --partition=compute
#SBATCH --account=mh1126
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --job-name=resexpcntrl

/work/mh1126/m300950/superdropsV2/bin/python verticalres_experiment.py collsediICONgrid_1048576
