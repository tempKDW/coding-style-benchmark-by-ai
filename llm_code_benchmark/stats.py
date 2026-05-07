"""Statistical helpers for comparing benchmark runs.

Zero external deps — uses only stdlib (random, math). Methods chosen for
faithful, simple implementation and robustness on small N (≤30):

- bootstrap_ci: percentile bootstrap CI for the mean
- paired_permutation_test: exhaustive sign-flip test for n ≤ 16, random
  sampling otherwise. Two-sided p-value on the mean paired difference.
"""
from __future__ import annotations
import random


def bootstrap_ci(
    values: list[float],
    n_iter: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Percentile bootstrap CI for the mean.

    Returns (lo, hi, observed_mean) at confidence level 1-alpha.
    """
    if not values:
        return (0.0, 0.0, 0.0)
    n = len(values)
    observed = sum(values) / n
    if n == 1:
        return (observed, observed, observed)
    rng = random.Random(seed)
    means = []
    for _ in range(n_iter):
        sample_sum = 0.0
        for _ in range(n):
            sample_sum += values[rng.randrange(n)]
        means.append(sample_sum / n)
    means.sort()
    lo_idx = int(n_iter * (alpha / 2))
    hi_idx = int(n_iter * (1 - alpha / 2)) - 1
    return (means[lo_idx], means[hi_idx], observed)


def paired_permutation_test(
    a: list[float],
    b: list[float],
    n_iter: int = 10000,
    seed: int = 42,
) -> tuple[float, float]:
    """Two-sided paired permutation (sign-flip) test on the mean difference.

    Returns (observed_mean_diff, p_value). Diff is computed as a - b.
    For n ≤ 16 enumerates all 2^n sign assignments exhaustively; for larger
    n, draws n_iter random sign assignments. p-value is the fraction of
    permutations with abs(mean_diff) ≥ abs(observed).
    """
    if len(a) != len(b):
        raise ValueError("a and b must have equal length")
    n = len(a)
    if n == 0:
        return (0.0, 1.0)
    diffs = [ai - bi for ai, bi in zip(a, b)]
    observed = sum(diffs) / n
    abs_obs = abs(observed)
    eps = 1e-12

    if n <= 16:
        total = 1 << n
        count_extreme = 0
        for mask in range(total):
            s = 0.0
            for i in range(n):
                s += -diffs[i] if (mask >> i) & 1 else diffs[i]
            if abs(s / n) >= abs_obs - eps:
                count_extreme += 1
        return (observed, count_extreme / total)

    rng = random.Random(seed)
    count_extreme = 0
    for _ in range(n_iter):
        s = 0.0
        for i in range(n):
            s += diffs[i] if rng.random() < 0.5 else -diffs[i]
        if abs(s / n) >= abs_obs - eps:
            count_extreme += 1
    return (observed, count_extreme / n_iter)


def cohen_dz(a: list[float], b: list[float]) -> float:
    """Paired Cohen's dz = mean(diff) / stdev(diff). 0.2/0.5/0.8 ≈ small/med/large.

    Returns 0.0 if stdev is 0 or n < 2.
    """
    if len(a) != len(b) or len(a) < 2:
        return 0.0
    diffs = [ai - bi for ai, bi in zip(a, b)]
    n = len(diffs)
    m = sum(diffs) / n
    var = sum((d - m) ** 2 for d in diffs) / (n - 1)
    if var <= 0:
        return 0.0
    return m / (var ** 0.5)
