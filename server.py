from threadpool import ThreadPool
from datetime import datetime
from log import logger
import random
import socket
import argparse
import crypto
import sys

# server options predefined
HOST = "0.0.0.0"
PORT = 1337
NUM_THREADS = 8

# Description: the task that will be handled by a thread
# Arguments: 
#   - host (socket, string) - a tuple that contains the socket and the address of the client (sock, addr)
# Return: void

def handle_connection(host):
    sock, addr = host
    key = crypto.key_exchange_server(sock) # before communication a key exchange need to happen for the traffic to be encrypted
    
    # the thread will keep the connection until the client closes it
    while True:
        # receive and decrypt data
        client_data_enc = sock.recv(crypto.DATA_SIZE)
        client_data = crypto.xor_with_key(client_data_enc, key).decode('utf-8').strip().upper()

        match client_data:
            case "DATE":
                server_data = str(datetime.now().date()).encode('utf-8')
            case "TIME":
                server_data = str(datetime.now().time()).encode('utf-8')
            case "TEMP":
                server_data = str(random.randint(-100, 100)).encode('utf-8')
            case "END":
                break
            case _:
                server_data = b'\xde\xad\xbe\xef' # error message
        
        # encrypt and send the data
        sock.send(crypto.xor_with_key(server_data, key))

    sock.close()
    logger.warning(f"Connection ended with {addr[0]}:{addr[1]}")


if __name__ == "__main__":
    random.seed(1234) # set the seed for random

    # using argparse to specify options from the terminal
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='A simple server that can respond to 3 types of requests: TIME, DATE, TEMP')
    parser.add_argument('--host', help="The host address", type=str)
    parser.add_argument('-p', '--port', required=False, help="Port to which to listen", type=int)
    parser.add_argument('-t', '--threads', help="Number of threads to use. (max 64)", type=int)

    args = parser.parse_args()

    if args.threads is not None:
        NUM_THREADS = args.threads
    if args.host is not None:
        HOST = args.host
    if args.port is not None:
        PORT = args.port

    # starting the threadpool
    threadpool = ThreadPool(num_threads=NUM_THREADS)
    threadpool.start()

    # initializing the socket that will listen for connections
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master_socket.bind((HOST, PORT)) # binding to HOST:PORT
    master_socket.listen()

    logger.debug(f"Server started with {NUM_THREADS} threads and it's listening on {HOST}:{PORT}...")

    # since it's a simple server I will runnit with while True and stop it with Ctrl^C
    while True:
        conn_socket, conn_addr = master_socket.accept()
        logger.info(f"Connection received from {conn_addr[0]}:{conn_addr[1]}")

        threadpool.add_task((handle_connection, (conn_socket, conn_addr)))