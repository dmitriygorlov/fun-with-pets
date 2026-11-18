import math


def validate(p, n):
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("Probability must be between 0 and 1")
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("Trials must be a non-negative integer")


def cumulative(p, n):
    validate(p, n)
    if n == 0 or p == 0:
        return 0.0
    if p == 1:
        return 1.0
    return -math.expm1(n * math.log1p(-p))


def trials_for_95(p):
    validate(p, 1)
    if p == 0:
        return math.inf
    if p == 1:
        return 1
    return math.ceil(math.log(0.05) / math.log1p(-p))


def fraction(numerator, denominator):
    if denominator <= 0 or not 0 <= numerator <= denominator:
        raise ValueError("Wins must be between zero and total trials")
    result = numerator / denominator
    validate(result, 1)
    return result
