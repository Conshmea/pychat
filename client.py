from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from random import *
import ast

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

def receive():
    global d
    global n

    while True:
        try:
            msg = client_socket.recv(BUFSIZ)
            msg = msg.decode("utf8")
            msg = eval(msg)
            text = msg[0]
            key = msg[1]
            d = key[0]
            n = key[1]
            text = str(text)
            text = eval(text)
            text = decrypt(text,d,n)
            msg_list.insert(tkinter.END, text)
        except OSError:
            break


def send(event=None):
    global d
    global n   
    msg = my_msg.get()
    my_msg.set("")

    msg = encrypt(msg,d,n)
    msg = str(msg)
    
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    my_msg.set("{quit}")
    send()

top = tkinter.Tk()
top.title("Shmeamail")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)
msg_list = tkinter.Listbox(messages_frame, height=30, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

HOST = input('Enter host: ')
PORT = input('Enter port: ')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

if not HOST:
    HOST = "192.168.1.157"
else:
    HOST = HOST

BUFSIZ = 10240
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()
