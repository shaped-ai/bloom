import pytest
import random

from shaped_bloom_filter import BloomFilter, BloomFilterExtended
from shaped_bloom_filter.exceptions import (
    BloomFilterIncorrectConstructorValues,
    BloomFilterIncorrectInputException,
)


def default_parametrized_bloom_filter(max_elements=10, error_rate=0.01):
    return BloomFilter(
        max_elements=max_elements,
        error_rate=error_rate,
    )


def default_parametrized_bloom_filter_extended():
    return BloomFilterExtended(
        max_elements=10,
        error_rate=0.01,
    )


def test_bloom_filter_creation_no_args():
    with pytest.raises(BloomFilterIncorrectConstructorValues):
        BloomFilter()


def test_bloom_filter_creation_all_args():
    with pytest.raises(BloomFilterIncorrectConstructorValues):
        BloomFilter(
            max_elements=10,
            error_rate=0.01,
            restore_from_serialized=bytes([0, 1, 2, 3]),
        )


def test_bloom_filter_creation_params():
    default_parametrized_bloom_filter()


def test_bloom_filter_creation_serialized():
    bf = default_parametrized_bloom_filter()
    serialized = bf.serialize()

    new_bf = BloomFilter(restore_from_serialized=serialized)
    new_serialized = new_bf.serialize()

    assert serialized == new_serialized


def test_bloom_filter_add():
    bf = default_parametrized_bloom_filter()
    bf.add(3)


def test_bloom_filter_is_member():
    bf = default_parametrized_bloom_filter()
    assert bf.is_member(3) == False
    bf.add(3)
    assert bf.is_member(3) == True


def test_bloom_filter_add_batch():
    bf = default_parametrized_bloom_filter()
    bf.add_batch([1, 5, 6])


def test_bloom_filter_are_members():
    bf = default_parametrized_bloom_filter()
    assert any(bf.are_members(list(range(10)))) == False
    bf.add_batch([1, 5, 6])
    assert bf.are_members(list(range(10))) == [0, 1, 0, 0, 0, 1, 1, 0, 0, 0]


def test_bloom_filter_serialized_members():
    bf = default_parametrized_bloom_filter()
    bf.add_batch([1, 5, 6])
    serialized = bf.serialize()

    new_bf = BloomFilter(restore_from_serialized=serialized)
    assert new_bf.are_members(list(range(10))) == [0, 1, 0, 0, 0, 1, 1, 0, 0, 0]


def test_bloom_filter_extended_add_one_member_bad_input():
    bf = default_parametrized_bloom_filter_extended()
    with pytest.raises(BloomFilterIncorrectInputException):
        bf.add_one_member("some random string")


def test_bloom_filter_extended_add_one_member_overflow_error():
    bf = default_parametrized_bloom_filter_extended()
    with pytest.raises(OverflowError):
        bf.add_one_member(256)
    with pytest.raises(OverflowError):
        bf.add_one_member([256])


def test_bloom_filter_extended_add_one_member():
    bf = default_parametrized_bloom_filter_extended()
    bf.add_one_member([0, 5, 128])


def test_bloom_filter_extended_is_one_member():
    bf = default_parametrized_bloom_filter_extended()
    assert bf.is_one_member([0, 0, 0]) == False
    bf.add_one_member([0, 5, 128])
    assert bf.is_one_member([0, 5, 128]) == True


def test_bloom_filter_extended_multiple_addition_asserts():
    bf = default_parametrized_bloom_filter_extended()
    members_to_add = [0, 5, 9]
    members_to_test = list(range(10))

    for member in members_to_add:
        bf.add_one_member(member)

    for member in members_to_test:
        result = bf.is_one_member(member)
        if member in members_to_add:
            assert result == True, f"member {member} not found to be set"
        else:
            assert result == False, f"member {member} was set"
