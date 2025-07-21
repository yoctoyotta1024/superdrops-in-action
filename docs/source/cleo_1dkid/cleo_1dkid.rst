CLEO 1-D KiD Test Case
======================

The 1-D KiD test case uses the PYMPDATA libray alongside CLEO SDM. To run CLEO's C++ code alongside
PYMPDATA, we first make the pycleo Python module using pybind11.

CLEO's libraries (``libs``) and external depenencies (``extern``) from v0.51.0 have been copied
into the directory ``cleo_1dkid/cleo_deps``. Some files in the cartesiandomain and gridboxes
libraries, e.g. to set the KiD boundary conditions have since been modified. The CMakeLists.txt
files in the libs has also been modified because the coupldyn_yac library has been deleted. Also
the header guards have been updated across all the libraries. Accordingly, the CMake project is
called ``CLEO_1dkid`` instead of ``CLEO``.

Creating The Python Bindings
----------------------------

To build the python bindings for CLEO you can simply do
`` cmake -S ./cleo_1dkid/ -B ./build && cd build && make pycleo``. However,
you need to have certain :ref:`requirements <requirements>` fulfilled first
(compiler versions etc.). On Levante, we therefore reccomend you use the bash helper script
``cleo_1dkid/scripts/bash/compile_pycleo_levante.sh`` instead of directly calling cmake.

First activate the python environment you want to use, e.g.
``micromamba activate superdrops-in-action``.
Then call the helper script with the source and build directories you want to use, e.g.

.. code-block:: console

  $ ./cleo_1dkid/scripts/bash/compile_pycleo_levante.sh $HOME/superdrops-in-action/cleo_1dkid/cleo_deps $HOME/superdrops-in-action/build

After making the bindings, the ``pycleo`` Python module can used just like an ordinary python module.
To run the ``condevap_only`` and ``fullscheme`` examples you can use the helper scripts to
first generate the initial conditions and then run the executables:

.. code-block:: console

  $ ./cleo_1dkid/scripts/bash/inputfiles_cleo_1dkid.sh \
    $HOME/superdrops-in-action/cleo_1dkid/share/cleo_initial_conditions/1dkid/condevap_only/config.yaml \
    $HOME/superdrops-in-action/build
  $ ./cleo_1dkid/scripts/bash/inputfiles_cleo_1dkid.sh \
    $HOME/superdrops-in-action/cleo_1dkid/share/cleo_initial_conditions/1dkid/fullscheme/config.yaml \
    $HOME/superdrops-in-action/build
  $ ./cleo_1dkid/scripts/bash/run_cleo_1dkid.sh

You can find out more about pybind11 by visiting
`their repository <https://github.com/pybind/pybind11/>`_
