#!/bin/bash

# Update the fog password with the current OPE password if present
password=$IT_PW
username='fog'
#webdirdest=''
workingdir=$(pwd)

# Include fog libs so we can use its password setting code
. ../lib/common/functions.sh
. ../lib/common/config.sh

# echo "Webdir: $webdirdest"
# echo "Workdir: $workingdir"

if [ ! -z $password ]; then
    echo "Setting OPE password..."
    # Update user account
    configureUsers

    # Get the password hash
    pw_hash=$( php -r "echo password_hash('$IT_PW', PASSWORD_BCRYPT, ['cost'=>11]);" )
    #echo $pw_hash

    # Need to update the mysql password for the fog user
    sql="UPDATE fog.users SET uPass='$pw_hash' WHERE uName='fog'"
    echo $sql > tmp.sql
    mysql < tmp.sql
    rm tmp.sql

    # updateStorageNodeCredentials

fi





