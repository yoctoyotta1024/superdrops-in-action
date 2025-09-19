CLEO 1-D KiD Test Case
======================

The 1-D KiD test case uses the PYMPDATA libray alongside CLEO SDM. To run CLEO's C++ code alongside
PYMPDATA, we first make the CLEO's python bindings (Python module called ``cleo_python_bindings``)
using pybind11.

Creating The Python Bindings
----------------------------

CLEO's libraries are fetched and build via the ``CMakeLists.txt`` in the
directory ``cleo_1dkid/cleo_deps``.

To build the python bindings for CLEO you can simply do
`` cmake -S ./cleo_1dkid/ -B ./build && cd build && make cleo_python_bindings``. However,
you need to have certain :ref:`requirements <requirements>` fulfilled first
(compiler versions etc.). On Levante, we therefore reccomend you use the bash helper script
``cleo_1dkid/scripts/bash/compile_cleo_python_bindings_levante.sh`` instead of directly calling cmake.

First activate the python environment you want to use, e.g.
``micromamba activate superdrops-in-action``.
Then call the helper script with the source and build directories you want to use, e.g.

.. code-block:: console

  $ ./cleo_1dkid/scripts/bash/compile_cleo_python_bindings_levante.sh \
      $HOME/superdrops-in-action/cleo_1dkid \
      /work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build

After making the bindings, the ``cleo_python_bindings`` Python module can used just like an
ordinary python module. The bindings are by default built in
``[your_build_directory]/_deps/cleo-build/cleo_python_bindings/`` To run the
``condevap_only`` and ``fullscheme`` examples you can use the
helper scripts to first generate the initial conditions and then run the executables:

.. code-block:: console

  $ ./cleo_1dkid/scripts/bash/inputfiles_cleo_1dkid.sh \
      ${HOME}/superdrops-in-action/cleo_1dkid \
      /work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build 0 99
  $ ./cleo_1dkid/scripts/bash/run_cleo_1dkid.sh \
      ${HOME}/superdrops-in-action/cleo_1dkid \
      /work/bm1183/m300950/superdrops-in-action/cleo_1dkid/build 0 99

Checkout the quickplots plotting script ``cleo_1dkid/scripts/quickplot_cleo_1dkid.py``
to help you view your results.

You can find out more about pybind11 by visiting
`their repository <https://github.com/pybind/pybind11/>`_
