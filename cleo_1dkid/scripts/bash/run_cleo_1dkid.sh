#!/bin/bash
#SBATCH --job-name=kid
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --time=02:00:00
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
path2cleopythonbindings="${path2build}/_deps/cleo-build/cleo_python_bindings"
python="/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python"
pythonlibs="/work/bm1183/m300950/bin/envs/superdrops-in-action/lib/python3.13/site-packages"

nsupers_pergbxs=(256) # for superdroplet initial conditions
alphas=(0.5) # for superdroplet initial conditions alpha sampling

### loop over configs_directory for all different for run_ids
configs_directory=("${path2build}/tmp/condevap_only")
run_labels=("condevap_only")
bin_directory=("${path2build}/bin/condevap_only") # Note! must match paths in config's 'outputdata'
fig_directory=("${path2build}/bin/condevap_only")

### IDs of ensemble members (diff superdrop initial conditions) for each src_configs to create
if [[ "${start_id}" == "" || "${end_id}" == "" ]]
then
  echo "Please specify start and end id"
  exit 1
fi
run_ids=($(seq $start_id 1 $end_id))

# Necessary Levante packages
levante_gcc_fyamllib="/sw/spack-levante/libfyaml-0.7.12-fvbhgo/lib"
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

### ---- set relevant packages and runtime settings ---- ###
# add fyaml libraries path
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${levante_gcc_fyamllib}
# (optional) prepend to python path to make import searches faster
export PYTHONPATH=${pythonlibs}:${path2cleopythonbindings}:${path2cleo1dkid}:${PYTHONPATH}
### ---------------------------------------------------- ###

for i in "${!configs_directory[@]}"
do
  echo "---------------------- src ${i} ----------------------"
  for k in "${!nsupers_pergbxs[@]}"
  do
    for l in "${!alphas[@]}"
    do
      for m in "${run_ids[@]}"
      do
        alpha_string="${alphas[l]//./p}" # replace . with p for filename
        label="n${nsupers_pergbxs[k]}_a${alpha_string}_r${m}"
        config_filename="${configs_directory[i]}/config_${label}.yaml"
        run_name="${run_labels[i]}_${label}"
        binpath="${bin_directory[i]}"
        figpath="${fig_directory[i]}"
        echo "---- src ${i}, run number: ${m} ----"
        echo "---- nsupers ${nsupers_pergbxs[k]}, alpha ${alphas[l]} ----"
        echo "--run_name=${run_name}"
        echo "--config_filename=${config_filename}"
        echo "--figpath=${figpath}"
        echo "--path2cleopythonbindings=${path2cleopythonbindings}"

        echo "${python} ${path2cleo1dkid}/scripts/run_cleo_1dkid.py --config_filename=${config_filename} [...]"
        ${python} ${path2cleo1dkid}/scripts/run_cleo_1dkid.py \
          --run_name="${run_name}" \
          --config_filename="${config_filename}" \
          --binpath="${binpath}" \
          --figpath="${figpath}" \
          --path2cleopythonbindings="${path2cleopythonbindings}"
        done
      done
    done
  echo "---------------------------------------------------"
done
### ---------------------------------------------------- ###
