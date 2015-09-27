solhsm-mgmt
===========

Requirement
-----------
    
    python3
    python3-pip
    libsqlite3-dev
    sqlite3
    Pycrypto

How to use
----------

You should place solhsm-mgmt.py in /usr/bin

    sudo cp solhsm-mgmt.py /usr/bin/
    
Examples:

    solhsm-mgmt.py -h
    sudo solhsm-mgmt.py genkey --rsa --size 1024 --label foo
    solhsm-mgmt.py key --view --id 1
    
    
    
