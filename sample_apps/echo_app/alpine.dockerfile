# syntax=docker.io/docker/dockerfile:1
ARG APT_UPDATE_SNAPSHOT=20260113T030400Z
ARG MACHINE_GUEST_TOOLS_VERSION=0.17.1-r1
ARG MACHINE_GUEST_TOOLS_SHA256SUM=c077573dbcf0cdc146adf14b480bfe454ca63aa4d3e8408c5487f550a5b77a41
ARG APP_DIR=.
ARG INSTALL_STEP=install

# ARG IMAGE_VERSION=3.13.12-alpine3.22
ARG IMAGE_VERSION=3.12.12-alpine3.22
FROM --platform=linux/riscv64 riscv64/python:${IMAGE_VERSION} AS base

# Install tools
ARG MACHINE_GUEST_TOOLS_VERSION
ADD --chmod=644 https://edubart.github.io/linux-packages/apk/keys/cartesi-apk-key.rsa.pub /etc/apk/keys/cartesi-apk-key.rsa.pub
RUN echo "https://edubart.github.io/linux-packages/apk/stable" >> /etc/apk/repositories
RUN apk update && apk add cartesi-machine-guest-tools=$MACHINE_GUEST_TOOLS_VERSION

FROM base AS install

WORKDIR /opt/install

ARG APP_DIR
COPY ${APP_DIR}/requirements.txt .

RUN <<EOF
set -e
pip3 install -r requirements.txt
rm requirements.txt
EOF

RUN <<EOF
set -e
find /usr/local/lib -type d -name __pycache__ -exec rm -r {} +
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf /var/lib/apt/lists/* /var/log/* /var/cache/* /tmp/* /opt/install
EOF

FROM base AS builder

ARG MACHINE_GUEST_TOOLS_VERSION
RUN <<EOF
set -e
apk update
apk add \
    build-base=0.5-r3 \
    cartesi-machine-guest-libcmt-dev=${MACHINE_GUEST_TOOLS_VERSION}
EOF

ARG SETUPTOOLS_VERSION=82.0.0
ARG CYTHON_VERSION=3.2.4
RUN pip install setuptools==${SETUPTOOLS_VERSION} cython==${CYTHON_VERSION}

ARG PYCMT_PROJECT=.
ADD ${PYCMT_PROJECT} /opt/build

WORKDIR /opt/build

RUN pip3 wheel . --no-deps -w wheels/

FROM base AS install-local

WORKDIR /opt/install

ARG APP_DIR
COPY ${APP_DIR}/requirements.txt .

RUN <<EOF
set -e
sed -i '/pycmt/d' ./requirements.txt
pip3 install -r requirements.txt
EOF

COPY --from=builder /opt/build/wheels/ /opt/install/wheels

RUN <<EOF
set -e
pip3 install pycmt --find-links /opt/install/wheels
rm requirements.txt
EOF

RUN <<EOF
set -e
find /usr/local/lib -type d -name __pycache__ -exec rm -r {} +
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf /var/lib/apt/lists/* /var/log/* /var/cache/* /tmp/* /opt/install
EOF

FROM ${INSTALL_STEP} AS app

WORKDIR /opt/cartesi/app

ARG APP_DIR
COPY ${APP_DIR}/app.py .
COPY ${APP_DIR}/utils.py .

CMD ["/usr/local/bin/python3","/opt/cartesi/app/app.py"]
