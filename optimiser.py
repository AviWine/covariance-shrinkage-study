import cvxpy as cp
import numpy as np


def max_gain(alpha, wb, c):
    """Largest forecast active return x'alpha the constraints allow: fill the highest alphas up to c first."""
    w = np.zeros_like(wb)
    remaining = 1.0
    for i in np.argsort(-alpha):
        w[i] = min(c, remaining)
        remaining -= w[i]
        if remaining <= 0:
            break
    return (w - wb) @ alpha


class ActiveOptimiser:
    """
    Problem (1) of Ledoit & Wolf (2004):
        minimise x' Sigma x  subject to  x'alpha >= g,  x'1 = 0,  x >= -wb,  x <= c1 - wb
    Built once per N with cvxpy parameters so each month only updates data instead of recompiling.
    Sigma enters through its Cholesky factor (Sigma = L L'), so x' Sigma x = ||L' x||^2.
    """

    def __init__(self, n, c):
        self.wb = np.full(n, 1 / n)
        self.c = c
        self.x = cp.Variable(n)
        self.Lt = cp.Parameter((n, n))
        self.alpha = cp.Parameter(n)
        self.g = cp.Parameter()
        constraints = [
            self.x @ self.alpha >= self.g,
            cp.sum(self.x) == 0,
            self.x >= -self.wb,
            self.x <= c - self.wb,
        ]
        self.problem = cp.Problem(cp.Minimize(cp.sum_squares(self.Lt @ self.x)), constraints)

    def solve(self, Sigma, alpha, g):
        """Returns the active weights and whether the gain had to be lowered to the feasible maximum."""
        g_max = max_gain(alpha, self.wb, self.c)
        capped = g > g_max
        self.Lt.value = np.linalg.cholesky(Sigma).T
        self.alpha.value = alpha
        # If the target is out of reach this month, aim just below the maximum achievable gain
        self.g.value = min(g, g_max * (1 - 1e-4))
        self.problem.solve(solver=cp.CLARABEL)
        # Near the corner solution Clarabel can report 'optimal_inaccurate'; accept it only if the constraints hold
        assert self.problem.status in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE), self.problem.status
        x = self.x.value
        tol = 1e-6
        assert abs(x.sum()) < tol and np.all(x >= -self.wb - tol) and np.all(x <= self.c - self.wb + tol)
        assert x @ alpha >= self.g.value - tol
        return x, capped
