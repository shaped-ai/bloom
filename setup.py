import os

from setuptools import Extension, find_namespace_packages, setup

with open("README.md") as f:
    long_description = f.read()

version = "3.3.0"
circleci_build_number = os.getenv("CIRCLE_BUILD_NUM", "")
if circleci_build_number != "":
    version = f"{version}.dev{circleci_build_number}"

setup(
    name="shaped-bloom-filter",
    version=version,
    author="Shaped Team",
    author_email="support@shaped.ai",
    url="https://github.com/shaped-ai/bloom",
    description="Highly optimized bloom filter in Python with bindings in Go.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["bloom-filter", "shaped-ai"],
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
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
    include_package_data=True,
)
