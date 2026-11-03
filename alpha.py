import numpy as np

# Synthetic alpha forecasts following Appendix C of Ledoit & Wolf (2004) / Grinold & Kahn: alpha = volatility * IC * score.
# Everything is monthly. All standard deviations use ddof=0 so the ex-ante IR check below holds exactly.


def information_coefficient(ir, n):
    # Fundamental law: IR = IC * sqrt(breadth), breadth = 12 monthly rebalances * N assets
    return ir / np.sqrt(12 * n)


def forecast_alphas(excess, z, ir=1.5):
    """
    excess: M x N array of realised excess returns e_it (asset return minus benchmark return).
    z: M x N array of independent standard normal draws.
    Returns the M x N array of refined forecasts alpha_it.
    """
    M, N = excess.shape
    IC = information_coefficient(ir, N)

    # Volatility of each asset's excess return over time (hindsight, as in the paper)
    s_e = excess.std(axis=0)

    # Step 1: raw = e + u, noise scaled per asset so that corr(raw_i, e_i) is about IC
    u = s_e * np.sqrt(1 / IC**2 - 1) * z
    raw = excess + u

    # Step 2: scores, standardised per asset over time
    scores = (raw - raw.mean(axis=0)) / raw.std(axis=0)

    # Step 3: refined forecasts
    alphas = s_e * IC * scores

    # Check: unconstrained ex-ante IR, sqrt(12 * mean_t sum_i (alpha_it / s_e,i)^2) = IC * sqrt(12N) = IR
    ex_ante_ir = np.sqrt(12 * np.mean(np.sum((alphas / s_e)**2, axis=1)))
    assert np.isclose(ex_ante_ir, ir), ex_ante_ir
    return alphas
