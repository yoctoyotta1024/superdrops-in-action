#!/bin/bash
#SBATCH --job-name=inputfiles
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=940M
#SBATCH --time=00:05:00
#SBATCH --mail-user=clara.bayley@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bm1183
#SBATCH --output=./inputfiles_out.%j.out
#SBATCH --error=./inputfiles_err.%j.out

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
### _NOTE_: best to use absolute paths here
path2cleo1dkid=$1
path2build=$2
start_id=$3 # inclusive start of run_ids
end_id=$4 # inclusive end of run_ids
path2CLEO=${HOME}/CLEO
python=/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python
path2initcondsscripts=${path2cleo1dkid}/libs/cleo_sdm/initconds

### src_configs is list of absolute paths to source config files seperated by spaces
### e.g. src_configs=("$HOME/config1" "$HOME/config2"), following lists are
src_configs=("${path2cleo1dkid}/share/cleo_initial_conditions/1dkid/condevap_only/config.yaml"
      "${path2cleo1dkid}/share/cleo_initial_conditions/1dkid/fullscheme/config.yaml")

### IDs of ensemble members (diff superdrop initial conditions) for each src_configs to create
if [[ "${start_id}" == "" || "${end_id}" == "" ]]
then
  echo "Please specify start and end id"
  exit 1
fi
run_ids=($(seq $start_id 1 $end_id))

### same files for all src_configs and all run_ids
cleoconstants_filepath="${path2cleo1dkid}/cleo_deps/libs/"
grid_filename="${path2build}/share/dimlessGBxboundaries.dat"

### same files for all src_configs, different for run_ids
initsupers_directory="${path2build}/share"

### different for all src_configs and different for run_ids
configs_directory=("${path2build}/tmp/condevap_only"
                 "${path2build}/tmp/fullscheme")
bin_directory=("${path2build}/bin/condevap_only"
                 "${path2build}/bin/fullscheme")
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###
### ---------------------------------------------------- ###

### ------------------ check arguments ----------------- ###
if [[ ${#src_configs[@]} -eq 0 ||
      "${path2build}" == "" ||
      "${run_ids}" == "" ]]
then
  echo "Please specify path2build, runs for ensemble," \
          "and source and destination config files"
  exit 1
fi

if [[ ${#src_configs[@]} -ne ${#configs_directory[@]} ||
      ${#src_configs[@]} -ne ${#bin_directory[@]} ]]
then
  echo "Please specify as many source configuration files as destinations"
  echo "(${#src_configs[@]}, ${#configs_directory[@]}, ${#bin_directory[@]})"
  exit 1
fi
### ---------------------------------------------------- ###

### --------------- make file directories -------------- ###
mkdir -p "${grid_filename%/*}" # for grid_filename(s)
mkdir -p "${initsupers_directory}" # for initsupers_filename(s)
for i in "${!src_configs[@]}"
do
  config_directory="${configs_directory[i]}" # for dest_configfile(s)
  bin_directory="${bin_directory[i]}" # for setup_filename(s) and zarrbasedir(s)
  mkdir -p "${config_directory}" && mkdir -p "${bin_directory}"
done
### ---------------------------------------------------- ###

### --------------- create configuration files -------------- ###
for i in "${!src_configs[@]}"
do
  echo "---------------------- src ${i} ----------------------"
  for j in "${!run_ids[@]}"
  do
    src_configfile="${src_configs[i]}"
    dest_configfile="${configs_directory[i]}/config_${j}.yaml"
    initsupers_filename="${initsupers_directory}/dimlessSDsinit_${j}.dat"
    setup_filename="${bin_directory[i]}/setup_${j}.txt"
    zarrbasedir="${bin_directory[i]}/sol_${j}.zarr"
    echo "---- src ${i}, run number: ${j} ----"
    echo "path to build directory: ${path2build}"
    echo "src config file: ${src_configfile}"
    echo "dest config file: ${dest_configfile}"
    echo "-- ${grid_filename}"
    echo "-- ${initsupers_filename}"
    echo "-- ${setup_filename}"
    echo "-- ${zarrbasedir}"

    echo "${python} create_config.py ${path2CLEO} ${src_configfile} ${dest_configfile} [...]"
    ${python} ${path2initcondsscripts}/create_config.py ${path2CLEO} ${src_configfile} ${dest_configfile} \
      --cleoconstants_filepath="${cleoconstants_filepath}" \
      --grid_filename="${grid_filename}" \
      --initsupers_filename="${initsupers_filename}" \
      --setup_filename="${setup_filename}" \
      --zarrbasedir="${zarrbasedir}"
  done
  echo "---------------------------------------------------"
done
### ---------------------------------------------------- ###

### ------------ create gbxboundaries file -------------- ###
### make same gbxboundaries file for all src_configs and all run_ids
echo "---- gbxs using src 0, run number: 0 ----"
dest_configfile="${configs_directory[0]}/config_0.yaml"
echo "path to build directory: ${path2build}"
echo "gbxs config file: ${dest_configfile}"
echo "${python} create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}"
${python} ${path2initcondsscripts}/create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}
### ---------------------------------------------------- ###

### -------- create superdrop initial conditions ------- ###
### make same superdroplets file for all src_configs
for j in "${!run_ids[@]}"
do
  dest_configfile="${configs_directory[0]}/config_${j}.yaml"
  echo "---- supers using src 0, run number: ${j} ----"
  echo "path to build directory: ${path2build}"
  echo "supers config file: ${dest_configfile}"

  echo "${python} create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}"
  ${python} ${path2initcondsscripts}/create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}
done
### ---------------------------------------------------- ###
