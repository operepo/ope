#!/bin/bash

CERT_PATH=/etc/nginx/certs
VOLUME_PATH=/public_certs/
APP_PATH=/app

#### DEBUG VALUES - SHOULD BE COMMENTED IF NOT DEBUGGING ####
#CERT_PATH=/ope/docker_build_files/ope-gateway
#rm -f $CERT_PATH/ca.*
#rm -f $CERT_PATH/default.*
#VOLUME_PATH=/
#APP_PATH=./
#### END DEBUG VALUES - SHOULD BE COMMENTED IF NOT DEBUGGING ####


# Remove certs from before 3/22/18
find $CERT_PATH/default.* ! -newermt "2018-03-23 00:00:00" | xargs rm -rf

# Make the CA cert
if [ -e $CERT_PATH/ca.crt ]; then
    echo "CA exists";
else
    echo "===== Generating CA Cert =====";

    # make the key
    #openssl genrsa -out $CERT_PATH/ca.key 4096

    # make the crt
    openssl req -newkey rsa:4096 -x509 -new -nodes -days 10780 -sha256 -reqexts v3_req -extensions v3_ca \
       -out $CERT_PATH/ca.crt -keyout $CERT_PATH/ca.key \
       -subj "/C=US/ST=Washington/L=Port Angeles/OU=IT/O=OpenPrisonEducation/CN=gateway.ed" \
       -config $APP_PATH/openssl.cnf

fi


# Make sure there is a default cert that is a wildcard for *.ed
if [ -e $CERT_PATH/default.crt ]; then
    echo "Cert exists";
else
    echo "===== Generating default cert =====";

    # create CSR

    openssl req -newkey rsa:4096 -new -nodes -days 10780 -sha256 -extensions v3_req  \
       -out $CERT_PATH/default.csr -keyout $CERT_PATH/default.key \
       -subj "/C=US/ST=Washington/L=Port Angeles/OU=IT/O=OpenPrisonEducation/CN=*.ed" \
       -config $APP_PATH/openssl.cnf


    # Create signed CRT
    openssl x509 -req -in $CERT_PATH/default.csr -CA $CERT_PATH/ca.crt -CAkey $CERT_PATH/ca.key \
       -CAcreateserial -out $CERT_PATH/default.crt -days 10780 \
       -extensions v3_req \
       -extfile $APP_PATH/openssl.cnf;


    # Make the cert bundle with the cert and CA combined
    cat $CERT_PATH/default.crt $CERT_PATH/ca.crt > $CERT_PATH/default.bundle.crt
    mv $CERT_PATH/default.bundle.crt $CERT_PATH/default.crt
fi

# Copy the public certs to the server
cp $CERT_PATH/ca.crt $VOLUME_PATH
cp $CERT_PATH/default.crt $VOLUME_PATH

