Bloom filters
-------------
[![PyPI version](https://badge.fury.io/py/shaped-bloom-filter.svg)](https://badge.fury.io/py/shaped-bloom-filter)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/shaped-ai/bloom/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/shaped-ai/bloom/tree/master)

## Source project & considerations

This implementation of the Bloom filter is ported from the https://github.com/bits-and-blooms/bloom ([![Test](https://github.com/bits-and-blooms/bloom/actions/workflows/test.yml/badge.svg)](https://github.com/bits-and-blooms/bloom/actions/workflows/test.yml)
[![Go Report Card](https://goreportcard.com/badge/github.com/bits-and-blooms/bloom)](https://goreportcard.com/report/github.com/bits-and-blooms/bloom)
[![Go Reference](https://pkg.go.dev/badge/github.com/bits-and-blooms/bloom.svg)](https://pkg.go.dev/github.com/bits-and-blooms/bloom/v3)) project. The reason for porting this project from Go is due to the fact that there are no high-performance implementations of the Bloom filter in Python. All Bloom filter packages we found on PyPi are just too slow for our real-time inference pipeline.

The Godoc documentation of the ported library can be found here: https://pkg.go.dev/github.com/bits-and-blooms/bloom/v3

## Benchmark

The following PyPi libraries have been benchmarked on a filter configuration of 1 mil elements and an error rate of 1%. The following shows the time needed to evaluate all elements. These are the results of running the benchmark on an Apple M1 chip. The clear winner is this library.

```text
           shaped-bloom-filter  bloom-filter2  fastbloom-rs  easy-bloom-filter
count               100.000000     100.000000    100.000000         100.000000
mean (ms)            62.859311    2508.295782    464.162710        2201.442912
std (ms)              2.300990      25.811489      6.834798          19.279795
min (ms)             61.051130    2488.384008    457.671881        2177.664995
25% (ms)             61.701119    2496.009886    459.175646        2190.251410
50% (ms)             62.229514    2502.063990    462.151527        2196.185470
75% (ms)             63.203335    2506.640196    466.094494        2205.390155
max (ms)             76.441765    2666.959047    485.892057        2307.396173
speedup               1.000000      39.903329      7.384152          35.021747
```

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
filter = BloomFilter(1000000, 0.01)
```

Operations like the following can be done:

```python
# single member addition
assert filter.is_member(10) == False
filter.add(10)
assert filter.is_member(10) == True

# multiple member addition
assert filter.are_members([1, 5, 9]) == [0, 0, 0]
filter.add_batch([5, 9])
assert filter.are_members([1, 5, 9]) == [0, 1, 1]

# serialization
serialized = filter.serialize()
new_filter = BloomFilter(restore_from_serialized=serialized)
assert new_filter.are_members([1, 5, 9]) == [0, 1, 1]
```

For composing your own keys using Python-serializable objects, you can use the following method:

```python
from shaped_bloom_filter import BloomFilterExtended
filter = BloomFilterExtended(1000000, 0.01)

assert filter.is_one_member("Emma is writing a letter.".encode("utf-8")) == False
filter.add_one_member("Emma is writing a letter.".encode("utf-8"))
assert filter.is_one_member("Emma is writing a letter.".encode("utf-8")) == True
```

You should call the `BloomFilter`/`BloomFilterExtended` constructors conservatively: if you specify a number of elements that it is
too small, the false-positive bound might be exceeded. A Bloom filter is not a dynamic data structure:
you must know ahead of time what your desired capacity is.

## Installation

```bash
pip install shaped-bloom-filter
```

***Note: On MacOS/Windows machines, you also need Go as the Python package will be built from source.***

## Reference

<!-- markdownlint-disable -->

<a href="python/shaped_bloom_filter/filter.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>module</kbd> `filter.py`

---

#### <kbd>class</kbd> `BloomFilter`


<a href="python/shaped_bloom_filter/filter.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `__init__`

```python
__init__(
    max_elements: Optional[int] = None,
    error_rate: Optional[float] = None,
    restore_from_serialized: bytes = None
)
```

---

<a href="python/shaped_bloom_filter/filter.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `add`

```python
add(var: int)
```

Add a single 32-bit integer key to the filter. 

---

<a href="python/shaped_bloom_filter/filter.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `add_batch`

```python
add_batch(var: List[int])
```

Add a list of 32-bit integer keys to the filter. 

---

<a href="python/shaped_bloom_filter/filter.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `are_members`

```python
are_members(var: List[int]) → List[bool]
```

Check if a given list of 32-bit integer keys have been set. A boolean list is returned. 

---

<a href="python/shaped_bloom_filter/filter.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `is_member`

```python
is_member(var: int) → bool
```

Check if a given 32-bit integer key has been set. 

---

<a href="python/shaped_bloom_filter/filter.py#L104"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `serialize`

```python
serialize() → bytes
```

Serialize the filter for storing purposes. To restore it, pass the returned bytes into the constructor's restore_from_serialized parameter. 


---

<a href="python/shaped_bloom_filter/filter.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `__contains__`

```python
__contains__(var: int) → bool
```

Check if a given 32-bit integer key has been set.


---

#### <kbd>class</kbd> `BloomFilterExtended(BloomFilter)`


<a href="python/shaped_bloom_filter/filter.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>


##### <kbd>function</kbd> `add_one_member`

```python
add_one_member(var: Union[List[int], int, bytes])
```

Add a single key to the filter. Examples of keys: serialized Python objects, strings, 64-digit integers, etc. 

---

<a href="python/shaped_bloom_filter/filter.py#L170"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

##### <kbd>function</kbd> `is_one_member`

```python
is_one_member(var: Union[List[int], int, bytes]) → bool
```

Check if a single key has been set. Examples of keys: serialized Python objects, strings, 64-digit integers, etc. 

---

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
