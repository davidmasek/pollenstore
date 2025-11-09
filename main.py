import random
import string

from pollen.disk_store import DiskStorage


def generate_data():
    for _ in range(2000):
        how_many = random.randint(1, 200)
        key = "".join(random.choices(string.ascii_lowercase, k=8))
        val = "".join(random.choices(string.ascii_letters, k=how_many * 2**10))
        ds.set(key, val)


if __name__ == "__main__":
    ds = DiskStorage()
