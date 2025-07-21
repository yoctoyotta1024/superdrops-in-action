from PySDM.initialisation.sampling.spectral_sampling import AlphaSampling


def AlphaSamplingWrapper(probdistrib, alpha, size_range):
    alpha_sampling = AlphaSampling(probdistrib, alpha=alpha, size_range=size_range)

    def alpha_sampling_xi(radii, totxi):
        return alpha_sampling_xi.xi

    def alpha_sampling_radii(nsupers):
        radii, alpha_sampling_xi.xi = alpha_sampling.sample(nsupers)
        return radii

    return alpha_sampling_radii, alpha_sampling_xi
