# Results: sample covariance matrix under the Ledoit-Wolf evaluation algorithm

This applies the evaluation algorithm from page 8 of Ledoit & Wolf (2004), *Honey, I Shrunk the Sample
Covariance Matrix*, to the ETF universe, using the **sample covariance matrix** as the risk model. It is the
baseline the shrinkage estimators will be measured against. Reproduce with `python main.py` (and
`python main.py --cap 0.1` for the robustness check). The raw numbers are in [`results/`](results/).

## Evaluation algorithm

Each step follows page 8 of the paper. The last column shows what this study uses.

| Step | Paper | This study |
|---|---|---|
| Universe / benchmark | N largest US stocks, value-weighted | First N ETFs of a fixed nested list ([`data.py`](data.py)), **equal-weighted** |
| N | 30, 50, 100, 225, 500 | 11, 15, 19, 23, 27 |
| Risk model Σ̂ | Last **T = 60** monthly returns | Same: last 60 monthly returns, 1/T convention |
| Forecasts α̂ | Appendix C, unconstrained ex-ante IR = 1.5 | Same construction; ex-ante IR = 1.5 asserted every repetition |
| Optimiser | min x′Σ̂x s.t. x′α̂ ≥ g, x′1 = 0, −w_B ≤ x ≤ c1 − w_B | Same |
| Gain g | 300 bp a year | 300 bp a year (25 bp a month) |
| Weight cap c | 0.1 (= 3/N at N = 30) | **c = 3/N** (see below); c = 0.1 as a robustness check |
| Realised excess return | e = x′y at month end | Same |
| Out-of-sample period | 02/1983–12/2002, 239 months | **02/2013–09/2026, 164 months** |
| Ex-post IR | √12 · ē / s_e | Same, s_e with ddof = 1 |
| Repetitions | 50, mean-summaries reported | 50, seeds spawned from seed 7 |

**Why c = 3/N.** The paper's tightest case lets a stock be held at three times its average weight. With a 0.1
cap and only 11 ETFs, the most any ETF can be overweighted is 0.1 − 1/11 = 0.9 percentage points. The 300 bp target is
then out of reach in **every** month (see the robustness check), so the optimiser stops trading off risk against gain.
Fixing c at three times the benchmark weight keeps the constraint equally tight at every N, so N is the only
thing that changes.

**When g is out of reach.** In some months the forecasts are too weak for any feasible portfolio to reach 300 bp.
The optimiser then targets just below the largest achievable gain, and the table reports how often that happened.

## Mean-summary statistics (sample covariance, c = 3/N)

All numbers are annualised and are means over 50 repetitions. Mean and SD are in percent.

| N | N/T | IR | Mean excess return | SD of excess return | IR spread across reps (sd) | Months gain capped |
|---:|---:|---:|---:|---:|---:|---:|
| 11 | 0.18 | **0.86** | 1.84 | 2.15 | 0.26 | 1% |
| 15 | 0.25 | **0.89** | 1.83 | 2.06 | 0.24 | 4% |
| 19 | 0.32 | **0.88** | 1.81 | 2.08 | 0.22 | 7% |
| 23 | 0.38 | **0.88** | 1.94 | 2.21 | 0.22 | 16% |
| 27 | 0.45 | **0.85** | 1.86 | 2.19 | 0.20 | 8% |

For context, the paper's sample-covariance results at N = 30 were IR 0.97, Mean 2.18 and SD 2.26. The
equal-weighted benchmark itself returned 8.5–9.1% a year with a volatility of 10.0–10.5% over the same period
([`results/benchmark_summary.csv`](results/benchmark_summary.csv)).

## Discussion

