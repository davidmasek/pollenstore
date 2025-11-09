import random
import struct
import time
import typing
import uuid

import pytest

from pollen.format import (
    HEADER_SIZE,
    decode_header,
    decode_kv,
    encode_header,
    encode_kv,
)


def get_random_header() -> tuple[int, int, int]:
    max_size: int = (2**32) - 1

    def random_int() -> int:
        return random.randint(0, max_size)

    return random_int(), random_int(), random_int()


def get_random_kv() -> tuple[int, str, str, int]:
    return (
        int(time.time()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        HEADER_SIZE + (2 * len(str(uuid.uuid4()))),
    )


class Header(typing.NamedTuple):
    timestamp: int
    key_size: int
    val_size: int


class KeyValue(typing.NamedTuple):
    timestamp: int
    key: str
    val: str
    sz: int


class TestHeaderOp:
    def header_test(self, tt: Header) -> None:
        data = encode_header(tt.timestamp, tt.key_size, tt.val_size)
        t, k, v = decode_header(data)
        assert tt.timestamp == t
        assert tt.key_size == k
        assert tt.val_size == v

    @pytest.mark.parametrize(
        "tt",
        [
            Header(10, 10, 10),
            Header(0, 0, 0),
            Header(10000, 10000, 10000),
        ],
    )
    def test_header_serialisation(self, tt: Header) -> None:
        self.header_test(tt)

    def test_random(self) -> None:
        for _ in range(100):
            tt = Header(*get_random_header())
            self.header_test(tt)

    @pytest.mark.parametrize(
        "args",
        [
            (2**32, 5, 5),
            (5, 2**32, 5),
            (5, 5, 2**32),
        ],
    )
    def test_bad(self, args: tuple[int, int, int]) -> None:
        with pytest.raises(struct.error):
            encode_header(*args)


class TestEncodeKV:
    def kv_test(self, tt: KeyValue) -> None:
        sz, data = encode_kv(tt.timestamp, tt.key, tt.val)
        t, k, v = decode_kv(data)
        assert tt.timestamp == t
        assert tt.key == k
        assert tt.val == v
        assert tt.sz == sz

    @pytest.mark.parametrize(
        "tt",
        [
            KeyValue(10, "hello", "world", HEADER_SIZE + 10),
            KeyValue(0, "", "", HEADER_SIZE),
        ],
    )
    def test_KV_serialisation(self, tt: KeyValue) -> None:
        self.kv_test(tt)

    def test_random(self) -> None:
        for _ in range(100):
            tt = KeyValue(*get_random_kv())
            self.kv_test(tt)
