import random

DATA_SIZE = 1024 # global variable, maximum data size when receiving packets

# Description: uses key to xor byte_array
# Arguments:
#   - byte_array (byte array) - data to be encrypted
#   - key (byte array) - the key used to encrypt data
# Return: it returns the encrypted byte array
def xor_with_key(byte_array, key):
    result = bytearray()

    for i in range(len(byte_array)):
        result.append(byte_array[i] ^ key[i % len(key)])
    
    return result

# Description: generate a random array of bytes
# Arguments:
#   - size (int) - the size of the result byte array
# Return: the byte array generated
def generate_random_key(size=128):
    result = bytearray()

    for i in range(size):
        result.append(random.randint(1, 255))

    return result

# the key exchange has 5 steps (the algorithm used: XOR):
#   1. the client generates a shared key (X) which will be used to encrypt data between the the two nodes,
#      also the client and the server both generate a key to securely transmit the shared key (client key (C), server key (S))
#   2. the client encrypts X with C (=> XC) and sends it to the server.
#   3. the server receives XC and encrypts it with S (=> XCS) and sends it to the client
#   4. the client receives XCS and decrypts it with C (=> XS) and sends it to the server
#   5. the server receives XS and decrypts it with S (=> X).
# both sides now share the same key (X) and they can communicate with it securely

def key_exchange_client(sock, X):
    # step 1
    C = generate_random_key(64) # client key (C)
    
    # step 2
    XC = xor_with_key(X, C) # the client encrypts the shared key (X) with it's key (C) => XC
    sock.send(XC) # sents it to the server

    # step 4
    XCS = sock.recv(DATA_SIZE) # the client receives XCS from the server (from step 3)
    XS = xor_with_key(XCS, C) # the client decrypts XCS with C => XS
    sock.send(XS) # sents it to the server for step 5

def key_exchange_server(sock):
    # step 1
    S = generate_random_key(size=64) # server key (S)

    # step 3
    XC = sock.recv(DATA_SIZE) # shared key (X) encrypted by client's key (C) => XC (from step 2)
    XCS = xor_with_key(XC, S) # the server encrypts XC with S => XCS
    sock.send(XCS) # sends it to the client

    # step 5
    XS = sock.recv(DATA_SIZE) # receives XS from client
    X = xor_with_key(XS, S) # decrypts XS using S => X

    return X