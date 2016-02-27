# solhsm-mgmt
This is the key management tool for the solhsm-core.

## Requirements

    python3
    python3-pip
    libsqlite3-dev
    sqlite3
    Pycrypto

These packages can be installed by the install_dep.sh script, just run it.

## How to use

### Install

    chmod +x install.sh
    ./install.sh

### Run

Examples:

    solhsm-mgmt.py -h
    sudo solhsm-mgmt.py genkey --rsa --size 1024 --label foo
    solhsm-mgmt.py key --view --id 1

## Internal stuff

PySql library allows user to access to key.db sqlite3 database. This
library provides setter and getter methods in order to interact with db. The
database is located at /data/db/key.db

In order to forge the dummy key we had hardcoded d,p,q parameters, see
[well know security issues](https://github.com/jjungo/solhsm-core/wiki/Well-know-security-issues).

## Generate your Certificate Signing Sequest (CSR)
The current method for generating a CSR is rough because you need to open the
database and get the private key manual in order to create your CSR. We're working
on simplifying this step.

Todos
-----
* Generate CSR feature
* Let's Encrypt?
