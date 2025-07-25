/*
 * Copyright (c) 2025 MPI-M, Clara Bayley
 *
 *
 * ----- CLEO -----
 * File: py_observers.hpp
 * Project: pycleo
 * Created Date: Thursday 5th June 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors:
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Python bindings to various different CLEO's Observers instantiations
 */

#ifndef CLEO_1DKID_CLEO_DEPS_LIBS_PYCLEO_PY_OBSERVERS_HPP_
#define CLEO_1DKID_CLEO_DEPS_LIBS_PYCLEO_PY_OBSERVERS_HPP_

#include <pybind11/pybind11.h>

#include <stdexcept>

#include "../cleoconstants.hpp"
#include "./pycleo_aliases.hpp"
#include "configuration/config.hpp"
#include "initialise/timesteps.hpp"
#include "observers/collect_data_for_simple_dataset.hpp"
#include "observers/consttstep_observer.hpp"
#include "observers/gbxindex_observer.hpp"
#include "observers/massmoments_observer.hpp"
#include "observers/nsupers_observer.hpp"
#include "observers/observers.hpp"
#include "observers/sdmmonitor/do_sdmmonitor_obs.hpp"
#include "observers/sdmmonitor/monitor_precipitation_observer.hpp"
#include "observers/state_observer.hpp"
#include "observers/superdrops_observer.hpp"
#include "observers/time_observer.hpp"
#include "observers/totnsupers_observer.hpp"
#include "zarr/fsstore.hpp"
#include "zarr/simple_dataset.hpp"

namespace py = pybind11;
namespace pyca = pycleo_aliases;

void pyNullObserver(py::module &m);
void pyObserver(py::module &m);
void pycreate_observer(py::module &m);

#endif  // CLEO_1DKID_CLEO_DEPS_LIBS_PYCLEO_PY_OBSERVERS_HPP_
