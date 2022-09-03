from setuptools import setup, find_namespace_packages, Extension

setup(
    name="shaped-bloom-filter",
    version="3.3.0",
    author="Shaped Team",
    author_email="support@shaped.ai",
    url="https://github.com/shaped-ai/bloom",
    description="Python-importable bloom filter within bindings in Go.",
    keywords=["bloom-filter", "shaped-ai"],
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_namespace_packages(where="python"),
    package_dir={"": "python"},
    zip_safe=True,
    install_requires=["cffi==1.15.1"],
    build_golang={"root": "github.com/bits-and-blooms/bloom/v3"},
    ext_modules=[
        Extension(
            name="shaped_bloom_filter.libbloomf",
            sources=["python/shaped_bloom_filter/golib/main.go"],
            library_dirs=["python/shaped_bloom_filter/golib"],
        )
    ],
    package_data={"shaped_bloom_filter.golib": ["*.h"]},
)
