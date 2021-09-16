
import os
import socket
import sys
import socketserver
import threading



class ThreadingDNSHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        print("data in")
        # Deal with request
        data, sock = self.request
        data = self.request.recv(1024, 'ascii')
        socket = self.request[1]
        client = self.client_address[0]
        thread = threading.current_thread()
        response = bytes("PONG", 'ascii')
        self.request.sendall(response)

class ThreadingDNSServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    address_family = socket.AF_INET6
    def __init__(self, host="::", port=53):
        super().__init__((host, port), ThreadingDNSHandler, bind_and_activate=False)

        # Make this socket dual stack
        # NOTE - socket.IPPROTO_IPV6 missing in python 3.6, use 41 instead
        self.socket.setsockopt(41, socket.IPV6_V6ONLY, 0)
        
        self.server_bind()
    pass

if __name__ == "__main__":
    server = ThreadingDNSServer()
    print("Serving...")
    server.serve_forever()
    # with server:
    #     ip, port = server.server_address

    #     server_thread = threading.Thread(target=server.serve_forever)
    #     server_thread.daemon = True
    #     server_thread.start()

    