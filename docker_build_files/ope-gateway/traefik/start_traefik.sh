#!/bin/sh

echo "Checking Certs..."
if [ -e /certs/cert.pem ]
then
	echo "Certificates present."
else
	echo "Generating test cert..."
	openssl req -newkey rsa:4096 -x509 -nodes -days 1780 -subj "/C=US/ST=Washington/L=Port Angeles/O=OpenPrisonEducation/CN=www.example.com" -keyout /certs/cert.pem -out /certs/cert.pem
fi

echo "Starting daemon..."
#Start the traefik daemon
/traefik