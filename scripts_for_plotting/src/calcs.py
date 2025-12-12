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
