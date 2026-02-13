# syntax=docker.io/docker/dockerfile:1
ARG APT_UPDATE_SNAPSHOT=20260113T030400Z
ARG MACHINE_GUEST_TOOLS_VERSION=0.17.1-r1
ARG MACHINE_GUEST_TOOLS_SHA256SUM=c077573dbcf0cdc146adf14b480bfe454ca63aa4d3e8408c5487f550a5b77a41

FROM --platform=linux/riscv64 riscv64/python:3.12.12-alpine3.22 AS base
# FROM --platform=linux/riscv64 cartesi/python:3.12.9-slim-noble AS base

# Install tools
ARG MACHINE_GUEST_TOOLS_VERSION
ADD --chmod=644 https://edubart.github.io/linux-packages/apk/keys/cartesi-apk-key.rsa.pub /etc/apk/keys/cartesi-apk-key.rsa.pub
RUN echo "https://edubart.github.io/linux-packages/apk/stable" >> /etc/apk/repositories
RUN apk update && apk add cartesi-machine-guest-tools=$MACHINE_GUEST_TOOLS_VERSION

FROM base AS app

WORKDIR /opt/cartesi/app

COPY requirements.txt .

RUN <<EOF
set -e
pip3 install -r requirements.txt
rm requirements.txt
EOF

RUN <<EOF
set -e
find /usr/local/lib -type d -name __pycache__ -exec rm -r {} +
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf /var/lib/apt/lists/* /var/log/* /var/cache/* /tmp/*
EOF

COPY app.py .
COPY utils.py .

CMD ["/usr/local/bin/python3","/opt/cartesi/app/app.py"]
