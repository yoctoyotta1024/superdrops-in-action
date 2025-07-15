/*
 * Copyright (c) 2025 MPI-M, Clara Bayley
 *
 *
 * ----- CLEO -----
 * File: py_observers.cpp
 * Project: pycleo
 * Created Date: Thursday 5th June 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors:
 * -----
 * Last Modified: Wednesday 11th June 2025
 * Modified By: CB
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Functionality for creating python bindings to various different CLEO's Observers instantiations
 */

#include "./py_observers.hpp"

kid_observer::obs create_kid_observer(const Config &config, const Timesteps &tsteps,
                                    SimpleDataset<FSStore> &dataset, FSStore &store);

void pyNullObserver(py::module &m) {
  py::class_<pyca::obs_null>(m, "NullObserver")
      .def(py::init())
      .def("next_obs", &pyca::obs_null::next_obs, py::arg("t_mdl"));
}

void pyKiDObserver(py::module &m) {
  py::class_<kid_observer::obs>(m, "KiDObserver")
      .def(py::init<kid_observer::kid, kid_observer::time, kid_observer::mo>())
      .def("next_obs", &kid_observer::obs::next_obs, py::arg("t_mdl"));
}

void pycreate_kid_observer(py::module &m) {
  m.def(
      "pycreate_kid_observer", &create_kid_observer,
      "returns type of Observer suitable for KiD test case",
      py::arg("config"), py::arg("tsteps"), py::arg("dataset"), py::arg("store"));
}

kid_observer::obs create_kid_observer(const Config &config, const Timesteps &tsteps,
                                    SimpleDataset<FSStore> &dataset, FSStore &store) {
  const auto obsstep = tsteps.get_obsstep();
  const auto maxchunk = config.get_maxchunk();

  const Observer auto obs1 = TimeObserver(obsstep, dataset, store, maxchunk,
                                            &step2dimlesstime);
  const Observer auto obs2 = ConstTstepObserver(obsstep, DoKiDObs(dataset, store, maxchunk,
                                                                    &step2dimlesstime));
  return obs2 >> obs1;
}
