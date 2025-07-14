/*
 * Copyright (c) 2024 MPI-M, Clara Bayley
 *
 *
 * ----- CLEO -----
 * File: nulldyncomms.hpp
 * Project: coupldyn_null
 * Created Date: Friday 17th November 2023
 * Author: Clara Bayley (CB)
 * Additional Contributors:
 * -----
 * Last Modified: Friday 21st June 2024
 * Modified By: CB
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * struct obeying coupleddynamics concept for dynamics solver in CLEO where there is
 * no coupling / communication to SDM
 */

#ifndef CLEO_1DKID_CLEO_DEPS_LIBS_COUPLDYN_NULL_NULLDYNCOMMS_HPP_
#define CLEO_1DKID_CLEO_DEPS_LIBS_COUPLDYN_NULL_NULLDYNCOMMS_HPP_

#include <Kokkos_Core.hpp>

#include "../kokkosaliases.hpp"
#include "coupldyn_null/nulldynamics.hpp"

/* empty (no) coupling to/from to CLEO's gridboxes.
Struct obeys coupling comms concept */
struct NullDynComms {
  /* receive information from NullDynamics
  solver if null for no coupling to CLEO SDM */
  template <typename GbxMaps, typename CD = NullDynComms>
  KOKKOS_INLINE_FUNCTION void receive_dynamics(const GbxMaps &gbxmaps, const NullDynamics &nulldyn,
                                               const viewh_gbx h_gbxs) const {}

  /* send information from Gridboxes' states
  to coupldyn is null for NullDynamics */
  template <typename GbxMaps, typename CD = NullDynComms>
  KOKKOS_INLINE_FUNCTION void send_dynamics(const GbxMaps &gbxmaps, const viewh_constgbx h_gbxs,
                                            const NullDynamics &nulldyn) const {}
};

#endif  // CLEO_1DKID_CLEO_DEPS_LIBS_COUPLDYN_NULL_NULLDYNCOMMS_HPP_
