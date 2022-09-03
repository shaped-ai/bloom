package main

/*
#include <stdlib.h>
#include <string.h>

struct BloomFilter {
	unsigned int m;
    unsigned int k;
	unsigned int b_length;
	char *b;
};

// __attribute__((weak))
// void freeMemory(void *ptr) {
// 	free(ptr);
// }
*/
import "C"
import (
	"encoding/binary"
	"unsafe"

	"github.com/bits-and-blooms/bitset"
	"github.com/bits-and-blooms/bloom/v3"
)

func uint32ToBytes(number uint) []byte {
	a := make([]byte, 4)
	binary.LittleEndian.PutUint32(a, uint32(number))
	return a
}

func mallocBloomFilter() *C.struct_BloomFilter {
	const n = C.ulong(unsafe.Sizeof(C.struct_BloomFilter{}))
	p := C.malloc(n)
	C.memset(p, 0, n)
	return (*C.struct_BloomFilter)(p)
}

func deallocBloomFilter(p *C.struct_BloomFilter) {
	C.free(unsafe.Pointer(p))
	p = nil
}

//export NewWithEstimates
func NewWithEstimates(n uint, fp float64) *C.struct_BloomFilter {
	bloomFilterGo := bloom.NewWithEstimates(n, fp)

	cap := C.uint(bloomFilterGo.Cap())
	k := C.uint(bloomFilterGo.K())

	array, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		panic(err)
	}

	bLength := C.uint(uint(len(array)))
	cArray := C.CBytes(array)

	bfCPointer := mallocBloomFilter()
	bfCPointer.m = cap
	bfCPointer.k = k
	bfCPointer.b_length = bLength
	bfCPointer.b = (*C.char)(cArray)

	return bfCPointer
}

//export Add
func Add(bloomFilterC *C.struct_BloomFilter, data []byte) {
	array := bitset.BitSet{}
	myBitSetBytes := C.GoBytes(unsafe.Pointer(bloomFilterC.b), C.int(bloomFilterC.b_length))
	err := array.UnmarshalBinary(myBitSetBytes)
	if err != nil {
		panic(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bloomFilterC.m), uint(bloomFilterC.k))
	if err != nil {
		panic(err)
	}
	bloomFilterGo.Add(data)

	tmpArray, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		panic(err)
	}
	arrayC := C.CBytes(tmpArray)
	bloomFilterC.b = (*C.char)(arrayC)
}

//export AddListUint
func AddListUint(bloomFilterC *C.struct_BloomFilter, data []uint) {
	array := bitset.BitSet{}
	myBitSetBytes := C.GoBytes(unsafe.Pointer(bloomFilterC.b), C.int(bloomFilterC.b_length))
	err := array.UnmarshalBinary(myBitSetBytes)
	if err != nil {
		panic(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bloomFilterC.m), uint(bloomFilterC.k))
	if err != nil {
		panic(err)
	}

	for i := range data {
		element := uint32ToBytes(data[i])
		bloomFilterGo.Add(element)
	}

	tmpArray, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		panic(err)
	}
	cArray := C.CBytes(tmpArray)
	bloomFilterC.b = (*C.char)(cArray)
}

//export Test
func Test(bf_c *C.struct_BloomFilter, data []byte) bool {
	array := bitset.BitSet{}
	myBitSetBytes := C.GoBytes(unsafe.Pointer(bf_c.b), C.int(bf_c.b_length))
	err := array.UnmarshalBinary(myBitSetBytes)
	if err != nil {
		panic(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bf_c.m), uint(bf_c.k))
	if err != nil {
		panic(err)
	}

	return bloomFilterGo.Test(data)
}

//export TestListUint
func TestListUint(bf_c *C.struct_BloomFilter, data []uint) *C.char {
	array := bitset.BitSet{}
	myBitSetBytes := C.GoBytes(unsafe.Pointer(bf_c.b), C.int(bf_c.b_length))
	err := array.UnmarshalBinary(myBitSetBytes)
	if err != nil {
		panic(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bf_c.m), uint(bf_c.k))
	if err != nil {
		panic(err)
	}

	testResults := make([]byte, len(data))
	for i := range data {
		if bloomFilterGo.Test(uint32ToBytes(data[i])) {
			testResults[i] = 1
		}
	}
	return (*C.char)(C.CBytes(testResults))
}

func main() {}
