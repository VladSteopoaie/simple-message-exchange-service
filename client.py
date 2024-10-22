import socket
import crypto
import random
import argparse
import sys
import time
from log import logger

# global variables for server and client, both tuples with address and port (addr, port)
SERVER = ()
CLIENT = ()

# Description: prints the menu options
def print_menu():
    print("Choose a command (only the number):")
    print("1. get time")
    print("2. get date")
    print("3. get temperature")
    print("4. reset connection")
    print("5. exit")
    print("6. print menu")

# Description: connects to a server, does a key exchange and calculates the time it took to process
# Arguments: 
#   - host (string) - the address of the server
#   - port (int) - port of the server
# Return: returns the socket it created after connect, the shared key used for encryption, and the time
#   it took to accomplish the handshake
def make_connection(host, port):
    start_time = time.time()
    conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    
    try:
        conn_socket.connect((host, port))
        key = crypto.generate_random_key() # this is X (look at crypto.py for documentation) 
        crypto.key_exchange_client(conn_socket, key)
        rtt = time.time() - start_time
    except Exception as e:
        logger.error(f"make_connection error: {e}")
        exit(0)
    
    return conn_socket, key, rtt


if __name__ == "__main__":
    random.seed(4321) # seed for random

    # parsing terminal arguments
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='A simple client that can comunicate with the server designed for this assignment')
    parser.add_argument('host', help="The server address", type=str)
    parser.add_argument('port', help="Port to which to connect", type=int)
    args = parser.parse_args()
    SERVER = (args.host, args.port) # server specified in the terminal

    sock, key, rtt = make_connection(*SERVER)
    CLIENT = sock.getsockname() # getting the client ip address and port number
    logger.success(f"Connection established with {SERVER[0]}:{SERVER[1]} from {CLIENT[0]}:{CLIENT[1]}. Sum: {SERVER[1] + CLIENT[1]}")
    logger.info(f"Key exchange time: {rtt * 1000:.2f} ms")

    print_menu()
    while True: # the connection will hold until the client ends it

        try:
            # the int() function might throw an error if the conversion is not possible
            option = int(input("> ").strip()) # selecting input from user
        except:
            logger.warning("Option not valid! try again.")
            continue

        match option:
            case 1:
                request = "TIME"
            case 2:
                request = "DATE"
            case 3:
                request = "TEMP"
            case 4: # reset connection
                request = "END"
            case 5: # end connection
                request = "END"
            case 6:
                print_menu()
                continue
            case _:
                logger.warning("Invalid option! try again.")
                continue
        
        start_time = time.time() # calculating RTT
        sock.send(crypto.xor_with_key(request.encode("utf-8"), key)) # encrypt and send request

        if option == 4: # reset connection
            sock.close() # close the socket (the request to end connection was already sent)
            sock, key, rtt = make_connection(*SERVER) # start a new connection
            CLIENT = sock.getsockname()
            logger.success(f"Connection established with {SERVER[0]}:{SERVER[1]} from {CLIENT[0]}:{CLIENT[1]}. Sum: {SERVER[1] + CLIENT[1]}")
            logger.info(f"Key exchange time: {rtt * 1000:.2f} ms")

        elif option == 5: # exit
            logger.warning("Exiting ...")
            break 
        else: # otherwise we wait for a response
            server_data = crypto.xor_with_key(sock.recv(crypto.DATA_SIZE), key) # receiving and decrypting
            rtt = time.time() - start_time
            logger.info(f"Response from server: {server_data.decode("utf-8")}")
            logger.info(f"RTT: {rtt * 1000:.2f} ms")
    sock.close()
