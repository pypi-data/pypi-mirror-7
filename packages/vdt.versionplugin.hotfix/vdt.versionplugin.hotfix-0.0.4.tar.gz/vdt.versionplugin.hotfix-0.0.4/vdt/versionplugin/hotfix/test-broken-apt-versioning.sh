#!/bin/bash

SMALLER="le"
GREATER="gt"

function compare ()
{
    echo "$1 $2 $3"
    dpkg --compare-versions $1 $2 $3
    if ! [ $? -eq 0 ]; then
        echo ">> fail"
        exit 1
    else
        echo ">> success"
    fi
}

echo "######################################################################"
echo "# The following tests proof that apt is not working correct...       #"
echo "######################################################################"
compare "0.0.1-jenkins-999-1" $GREATER "0.0.1-jenkins-1000"

echo -e "\n"

echo "######################################################################"
echo " The following tests proof that our workaround is working correct... #"
echo "######################################################################"
compare "0.0.1-jenkins-1000" $GREATER "0.0.1-jenkins-999.1"
compare "0.0.1-jenkins-1000" $GREATER "0.0.1-jenkins-999"
compare "0.0.1-jenkins-999.2" $GREATER "0.0.1-jenkins-999.1"
compare "0.0.1-jenkins-999.1" $SMALLER "0.0.1-jenkins-1000"