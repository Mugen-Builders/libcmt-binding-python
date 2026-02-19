<br>
<p align="center">
    <img src="https://github.com/user-attachments/assets/080bb0be-060c-4813-85b4-6d9bf25af01f" align="center" width="20%">
</p>
<br>
<div align="center">
	<i>Cartesi Rollups LIBCMT Binding for PYTHON</i>
</div>
<div align="center">
	<!-- <b>Any Code. Ethereum’s Security.</b> -->
</div>
<br>
<p align="center">
	<img src="https://img.shields.io/github/license/Mugen-Builders/libcmt-binding-python?style=default&logo=opensourceinitiative&logoColor=white&color=008DA5" alt="license">
	<img src="https://img.shields.io/github/last-commit/Mugen-Builders/libcmt-binding-python?style=default&logo=git&logoColor=white&color=000000" alt="last-commit">
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Requirements](#requirements)
- [Usage](#usage)

## Overview

This repository contains the Python bindings for the [Cartesi machine guest library (libcmt)](https://github.com/cartesi/machine-guest-tools/tree/main/sys-utils/libcmt). The bindings expose libcmt’s C API (rollup I/O, ABI, Merkle trees, buffers, etc.) for utilization in python applications as an object. The library is written in cython and it should be compiled for the system. This would serve as an alternative to the HttpServer and offer methods to manage a Cartesi application instance.

The repo includes:

- **Library**: `pycmt` — the main cython library definition.
- **Sample apps**: `echo_app` (handles asset deposit and voucher emission) and `app_template` (minimal starter).
- **Cartesi config**: `cartesi.echoApp.toml` for building and running the echo app in the Cartesi machine.
- **Tests**: `/tests` Utilizes cartesapp to test the sample application which uses the libcmt-python-bindings.

## Requirements

- **Docker** — for building the RISC-V image and running the Cartesi machine.
- **Python 3.8+** — for the test suite (cartesapp).

## Usage

### Add the binding to your Cartesi project

You can use `pip` to install:

```shell
pip3 install pycmt --find-links https://prototyp3-dev.github.io/pip-wheels-riscv/wheels/
```

Note: the wheels are already compiled at https://prototyp3-dev.github.io/pip-wheels-riscv/wheels/. Alternatively you can install directly from the repo:

```shell
pip3 install pycmt@git+https://github.com/Mugen-Builders/libcmt-binding-python
```

### Code Snippets

The following snippets show how to use the libcmt Python bindings. A more detailed use can be found on the [echo app](sample_apps/echo_app/app.py).

**Creating a rollup and main request loop:**

```python
from pycmt import Rollup

rollup = Rollup()

# Main loop
while True:
    next_request_type = rollup.finish(True)
```

**Handling an advance request (read input, optionally emit voucher/notice):**

```python
from pycmt import Rollup

def handle_advance(rol):
    advance = rol.read_advance_state()
    msg_sender = advance['msg_sender'].hex().lower()
    print(f"[app] Received advance request from {msg_sender=} with length {len(advance['payload']['data'])}")
    return True

rollup = Rollup()

accept_previous_request = True
# Main loop
while True:
    next_request_type = rollup.finish(accept_previous_request)
    if next_request_type == 'advance':
        accept_previous_request = handle_advance(rollup):
```

**Handling an inspect request (read-only query):**

```python
from pycmt import Rollup

def handle_inspect(rol):
    advance = rol.read_advance_state()
    print(f"[app] Received inspect request with length {len(advance['payload']['data'])}")
    return True

rollup = Rollup()

accept_previous_request = True
# Main loop
while True:
    next_request_type = rollup.finish(accept_previous_request)
    if next_request_type == 'inspect':
        accept_previous_request = handle_inspect(rollup):
```

**Emitting a notice** (data that can be validated on-chain):

```python
from pycmt import Rollup

rollup = Rollup()

# Main loop
while True:
    next_request_type = rollup.finish(True)
    if next_request_type == 'advance':
        # payload in bytes
        rollup.emit_notice(b'Hello')
```

**Emitting a voucher** (transaction to be executed on L1):

```python
from pycmt import Rollup

rollup = Rollup()

# Main loop
while True:
    next_request_type = rollup.finish(True)
    if next_request_type == 'advance':
        # address_hex: 20-byte destination (40 hex chars), e.g. "0x..."
        # value: int ETH value
        # payload: calldata
        rollup.emit_voucher(
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            1_000_000_000_000_000_000,
            b''
        )
```

**Emitting a report** (log; not validated on-chain):

```python
from pycmt import Rollup

rollup = Rollup()

# Main loop
while True:
    next_request_type = rollup.finish(True)
    rollup.emit_report(b'report')
```

## Building and running the Sample echo app

The `sample_apps/echo_app` is a sample application using the libcmt Python bindings. The app simply receives deposits and emits a voucher to the sender with the same amount. To build and run, go the the `sample_apps/echo_app` directory and:

**Build the machine image (RISC-V):**

```bash
cartesi build
```

**Run the Cartesi machine:**

```bash
cartesi run
```

This starts the rollup node with the echo app; you can then send deposits, advances and inspect requests to the application.

## Testing

Tests are written in Python using [cartesapp](https://github.com/prototyp3-dev/cartesapp) and run inside the Cartesi machine.

**Prerequisites:** Python 3.12+, virtualenv with cartesapp installed (see [Installation](#5-python-test-suite-optional-for-testing)).

**Run tests (with Cartesi machine emulator):**

```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install cartesapp[dev]@git+https://github.com/prototyp3-dev/cartesapp@v1.2.1
cartesapp test --config-file "./cartesi.echoApp.toml" --log-level debug --cartesi-machine
```

This builds, and runs the test client.

## Local Builds and Testing

You'll need to build the library locally and install it in the sample app's environment. But first you'll need to create the builder docker image:

```bash
docker build --platform=linux/riscv64 -t builder -f alpine.builder .
```

Then, to build the library and install it in the sample app:

```bash
docker run --rm -v $PWD:/mnt/build -w /mnt/build -u $(id -u):$(id -g) builder /mnt/build/build_wheels.sh
```

Note: you can do a similar task for ubuntu repo using the `ubuntu.dockerfile`.

Then you can test the library with the sample app using `cartesapp`:

```bash
cartesapp test --config-file "./cartesi.echoApp.toml" --log-level debug --cartesi-machine
```

## License

See [LICENSE](LICENSE).
