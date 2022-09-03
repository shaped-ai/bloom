import cffi

ffi = cffi.FFI()

# ffi.cdef("""
# typedef struct {
#     void* data;
#     GoInt len;
#     GoInt cap;
# } GoSlice;

# typedef struct {
#     const char *data;
#     GoInt len;
# } GoString;

# GoInt Add(GoInt a, GoInt b);
# double Cosine(double v);
# void Sort(GoSlice values);
# GoInt Log(GoString str);
# """)

ffi.cdef(
    """
typedef double GoFloat64;
typedef unsigned long long GoUint64;
typedef long long GoInt64;

typedef unsigned char GoUint8;
typedef GoUint64 GoUint;
typedef GoInt64 GoInt;
typedef size_t GoUintptr;

typedef void *GoMap;
typedef void *GoChan;

struct BloomFilter {
	unsigned int m;
    unsigned int k;
	unsigned int b_length;
	char *b;
};

typedef struct { 
    void *t;
    void *v;
} GoInterface;

typedef struct {
    void *data;
    GoInt len;
    GoInt cap;
} GoSlice;

extern struct BloomFilter* NewWithEstimates(GoUint n, GoFloat64 fp);
extern void Add(struct BloomFilter* bf_c, GoSlice data);
extern void AddListUint(struct BloomFilter* bf_c, GoSlice data);
extern GoUint8 Test(struct BloomFilter* bf_c, GoSlice data);
extern char* TestListUint(struct BloomFilter* bf_c, GoSlice data);
extern void free(void *ptr);
"""
)


def get_dll():
    lib = ffi.dlopen(
        "/home/ubuntu/.conda/envs/bloom/lib/python3.9/site-packages/shaped_bloom_filter/libbloomf.cpython-39-x86_64-linux-gnu.so"
    )
    return lib


lib = get_dll()

bloom = lib.NewWithEstimates(10, 0.01)
print(bloom.m, bloom.k, bloom.b_length, ffi.unpack(bloom.b, bloom.b_length))

data = ffi.new("GoUint8[]", ffi.unpack(bloom.b, bloom.b_length))
newf = ffi.new(
    "struct BloomFilter*",
    {
        "m": bloom.m,
        "k": bloom.k,
        "b_length": bloom.b_length,
        "b": ffi.cast("char*", data),
    },
)
print(newf.m, newf.k, newf.b_length, ffi.unpack(newf.b, newf.b_length))

# data = ffi.new("GoUint8[]", [15, 30, 50])
# nums = ffi.new("GoSlice*", {"data": ffi.cast("void*", data), "len": 3, "cap": 3})
# lib.Add(bloom, nums[0])
# print(lib.Test(bloom, nums[0]))

data = ffi.new("GoUint[]", [3, 5])
nums = ffi.new("GoSlice*", {"data": ffi.cast("void*", data), "len": 2, "cap": 2})
lib.AddListUint(bloom, nums[0])

data = ffi.new("GoUint[]", list(range(10)))
nums = ffi.new("GoSlice*", {"data": ffi.cast("void*", data), "len": 10, "cap": 10})
out = lib.TestListUint(bloom, nums[0])
print(list(ffi.unpack(out, 10)))
lib.free(ffi.cast("void*", out))
print(list(ffi.unpack(out, 10)))

# print("bloom.Add(12,99) = %d" % lib.Add(12,99))
# print("bloom.Cosine(1) = %f" % lib.Cosine(1))

# data = ffi.new("GoInt[]", [74,4,122,9,12])
# nums = ffi.new("GoSlice*", {'data':data, 'len':5, 'cap':5})
# lib.Sort(nums[0])
# print("awesome.Sort(74,4,122,9,12) = %s" % [
#     ffi.cast("GoInt*", nums.data)[i]
#     for i in range(nums.len)])

# data = ffi.new("char[]", b"Hello Python!")
# msg = ffi.new("GoString*", {'data':data, 'len':13})
# print("log id %d" % lib.Log(msg[0]))
