CLEO 1-D KiD Test Case
======================

The 1-D KiD test case uses the PYMPDATA libray alongside CLEO SDM. To run CLEO's C++ code alongside
PYMPDATA, we first make the pycleo Python module using pybind11.

Creating The Python Bindings
----------------------------

To build the python bindings for CLEO you can simply do
`` cmake -S ./cleo_1dkid/ -B ./build && cd build && make pycleo``. However,
you need to have certain :ref:`requirements <requirements>` fulfilled first
(compiler versions etc.). On Levante, we therefore reccomend you use the bash helper script
``scripts/compile_pycleo_levante.sh`` instead of directly calling cmake.

First activate the python environment you want to use, e.g.
``micromamba activate superdrops-in-action``.
Then call the helper script with the source and build directories you want to use, e.g.

.. code-block:: console

  $ ./scripts/compile_bindings_levante.sh $HOME/superdrops-in-action/cleo_1dkid $HOME/superdrops-in-action/build

After making the bindings, the ``pycleo`` Python module can used just like an ordinary python module.

You can find out more about pybind11 by visiting
`their repository <https://github.com/pybind/pybind11/>`_
