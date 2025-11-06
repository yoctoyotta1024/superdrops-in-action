.. _requirements:

Requirements
============

The following requirements ensure CLEO's build, compilation and execution on DKRZ's Levante HPC.
If they do not work, please :ref:`contact us <contact>` or `open a new
issue <https://github.com/yoctoyotta1024/superdrops-in-action/issues/new>`_ on our GitHub repository.

Of course other architectures, other compilers, versions etc. are possible, but we leave this for
you to discover.

Compilers
---------
A C++ compiler with the C++20 standard library and MPI is the absolute minimum.

On Levante you can use the latest MPI compiler wrappers for the gcc compilers.
At the time of writing this is gcc 11.2.0, e.g.

.. code-block:: console

  $ module load gcc/11.2.0-gcc-11.2.0 openmpi/4.1.2-gcc-11.2.0

CMake
-----
CMake minimum version 3.18.0.

On Levante the default version is above 3.26.0 so this should be fine. In case you have trouble,
you can use spack to find (and load) a higher version yourself (``spack find cmake``).

Python
------
We advise you to create an environment using our ``envirnoment.yaml`` file.
This environment should automatically include all the additional packages you may require.
If not, please :ref:`contact us <contact>` or
`open a new issue <https://github.com/yoctoyotta1024/superdrops-in-action/issues/new>`_
on our GitHub repository.

You can install Python packages to an existing Conda (or Micromamba) environment via:

.. code-block:: console

  $ micromamba env create --file=environment.yaml
  $ micromamba activate [your environment]

On HPCs, running python with MPI via a conda/mamba environment can create all sorts of issues
because you want to use the HPC's MPI installation, but conda/mamba installs it's own
(see e.g. https://conda-forge.org/docs/user/tipsandtricks/#using-external-message-passing-interface-mpi-libraries).
On Levante, we have found that installing conda's mpi wrapper, de- and re-installing mpi4py and then
deleting any mpi libraries installed by mamba/conda seems to do the trick via this sequence of
commands:

.. code-block:: console

  $ module load python3 gcc/11.2.0-gcc-11.2.0 openmpi/4.1.2-gcc-11.2.0
  $ export MPI4PY_BUILD_MPICC=/sw/spack-levante/openmpi-4.1.2-mnmady/bin/mpicc
  $ export MPI4PY_BUILD_MPILD=/sw/spack-levante/openmpi-4.1.2-mnmady/lib

  $ mamba install mpi=*=*
  $ python -m pip uninstall mpi4py
  $ python -m pip install --no-cache-dir --no-binary=mpi4py mpi4py
  $ rm  /work/bm1183/m300950/bin/envs/superdrops-in-action/lib/libmpi.so
  $ rm  /work/bm1183/m300950/bin/envs/superdrops-in-action/lib/libmpi.so.40

  $ python -c 'import ctypes.util; print(ctypes.util.find_library("mpi"))'

(If this still doesn't work: try creating a ``superdrops-in-action`` environment from a clone of
another environment that does work with MPI (e.g. ```clouds``), then install mpi4py, and afterwards
install the other requirements (``python -m pip install -r requirements.txt``) and delete any
``libmpi.so`` and ``libmpi.so.40`` libraries created in the process.)
