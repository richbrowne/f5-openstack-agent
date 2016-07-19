#!/bin/bash -ex

OS_TYPE=$1
OS_VERSION=$2
PKG_ROOT=$(pwd)
DEST_DIR=${PKG_ROOT}/dist/${OS_TYPE}/${OS_VERSION}

if [ $OS_TYPE == "redhat" ]; then
	git clone https://github.com/richbrowne/f5-openstack-agent-rpmdist.git ${DEST_DIR}
elif [ $OS_TYPE == "ubuntu" ]; then
	echo "DEBIAN PACKAGING NOT IMPLEMENTED"
	exit 0
else
	echo "Unknown os type: ${OS_TYPE}"
	exit 1
fi

BUILD_CONTAINER=${OS_TYPE}${OS_VERSION}-pkg-builder
BUILD_DIR="/var/bdir"
docker build -t ${BUILD_CONTAINER} ${DEST_DIR}/Docker/${OS_TYPE}/${OS_VERSION}
docker run --privileged -v ${PKG_ROOT}:${BUILD_DIR} ${BUILD_CONTAINER} /bin/bash /build-rpms.sh
sudo chown -R travis:travis ${DEST_DIR}
