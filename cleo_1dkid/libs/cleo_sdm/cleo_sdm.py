"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: microphysics_scheme_wrapper.py
Project: cleo_sdm
Created Date: Monday 23rd June 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Thursday 10th July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
class and functions for handing setup and running of CLEO via python bindings adapted from
CLEO v0.44.0 python_bindings example.
NOTE: To use the wrapper, you must first export "PYCLEO_DIR". E.g. if python bindings are
built in $HOME/superdrops-in-action/build/, do:
export PYCLEO_DIR=$HOME/superdrops-in-action/build/pycleo/
"""

import os
import sys
from mpi4py import MPI

sys.path.append(os.environ["PYCLEO_DIR"])
import pycleo
from pycleo import coupldyn_numpy


def mpi_info(comm):
    print("\n--- PYCLEO STATUS: MPI INFORMATION ---")
    print(f"MPI version: {MPI.Get_version()}")
    print(f"Processor name: {MPI.Get_processor_name()}")
    print(f"Total processes: {comm.Get_size()}")
    print(f"Process rank: {comm.Get_rank()}")
    print("--------------------------------------")


def create_sdm(config, tsteps, is_motion):
    print("PYCLEO STATUS: creating GridboxMaps")
    gbxmaps = pycleo.create_cartesian_maps(
        config.get_ngbxs(),
        config.get_nspacedims(),
        config.get_grid_filename(),
    )

    print("PYCLEO STATUS: creating Observer")
    store = pycleo.FSStore(config.get_zarrbasedir())
    dataset = pycleo.SimpleDataset(store)
    obs = pycleo.pycreate_observer(config, tsteps, dataset, store)

    print("PYCLEO STATUS: creating MicrophysicalProcess")
    micro = pycleo.pycreate_microphysical_process(
        config, tsteps
    )  # config gives microphysics

    if is_motion:
        print("PYCLEO STATUS: creating Superdroplet Movement")
        motion = pycleo.create_cartesian_predcorr_motion(
            config, tsteps.get_motionstep()
        )
    else:
        print("PYCLEO STATUS: creating Superdroplet Movement without Motion")
        motion = pycleo.create_cartesian_predcorr_motion(config, False)
    transport = pycleo.CartesianTransportAcrossDomain()
    boundary_conditions = pycleo.NullBoundaryConditions()
    move = pycleo.CartesianMoveSupersInDomain(motion, transport, boundary_conditions)

    print("PYCLEO STATUS: creating SDM Methods")
    sdm = pycleo.CartesianSDMMethods(tsteps.get_couplstep(), gbxmaps, micro, move, obs)

    print(f"PYCLEO STATUS: SDM created with couplstep = {sdm.get_couplstep()}")
    return sdm, dataset, store


def prepare_to_timestep_sdm(config, sdm):
    print("PYCLEO STATUS: creating superdroplets")
    initsupers = pycleo.InitSupersFromBinary(
        config.get_initsupersfrombinary(), sdm.gbxmaps
    )
    allsupers = pycleo.create_supers_from_binary(
        initsupers, sdm.gbxmaps.get_local_ngridboxes_hostcopy()
    )

    print("PYCLEO STATUS: creating gridboxes")
    initgbxs = pycleo.InitGbxsNull(sdm.gbxmaps.get_local_ngridboxes_hostcopy())
    gbxs = pycleo.create_gbxs_cartesian_null(sdm.gbxmaps, initgbxs, allsupers)

    print("PYCLEO STATUS: preparing sdm")
    sdm.prepare_to_timestep(gbxs, allsupers)

    print("PYCLEO STATUS: preparation complete")
    return sdm, gbxs, allsupers


class CleoSDM:
    def __init__(
        self,
        config,
        is_motion,
        t_start,
        timestep,
        press,
        temp,
        qvap,
        qcond,
        wvel,
        uvel,
        vvel,
    ):
        """Initialize the CleoSDM object.

        CleoSDM class only works correctly if addresses of press, temp,
        qvap, qcond, wvel, uvel, and vvel arrays remain unchanged throughout a simulation.
        Undefined behaviour if values are changed by reassigning arrays rather than by copying
        data into the arrays given during class initialisation.
        """
        self.name = "CLEO SDM microphysics"

        tsteps = pycleo.pycreate_timesteps(config)
        assert (
            pycleo.realtime2step(timestep) == tsteps.get_couplstep()
        ), "timestep and SDM coupling not equal"

        self.t_sdm = pycleo.realtime2step(
            t_start
        )  # convert from seconds to model timesteps (!)

        self.coupldyn = coupldyn_numpy.NumpyDynamics(
            tsteps.get_couplstep(),
            press,
            temp,
            qvap,
            qcond,
            wvel,
            uvel,
            vvel,
        )
        self.comms = coupldyn_numpy.NumpyComms()

        self.sdm, self.dataset, self.store = create_sdm(config, tsteps, is_motion)
        self.sdm, self.gbxs, self.allsupers = prepare_to_timestep_sdm(config, self.sdm)

    def run(self, timestep):
        timestep = pycleo.realtime2step(
            timestep
        )  # convert from seconds to model timesteps (!)
        t_mdl_next = self.t_sdm + timestep
        assert t_mdl_next == self.sdm.next_couplstep(
            self.t_sdm
        ), "SDM out of sync with coupling"

        # print(f"PYCLEO STATUS: start t_sdm = {self.t_sdm} [model timesteps]")
        while self.t_sdm < t_mdl_next:
            t_sdm_next = min(
                self.sdm.next_couplstep(self.t_sdm), self.sdm.obs.next_obs(self.t_sdm)
            )

            if self.t_sdm % self.sdm.get_couplstep() == 0:
                self.comms.receive_dynamics(self.sdm.gbxmaps, self.coupldyn, self.gbxs)

            self.sdm.at_start_step(self.t_sdm, self.gbxs, self.allsupers)

            self.coupldyn.run_step(self.t_sdm, t_sdm_next)

            self.sdm.run_step(self.t_sdm, t_sdm_next, self.gbxs, self.allsupers)

            if self.t_sdm % self.sdm.get_couplstep() == 0:
                self.comms.send_dynamics(self.sdm.gbxmaps, self.gbxs, self.coupldyn)

            self.t_sdm = t_sdm_next
        # print(f"PYCLEO STATUS: end t_sdm = {self.t_sdm} [model timesteps]")
