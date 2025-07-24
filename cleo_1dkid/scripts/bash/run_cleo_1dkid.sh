#!/bin/bash
#SBATCH --job-name=kid
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
### _NOTE_: best to use absolute paths here
path2cleo1dkid=$1
path2build=$2
start_id=$3 # inclusive start of run_ids
end_id=$4 # inclusive end of run_ids
path2pycleo="${path2build}/pycleo"
python=/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python

### loop over configs_directory for all different for run_ids
configs_directory=("${path2build}/tmp/condevap_only"
                 "${path2build}/tmp/fullscheme")
run_labels=("condevap_only" "fullscheme")
fig_directory=("${path2build}/bin/condevap_only"
                "${path2build}/bin/fullscheme")

### IDs of ensemble members (diff superdrop initial conditions) for each src_configs to create
if [[ "${start_id}" == "" || "${end_id}" == "" ]]
then
  echo "Please specify start and end id"
  exit 1
fi
run_ids=($(seq $start_id 1 $end_id))
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###

### ------------------ check arguments ----------------- ###
if [[ ${#configs_directory[@]} -eq 0 ||
      "${path2build}" == "" ||
      "${run_ids}" == "" ]]
then
  echo "Please specify path2build, runs for ensemble," \
          "and source and destination config files"
  exit 1
fi

if [[ ${#configs_directory[@]} -ne ${#run_labels[@]} ||
      ${#configs_directory[@]} -ne ${#fig_directory[@]} ]]
then
  echo "Please specify as many source configuration files as destinations"
  echo "(${#configs_directory[@]}, ${#run_labels[@]}, ${#fig_directory[@]})"
  exit 1
fi
### ---------------------------------------------------- ###

for i in "${!configs_directory[@]}"
do
  echo "---------------------- src ${i} ----------------------"
  for j in "${!run_ids[@]}"
  do
    config_filename="${configs_directory[i]}/config_${j}.yaml"
    run_name="${run_labels[i]}_${j}"
    figpath="${fig_directory[i]}"
    echo "---- src ${i}, run number: ${j} ----"
    echo "--run_name=${run_name}"
    echo "--config_filename=${config_filename}"
    echo "--figpath=${figpath}"
    echo "--path2pycleo=${path2pycleo}"

    echo "${python} ${path2cleo1dkid}/scripts/run_cleo_1dkid.py --config_filename=${config_filename} [...]"
    ${python} ${path2cleo1dkid}/scripts/run_cleo_1dkid.py \
      --run_name="${run_name}" \
      --config_filename="${config_filename}" \
      --figpath="${figpath}" \
      --path2pycleo="${path2pycleo}"
    done
  echo "---------------------------------------------------"
done
### ---------------------------------------------------- ###
