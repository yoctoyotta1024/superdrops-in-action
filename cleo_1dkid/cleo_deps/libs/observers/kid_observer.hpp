/*
 * Copyright (c) 2024 MPI-M, Clara Bayley
 *
 * ----- CLEO_1dkid -----
 * File: observers.hpp
 * Project: observers
 * Created Date: Monday 14th July 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors:
 * -----
 * Last Modified: Monday 14th July 2025
 * Modified By: CB
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Observer specifically for output needed to plot KiD 1-D test case
 */

#ifndef CLEO_1DKID_CLEO_DEPS_LIBS_OBSERVERS_KID_OBSERVER_HPP_
#define CLEO_1DKID_CLEO_DEPS_LIBS_OBSERVERS_KID_OBSERVER_HPP_

#include <Kokkos_Core.hpp>
#include <concepts>
#include <cstdint>
#include <iostream>
#include <memory>

#include "../cleoconstants.hpp"
#include "../kokkosaliases.hpp"
#include "gridboxes/gridbox.hpp"
#include "observers/consttstep_observer.hpp"
#include "observers/observers.hpp"
#include "superdrops/sdmmonitor.hpp"
#include "zarr/buffer.hpp"
#include "zarr/xarray_zarr_array.hpp"


/**
 * @brief Structure NullObserver does nothing at all.
 *
 * NullObserver defined for completion of Observer's Monoid Set.
 *
 */
struct KiDObserver {
  /**
   * @brief No operations before timestepping.
   *
   * @param d_gbxs The view of gridboxes in device memory.
   */
  void before_timestepping(const viewd_constgbx d_gbxs) const {}

  /**
   * @brief No perations after timestepping.
   */
  void after_timestepping() const {}

  /**
   * @brief Next observation time is largest possible value.
   *
   * @param t_mdl Unsigned int for current timestep.
   * @return The next observation time (maximum unsigned int).
   */
  unsigned int next_obs(const unsigned int t_mdl) const { return LIMITVALUES::uintmax; }

  /**
   * @brief Check if on step always returns false.
   *
   * Null observer is never on_step.
   *
   * @param t_mdl The unsigned int parameter.
   * @return bool, always false.
   */
  bool on_step(const unsigned int t_mdl) const { return false; }

  /**
   * @brief No operations at the start of a step.
   *
   * @param t_mdl The unsigned int for the current timestep.
   * @param d_gbxs The view of gridboxes in device memory.
   * @param d_supers View of superdrops on device.
   */
  void at_start_step(const unsigned int t_mdl, const viewd_constgbx d_gbxs,
                     const subviewd_constsupers d_supers) const {}

  /**
   * @brief Get null monitor for SDM processes from observer.
   *
   * @return monitor 'mo' of the observer that does nothing
   */
  SDMMonitor auto get_sdmmonitor() const { return NullSDMMonitor{}; }
};

#endif  // CLEO_1DKID_CLEO_DEPS_LIBS_OBSERVERS_KID_OBSERVER_HPP_
