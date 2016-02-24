# solhsm-mgmt
This is the key management tool for the solhsm-core.

## Requirement

    python3
    python3-pip
    libsqlite3-dev
    sqlite3
    Pycrypto

Theses packages can be installed by the install_dep.sh script, just run it.

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
library provide accesser and getter methods in order to interact with db. The
database is located at /data/db/key.db

In order to forge the dummy key we had hardcoded d,p,q parameters, see
[well know security issues](https://github.com/jjungo/solhsm-core/wiki/Well-know-security-issues).

Todos
-----
* Generate CSR
* Let's Encrypt?
