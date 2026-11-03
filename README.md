# covariance-shrinkage-study

A research study of **Ledoit-Wolf covariance shrinkage** in active portfolio construction.

**Question:** when does shrinking the sample covariance matrix change the optimal portfolio enough to matter,
and does any benefit survive transaction costs? The main variable is the ratio of observations to assets (T/N).

> **Read this first: the alpha signal is synthetic.** Forecasts are built from *realised* returns plus noise, calibrated
> to a known information ratio. The project shows how the covariance estimators behave under a signal of
> known quality. It does **not** claim that a tradable strategy exists.

## Status

This is a work in progress. [`exploratory_analysis.ipynb`](exploratory_analysis.ipynb) works through a single
estimation window and month. The consolidated code runs the paper's full evaluation algorithm, and its results are in
**[RESULTS.md](RESULTS.md)**.

- [x] Data download and cleaning checks
- [x] Sample covariance `S` and Ledoit-Wolf (2004) shrinkage towards a constant-correlation target, `S_hat`
- [x] Synthetic alpha forecast with a constant IR of 1.5, checked by assertion
- [x] Quadratic optimiser run with `S` and `S_hat`, and comparison of the two portfolios over January 2011
- [x] Rolling monthly evaluation (paper, p. 8): 164 months × 50 repetitions × N = 11–27, **sample covariance**
- [ ] The same evaluation for Shrink-CC (code is ready: `python main.py --estimator Shrink-CC`)
- [ ] T/N regimes where shrinkage is large (short windows, more assets)
- [ ] A second, non-variance-preserving shrinkage target (scaled identity)
- [ ] Transaction-cost model and turnover
- [ ] Sensitivity to sample length, IR and cost assumptions; repeated noise draws
- [x] Code split into data / estimators / alpha / optimisation / evaluation modules
- [ ] Tests for the numerical checks

## Code layout

| File | Contents |
|---|---|
| [`data.py`](data.py) | Load prices, monthly returns, nested ETF universes |
| [`estimators.py`](estimators.py) | Sample covariance, Ledoit-Wolf constant-correlation shrinkage |
| [`alpha.py`](alpha.py) | Appendix C synthetic forecasts, with the ex-ante IR check |
| [`optimiser.py`](optimiser.py) | Problem (1): minimum tracking variance subject to a gain target |
| [`evaluation.py`](evaluation.py) | Rolling evaluation algorithm and annualised IR, mean and SD |
| [`main.py`](main.py) | Runs the evaluation for each N and writes `results/` |

## Data

| | |
|---|---|
| Source | Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance), with dividend- and split-adjusted closes (`auto_adjust=True`) |
| Downloaded | 27 ETFs, 2008-01-02 to 2026-10-09 ([`download_data.py`](download_data.py) → `etf_prices.csv`) |
| Study universe | 11 ETFs across asset classes: DBC, GLD, HYG, QQQ, SHY, TLT, XLB, XLE, XLI, XLU, XLY |
| Estimation window | Daily returns, 2009-01-01 to 2010-12-31 (T = 504, N = 11, T/N ≈ 46) |
| Evaluation period | January 2011 (one month) |

No risk-free rate is used. "Excess" returns are measured against the **equal-weighted benchmark**: each ETF's return
minus the cross-sectional average. Yahoo revises adjusted prices over time, so the exact price snapshot used
here is committed as `etf_prices.csv`. Re-running `download_data.py` overwrites it and can shift the results slightly.

## Method

1. **Sample covariance `S`** of daily returns, using the 1/T convention (`ddof=0`). The Ledoit-Wolf
   estimator is derived with 1/T, so the same convention is used throughout.
2. **Shrinkage** `S_hat = δ*·F + (1 − δ*)·S`, where `F` is the constant-correlation target (sample variances on the
   diagonal, average pairwise correlation off it). The intensity δ* = κ̂/T is computed from the π̂, ρ̂ and γ̂
   estimators in Ledoit & Wolf (2004), clipped to [0, 1]. This target preserves the sample variances, so
   `diag(S_hat) = diag(S)`.
