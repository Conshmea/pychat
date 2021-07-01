import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from socket import AF_INET, socket, SOCK_STREAM
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import sys
from random import *
import ast
from multiprocessing import Process
from threading import Thread
import time

kivy.require("1.10.1")

BUFSIZ = 102400

#START OF ENCRPTION#

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


#Page to enter details like server ip port and username.
class ConnectPage(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        #Read/Create a file called details.txt to save what ip/port you used.
        try:
            with open("details.txt","r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
        except:
            with open("details.txt","w") as f:
                f.write(f" , , ")


        #Add Kivy widgets
        self.add_widget(Label(text="""*STILL UNDER DEVELOPMENT*"""))
        self.add_widget(Label(text=""""""))

        self.add_widget(Label(text="""IP:
Use 109.74.195.219 for public server."""))
        self.ip = TextInput(text=prev_ip, multiline=False)
        self.add_widget(self.ip)

        self.add_widget(Label(text="""Port:
Use 33333 for public server."""))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text='Username:'))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)

        self.join = Button(text="Join")
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())
        self.add_widget(self.join)
        
    #On join button pressed
    def join_button(self, instance):

        #Set ip, port, username to easy to read variable names
        port = self.port.text
        ip = self.ip.text
        username = self.username.text

        #Add details to details.txt
        with open("details.txt","w") as f:
            f.write(f"{ip},{port},{username}")

        #Show username ip and port on info page when joining
        info = f"Joining {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = 'Info'
        Clock.schedule_once(self.connect, 1)

    #Connect to server
    def connect(self, _):

        #Set Client_socket and username to global variables
        global client_socket
        global username

        #Set ip, port, username to easy to read variable names
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text

        #Connect to the socket server
        ADDR = (ip, port)
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(ADDR)

        #Set encryption keys and greet to global variables
        global d
        global n
        global greet

        #Recive and decrypt the join message keeping it hidden
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

        #Automatticaly Join using username instead of having to type it out evey time.

        message = encrypt(username,d,n)
        message = str(message)
        client_socket.send(bytes(message,"utf8"))

        #Recive and decrypt the welcome message and greet to it.
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
        text = eval(text)
        greet = text[0]
        print(greet)

        #Switch to page chat page.
        chat_app.create_chat_page()
        chat_app.screen_manager.current = 'Chat'

#Make a scrollable chat history
class ScrollableLabel(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history(self, message):

        self.chat_history.text += '\n' + message

        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

        self.scroll_to(self.scroll_to_point)


#Main chat page
class ChatPage(GridLayout):
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        #Add widgets to Kivy app.
        self.cols = 1
        self.rows = 2
        
        self.history = ScrollableLabel(height=Window.size[1]*0.9, size_hint_y=None)
        self.add_widget(self.history)

        self.new_message = TextInput(width=Window.size[0]*0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Send")
        self.send.bind(on_press=self.send_message)

        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)

        Window.bind(on_key_down=self.on_key_down)

        self.history.update_chat_history(greet)

        Clock.schedule_once(self.focus_text_input, 1)
        Clock.schedule_interval(self.incoming_message, 1)
        

    #When return pressed send message
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):

        if keycode == 40:
            self.send_message(None)

    
    def send_message(self, _):
        #Get global encryption keys
        global d
        global n

        #get message from input box
        message = self.new_message.text

        #If there is a message encrypt it and send it
        if message:
            msg = encrypt(message,d,n)
            msg = str(msg)
            
            self.new_message.text = ''
            client_socket.send(bytes(msg,"utf8"))

        #If message = {quit} leave the app
        if message == "{quit}":
            chat_app.stop()
            sys.exit()

        #Refocus Input to input box
        Clock.schedule_once(self.focus_text_input, 0.1)


    #Refocus Input to input box
    def focus_text_input(self, _):
        self.new_message.focus = True

    def incoming_message(self, _):
        #Get global encryption and username
        global d
        global n
        global username

        #Recive the fist 2 bytes of the message (It doesnt recive the whole 102400 bytes so it doesnt hang or lag the App
        data = 0
        client_socket.settimeout(0.1)
        try:
            data = client_socket.recv(2)
        except:
            pass

        #If there was a message get the rest of it
        if data == bytes("[[", "utf8"):
            client_socket.settimeout(10)
            pass
            try:
                #Recive and decode the rest of the message and add the first 2 bytes back
                msg = client_socket.recv(BUFSIZ)
                msg = msg.decode("utf8")
                msg = "[["+msg

                #Using new encryption keys from server decrypt the message
                msg = eval(msg)
                text = msg[0]
                key = msg[1]
                d = key[0]
                n = key[1]
                text = str(text)
                text = eval(text)
                text = decrypt(text,d,n)

                #Add message to chat history
                if text:
                    text = eval(text)
                    name = text[0]
                    text = text[1]

                    if name == username+":":
                        self.history.update_chat_history(f'[color=dd2020] {name} [/color] > {text}')
                    else:
                        self.history.update_chat_history(f'[color=20dd20] {name} [/color] > {text}')
            except:
                pass
        else:
            pass

#Page To show a text only
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1

        self.message = Label(halign="center", valign="middle", font_size=30)

        self.message.bind(width=self.update_text_width)

        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


#Define Kivy Pages
class ShmeamailApp(App):
    def build(self):
        
        self.screen_manager = ScreenManager()

        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name='Chat')
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)


#Shows any error messages
def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = 'Info'
    Clock.schedule_once(sys.exit, 10)


#Run App
if __name__ == "__main__":
    chat_app = ShmeamailApp()
    chat_app.run()
