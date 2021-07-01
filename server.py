from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from random import *
import socket as ipfinder

__DEBUG__ = False
PRIME_LIMIT = 10000000

#START OF ENCRPTION#

def degenerate(p_num1,p_num2,e, key_size = 128):
    n = p_num1 * p_num2
    tot = (p_num1 - 1) * (p_num2 - 1)
    e = generatePublicKey(tot,key_size)
    return d,n

#Generates the encryption keys using 2 random prime numbers and the key size in bytes.
def generate(p_num1,p_num2, key_size = 128):
    #Set N to Prime number 1 * Prime Number 2
    n = p_num1 * p_num2
    #Set tot to (Prime number 1 - 1) * (Prime Number 2 - 1)
    tot = (p_num1 - 1) * (p_num2 - 1)
    #Generate E and D using tot
    e = generatePublicKey(tot,key_size)
    d = generatePrivateKey(e,tot)
    return e,d,n


def generatePublicKey(tot,key_size):
    e = randint(2**(key_size-1),2**key_size - 1)
    g = gcd(e,tot)
    while g != 1:
        e = randint(2**(key_size-1),2**key_size - 1)
        g = gcd(e,tot)
    return e

#Euclid's extended algorithm for finding the multiplicative inverse of two numbers
def generatePrivateKey(e,tot):
    d = egcd(e,tot)[1]
    d = d % tot
    if d < 0 :
        d += tot
    return d

def egcd(a,b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

#Check if e and tot are comprime
def gcd(e,tot):
    temp = 0
    while True:
        temp = e % tot
        if temp == 0:
            return tot
        e = tot
        tot = temp

#Gets a prime number up to the prime limit
def getPrime(limit = PRIME_LIMIT):
         num = 0
         while True:
             num = randint(0,limit)
             if isPrime(num):
                 break
         return num

#Checks if a number is a prime number
def isPrime(num):
    if num < 2 : return False
    if num == 2 : return True
    if num & 0x01 == 0 : return False
    n = int(num ** 0.5 )
    for i in range(3,n,2):
        if num % i == 0:
            return False
    return True

#Uses Encription keys to encrypt/decrypt using a kind of RSA cippher.
def encrypt(text,e,n):
         ctext = [pow(ord(char),e,n) for char in text]
         return ctext

def decrypt(ctext,d,n):
    try:
        text = [chr(pow(char,d,n)) for char in ctext]
        return "".join(text)
    except TypeError as e:
        print(e)

#END OF ENCRPTION#

def accept_incoming_connections():
    #When new people join add them to the client list and print that they have joined to the server.
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        #Send the person who has joined the greet message
        client.send(bytes(greet, "utf8"))
        #add them to the client list and start the handel client thread for them
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    #Get global variables E,D,N for encryption keys.
    global e
    global n
    global d
    #Get the clients username
    name = decrypt(eval(client.recv(BUFSIZ).decode("utf8")),e,n)
    #Send the Welcome message to the client
    welcome = ['Welcome %s! If you ever want to quit, type {quit} to exit.' % name]
    welcome = str(welcome)
    client.send(bytes(str([encrypt(welcome,e,n),key]), "utf8"))

    #Brodcast to every one that they have joined the chat.
    msg = "%s has joined the chat!" % name
    print(f"{client} joined the chat as {name}")
    broadcast(msg)
    #Add thier name to the client name list.
    clients[client] = name

    #Start checking if they have sent a message
    while True:
        #if they send a message decode it to utf8
        msg = client.recv(BUFSIZ)
        msg = msg.decode("utf8")
        
        #decrypt the message using the servers private encription keys
        msg = decrypt(eval(msg),e,n)

        #If the message is {quit} remove them from the client list and brodcast that they have left the chat and stop their client thread
        if msg == "{quit}":
            client.close()
            del clients[client]
            broadcast("%s has left the chat." % name)
            break
        #brodcast thier message if it is not quit.
        else:
            broadcast(msg, name+": ")
            

def broadcast(msg, prefix=""):
    #Print the message to the log.
    print(prefix,msg)
    #encrypt the message using servers private encryption keys
    msg = (prefix,msg)
    msg = str(msg)
    msg = encrypt(msg,e,n)

    #Join the message + the key to decrypt it
    send = [msg,key]
    send = str(send)
    send = bytes(send, "utf8")

    #Try to send it to every client but if it fails the client has forcibly dissconected.
    for sock in clients:
        try:
            sock.send(send)
        except:
            print(f"Failed to send to client {sock} . Client is disconnected.")

#Set up server variables
clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 102400
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

#Generate the Encryption keys.
e,d,n = generate(getPrime(),getPrime())

#Join d and n together to make the public key.
key = [d,n]

#Set the greet message for people joining
greet = [encrypt("Welcome type your name and press enter!!",e,n),key]
greet = str(greet)

#Run the main server.
if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    print("IP:",ipfinder.gethostbyname(ipfinder.gethostname()),"PORT:",PORT)
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
