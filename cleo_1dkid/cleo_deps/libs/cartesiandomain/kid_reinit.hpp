/*
 * Copyright (c) 2025 MPI-M, Clara Bayley
 *
 *
 * ----- CLEO_1dkid -----
 * File: kid_reinit.hpp
 * Project: cartesiandomain
 * Created Date: Monday 14th July 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors:
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Definition of the boundary condition for the KiD 1-D test case where superdroplets that leave the
 * top of the domain are reinitialised with their dry radius.
 */

#ifndef CLEO_1DKID_CLEO_DEPS_LIBS_CARTESIANDOMAIN_KID_REINIT_HPP_
#define CLEO_1DKID_CLEO_DEPS_LIBS_CARTESIANDOMAIN_KID_REINIT_HPP_

#include <Kokkos_Core.hpp>

/* combiined with change_radius function this will set a superdroplet's radius to its dry radius */
KOKKOS_INLINE_FUNCTION
double kid_reinitialise_radius(const double radius) {
  return 0.0;
}

#endif  // CLEO_1DKID_CLEO_DEPS_LIBS_CARTESIANDOMAIN_KID_REINIT_HPP_
