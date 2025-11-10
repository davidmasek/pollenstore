import os
import tempfile
from typing import Iterator

import pytest

from pollen.disk_store import DiskStorage


@pytest.fixture(scope="function")
def temp_db_path() -> Iterator[str]:
    """
    Uses tempfile.mkstemp (instead of tempfile.TemporaryFile) for persistent files.
    """
    fd, path = tempfile.mkstemp()
    os.close(fd)

    yield path

    os.remove(path)


def test_get(temp_db_path: str) -> None:
    """Test basic get/set functionality."""
    store = DiskStorage(file_name=temp_db_path)
    store.set("name", "jojo")
    assert store.get("name") == "jojo"
    store.close()

    # check persistence
    store = DiskStorage(file_name=temp_db_path)
    assert store.get("name") == "jojo"
    store.close()

def test_remove(temp_db_path: str) -> None:
    store = DiskStorage(file_name=temp_db_path)
    store.set("name", "jojo")
    store.remove("name")
    assert store.get("name") == ""
    store.close()

    # check persistence
    store = DiskStorage(file_name=temp_db_path)
    assert store.get("name") == ""
    store.close()


def test_list(temp_db_path: str) -> None:
    store = DiskStorage(file_name=temp_db_path)
    store.set("alpha", "xyz")
    store.set("beta", "xyz")
    store.set("alpha", "foo")
    assert set(store.list()) == {"alpha", "beta"}
    store.remove("alpha")
    assert set(store.list()) == {"beta"}
    store.close()

    # check persistence
    store = DiskStorage(file_name=temp_db_path)
    assert set(store.list()) == {"beta"}
    store.close()


def test_missing_key(temp_db_path: str) -> None:
    """Test getting a non-existent key returns an empty string."""
    store = DiskStorage(file_name=temp_db_path)
    assert store.get("some key") == ""
    store.close()


def test_dict_api(temp_db_path: str) -> None:
    """Test the dictionary-style __getitem__ and __setitem__."""
    store = DiskStorage(file_name=temp_db_path)
    store["name"] = "jojo"
    assert store["name"] == "jojo"
    store.close()


def test_persistence(temp_db_path: str) -> None:
    """Test that data persists after closing and reopening the store."""
    store = DiskStorage(file_name=temp_db_path)

    tests = {
        "crime and punishment": "dostoevsky",
        "anna karenina": "tolstoy",
        "war and peace": "tolstoy",
        "hamlet": "shakespeare",
        "othello": "shakespeare",
        "brave new world": "huxley",
        "dune": "frank herbert",
    }
    for k, v in tests.items():
        store.set(k, v)
        assert store.get(k) == v
    store.close()

    # Reopen the store to check for persistence
    store = DiskStorage(file_name=temp_db_path)
    for k, v in tests.items():
        assert store.get(k) == v
    store.close()
