"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: run_1dkid.py
Project: test_case_1dkid
Created Date: Monday 2nd September 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Wednesday 4th June 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
run 1-D KiD rainshaft model by timestepping and outputting data
"""

from .kid_dynamics import KiDDynamics
from libs.thermo.output_thermodynamics import OutputThermodynamics


def run_1dkid(
    z_delta, z_max, time_end, timestep, thermo, microphys_scheme, advect_hydrometeors
):
    """Run 1-D KiD rainshaft model with a specified microphysics scheme and KiD dynamics.

    This function runs a 1-D KiD rainshaft model with the given initial
    thermodynamic conditions, and microphysics scheme from time to time_end with
    a constant timestep based on the Shipway and Hill (2012) setup.

    Parameters:
        z_delta (float):
          Grid spacing od 1-D column (m).
        z_max (float):
          Upper limit of 1-D column (m).
        time_end (float):
          End time for the simulation (s).
        timestep (float):
          Timestep for the simulation (s).
        thermo (Thermodynamics):
          Initial thermodynamic conditions.
        microphys_scheme:
          Microphysics scheme to use.

    Returns:
          OutputThermodynamics: Output containing thermodynamic data from the model run.
    """

    ### type of dynamics rainshaft will undergo
    kid_dynamics = KiDDynamics(
        z_delta, z_max, timestep, time_end, advect_hydrometeors=advect_hydrometeors
    )

    ### run dynamics + microphysics from time to time_end
    microphys_scheme.initialize()

    ### data to output during model run
    ntime = int(time_end / timestep) + 1
    nz = len(kid_dynamics.zhalf) - 1
    shape = (ntime, nz)
    out = OutputThermodynamics(shape, zhalf=kid_dynamics.zhalf)

    time = 0.0
    thermo = kid_dynamics.set_thermo(time, thermo)
    out.output_thermodynamics(time, thermo)
    while time < time_end:
        thermo = kid_dynamics.run(time, timestep, thermo)
        thermo = microphys_scheme.run(timestep, thermo)
        kid_dynamics.set_advectees(thermo)

        time += timestep

        out.output_thermodynamics(time, thermo)

    microphys_scheme.finalize()

    out.finalize()
    return out
