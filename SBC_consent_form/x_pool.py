import random

X_POOL_SIZE = 900
X_MIN = 0
X_MAX = 8
X_POOL_SEED = 20261016


def make_x_pool():
    # Each integer from 0 to 8 appears exactly 100 times
    values = list(range(X_MIN, X_MAX + 1)) * (
        X_POOL_SIZE // (X_MAX - X_MIN + 1)
    )

    # Shuffle reproducibly
    rng = random.Random(X_POOL_SEED)
    rng.shuffle(values)

    return values


X_POOL = make_x_pool()
