from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from random import *

__DEBUG__ = False
PRIME_LIMIT = 10000000

def degenerate(p_num1,p_num2,e, key_size = 128):
    n = p_num1 * p_num2
    tot = (p_num1 - 1) * (p_num2 - 1)
    e = generatePublicKey(tot,key_size)
    d = generatePrivateKey(e,tot)
    if __DEBUG__ == True:
      print(f"n = {n}" )
      print(f"tot = {tot}")
      print(f"e = {e}" )
      print(f"d = {d}" )
    return d,n

def generate(p_num1,p_num2, key_size = 128):
    n = p_num1 * p_num2
    tot = (p_num1 - 1) * (p_num2 - 1)
    e = generatePublicKey(tot,key_size)
    d = generatePrivateKey(e,tot)
    if __DEBUG__ == True:
      print(f"n = {n}" )
      print(f"tot = {tot}")
      print(f"e = {e}" )
      print(f"d = {d}" )
    return e,d,n

def generatePublicKey(tot,key_size):
    e = randint(2**(key_size-1),2**key_size - 1)
    g = gcd(e,tot)
    while g != 1:
        e = randint(2**(key_size-1),2**key_size - 1)
        g = gcd(e,tot)
    return e

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

def gcd(e,tot):
    temp = 0
    while True:
        temp = e % tot
        if temp == 0:
            return tot
        e = tot
        tot = temp

def getPrime(limit = PRIME_LIMIT):
         num = 0
         while True:
             num = randint(0,limit)
             if isPrime(num):
                 break
         if __DEBUG__ == True:
             print(f"Generated Prime number: {num}")
         return num

def isPrime(num):
    if num < 2 : return False
    if num == 2 : return True
    if num & 0x01 == 0 : return False
    n = int(num ** 0.5 )
    for i in range(3,n,2):
        if num % i == 0:
            return False
    return True

def encrypt(text,e,n):
         ctext = [pow(ord(char),e,n) for char in text]
         return ctext

def decrypt(ctext,d,n):
    try:
        text = [chr(pow(char,d,n)) for char in ctext]
        return "".join(text)
    except TypeError as e:
        print(e)

def accept_incoming_connections():

    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes(greet, "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    global e
    global n
    global d
    name = decrypt(eval(client.recv(BUFSIZ).decode("utf8")),e,n)
    welcome = ['Welcome %s! If you ever want to quit, type {quit} to exit.' % name]
    welcome = str(welcome)
    client.send(bytes(str([encrypt(welcome,e,n),key]), "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(msg)
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        msg = msg.decode("utf8")

        msg = decrypt(eval(msg),e,n)

        if msg == "{quit}":
            client.close()
            del clients[client]
            broadcast("%s has left the chat." % name)
            break
        else:
            broadcast(msg, name+": ")
            

def broadcast(msg, prefix=""):
    msg = prefix+msg
    msg = encrypt(msg,e,n)
    send = [msg,key]
    send = str(send)
    send = bytes(send, "utf8")
    for sock in clients:
        try:
            sock.send(send)
        except:
            print("client is disconnected")


clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 102400
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

e,d,n = generate(getPrime(),getPrime())

key = [d,n]

greet = [encrypt("Type your name and press enter!",e,n),key]
greet = str(greet)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
