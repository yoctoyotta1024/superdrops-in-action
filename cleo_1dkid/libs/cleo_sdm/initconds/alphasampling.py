"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- superdrops-in-action -----
File: alphasampling.py
Project: initconds
Created Date: Tuesday 18th November 2025
Author: Clara Bayley (CB)
Additional Contributors:
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
Wrapper around PySDM aloha sampling functions (see create_initsuperdropsbinary_script.py)
"""

from PySDM.initialisation.sampling.spectral_sampling import AlphaSampling


def AlphaSamplingWrapper(probdistrib, alpha, size_range):
    alpha_sampling = AlphaSampling(probdistrib, alpha=alpha, size_range=size_range)

    def alpha_sampling_xi(radii, totxi):
        return alpha_sampling_xi.xi

    def alpha_sampling_radii(nsupers):
        radii, alpha_sampling_xi.xi = alpha_sampling.sample(nsupers)
        return radii

    return alpha_sampling_radii, alpha_sampling_xi
