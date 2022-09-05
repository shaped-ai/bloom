import pickle
from typing import Optional, Union, List

from shaped_bloom_filter.binding import load_bloom_filter_dll
from shaped_bloom_filter.exceptions import (
    BloomFilterIncorrectConstructorValues,
    BloomFilterIncorrectInputException,
)


class BloomFilter:
    def __init__(
        self,
        max_elements: Optional[int] = None,
        error_rate: Optional[float] = None,
        restore_from_serialized: bytes = None,
    ):
        self._ffi, self._libbloomf = load_bloom_filter_dll()
        if max_elements and error_rate and restore_from_serialized:
            raise BloomFilterIncorrectConstructorValues(
                "either set max_elements and error_rate or set restore_from_serialized params"
            )
        if max_elements is not None and error_rate is not None:
            self._filter = self._libbloomf.NewWithEstimates(max_elements, error_rate)
        elif restore_from_serialized is not None:
            deserialized = pickle.loads(restore_from_serialized)

            m = deserialized["m"]
            k = deserialized["k"]
            b_length = deserialized["b_length"]
            b = deserialized["b"]

            data = self._ffi.new("GoUint8[]", list(b))
            go_slice = self._ffi.new(
                "GoSlice*",
                {
                    "data": self._ffi.cast("void*", data),
                    "len": b_length,
                    "cap": b_length,
                },
            )
            self._filter = self._libbloomf.NewFromSerialized(
                m, k, b_length, go_slice[0]
            )

            # # Create structure directly with ffi instead.
            # # Leads to an "Aborted (core dumped)" error for some reason.
            # backend_array = self._ffi.new("GoUint8[]", deserialized["b"])
            # cast_array = self._ffi.cast("char*", backend_array)
            # self._filter = self._ffi.new(
            #     "struct BloomFilter*",
            #     {
            #         "m": deserialized["m"],
            #         "k": deserialized["k"],
            #         "b_length": deserialized["b_length"],
            #         "b": cast_array,
            #     },
            # )
        else:
            raise BloomFilterIncorrectConstructorValues(
                "either set max_elements and error_rate or set restore_from_serialized params"
            )

    def add(self, var: int):
        self.add_batch([var])

    def add_batch(self, var: List[int]):
        data = self._ffi.new("GoUint[]", var)
        length = len(data)

        go_slice = self._ffi.new(
            "GoSlice*",
            {
                "data": self._ffi.cast("void*", data),
                "len": length,
                "cap": length,
            },
        )

        self._libbloomf.AddListUint(self._filter, go_slice[0])

    def is_member(self, var: int) -> bool:
        return self.are_members([var])[0]

    def are_members(self, var: List[int]) -> List[bool]:
        data = self._ffi.new("GoUint[]", var)
        length = len(var)

        go_slice = self._ffi.new(
            "GoSlice*",
            {
                "data": self._ffi.cast("void*", data),
                "len": length,
                "cap": length,
            },
        )

        out = self._libbloomf.TestListUint(self._filter, go_slice[0])
        try:
            unpacked = list(self._ffi.unpack(out, length))
        finally:
            self._libbloomf.free(self._ffi.cast("void*", out))
        return unpacked

    def serialize(self):
        serializable = {
            "m": self._filter.m,
            "k": self._filter.k,
            "b_length": self._filter.b_length,
            "b": self._ffi.unpack(self._filter.b, self._filter.b_length),
        }
        return pickle.dumps(serializable, protocol=pickle.HIGHEST_PROTOCOL)

    def __del__(self):
        if hasattr(self, "_filter"):
            cast_p1 = self._ffi.cast("void*", self._filter.b)
            cast_p2 = self._ffi.cast("void*", self._filter)
            self._libbloomf.free(cast_p1)
            self._libbloomf.free(cast_p2)


class BloomFilterExtended(BloomFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _check_input_type(self, var: Union[List[int], int, bytes]):
        if isinstance(var, list):
            # Assuming the list is composed of integer elements.
            # Checking its elements for their type is too much of an expensive procedure.
            data = self._ffi.new("GoUint8[]", var)
            length = len(data)
        elif isinstance(var, int):
            data = self._ffi.new("GoUint8[]", [var])
            length = 1
        elif isinstance(var, bytes):
            data = self._ffi.new("GoUint8[]", list(var))
            length = len(data)
        else:
            raise BloomFilterIncorrectInputException(
                "var must be a list of integers, an integer or a bytes object"
            )

        return data, length

    def add_one_member(self, var: Union[List[int], int, bytes]):
        data, length = self._check_input_type(var)
        go_slice = self._ffi.new(
            "GoSlice*",
            {
                "data": self._ffi.cast("void*", data),
                "len": length,
                "cap": length,
            },
        )
        self._libbloomf.Add(self._filter, go_slice[0])

    def is_one_member(self, var: Union[List[int], int, bytes]) -> bool:
        data, length = self._check_input_type(var)
        go_slice = self._ffi.new(
            "GoSlice*",
            {
                "data": self._ffi.cast("void*", data),
                "len": length,
                "cap": length,
            },
        )
        return self._libbloomf.Test(self._filter, go_slice[0])