**Information ratio.** The ex-post IR is about 0.87, roughly 58% of the ex-ante 1.5 built into the forecasts
(the paper's figure at N = 30 is 65%). The shortfall has the causes Appendix C lists: the long-only and cap
constraints, the risk model being estimated, and the noise draw itself. The spread across repetitions is wide.
Within each N the middle 80% of IRs runs from about 0.6 to 1.1–1.2, so the luck of the forecast noise matters
as much as the risk model.

**Mean excess return.** The realised mean of 1.8–1.9% a year falls short of the 3% target in every case. The
target is an ex-ante expectation built from noisy forecasts, so a shortfall is expected. Across repetitions,
the IR is almost entirely driven by the realised mean: their correlation is 0.91–0.95, while IR and SD are
only weakly correlated (−0.23 to 0.04). The repetitions differ in how much of the forecast's skill came through, not in how much
risk they took.

**Standard deviation (tracking error).** The realised SD is steady at 2.1–2.2% across N. The sample covariance
**under-forecasts** it: the optimiser expected about 1.8% a year, and the realised figure is 12–21% higher at
every N. This is the known bias of optimising on S. The optimiser leans on directions that look low-risk partly
because of estimation error, and those directions turn out riskier out of sample. It is the error shrinkage is
designed to reduce.

**IR as N increases.** In the paper, the sample-covariance IR falls steadily, from 0.97 at N = 30 to 0.20 at
N = 500, and the SD of excess returns nearly quadruples. Here the IR is **flat**: 0.85–0.89, with differences
no larger than about one standard error of the mean (0.03). This is consistent with the paper's mechanism rather
than a contradiction of it:

- The decline in the paper is driven by **N/T**. With T = 60, its benchmarks run from N/T = 0.5 to 8.3, and for
  N ≥ 60, S is singular. Estimation error then dominates, so the realised SD balloons and the IR collapses. Our
  universe only reaches N/T = 0.45, where S is still full rank and its estimation error grows only slowly with N.
  The predicted-vs-realised TE gap shows no trend, and the realised SD doesn't move.
- The forecast skill is calibrated to a constant ex-ante IR of 1.5 at every N, as in the paper. More assets don't
  add skill, so the only way N can change the IR is through the risk model and the constraints. Neither
  changes much over this range.

So, **with at most 27 ETFs and 60 months of data, the sample covariance has not yet reached the regime where it
breaks down.** This mirrors the single-window result in the exploratory notebook, where the estimated shrinkage
intensity was under 2%. To show where shrinkage matters, the study needs a higher N/T: shorter estimation windows
(e.g. T = 24 or 36) or a larger universe.

## Robustness check: the paper's literal c = 0.1

| N | IR | Mean | SD | Months gain capped |
|---:|---:|---:|---:|---:|
| 11 | 0.74 | 1.07 | 1.47 | 100% |
| 15 | 1.07 | 2.50 | 2.34 | 88% |
| 19 | 1.01 | 2.49 | 2.46 | 61% |
| 23 | 1.01 | 2.44 | 2.43 | 51% |
| 27 | 0.86 | 1.98 | 2.30 | 15% |

With a fixed 0.1 cap the IR moves with N, but it does so because the constraint loosens as 1/N falls, not because of
the risk model. At N = 11 the 300 bp target is never reachable. Between N = 15 and 23 it is mostly
unreachable, and the optimiser is pushed to the maximum-gain corner portfolio. This is why the main results use
c = 3/N.

## Caveats

- **The alpha is synthetic.** Forecasts are built from realised returns plus noise, so these results describe how
  the risk model behaves under a signal of known quality. They do not show that a tradable strategy exists.
- **The universes are nested and differ in composition.** Each step up in N adds four specific ETFs. Part of any
  difference between N values comes from which ETFs were added, not from N itself.
- **One historical period**, 2013–2026, with no transaction costs. Turnover (the paper's Table 3) is not yet
  measured.
- The 50 repetitions share the same noise draws for an ETF at every N, so differences between N values are
  measured with less noise than the per-N spreads suggest.

## Next steps

1. Run the same evaluation with **Shrink-CC** (`python main.py --estimator Shrink-CC`) and compare it repetition by
   repetition against Sample, as in the paper's Table 2 and Figure 1.
2. Raise N/T by shortening T, to reach the regime where the paper finds the largest gains.
3. Add turnover and a transaction-cost model.
