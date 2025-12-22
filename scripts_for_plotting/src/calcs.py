"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: calcs.py
Project: scripts
Created Date: Thursday 11th December 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Calculations for xarray datasets of CLEO and PySDM 1-D kid test case
"""

import numpy as np
from metpy import calc as mtpy_calc
from metpy.units import units as mtpy_units


# %%
def vapor_pressure(ds):
    press = ds.press.values * 100 * mtpy_units.Pa  # [Pa]
    qvap = ds.qvap.values / 1000  # [kg/kg]

    return mtpy_calc.vapor_pressure(press, qvap).magnitude / 100  # [hPa]


def dry_pressure(ds):
    return ds.press.values - vapor_pressure(ds)  # [hPa]


# %%
def cleo_theta(ds):
    press = ds.press.values * 100 * mtpy_units.Pa  # [Pa]
    temp = ds.temp.values * mtpy_units.kelvin  # [K]

    theta = mtpy_calc.potential_temperature(press, temp).magnitude

    return theta  # [K]


def cleo_virtual_theta(ds):
    """sometimes called "dry theta, is theta as if parcel was dry"""
    press = ds.press.values * 100 * mtpy_units.Pa  # [Pa]
    temp = ds.temp.values * mtpy_units.kelvin  # [K]
    qvap = ds.qvap.values / 1000  # [kg/kg]

    theta_virtual = mtpy_calc.virtual_potential_temperature(press, temp, qvap).magnitude

    return theta_virtual  # [K]


def cleo_density(ds):
    press = ds.press.values * 100 * mtpy_units.Pa  # [Pa]
    temp = ds.temp.values * mtpy_units.kelvin  # [K]
    qvap = ds.qvap.values / 1000  # [kg/kg]

    return mtpy_calc.density(press, temp, qvap).magnitude  # [kg/m^3]


def cleo_dry_density(ds):
    qvap = ds.qvap.values / 1000  # [kg/kg]

    return cleo_density(ds) / (1 + qvap)  # [kg/m^3]


# %%
def pysdm_density(ds):
    qvap = ds.qvap.values / 1000  # [kg/kg]

    return ds.rho_dry.values * (1 + qvap)  # [kg/m^3]


def pysdm_theta(ds):
    press = ds.press.values * 100 * mtpy_units.Pa  # [Pa]
    temp = ds.temp.values * mtpy_units.kelvin  # [K]

    theta = mtpy_calc.potential_temperature(press, temp).magnitude

    return theta  # [K]


# %%
def mean_rolling_window(arr, rolling_window):
    return arr.rolling(time=rolling_window, center=True).mean()


def mean_pm_stddev(arr, dim="ensemble"):
    """return mean +- stddev over dimension of array (default over ensemble)"""
    mean = arr.mean(dim=dim)
    stddev = arr.std(dim=dim) / (arr[dim].size ** (0.5))

    assert not np.any(np.isnan(mean)) and not np.any(np.isnan(stddev))

    return mean - stddev, mean + stddev


def mean_pm_stddev_surfprecip_rolling(ds, precip_rolling_window, dim="ensemble"):
    lower, upper = mean_pm_stddev(ds.surfprecip_rate, dim=dim)
    lower = mean_rolling_window(lower, precip_rolling_window)
    upper = mean_rolling_window(upper, precip_rolling_window)
    return lower, upper
