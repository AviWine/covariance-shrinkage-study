import numpy as np

# All estimators use the 1/T convention (ddof=0), as in the Ledoit-Wolf derivation.


def sample_covariance(Y):
    """Sample covariance of a T x N array of returns."""
    Y_centered = Y - Y.mean(axis=0)
    return Y_centered.T @ Y_centered / Y.shape[0]


def constant_correlation_target(S, Y):
    """Ledoit-Wolf (2004) target F: sample variances on the diagonal, average pairwise correlation off it."""
    N = S.shape[0]
    std_devs = np.sqrt(np.diag(S))
    corr = S / np.outer(std_devs, std_devs)
    rbar = corr[np.triu_indices(N, k=1)].mean()
    F = rbar * np.outer(std_devs, std_devs)
    np.fill_diagonal(F, np.diag(S))
    return F, rbar


def shrinkage_intensity(Y, S, F, rbar):
    """delta* = max(0, min(kappa_hat / T, 1)) from the pi, rho and gamma estimators in Appendix B."""
    T = Y.shape[0]
    Y_centered = Y - Y.mean(axis=0)
    products = Y_centered[:, :, None] * Y_centered[:, None, :]
    covariance_deviations = products - S

    pi_mat = np.mean(covariance_deviations**2, axis=0)
    pi_hat = pi_mat.sum()

    variances = np.diag(S)
    squared_deviations = Y_centered**2 - variances
    theta_ii_ij = np.mean(squared_deviations[:, :, None] * covariance_deviations, axis=0)
    theta_jj_ij = np.mean(squared_deviations[:, None, :] * covariance_deviations, axis=0)
    ratio = np.sqrt(variances[None, :] / variances[:, None])  # [i, j] = sqrt(s_jj / s_ii)
    terms = rbar / 2 * (ratio * theta_ii_ij + (1 / ratio) * theta_jj_ij)
    np.fill_diagonal(terms, 0)
    rho_hat = np.trace(pi_mat) + terms.sum()

    gamma_hat = np.sum((F - S)**2)
    kappa_hat = (pi_hat - rho_hat) / gamma_hat
    return max(0.0, min(kappa_hat / T, 1.0))


def shrink_constant_correlation(Y):
    """Ledoit-Wolf (2004) shrinkage estimator delta* F + (1 - delta*) S."""
    S = sample_covariance(Y)
    F, rbar = constant_correlation_target(S, Y)
    delta = shrinkage_intensity(Y, S, F, rbar)
    return delta * F + (1 - delta) * S


ESTIMATORS = {
    'Sample': sample_covariance,
    'Shrink-CC': shrink_constant_correlation,
}
