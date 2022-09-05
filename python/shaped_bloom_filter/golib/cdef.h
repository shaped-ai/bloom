typedef double GoFloat64;
typedef unsigned long long GoUint64;
typedef long long GoInt64;

typedef char GoInt8;
typedef unsigned char GoUint8;
typedef GoUint64 GoUint;
typedef GoInt64 GoInt;

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

extern struct BloomFilter* NewFromSerialized(GoUint n, GoUint k, GoUint b_length, GoSlice data);
extern struct BloomFilter* NewWithEstimates(GoUint n, GoFloat64 fp);
extern void Add(struct BloomFilter* bf_c, GoSlice data);
extern void AddListUint(struct BloomFilter* bf_c, GoSlice data);
extern GoUint8 Test(struct BloomFilter* bf_c, GoSlice data);
extern char* TestListUint(struct BloomFilter* bf_c, GoSlice data);
extern void free(void *ptr);
