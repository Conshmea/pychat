from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from random import *
#import ast

#START OF ENCRPTION#

def encrypt(text,e,n):
    #Encrypt using a kind of RSA cipher
    ctext = [pow(ord(char),e,n) for char in text]
    return ctext

def decrypt(ctext,d,n):
    #Decrypt using a kind of RSA cipher
    try:
        text = [chr(pow(char,d,n)) for char in ctext]
        return "".join(text)
    except TypeError as e:
        print(e)

#END OF ENCRPTION#

def receive():

    #Sets encryption keys to global variables
    global d
    global n
    
    
    while True:
        try:
            #test for incomming message
            msg = socket_client.recv(BUFSIZ)
            
            #decode message to utf8
            msg = msg.decode("utf8")
            
            #Extract encryption keys and encrypted string from variable
            msg = eval(msg)
            text = msg[0]
            key = msg[1]
            d = key[0]
            n = key[1]

            #decrypt the message using encryption keys
            text = str(text)
            text = eval(text)
            text = decrypt(text,d,n)

            #check if username is seperate from message if so join username+message
            try:
                text = eval(text)
                text = text[0]+text[1]
            except:
                pass
            
            #insert message tin gui list
            message_list.insert(tkinter.END, text)
        except OSError:
            break


#Send Message
def send(event=None):
    #Gets encryption keys from global variables
    global d
    global n

    #get message from tkinter GUI
    msg = my_msg.get()
    my_msg.set("")
    
    #Encrypt Message using keys.
    msg = encrypt(msg,d,n)
    msg = str(msg)

    #Send socket message to the server
    socket_client.send(bytes(msg, "utf8"))

    #quit the app if {quit is used
    if msg == "{quit}":
        socket_client.close()
        app.quit()


#Send {quit} to the server
def on_closing(event=None):
    my_msg.set("{quit}")
    send()


#Define tkinter
app = tkinter.Tk()
app.title("Shmeamail")




#Add widgets to tkinter
messages_frame = tkinter.Frame(app)

my_msg = tkinter.StringVar()
my_msg.set("Type your messages here.")

scroll = tkinter.Scrollbar(messages_frame)

message_list = tkinter.Listbox(messages_frame, height=30, width=100, yscrollcommand=scroll.set)

scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
message_list.pack()

messages_frame.pack()

#Run send() on return key pressed.
entry_field = tkinter.Entry(app, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()

#send button to run send()
send_button = tkinter.Button(app, text="Send", command=send)
send_button.pack()


#Run on_closing() when app is closed
app.protocol("WM_DELETE_WINDOW", on_closing)

#Get host ip and port
HOST = input('Enter host (leave blank for public server): ')
PORT = input('Enter port (leave blank for public server): ')

#Set HOST AND PORT to public server host and port if left empty
if not PORT:
    PORT = 33333
else:
    PORT = int(PORT)

if not HOST:
    HOST = "109.74.195.219"
else:
    HOST = HOST

#Set buffer size and address for socket
BUFSIZ = 102400
ADDR = (HOST, PORT)

socket_client = socket(AF_INET, SOCK_STREAM)
socket_client.connect(ADDR)

#Start recive() in a new thread to not interfere with the app
receive_thread = Thread(target=receive)
receive_thread.start()

#Start tkinter app
tkinter.mainloop()
