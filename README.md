Bloom filters
-------------
[![PyPI version](https://badge.fury.io/py/shaped-bloom-filter.svg)](https://badge.fury.io/py/shaped-bloom-filter)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/shaped-ai/bloom/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/shaped-ai/bloom/tree/master)

## Source project & considerations

This implementation of the Bloom filter is ported from the https://github.com/bits-and-blooms/bloom ([![Test](https://github.com/bits-and-blooms/bloom/actions/workflows/test.yml/badge.svg)](https://github.com/bits-and-blooms/bloom/actions/workflows/test.yml)
[![Go Report Card](https://goreportcard.com/badge/github.com/bits-and-blooms/bloom)](https://goreportcard.com/report/github.com/bits-and-blooms/bloom)
[![Go Reference](https://pkg.go.dev/badge/github.com/bits-and-blooms/bloom.svg)](https://pkg.go.dev/github.com/bits-and-blooms/bloom/v3)) project. The reason for porting this project from Go is due to the fact that there are no high-performance implementations of the Bloom filter in Python. All Bloom filter packages we found on PyPi are written in pure Python and are just too slow for our real-time inference pipeline. We measured this implementation to be 60x faster than what we have gotten with the other libraries.

## Description

A Bloom filter is a concise/compressed representation of a set, where the main
requirement is to make membership queries; _i.e._, whether an item is a
member of a set. A Bloom filter will always correctly report the presence
of an element in the set when the element is indeed present. A Bloom filter 
can use much less storage than the original set, but it allows for some 'false positives':
it may sometimes report that an element is in the set whereas it is not.

When you construct, you need to know how many elements you have (the desired capacity), and what is the desired false positive rate you are willing to tolerate. A common false-positive rate is 1%. The
lower the false-positive rate, the more memory you are going to require. Similarly, the higher the
capacity, the more memory you will use.
You may construct the Bloom filter capable of receiving 1 million elements with a false-positive
rate of 1% in the following manner. 

```python
from shaped_bloom_filter import BloomFilter
filter := BloomFilter(1000000, 0.01) 
```

You should call the `BloomFilter` constructor conservatively: if you specify a number of elements that it is
too small, the false-positive bound might be exceeded. A Bloom filter is not a dynamic data structure:
you must know ahead of time what your desired capacity is.

Godoc documentation:  https://pkg.go.dev/github.com/bits-and-blooms/bloom/v3 

## Installation

```bash
pip install shaped-bloom-filter
```

***Note: On MacOS/Windows machines, you also need Go as the Python package will be built from source.***

## Reference

<!-- markdownlint-disable -->

<a href="../python/shaped_bloom_filter/filter.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>module</kbd> `filter.py`

---

#### <kbd>class</kbd> `BloomFilter`


<a href="../python/shaped_bloom_filter/filter.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `__init__`

```python
__init__(
    max_elements: Optional[int] = None,
    error_rate: Optional[float] = None,
    restore_from_serialized: bytes = None
)
```

---

<a href="../python/shaped_bloom_filter/filter.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `add`

```python
add(var: int)
```

Add a single 32-bit integer key to the filter. 

---

<a href="../python/shaped_bloom_filter/filter.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `add_batch`

```python
add_batch(var: List[int])
```

Add a list of 32-bit integer keys to the filter. 

---

<a href="../python/shaped_bloom_filter/filter.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `are_members`

```python
are_members(var: List[int]) → List[bool]
```

Check if a given list of 32-bit integer keys have been set. A boolean list is returned. 

---

<a href="../python/shaped_bloom_filter/filter.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `is_member`

```python
is_member(var: int) → bool
```

Check if a given 32-bit integer key has been set. 

---

<a href="../python/shaped_bloom_filter/filter.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `serialize`

```python
serialize() → bytes
```

Serialize the filter for storing purposes. To restore it, pass the returned bytes into the constructor's restore_from_serialized parameter. 


---

#### <kbd>class</kbd> `BloomFilterExtended(BloomFilter)`


##### <kbd>function</kbd> `add_one_member`

```python
add_one_member(var: Union[List[int], int, bytes])
```

Add a single key to the filter. Examples of keys: serialized Python objects, strings, 64-digit integers, etc. 

---

##### <kbd>function</kbd> `is_one_member`

```python
is_one_member(var: Union[List[int], int, bytes]) → bool
```

Check if a single key has been set. Examples of keys: serialized Python objects, strings, 64-digit integers, etc. 

---

<a href="../python/shaped_bloom_filter/filter.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

## Contributing

If you wish to contribute to this project, please branch and issue a pull request against master ("[GitHub Flow](https://guides.github.com/introduction/flow/)")

This project includes a Makefile that allows you to test and build the project with simple commands.
To see all available options:
```bash
make help
```

## Running all tests

Before committing the code, please check if it passes all tests using (note: this will install some dependencies):
```bash
make python-environment
make python-build
make python-install
make python-tests
```

## Design

A Bloom filter has two parameters: _m_, the number of bits used in storage, and _k_, the number of hashing functions on elements of the set. (The actual hashing functions are important, too, but this is not a parameter for this implementation). A Bloom filter is backed by a [BitSet](https://github.com/bits-and-blooms/bitset); a key is represented in the filter by setting the bits at each value of the  hashing functions (modulo _m_). Set membership is done by _testing_ whether the bits at each value of the hashing functions (again, modulo _m_) are set. If so, the item is in the set. If the item is actually in the set, a Bloom filter will never fail (the true positive rate is 1.0); but it is susceptible to false positives. The art is to choose _k_ and _m_ correctly.

In this implementation, the hashing functions used is [murmurhash](github.com/twmb/murmur3), a non-cryptographic hashing function.


Given the particular hashing scheme, it's best to be empirical about this. Note
that estimating the FP rate will clear the Bloom filter.
