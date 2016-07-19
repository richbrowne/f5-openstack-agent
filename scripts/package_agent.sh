#!/bin/bash -ex

OS_TYPE=$1
OS_VERSION=$2

PKG_DIST="pkg_dist/${OS_TYPE}/${OS_VERSION}"

rm -rf ${PKG_DIST}
if [ $OS_TYPE == "redhat" ]; then
	git clone https://github.com/richbrowne/f5-openstack-agent-rpmdist.git ${PKG_DIST}
elif [ $OS_TYPE == "ubuntu" ]; then
	exit 0
else
	echo "Unknown os type: ${OS_TYPE}"
	exit 1
fi

BUILD_CONTAINER=${OS_TYPE}${OS_VERSION}-pkg-builder
WORKING_DIR="/var/wdir"

docker build -t ${BUILD_CONTAINER} ${PKG_DIST}/Docker/${OS_TYPE}/${OS_VERSION}
docker run --privileged -v $(pwd):${WORKING_DIR} ${BUILD_CONTAINER} /bin/bash /build-rpms.sh "${WORKING_DIR}" "${PKG_DIST}"
sudo chown -R travis:travis ${PKG_DIST}

exit 0
