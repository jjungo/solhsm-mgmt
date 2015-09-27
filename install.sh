#!/bin/bash

check_dep() {
    DEPENDENCIES="python python-dev python-pip python3 python3-dev python3-pip libsqlite3-dev sqlite3"
    INSTALL=""

    for pkg in $DEPENDENCIES ; do
        if which dpkg &> /dev/null; then
            PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $pkg |grep "install ok installed")
            echo Checking for $pkg $PKG_OK
            if [ "" == "$PKG_OK" ]; then
                INSTALL=$INSTALL" "$pkg
            fi

        elif which pacman &> /dev/null; then
            PKG_OK=$(pacman -Qs $pkg)
            echo Checking for $pkg $PKG_OK
            if [ "$PKG_OK" == "" ]; then
                INSTALL=$INSTALL" "$pkg
            fi
        fi
    done

    if [ "$INSTALL" != "" ]; then
        echo  "Some dependencies are missing:"
        echo $INSTALL
        echo -n "Install them? (Y/n): "
        read CONFIRM

        if [[ $CONFIRM = "Y" || $CONFIRM = "y" || $CONFIRM = "" ]]; then
            if which apt-get &> /dev/null; then
                apt-get update
                apt-get install -y $INSTALL
                pip3 install pycrypto

            elif which pacman &> /dev/null; then
                echo will install $INSTALL
                pacman -Sy $INSTALL
                pip install pycrypto

            else 
                echo "NO package manager is found for your distribution, please install mannualy $INSTALL"
                exit -1
            fi 
        fi
    fi
}

install_mgmt(){
    cd ./lib/
    python3 setup.py install
    cd ..
    cp solhsm-mgmt.py /usr/bin/
    chmod +x /usr/bin/solhsm-mgmt.py
    mkdir -p /data/db
}

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
else
    check_dep
    install_mgmt
fi

