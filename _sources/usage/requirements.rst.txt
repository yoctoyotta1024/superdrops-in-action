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
