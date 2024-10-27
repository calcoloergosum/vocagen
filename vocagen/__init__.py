"""Reversible Linear Congruential Generator; Credit to the following link:
https://stackoverflow.com/questions/62797012/how-to-generate-8-bytes-unique-random-number-in-python
"""
import numpy as np


class ReversibleRandom:
    UZERO: np.uint64 = np.uint64(0)
    UONE : np.uint64 = np.uint64(1)

    def __init__(self, seed: np.uint64,) -> None:
        self._seed: np.uint64 = np.uint64(seed)
        self._a   : np.uint64 = np.uint64(6364136223846793005)
        self._a_inv: np.uint64 = np.uint64(13877824140714322085)
        self._c   : np.uint64 = self.UONE

    def next(self) -> np.uint64:
        self._seed = self._a * self._seed + self._c
        return self._seed

    def prev(self) -> np.uint64:
        self._seed = self._a_inv * (self._seed - self._c)
        return self._seed

    def seed(self) -> np.uint64:
        return self._seed

    def set_seed(self, seed: np.uint64) -> np.uint64:
        self._seed = seed

    def skip(self, ns: np.int64) -> None:
        """
        Signed argument - skip forward as well as backward

        The algorithm here to determine the parameters used to skip ahead is
        described in the paper F. Brown, "Random Number Generation with Arbitrary Stride,"
        Trans. Am. Nucl. Soc. (Nov. 1994). This algorithm is able to skip ahead in
        O(log2(N)) operations instead of O(N). It computes parameters
        A and C which can then be used to find x_N = A*x_0 + C mod 2^M.
        """

        nskip: np.uint64 = np.uint64(ns)

        a: np.uint64 = self._a
        c: np.uint64 = self._c

        a_next: np.uint64 = LCG.UONE
        c_next: np.uint64 = LCG.UZERO

        while nskip > LCG.UZERO:
            if (nskip & LCG.UONE) != LCG.UZERO:
                a_next = a_next * a
                c_next = c_next * a + c

            c = (a + LCG.UONE) * c
            a = a * a

            nskip = nskip >> LCG.UONE

        self._seed = a_next * self._seed + c_next
