#!/bin/bash
set -e -x

export PYHOME=/home
cd ${PYHOME}

curl --output go1.19.linux-amd64.tar.gz -L https://go.dev/dl/go1.19.linux-amd64.tar.gz && \
    rm -rf /usr/local/go && \
    tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

/opt/python/cp37-cp37m/bin/pip install twine cmake
ln -s /opt/python/cp37-cp37m/bin/cmake /usr/bin/cmake

# Compile wheels
cd /io
for PYBIN in /opt/python/cp3*/bin; do
    "${PYBIN}/pip" install setuptools setuptools-golang
    "${PYBIN}/pip" wheel . -w /home/wheelhouse/
    "${PYBIN}/python" setup.py sdist -d /io/wheelhouse/
done
cd ${PYHOME}

# Bundle external shared libraries into the wheels and fix naming
for whl in wheelhouse/shaped_bloom_filter*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Test
for PYBIN in /opt/python/cp3*/bin/; do
    "${PYBIN}/pip" install pytest cffi==1.15.1
    "${PYBIN}/pip" install --no-index -f /io/wheelhouse shaped-bloom-filter
    (cd "$PYHOME"; "${PYBIN}/pytest" -v -s /io/python/tests/*.py)
done

# Upload wheels
for WHEEL in /io/wheelhouse/shaped_bloom_filter*; do
    /opt/python/cp37-cp37m/bin/twine upload \
        --skip-existing \
        --repository-url "${TWINE_REGISTRY_URL}" \
        -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
        "${WHEEL}"
done
# Upload archive
/opt/python/cp37-cp37m/bin/twine upload \
    --skip-existing \
    --repository-url "${TWINE_REGISTRY_URL}" \
    -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
    /io/wheelhouse/shaped-bloom-filter-*.tar.gz
