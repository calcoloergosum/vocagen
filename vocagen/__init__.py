"""Reversible Linear Congruential Generator; Credit to the following link:
https://stackoverflow.com/questions/62797012/how-to-generate-8-bytes-unique-random-number-in-python
"""
import numpy as np
import numba as nb


@nb.jit
def next_(seed: np.uint64, a: np.uint64, c: np.uint64) -> np.uint64:
    return a * seed + c


@nb.jit
def prev(seed: np.uint64, a_inv: np.uint64, c: np.uint64) -> np.uint64:
    return a_inv * (seed - c)


class ReversibleRandom:
    UZERO: np.uint64 = np.uint64(0)
    UONE : np.uint64 = np.uint64(1)

    A   : np.uint64 = np.uint64(6364136223846793005)
    A_inv: np.uint64 = np.uint64(13877824140714322085)
    C: np.uint64 = UONE

    def __init__(self, seed: np.uint64,) -> None:
        self._seed: np.uint64 = np.uint64(seed)

    def next(self) -> np.uint64:
        self._seed = next_(self._seed, self.A, self.C)
        return self._seed

    def prev(self) -> np.uint64:
        self._seed = prev(self._seed, self.A_inv, self.C)
        return self._seed

    def seed(self) -> np.uint64:
        return self._seed

    def set_seed(self, seed: np.uint64) -> np.uint64:
        self._seed = seed
