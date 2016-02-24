# solhsm-mgmt
This is the key management tool for the solhsm-core.

## Requirement

    python3
    python3-pip
    libsqlite3-dev
    sqlite3
    Pycrypto

## How to use

### Install

    chmod +x install.sh
    ./install.sh

### Run

Examples:

    solhsm-mgmt.py -h
    sudo solhsm-mgmt.py genkey --rsa --size 1024 --label foo
    solhsm-mgmt.py key --view --id 1

Todos
-----
* Generate CSR
* Let's Encrypt?
