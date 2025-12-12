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
class and functions for handing setup and running of CLEO via python bindings,
functions adapted from CLEO v0.64.0 python_bindings example.
NOTE: To use the wrapper, you must first export "CLEO_PYTHON_BINDINGS".
E.g. if python bindings are built in $HOME/superdrops-in-action/build/, do:
export CLEO_PYTHON_BINDINGS=$HOME/superdrops-in-action/build/_deps/cleo-build/cleo_python_bindings/
"""

import os
import sys
from mpi4py import MPI

sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])
import cleo_python_bindings as cleo
from cleo_python_bindings import coupldyn_numpy


def mpi_info(comm):
    print("\n--- CLEO STATUS: MPI INFORMATION ---")
    print(f"MPI version: {MPI.Get_version()}")
    print(f"Processor name: {MPI.Get_processor_name()}")
    print(f"Total processes: {comm.Get_size()}")
    print(f"Process rank: {comm.Get_rank()}")
    print("--------------------------------------")


def create_sdm(config, tsteps, is_motion):
    print("CLEO STATUS: creating GridboxMaps")
    gbxmaps = cleo.create_cartesian_maps(
        config.get_ngbxs(),
        config.get_nspacedims(),
        config.get_grid_filename(),
    )

    print("CLEO STATUS: creating Observer")
    store = cleo.FSStore(config.get_zarrbasedir())
    dataset = cleo.SimpleDataset(store)
    obs = cleo.pycreate_observer(config, tsteps, dataset, store)

    print("CLEO STATUS: creating MicrophysicalProcess")
    micro = cleo.pycreate_microphysical_process(
        config, tsteps
    )  # config gives microphysics

    if is_motion:
        print("CLEO STATUS: creating Superdroplet Movement")
        motion = cleo.create_cartesian_predcorr_motion(config, tsteps.get_motionstep())
    else:
        print("CLEO STATUS: creating Superdroplet Movement without Motion")
        motion = cleo.create_cartesian_predcorr_motion(config, False)
    transport = cleo.CartesianTransportAcrossDomain()
    boundary_conditions = cleo.AddSupersToDomain(config.get_addsuperstodomain())
    move = cleo.CartesianMoveSupersInDomain(motion, transport, boundary_conditions)

    print("CLEO STATUS: creating SDM Methods")
    sdm = cleo.CartesianSDMMethods(tsteps.get_couplstep(), gbxmaps, micro, move, obs)

    print(f"CLEO STATUS: SDM created with couplstep = {sdm.get_couplstep()}")
    return sdm, dataset, store


def prepare_to_timestep_sdm(config, sdm):
    print("CLEO STATUS: creating superdroplets")
    initsupers = cleo.InitSupersFromBinary(
        config.get_initsupersfrombinary(), sdm.gbxmaps
    )
    allsupers = cleo.create_supers_from_binary(
        initsupers, sdm.gbxmaps.get_local_ngridboxes_hostcopy()
    )

    print("CLEO STATUS: creating gridboxes")
    initgbxs = cleo.InitGbxsNull(sdm.gbxmaps.get_local_ngridboxes_hostcopy())
    gbxs = cleo.create_gbxs_cartesian_null(sdm.gbxmaps, initgbxs, allsupers)

    print("CLEO STATUS: preparing sdm")
    sdm.prepare_to_timestep(gbxs, allsupers)

    print("CLEO STATUS: preparation complete")
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

        tsteps = cleo.pycreate_timesteps(config)
        assert (
            cleo.realtime2step(timestep) == tsteps.get_couplstep()
        ), "timestep and SDM coupling not equal"

        self.t_sdm = cleo.realtime2step(
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
        timestep = cleo.realtime2step(
            timestep
        )  # convert from seconds to model timesteps (!)
        t_mdl_next = self.t_sdm + timestep
        assert t_mdl_next == self.sdm.next_couplstep(
            self.t_sdm
        ), "SDM out of sync with coupling"

        # print(f"CLEO STATUS: start t_sdm = {self.t_sdm} [model timesteps]")
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
        # print(f"CLEO STATUS: end t_sdm = {self.t_sdm} [model timesteps]")
