import numpy as np
import pandas as pd

from alpha import forecast_alphas
from data import UNIVERSE_ORDER, universe
from optimiser import ActiveOptimiser

# Evaluation algorithm from page 8 of Ledoit & Wolf (2004), with an equal-weighted ETF benchmark:
#   - at the start of each month, estimate Sigma from the last T monthly returns and feed wb, alpha, Sigma, g, c to the optimiser
#   - at the end of the month the realised excess return is e = x'y
#   - annualised ex-post IR = sqrt(12) * mean(e) / sd(e); repeat with fresh forecast noise and report mean-summaries


def annualised_stats(e):
    # Sample standard deviation (ddof=1) as in the paper's ex-post statistics. Mean and SD are in percent.
    mean, sd = e.mean(), e.std(ddof=1)
    return {'IR': np.sqrt(12) * mean / sd, 'Mean': 1200 * mean, 'SD': np.sqrt(12) * 100 * sd}


def evaluate(returns, n, estimator, n_reps=50, seed=7, T=60, c=0.1, gain=0.03, ir=1.5):
    """
    returns: DataFrame of monthly returns for the full ETF universe.
    Returns one row per repetition with the annualised IR, Mean and SD of the realised excess returns,
    plus the share of months where the gain target was above the feasible maximum.
    """
    R = returns[universe(n)].to_numpy()
    Y = R[T:]                                             # out-of-sample months
    excess = Y - Y.mean(axis=1, keepdims=True)            # e_it: asset return minus equal-weighted benchmark
    M = len(Y)

    # Sigma only depends on the estimation window, so estimate it once per month and reuse across repetitions
    sigmas = [estimator(R[t - T:t]) for t in range(T, T + M)]
    optimiser = ActiveOptimiser(n, c)

    # Seed 7 defines the experiment: repetition r always gets the same child stream. Noise is drawn for the
    # full universe and sliced, so an ETF gets the same draws whatever N it is part of.
    children = np.random.SeedSequence(seed).spawn(n_reps)
    rows = []
    for r, child in enumerate(children):
        z = np.random.default_rng(child).standard_normal((M, len(UNIVERSE_ORDER)))[:, :n]
        alphas = forecast_alphas(excess, z, ir)

        e = np.empty(M)
        capped = 0
        for t in range(M):
            x, was_capped = optimiser.solve(sigmas[t], alphas[t], gain / 12)
            e[t] = x @ Y[t]
            capped += was_capped
        rows.append({'N': n, 'rep': r, **annualised_stats(e), 'capped_months': capped / M})
    return pd.DataFrame(rows)


def benchmark_stats(returns, n, T=60):
    """Annualised mean and SD (percent) of the equal-weighted benchmark over the out-of-sample period."""
    b = returns[universe(n)].to_numpy()[T:].mean(axis=1)
    return {'N': n, 'Mean': 1200 * b.mean(), 'SD': np.sqrt(12) * 100 * b.std(ddof=1)}
