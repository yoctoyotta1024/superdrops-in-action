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

from .arakawa_c import arakawa_c
from PyMPDATA_examples.Shipway_and_Hill_2012 import formulae
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
        z_min: float = 0 * si.metres,
        z_max: float = 3000 * si.metres,
        p_surf: float = 1000 * si.hPa,
        is_exner_novapour: Optional[bool] = False,
        is_exner_novapour_uniformrho: Optional[bool] = False,
        is_approx_drhod_dz: Optional[bool] = False,
    ):
        self.dt = dt
        self.dz = dz

        self.z_min = z_min
        self.z_max = z_max
        self.t_max = t_max

        self.qv = interp1d(
            (0, 740, 3260), (0.015, 0.0138, 0.0024), fill_value="extrapolate"
        )
        self._th = interp1d(
            (0, 740, 3260), (297.9, 297.9, 312.66), fill_value="extrapolate"
        )

        self.thd = lambda z: formulae.th_dry(self._th(z), self.qv(z))

        z_points = np.arange(0, self.z_max + self.dz / 2, self.dz / 2)

        def zpos(z):
            return np.where(z < 0, 0, z)  # deal with z < 0 like it is z == 0

        if is_exner_novapour or is_exner_novapour_uniformrho:
            # note: not in the paper,
            # https://github.com/BShipway/KiD/blob/bad81aa6efa4b7e4743b6a1867382fc74c10a884/src/test_cases.f90#L784
            def z2exner(z, return_rho=False, return_press=False, return_temp=False):
                nz = len(z)
                p_ref = 100000.0
                r_on_cp = const.Rd / const.c_pd
                theta = self.thd(z)

                dexner = np.zeros(nz)
                dexner[0] = const.g * z[0] / (const.c_pd * theta[0])
                for k in range(1, nz):
                    dexner[k] = (
                        const.g
                        * (z[k] - z[k - 1])
                        / (const.c_pd * 0.5 * (theta[k] + theta[k - 1]))
                    )

                exner = np.zeros(nz)
                exner[-1] = (p_surf / p_ref) ** r_on_cp - np.sum(dexner)
                for k in range(nz - 2, -1, -1):
                    exner[k] = exner[k + 1] + dexner[k]

                if return_rho:
                    rho = (p_ref * exner ** (1.0 / r_on_cp - 1.0)) / (const.Rd * theta)
                    return rho
                if return_press:
                    return p_ref * exner ** (1.0 / r_on_cp)
                if return_temp:
                    return theta * exner
                else:
                    return exner

            self.temp = lambda z: z2exner(zpos(z), return_temp=True)
            self.press = lambda z: z2exner(zpos(z), return_press=True)
            self.rhod = lambda z: z2exner(zpos(z), return_rho=True)
            if is_exner_novapour_uniformrho:
                rhod0 = 1.0 * np.ones_like(z_points)  # [kg / m^3]
                self.rhod = lambda z: interp1d(z_points, rhod0)(zpos(z))

        else:
            # note: not in the paper,
            # https://github.com/BShipway/KiD/tree/master/src/physconst.f90#L43
            def drhod_dz(z, rhod):
                T = formulae.temperature(rhod[0], self.thd(z))
                p = formulae.pressure(rhod[0], T, self.qv(z))
                drhod_dz = formulae.drho_dz(const.g, p, T, self.qv(z), const.lv)
                if not is_approx_drhod_dz:  # to resolve issue #335
                    qv = self.qv(z)
                    dqv_dz = Derivative(self.qv)(z)
                    drhod_dz = drhod_dz / (1 + qv) - rhod * dqv_dz / (1 + qv) ** 2
                return drhod_dz

            rhod0 = formulae.rho_d(p_surf, self.qv(0), self._th(0))
            rhod_solution = solve_ivp(
                fun=drhod_dz,
                t_span=(0, self.z_max),
                y0=np.asarray((rhod0,)),
                t_eval=z_points,
            )
            assert rhod_solution.success

            self.rhod = lambda z: interp1d(z_points, rhod_solution.y[0])(zpos(z))
            self.temp = lambda z: formulae.temperature(
                self.rhod(zpos(z)), self.thd(zpos(z))
            )
            self.press = lambda z: formulae.pressure(
                self.rhod(zpos(z)), self.temp(zpos(z)), self.qv(zpos(z))
            )

        rhod_w_const = wmax_const * si.m / si.s * si.kg / si.m**3
        self.t_1 = tscale_const * si.s
        self.rhod_w = lambda t: (
            rhod_w_const * np.sin(np.pi * t / self.t_1) if t < self.t_1 else 0
        )

        self.nz_vec = arakawa_c.z_vector_coord((self.nz,))

    @property
    def nz(self):
        nz = (self.z_max - self.z_min) / self.dz
        assert nz == int(nz)
        return int(nz)

    @property
    def nt(self):
        nt = self.t_max / self.dt
        assert nt == int(nt)
        return int(nt)