3. **Synthetic alpha** (Grinold-Kahn: *alpha = volatility × IC × score*):
   - IC = IR / √(12·N) by the fundamental law of active management, with IR = 1.5 and monthly rebalancing.
   - Raw forecast = realised January active return + noise. The noise is N independent normal draws, each scaled by
     that ETF's monthly residual volatility.
   - Scores are standardised cross-sectionally. With this construction the ex-ante IR equals 1.5 exactly, for any
     draw, and the notebook asserts it.
   - **Seed 7** (`np.random.default_rng(7)`) is part of the experiment's definition. Changing the seed, the
     number of draws or the scaling changes the results.
4. **Optimiser** ([cvxpy](https://www.cvxpy.org/)): find the active weights `x` relative to the equal-weighted
   benchmark that minimise tracking variance `x'Σx`, where Σ is `S` or `S_hat`, subject to:
   - fully invested: `Σx = 0`
   - long-only: `x ≥ −w_b`
   - at most 15% per asset
   - forecast alpha `x'α ≥ g`

   The target `g` is set to **half the maximum forecast alpha the constraints allow**. A fixed 3% monthly target
   was infeasible.
5. **Evaluation:** forecast alpha, ex-ante tracking error under both matrices, realised active return and realised
   tracking error over the month, and the size of the active positions.

Units: covariances are daily and alphas are monthly. Tracking errors are converted to monthly with a factor of 21
trading days (variance × 21, standard deviation × √21).

## Result so far (one window, one month)

| | S | S_hat |
|---|---|---|
| Shrinkage intensity δ* | – | 0.017 |
| Forecast alpha (monthly) | 0.186% | 0.186% |
| Ex-ante TE, monthly (own estimator) | 0.287% | 0.300% |
| Realised active return, Jan 2011 | −0.052% | −0.036% |
| Realised TE, Jan 2011 (monthly) | 0.258% | 0.264% |
| Σ\|active weights\| | 0.368 | 0.365 |

With T/N ≈ 46 the estimated shrinkage is under 2%. The two portfolios differ by only about 1.2% of total weight, and
their outcomes are indistinguishable. **This is the expected "shrinkage doesn't matter" baseline**, not evidence for or
against shrinkage. One month and one noise draw can't separate the estimators. The rolling backtest across
T/N regimes is what will answer the question.

## Limitations

- The alpha is synthetic and uses realised returns (look-ahead by design). Results describe the estimators, not a strategy.
- So far there is one estimation window, one evaluation month and one noise draw.
- No transaction costs yet.
- The constant-correlation target is the only target implemented so far.
- Survivorship: the universe is ETFs that still exist today.

## Reproducing

Python 3.14. Package versions used:

```
numpy==2.5.4  pandas==3.0.6  scipy==1.18.1  cvxpy==1.9.3  matplotlib==3.11.2  yfinance==1.7.0  ipykernel==7.4.0
```

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy==2.5.4 pandas==3.0.6 scipy==1.18.1 cvxpy==1.9.3 matplotlib==3.11.2 yfinance==1.7.0 ipykernel==7.4.0
# etf_prices.csv is in the repo; only run download_data.py to refresh it (results may then differ slightly)
python main.py                   # evaluation for the sample covariance, writes results/ (about 30 seconds)
python main.py --cap 0.1         # robustness check with the paper's literal weight cap
# the exploratory notebook: open exploratory_analysis.ipynb with this .venv as the kernel, and Run All
```

## References

- Ledoit, O. and Wolf, M. (2004). *Honey, I Shrunk the Sample Covariance Matrix.* Journal of Portfolio Management, 30(4), 110–119.
- Grinold, R. and Kahn, R. (2000). *Active Portfolio Management*, 2nd ed. McGraw-Hill.
