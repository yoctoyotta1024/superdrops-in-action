"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: settings.py
Project: test_case_1dkid
Created Date: Wednesday 2nd July 2025
Author: PyMPATA Authors (PyMPDATA)
Additional Contributors: Clara Bayley (CB)
-----
Last Modified: Wednesday 2nd July 2025
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
File is adaptation from PyMPDATA Shipway and Hill 2012 example, copied from:
https://github.com/open-atmos/PyMPDATA/blob/main/examples/PyMPDATA_examples/Shipway_and_Hill_2012/settings.py
between v1.6.1 and v1.6.2
"""

from typing import Optional

import numpy as np
from numdifftools import Derivative
from pystrict import strict
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d

from PyMPDATA_examples.Shipway_and_Hill_2012 import formulae
from .arakawa_c import arakawa_c
from PyMPDATA_examples.Shipway_and_Hill_2012.formulae import const, si


@strict
class Settings:
    def __init__(
        self,
        dt: float,
        dz: float,
        wmax_const: float,
        tscale_const: float,
        t_max: float = 15 * si.minutes,
        p0: Optional[float] = None,
        z_max: float = 3000 * si.metres,
        apprx_drhod_dz: bool = True,
    ):
        self.dt = dt
        self.dz = dz

        self.z_max = z_max
        self.t_max = t_max

        self.qv = interp1d(
            (0, 740, 3260), (0.015, 0.0138, 0.0024), fill_value="extrapolate"
        )
        self._th = interp1d(
            (0, 740, 3260), (297.9, 297.9, 312.66), fill_value="extrapolate"
        )

        # note: not in the paper,
        # https://github.com/BShipway/KiD/tree/master/src/physconst.f90#L43
        p0 = p0 or 1000 * si.hPa

        self.rhod0 = formulae.rho_d(p0, self.qv(0), self._th(0))
        self.thd = lambda z: formulae.th_dry(self._th(z), self.qv(z))

        def drhod_dz(z, rhod):
            T = formulae.temperature(rhod[0], self.thd(z))
            p = formulae.pressure(rhod[0], T, self.qv(z))
            drhod_dz = formulae.drho_dz(const.g, p, T, self.qv(z), const.lv)
            if not apprx_drhod_dz:  # to resolve issue #335
                qv = self.qv(z)
                dqv_dz = Derivative(self.qv)(z)
                drhod_dz = drhod_dz / (1 + qv) - rhod * dqv_dz / (1 + qv)
            return drhod_dz

        z_points = np.arange(0, self.z_max + self.dz / 2, self.dz / 2)
        rhod_solution = solve_ivp(
            fun=drhod_dz,
            t_span=(0, self.z_max),
            y0=np.asarray((self.rhod0,)),
            t_eval=z_points,
        )
        assert rhod_solution.success

        self.rhod = interp1d(z_points, rhod_solution.y[0])

        rhod_w_const = wmax_const * si.m / si.s * si.kg / si.m**3
        self.t_1 = tscale_const * si.s
        self.rhod_w = lambda t: (
            rhod_w_const * np.sin(np.pi * t / self.t_1) if t < self.t_1 else 0
        )

        self.z_vec = self.dz * arakawa_c.z_vector_coord((self.nz,))

    @property
    def nz(self):
        nz = self.z_max / self.dz
        assert nz == int(nz)
        return int(nz)

    @property
    def nt(self):
        nt = self.t_max / self.dt
        assert nt == int(nt)
        return int(nt)
