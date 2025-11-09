"""
disk_store module implements DiskStorage class which implements the KV store on the
disk

DiskStorage provides two simple operations to get and set key value pairs. Both key and
value needs to be of string type. All the data is persisted to disk. During startup,
DiskStorage loads all the existing KV pair metadata.  It will throw an error if the
file is invalid or corrupt.

Do note that if the database file is large, then the initialisation will take time
accordingly. The initialisation is also a blocking operation, till it is completed
the DB cannot be used.

Typical usage example:

    disk: DiskStorage = DiskStore(file_name="books.db")
    disk.set(key="othello", value="shakespeare")
    author: str = disk.get("othello")
    # it also supports dictionary style API too:
    disk["hamlet"] = "shakespeare"
"""

import os.path
import time
from dataclasses import dataclass

from pollen.format import HEADER_SIZE, decode_header, decode_kv, encode_kv

# DiskStorage is a Log-Structured Hash Table as described in the BitCask paper. We
# keep appending the data to a file, like a log. DiskStorage maintains an in-memory
# hash table called KeyDir, which keeps the row's location on the disk.
#
# The idea is simple yet brilliant:
#   - Write the record to the disk
#   - Update the internal hash table to point to that byte offset
#   - Whenever we get a read request, check the internal hash table for the address,
#       fetch that and return
#
# KeyDir does not store values, only their locations.
#
# The above approach solves a lot of problems:
#   - Writes are insanely fast since you are just appending to the file
#   - Reads are insanely fast since you do only one disk seek. In B-Tree backed
#       storage, there could be 2-3 disk seeks
#
# However, there are drawbacks too:
#   - We need to maintain an in-memory hash table KeyDir. A database with a large
#       number of keys would require more RAM
#   - Since we need to build the KeyDir at initialisation, it will affect the startup
#       time too
#   - Deleted keys need to be purged from the file to reduce the file size
#
# Read the paper for more details: https://riak.com/assets/bitcask-intro.pdf


@dataclass
class KeyEntry:
    timestamp: int
    position: int
    size: int


class DiskStorage:
    """
    Implements the KV store on the disk

    Args:
        file_name (str): name of the file where all the data will be written. Just
            passing the file name will save the data in the current directory. You may
            pass the full file location too.
    """

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.key_dir: dict[str, KeyEntry] = {}
        self.write_position: int = 0
        if os.path.exists(file_name):
            self._init_key_dir()

        try:
            self.file = open(self.file_name, mode="a+b")
        except OSError as ex:
            raise ValueError(f'Failed to open "{file_name}"') from ex

    def _write(self, data: bytes) -> None:
        self.file.write(data)
        self.file.flush()
        os.fsync(self.file.fileno())

    def list(self) -> list[str]:
        return list(self.key_dir.keys())

    def _init_key_dir(self) -> None:
        print(f"--- loading DB from {self.file_name} ---")
        with open(self.file_name, "rb") as f:
            while header_bytes := f.read(HEADER_SIZE):
                timestamp, key_size, value_size = decode_header(data=header_bytes)
                key_bytes = f.read(key_size)
                f.seek(value_size, 1)
                key = key_bytes.decode("utf-8")
                total_size = HEADER_SIZE + key_size + value_size
                kv = KeyEntry(
                    timestamp=timestamp,
                    position=self.write_position,
                    size=total_size,
                )
                self.key_dir[key] = kv
                self.write_position += total_size
        print(f"--- loaded {len(self.key_dir):,} keys ---")

    def set(self, key: str, value: str) -> None:
        ts = int(time.time())
        size, data = encode_kv(ts, key, value)
        self._write(data)
        self.key_dir[key] = KeyEntry(ts, self.write_position, size)
        self.write_position += size

    def get(self, key: str) -> str:
        entry = self.key_dir.get(key)
        if not entry:
            return ""
        self.file.seek(entry.position)
        ts, key, value = decode_kv(self.file.read(entry.size))
        return value

    def remove(self, key: str) -> None:
        if key in self.key_dir:
            # overwrite with empty value on disk
            self.set(key, "")
            # remove from in-memory storage
            del self.key_dir[key]

    def close(self) -> None:
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def __getitem__(self, item: str) -> str:
        return self.get(item)
