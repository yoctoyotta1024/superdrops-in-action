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
#SBATCH --output=./build/bin/inputfiles_out.%j.out
#SBATCH --error=./build/bin/inputfiles_err.%j.out

### ----- You need to edit these lines to set your ----- ###
### ----- default compiler and python environment   ---- ###
### ----  and paths for CLEO and build directories  ---- ###
### _NOTE_: best to use absolute paths here
path2cleo1dkid=$1
path2build=$2
path2CLEO=${HOME}/CLEO
python=/work/bm1183/m300950/bin/envs/superdrops-in-action/bin/python
path2scripts=${path2cleo1dkid}/libs/cleo_sdm/initconds

cleoconstants_filepath="${path2cleo1dkid}/cleo_deps/libs/"
grid_filename="${path2build}/share/dimlessGBxboundaries.dat"
initsupers_filename="${path2build}/share/dimlessSDsinit.dat"

### srcs and dests are lists of absolute paths to source and destination config files
### seperated by spaces e.g. srcs=("$HOME/config1" "$HOME/config2")
srcs=("${path2cleo1dkid}/share/cleo_initial_conditions/1dkid/condevap_only/config.yaml"
      "${path2cleo1dkid}/share/cleo_initial_conditions/1dkid/fullscheme/config.yaml")
dests=("${path2build}/tmp/condevap_only/config.yaml"
       "${path2build}/tmp/fullscheme/config.yaml")
setup_filenames=("${path2build}/bin/condevap_only/setup.txt"
                 "${path2build}/bin/fullscheme/setup.txt")
zarrbasedirs=("${path2build}/bin/condevap_only/sol.zarr"
              "${path2build}/bin/fullscheme/sol.zarr")
### ---------------------------------------------------- ###


if [[ ${#srcs[@]} -eq 0 || "${path2build}" == "" ]]
then
  echo "Please specify path2build and source and destination config files"
  exit 1
fi

if [[ ${#srcs[@]} -ne ${#dests[@]} || ${#srcs[@]} -ne ${#setup_filenames[@]} || ${#srcs[@]} -ne ${#zarrbasedirs[@]} ]]
then
  echo "Please specify as many source configuration files as destinations"
  echo "(${#srcs[@]}, ${#dests[@]}, ${#setup_filenames[@]}, ${#zarrbasedirs[@]})"
  exit 1
fi

for i in "${!srcs[@]}"
do
  src_configfile="${srcs[i]}"
  dest_configfile="${dests[i]}"
  setup_filename="${setup_filenames[i]}"
  zarrbasedir="${zarrbasedirs[i]}"
  echo "path to build directory: ${path2build}"
  echo "src config file: ${src_configfile}"
  echo "dest config file: ${dest_configfile}"

  ### --------------- create configuration file -------------- ###
  echo "${python} create_config.py ${path2CLEO} ${src_configfile} ${dest_configfile} [...]"
  ${python} ${path2scripts}/create_config.py ${path2CLEO} ${src_configfile} ${dest_configfile} \
    --cleoconstants_filepath="${cleoconstants_filepath}" \
    --grid_filename="${grid_filename}" \
    --initsupers_filename="${initsupers_filename}" \
    --setup_filename="${setup_filename}" \
    --zarrbasedir="${zarrbasedir}"
  ### ---------------------------------------------------- ###

  ### --------------- create gbx boundaries -------------- ###
  echo "${python} create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}"
  ${python} ${path2scripts}/create_gbxboundariesbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}
  ### ---------------------------------------------------- ###

  ### -------- create superdrop initial conditions ------- ###
  echo "${python} create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}"
  ${python} ${path2scripts}/create_initsuperdropsbinary_script.py ${path2CLEO} ${path2build} ${dest_configfile}
  ### ---------------------------------------------------- ###
done
