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
*/
import "C"
import (
	"encoding/binary"
	"fmt"
	"os"
	"unsafe"

	"github.com/bits-and-blooms/bitset"
	"github.com/bits-and-blooms/bloom/v3"
)

func printStacktraceAndExit(err error) {
	fmt.Printf("%+v\n", err)
	os.Exit(1)
}

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

//export NewFromSerialized
func NewFromSerialized(m uint, k uint, b_length uint, data []uint8) *C.struct_BloomFilter {
	mC := C.uint(m)
	kC := C.uint(k)
	bLengthC := C.uint(b_length)
	cArray := C.CBytes(data)

	bfCPointer := mallocBloomFilter()
	bfCPointer.m = mC
	bfCPointer.k = kC
	bfCPointer.b_length = bLengthC
	bfCPointer.b = (*C.char)(cArray)

	return bfCPointer
}

//export NewWithEstimates
func NewWithEstimates(n uint, fp float64) *C.struct_BloomFilter {
	bloomFilterGo := bloom.NewWithEstimates(n, fp)

	cap := C.uint(bloomFilterGo.Cap())
	k := C.uint(bloomFilterGo.K())

	array, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		printStacktraceAndExit(err)
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
		printStacktraceAndExit(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bloomFilterC.m), uint(bloomFilterC.k))
	if err != nil {
		printStacktraceAndExit(err)
	}
	bloomFilterGo.Add(data)

	tmpArray, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		printStacktraceAndExit(err)
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
		printStacktraceAndExit(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bloomFilterC.m), uint(bloomFilterC.k))
	if err != nil {
		printStacktraceAndExit(err)
	}

	for i := range data {
		element := uint32ToBytes(data[i])
		bloomFilterGo.Add(element)
	}

	tmpArray, err := bloomFilterGo.BitSet().MarshalBinary()
	if err != nil {
		printStacktraceAndExit(err)
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
		printStacktraceAndExit(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bf_c.m), uint(bf_c.k))
	if err != nil {
		printStacktraceAndExit(err)
	}

	return bloomFilterGo.Test(data)
}

//export TestListUint
func TestListUint(bf_c *C.struct_BloomFilter, data []uint) *C.char {
	array := bitset.BitSet{}
	myBitSetBytes := C.GoBytes(unsafe.Pointer(bf_c.b), C.int(bf_c.b_length))
	err := array.UnmarshalBinary(myBitSetBytes)
	if err != nil {
		printStacktraceAndExit(err)
	}

	bloomFilterGo, err := bloom.FromWithMAndBytes(myBitSetBytes, uint(bf_c.m), uint(bf_c.k))
	if err != nil {
		printStacktraceAndExit(err)
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
