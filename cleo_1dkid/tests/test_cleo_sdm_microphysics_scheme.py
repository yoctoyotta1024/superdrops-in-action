"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: test_cleo_sdm_microphysics_scheme.py
Project: tests
Created Date: Monday 23rd June 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Tuesday 1st July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
unit tests for cleo_sdm microphysics module.
NOTE: tests assume CLEO's initial condition binary files already exist
    (i.e. 'dimlessGBxboundaries.dat' and 'dimlessSDsinit.dat' files, whose
    locations are given in CLEO's config file ('config_filename')
"""

import pytest
from mpi4py import MPI
import os
import sys
import numpy as np
from ruamel.yaml import YAML


@pytest.fixture(scope="module")
def path2cleopythonbindings(pytestconfig):
    return pytestconfig.getoption("cleo_path2cleopythonbindings")


@pytest.fixture(scope="module")
def config_filename(pytestconfig):
    return pytestconfig.getoption("cleo_test_generic_config_filename")


def _test_mpi_is_initialised():
    print(f"MPI version: {MPI.Get_version()}")

    return 0


def _test_initialize(path2cleopythonbindings, config_filename):
    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    from libs.cleo_sdm.cleo_sdm import CleoSDM as MicrophysicsScheme

    sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])
    import cleo_python_bindings as cleo

    yaml = YAML()
    with open(config_filename, "r") as file:
        python_config = yaml.load(file)

    t_start = 0
    timestep = python_config["timesteps"]["COUPLTSTEP"]  # [s]
    is_motion = python_config["python_bindings_setup"]["is_motion"]
    arr = np.array([], dtype=np.float64)
    press = temp = qvap = qcond = wvel = uvel = vvel = arr
    config = cleo.Config(str(config_filename))
    microphys = MicrophysicsScheme(
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
    )

    assert microphys.name == "CLEO SDM microphysics"

    return 0


def _test_initialize_wrapper(path2cleopythonbindings, config_filename):
    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    from libs.cleo_sdm.microphysics_scheme_wrapper import MicrophysicsSchemeWrapper

    sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])

    yaml = YAML()
    with open(config_filename, "r") as file:
        python_config = yaml.load(file)

    t_start = 0
    timestep = python_config["timesteps"]["COUPLTSTEP"]  # [s]
    is_motion = python_config["python_bindings_setup"]["is_motion"]
    arr = np.array([], dtype=np.float64)
    press = temp = qvap = qcond = wvel = uvel = vvel = arr
    microphys_wrapped = MicrophysicsSchemeWrapper(
        config_filename,
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
        do_init=False,
    )

    assert microphys_wrapped.initialize() == 0

    return 0


def _test_finalize_wrapper(path2cleopythonbindings, config_filename):
    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    from libs.cleo_sdm.microphysics_scheme_wrapper import MicrophysicsSchemeWrapper

    sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])

    yaml = YAML()
    with open(config_filename, "r") as file:
        python_config = yaml.load(file)

    t_start = 0
    timestep = python_config["timesteps"]["COUPLTSTEP"]  # [s]
    is_motion = python_config["python_bindings_setup"]["is_motion"]
    arr = np.array([], dtype=np.float64)
    press = temp = qvap = qcond = wvel = uvel = vvel = arr
    microphys_wrapped = MicrophysicsSchemeWrapper(
        config_filename,
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
        do_init=False,
    )

    assert microphys_wrapped.finalize() == 0

    return 0


def _test_microphys_with_wrapper(path2cleopythonbindings, config_filename):
    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    from libs.cleo_sdm.cleo_sdm import CleoSDM as MicrophysicsScheme
    from libs.cleo_sdm.microphysics_scheme_wrapper import MicrophysicsSchemeWrapper
    from libs.thermo.thermodynamics import Thermodynamics

    sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])
    import cleo_python_bindings as cleo

    yaml = YAML()
    with open(config_filename, "r") as file:
        python_config = yaml.load(file)

    t_start = 0
    timestep = python_config["timesteps"]["COUPLTSTEP"]  # [s]
    is_motion = python_config["python_bindings_setup"]["is_motion"]
    ngbxs = python_config["domain"]["ngbxs"]
    temp1 = np.tile(np.array([288.15], dtype=np.float64), ngbxs)
    temp2 = np.tile(np.array([288.15], dtype=np.float64), ngbxs)
    press1 = np.tile(np.array([101325], dtype=np.float64), ngbxs)
    press2 = np.tile(np.array([101325], dtype=np.float64), ngbxs)
    qvap1 = np.tile(np.array([0.015], dtype=np.float64), ngbxs)
    qvap2 = np.tile(np.array([0.015], dtype=np.float64), ngbxs)
    qcond1 = np.tile(np.array([0.0001], dtype=np.float64), ngbxs)
    qcond2 = np.tile(np.array([0.0001], dtype=np.float64), ngbxs)
    rho = np.tile(np.array([1.225], dtype=np.float64), ngbxs)
    qice = np.tile(np.array([0.0002], dtype=np.float64), ngbxs)
    qrain = np.tile(np.array([0.0003], dtype=np.float64), ngbxs)
    qsnow = np.tile(np.array([0.0004], dtype=np.float64), ngbxs)
    qgrau = np.tile(np.array([0.0005], dtype=np.float64), ngbxs)
    wvel = np.tile(np.array([-1.2, 1.0], dtype=np.float64), ngbxs)
    uvel = np.tile(np.array([-0.1, 0.2], dtype=np.float64), ngbxs)
    vvel = np.tile(np.array([0.0, 0.0], dtype=np.float64), ngbxs)

    thermo1 = Thermodynamics(
        temp1,
        rho,
        press1,
        qvap1,
        qcond1,
        qice,
        qrain,
        qsnow,
        qgrau,
        wvel,
        uvel,
        vvel,
    )
    thermo2 = Thermodynamics(
        temp2,
        rho,
        press2,
        qvap2,
        qcond2,
        qice,
        qrain,
        qsnow,
        qgrau,
        wvel,
        uvel,
        vvel,
    )

    config = cleo.Config(str(config_filename))
    microphys = MicrophysicsScheme(
        config,
        is_motion,
        t_start,
        timestep,
        thermo1.press,
        thermo1.temp,
        thermo1.massmix_ratios["qvap"],
        thermo1.massmix_ratios["qcond"],
        thermo1.wvel,
        thermo1.uvel,
        thermo1.vvel,
    )

    microphys_wrapped = MicrophysicsSchemeWrapper(
        config_filename,
        is_motion,
        t_start,
        timestep,
        thermo2.press,
        thermo2.temp,
        thermo2.massmix_ratios["qvap"],
        thermo2.massmix_ratios["qcond"],
        thermo2.wvel,
        thermo2.uvel,
        thermo2.vvel,
        do_init=False,
    )

    microphys.run(timestep)  # implict change of thermo1
    thermo2 = microphys_wrapped.run(timestep, thermo2)

    assert np.all(thermo1.press == thermo2.press)
    assert np.all(thermo1.temp == thermo2.temp)
    for q1, q2 in zip(thermo1.unpack_massmix_ratios(), thermo2.unpack_massmix_ratios()):
        assert np.all(q1 == q2)

    return 0


def test_cleo_sdm(path2cleopythonbindings, config_filename):
    os.environ["CLEO_PYTHON_BINDINGS"] = str(path2cleopythonbindings)

    sys.path.append(os.environ["CLEO_PYTHON_BINDINGS"])
    import cleo_python_bindings as cleo

    # only initialise CLEO once for all the following tests (also see do_init=False flag on wrapper)
    config = cleo.Config(str(config_filename))
    cleo.cleo_initialize(config)

    returns = [1] * 5
    returns[0] = _test_mpi_is_initialised()
    returns[1] = _test_initialize(path2cleopythonbindings, config_filename)
    returns[2] = _test_initialize_wrapper(path2cleopythonbindings, config_filename)
    returns[3] = _test_finalize_wrapper(path2cleopythonbindings, config_filename)
    returns[4] = _test_microphys_with_wrapper(path2cleopythonbindings, config_filename)

    for r in range(len(returns)):
        assert returns[r] == 0, f"test {r} failed"
