import argparse
import time
from pathlib import Path

import pandas as pd

from data import load_prices, monthly_returns
from estimators import ESTIMATORS
from evaluation import benchmark_stats, evaluate

N_VALUES = [11, 15, 19, 23, 27]

# Upper bound c on any ETF's total weight. The paper uses c = 0.1 with N >= 30, i.e. at least 3x the average weight.
# With an equal-weighted benchmark and N = 11-27, c = 0.1 leaves almost no room to overweight (0.1 - 1/11 = 0.9pp),
# so the default keeps the paper's ratio instead: c = 3/N.
CAP_RULES = {
    '3/N': lambda n: 3 / n,
    '0.1': lambda n: 0.1,
}


def main():
    parser = argparse.ArgumentParser(description='Ledoit-Wolf (2004) evaluation algorithm on the ETF universe.')
    parser.add_argument('--estimator', default='Sample', choices=ESTIMATORS)
    parser.add_argument('--cap', default='3/N', choices=CAP_RULES)
    parser.add_argument('--reps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=7)
    args = parser.parse_args()

    returns = monthly_returns(load_prices())
    out = Path('results')
    out.mkdir(exist_ok=True)

    bench = pd.DataFrame([benchmark_stats(returns, n) for n in N_VALUES]).set_index('N')
    bench.round(2).to_csv(out / 'benchmark_summary.csv')
    print('Equal-weighted benchmark, annualised %\n', bench.round(2), '\n')

    reps = []
    for n in N_VALUES:
        start = time.time()
        c = CAP_RULES[args.cap](n)
        reps.append(evaluate(returns, n, ESTIMATORS[args.estimator], n_reps=args.reps, seed=args.seed, c=c))
        print(f'N = {n}, c = {c:.3f}: {time.time() - start:.0f}s')
    reps = pd.concat(reps)

    name = f"{args.estimator.lower()}_cap{args.cap.replace('/', 'over')}"
    reps.to_csv(out / f'{name}_reps.csv', index=False)
    summary = reps.groupby('N')[['IR', 'Mean', 'SD', 'capped_months']].mean()
    summary['IR (sd across reps)'] = reps.groupby('N')['IR'].std(ddof=1)
    summary.round(3).to_csv(out / f'{name}_summary.csv')
    print(f'\nMean-summary over {args.reps} repetitions, {args.estimator}\n', summary.round(2))


if __name__ == '__main__':
    main()
