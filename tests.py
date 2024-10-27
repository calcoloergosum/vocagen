import vocagen

r1 = vocagen.ReversibleRandom(4771436933726426000)
v = r1.next()
assert v == 17231469391857590000, v
print(v)
r2 = vocagen.ReversibleRandom(v)
assert r1.next() == r2.next()
print(f"{r1.seed()}, {r2.seed()}")
