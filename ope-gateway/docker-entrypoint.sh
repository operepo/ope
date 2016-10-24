#!/bin/bash
set -e

# Make sure there is a default cert
if [ -e /etc/nginx/certs/default.crt ]; then echo "certs exist"; else echo "generating default cert"; openssl req -newkey rsa:4096 -x509 -nodes -days 1780 -subj "/C=US/ST=Washington/L=Port Angeles/O=OpenPrisonEducation/CN=gateway.ed" -keyout /etc/nginx/certs/default.key -out /etc/nginx/certs/default.crt; fi


# Warn if the DOCKER_HOST socket does not exist
if [[ $DOCKER_HOST == unix://* ]]; then
	socket_file=${DOCKER_HOST#unix://}
	if ! [ -S $socket_file ]; then
		cat >&2 <<-EOT
			ERROR: you need to share your Docker host socket with a volume at $socket_file
			Typically you should run your jwilder/nginx-proxy with: \`-v /var/run/docker.sock:$socket_file:ro\`
			See the documentation at http://git.io/vZaGJ
		EOT
		socketMissing=1
	fi
fi

# If the user has run the default command and the socket doesn't exist, fail
if [ "$socketMissing" = 1 -a "$1" = forego -a "$2" = start -a "$3" = '-r' ]; then
	exit 1
fi


exec "$@"