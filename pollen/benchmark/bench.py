import random
import string
import time


def bench(store, iterations):
    KB = 2**10
    SIZES = [KB, 5 * KB, 100 * KB, KB]
    data = [str(random.randbytes(s)) for s in SIZES]
    keys = ["".join(random.choices(string.ascii_letters)) for _ in range(iterations)]
    start = time.perf_counter()
    for i in range(iterations):
        key = keys[i % len(keys)]
        value = data[i % len(data)]
        store.set(key, value)
    dt = time.perf_counter() - start
    print(f"Time: {dt:.2f}s")
    print(f"Iterations: {iterations:,}")
    print(f"Sizes: {SIZES}")
    print(f"   Ops/sec (SET): {iterations / dt:,.0f}")
