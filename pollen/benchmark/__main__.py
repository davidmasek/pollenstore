import os

from pollen.benchmark.bench import bench
from pollen.disk_store import DiskStorage
from pollen.memory_store import MemoryStorage

if __name__ == "__main__":
    print("--- Memory Storage ---")
    iterations = 100_000
    store = MemoryStorage()
    bench(store, iterations)

    print("--- Disk Storage ---")
    iterations = 1_000
    file_path = "temp.db"
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    store = DiskStorage(file_path)
    bench(store, iterations)
