# coding: utf-8
# ChatBox v3.3
# derniere modification : 04/05/2022

# A FAIRE :
#   - Changer pseudo si déjà pris (Actuellement refuse la connection)
#   - Ajouter un système de mise à jour automatique (EN COURS)
#   - Messages d'erreurs des commandes incomplètes (QUASIMENT FINI)
#   - Echanger Ctrl Entree / Entree
#   - Nom et ip confirmées en appuyant sur Entrée
#   - R.S.A. (tout dépend d'Antonin)


#------------------------------------------------------------------------------------
#                                      BIBLIOTHEQUES
#------------------------------------------------------------------------------------

import sys
import os
import timeit
import socket
import threading
import tkinter
from tkinter import scrolledtext, messagebox
import requests

 



#------------------------------------------------------------------------------------
#                                      CONSTANTES
#------------------------------------------------------------------------------------

HELP_MESSAGE = """Liste des commandes :
/help                       : Affiche ce message
/help_syntax                : Affiche le message d'aide concernant la syntaxe
/kick <nom>                 : Exclu un client
/ban <nom>                  : Banni un client
/blacklist                  : Affiche la liste des adresse bannies
/broadcast | /br <message>  : Envoie un message à tous les clients
/msg | /w <nom> <message>   : Envoie un message à un client donné
/online | /list             : Affiche la liste des clients connectés
/close | /stop              : Eteint le serveur (demande confirmation)
/ip                         : Affiche l'ip et le port du serveur
"""

SYNTAX_HELP_MESSAGE = """Avec les commandes /broadcast | /br et /msg | /w :
Avant le message :
*   : Gras
_   : Souligné
-   : Italique
[   : Gras et bleu
!   : Gros (16 -> 32)
/!\ : Gros et rouge
"""

NEW_LINE_CHAR = """
"""

MONO_FONT = ("Courier New",20)
BASE_FONT = "Helvetica"
DEFAULT_FONT = (BASE_FONT,16)
BOLD_FONT = (BASE_FONT,16,"bold")
BIG_FONT = (BASE_FONT,32,"bold")
UNDERLINED_FONT = (BASE_FONT,16,"underline")
ITALIC_FONT = (BASE_FONT,16,"italic")

TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"
X = "x"
Y = "y"
BOTH = "both"

RED = "#ff0000"
DARK_BLUE = "#004080"
DARKER_BLUE = "#003070"
INVERTED_DARK_BLUE = "#FFBF7F"
WHITE = "#ffffff"
LIGHT_GRAY = "#dddddd"
GRAY = "#888888"
DARK_GRAY = "#222222"
BLACK = "#000000"
PALE_YELLOW = "#e0e090"

GITHUB_PATH = "https://raw.githubusercontent.com/HubertBDLB/ChatBox/main/main.py"

VERSION = "ChatBox v3.3"

#------------------------------------------------------------------------------------
#                                      FONCTIONS
#------------------------------------------------------------------------------------
def update():
    r = requests.get(GITHUB_PATH)
    with open("last_version.py", 'wb') as f:    
        f.write(r.content)
    
    with open("last_version.py") as f:
        lines = f.read()
        if lines.split('\n')[1] != ("# " + VERSION):
            print('NEW VERSION')
        else:
            print('ALREADY UPDATED')

def resource_path(relative_path):
    """Récupère le chemin absolu d'un chemin relatif d'une ressource"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def start_server():
    """Démarre une instance de la classe SERVER"""
    window.destroy()
    SERVER()

def start_client():
    """Démarre une instance de la classe CLIENT"""
    window.destroy()
    CLIENT()

ICON_PATH = resource_path("icon.ico")
LOGO_PATH = resource_path("logo.png")




#------------------------------------------------------------------------------------
#                                       SERVEUR
#------------------------------------------------------------------------------------

class SERVER:
    def __init__(self):
        self.host = socket.gethostbyname_ex(socket.getfqdn())[2][1]
        self.port = 9090
        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        
        self.server.listen()

        self.blacklist = [] 
        self.clients = {} # dictionnaire socket : surnom 

        while not self.gui_done:
            pass
        if self.gui_done:
            self.log(f"Le serveur {self.host}:{self.port} est en ligne\n")
            self.receive()

    def gui_loop(self):
        """Construit l'interface"""
        self.win = tkinter.Tk()
        self.win.configure(bg=DARK_BLUE)
        self.win.title("Serveur")
        self.win.wm_iconbitmap(ICON_PATH)
        self.logo = tkinter.PhotoImage(file=LOGO_PATH)
        self.win.bind("<Control_L><Return>", self.execute) # Ctrl+Entrée envoie le message

        self.text_frame = tkinter.Frame(self.win,bg=DARK_BLUE)
        self.text_area = scrolledtext.ScrolledText(self.text_frame,font = MONO_FONT)
        self.input_area = tkinter.Text(self.text_frame,height=3)
        self.send_button = tkinter.Button(self.text_frame,height=3,text="Envoyer",command=self.execute)
        
        self.text_frame.pack(expand=True)
        tkinter.Label(self.text_frame,image=self.logo,bg=DARK_BLUE).grid(column=0,row=0,columnspan=2)
        self.text_area.grid(column=0,row=1,columnspan=2,sticky="nesw")    
        self.input_area.grid(column=0,row=2,sticky="nesw")                
        self.send_button.grid(column=1,row=2,sticky="nesw")               

        self.text_area.config(state="disabled")

        self.gui_done = True
        self.win.protocol('WM_DELETE_WINDOW',self.stop)
        self.win.mainloop()

    # Commandes
    
    def execute(self,event = None):
        """execute les commandes admin"""
        message = self.input_area.get('1.0','end')

        if message.startswith("/"):
            self.log(message,"command")
            command = message.split()[0][1:]
            parameter = message[(len(command)+2):]
            
            if command in ["help"]:
                self.log(HELP_MESSAGE,"command_result")

            elif command in ["help_syntax"]:
                self.log(SYNTAX_HELP_MESSAGE,"command_result")

            elif command in ["kick"]:
                try:
                    self.kick(parameter.replace(NEW_LINE_CHAR,''))
                except Exception as e:
                    self.log(e,"error")
                    
            elif command in ["broadcast","br"]:
                self.broadcast(parameter)

            elif command in ["close","stop"]:
                self.stop()
            
            elif command in ["online","list"]:
                self.log_online_members()

            elif command in ["ban"]:
                client_name = parameter.split()[0]
                self.ban(client_name)

            elif command in ["msg","w"]:
                try:
                    client_name = parameter.split()[0]
                    msg = parameter[len(client_name)+1:]
                    client = self.get_socket_from_name(client_name)
                    client.send(msg.encode("utf-8"))
                    self.log(f"Message envoyé\n","command_result")
                except ValueError:
                    self.log(f"ERREUR : {client_name} n'est pas connecté\n","error")
                except IndexError:
                    self.log(f"ERREUR : Syntaxe : /msg | /w <nom>\n","error")

            elif command in ["ip"]:
                self.log(f"{self.host}:{self.port}","command_result")

            elif command in ["blacklist"]:
                self.log_banned_clients()

            else:
                self.log("Cette commande n'existe pas.\nAfficher la liste des commandes : /help\n","command_result")
        else:
            self.log(message)

    def get_socket_from_name(self,name):
        """Renvoie un socket a partir du nom du client associé"""
        sockets_list = list(self.clients.keys())
        nicknames_list = list(self.clients.values())
        socket = sockets_list[nicknames_list.index(name)]
        return socket  

    def log(self,message,message_type = None): # message_type est une chaine de caractère
        """Affiche un message dans la zone de texte"""
        self.text_area.config(state="normal")

        if message_type == None: # pas de type précisé
            self.text_area.insert('end', (message))

        else:
            self.text_area.insert('end', message,message_type)

            if message_type == "user_msg":
                self.text_area.tag_config("user_msg",background="#ddd")

            if message_type == "command":
                self.text_area.tag_config("command",foreground="#0a0")

            if message_type == "command_result":
                self.text_area.tag_config("command_result",background = "#eee", foreground="#0a0")
          
            if message_type == "error":
                self.text_area.tag_config("error",foreground="#f00")

        self.text_area.config(state="disabled")
        self.input_area.delete('1.0','end')
        self.text_area.yview("end")
    
    def get_online_members(self,names_only = False):
        online_members = ""
        if self.clients == {}: 
            online_members = "Aucun client connecté\n"

        for client in self.clients:
            client_name = self.clients[client]
            member_address = client.getpeername()
            if names_only:
                online_members += f"{client_name}"
            else:
                online_members += f"{client_name} : {member_address[0]}:{member_address[1]}\n"
        return online_members

    def log_online_members(self):
        self.log(self.get_online_members(names_only = False),"command_result")

    def log_banned_clients(self):
        self.log(str(self.blacklist),"command_result")

    def ban(self,name):
        """Kick et refuse les tentatives de connection d'un client donné"""
        client = self.get_socket_from_name(name)
        banned_ip = client.getpeername()[0]

        self.broadcast(f"[{name} a été banni]\n")
        
        self.blacklist.append(banned_ip)
        client.close()
        
        if self.clients != {}:
            for c in self.clients:
                if c.getpeername()[0] == banned_ip:
                    c.close()

    def kick(self,name):
        """Arrête le thread handle d'un client en particulier"""
        socket = self.get_socket_from_name(name)
        socket.send('[Vous avez été exclu]'.encode("utf-8"))
        self.log(f"{name} a été exclu\n","command_result")
        socket.close()

    def stop(self,force = False):
        """Eteint le serveur en demandant confirmation"""

        if force:
            self.broadcast("[Le serveur est fermé]\n")
            self.win.destroy()
            self.running = False
            self.server.close()
            exit(0)
        
        elif messagebox.askokcancel("Quitter", "Voulez vous éteindre le serveur ?"):
            self.broadcast("[Le serveur est fermé]\n")
            self.win.destroy()
            self.running = False
            self.server.close()
            exit(0)

    # Communication

    def broadcast(self,message):
        """Envoie un message donné à tous les clients"""
        self.log(message,"user_msg")
        for client in self.clients:
            try:
                client.send(message.encode("utf-8"))
            except:
                self.log(f"ERREUR : Le message n’a pas pu être envoyé\n","error")

    def handle(self,client):
        """Reçoit et broadcast les messages que chaque client envoie"""
        while self.running:
            nom_client = self.clients[client]
            try:
                raw_message = client.recv(1024).decode('utf-8')
                message = f"{nom_client}\n{raw_message}"
                self.broadcast(message)

            except: # client deconnecté
                self.clients.pop(client)
                self.log(f"DEPART : {nom_client} est parti\n","error")
                self.broadcast(f"[{nom_client} est parti]\n")
                client.close()
                break

    def receive(self):
        """Accepte les tentatives de connection des clients"""
        while self.running:
            try:
                client, address = self.server.accept()
            except:
                self.stop(force=True)

            self.log(f"le client {address[0]}:{address[1]} a tenté de se connecter au serveur\n")

            client.send(("[asking_nickname]").encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            if address[0] not in self.blacklist:
                if nickname not in self.clients.values(): # Si ce nom n'est pas déjà pris
                    self.clients[client] = nickname

                    self.log(f"{address[0]}:{address[1]} a pour surnom : <{nickname}>\n")
                    self.broadcast(f"[{nickname} s’est connecté au serveur]\n")
                
                    thread = threading.Thread(target=self.handle, args=(client,))
                    thread.start()
                else:
                    client.send(("[nickname_already_taken]").encode("utf-8"))
            else:
                client.send(("[address_banned]").encode("utf-8"))




#------------------------------------------------------------------------------------
#                                      CLIENT
#------------------------------------------------------------------------------------

class CLIENT:
    def __init__(self):
        self.gui_done = False
        self.connected = False
        self.running =  True
        self.sock = None
        self.host = None
        self.port = 9090
        self.gui_loop()

    # Gestion de la fenêtre

    def gui_loop(self):
        # Paramètres de la fenêtre
        self.win = tkinter.Tk()
        self.win.configure(bg=DARK_BLUE)
        self.win.title("ChatBox")
        self.win.wm_iconbitmap(ICON_PATH)
        self.create_nickname_choice_gui()

        self.win.protocol("WM_DELETE_WINDOW",self.stop)
        self.win.mainloop()

    def nickname_choice(self):
        self.nickname = ""
        self.nickname = self.nickname_entry.get()
        if self.is_nickname_valid(self.nickname):
            self.create_server_choice_gui()
        else:
            self.error_label.config(text="Le nom doit faire entre 3 et 16 caractères et ne\ncomporter que des caractères alphanumériques")

    def server_choice(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = self.server_entry.get()

        start = timeit.default_timer()

        self.connect_thread = threading.Thread(target=self.connect)
        self.connect_thread.start()

        while timeit.default_timer()-start < 4 and not self.connected:
            pass
        if timeit.default_timer()-start >= 4 and not self.connected:
            self.error_label.config(text=f"{self.host}:{self.port} a mis trop de temps pour répondre")

        # Ouverture de la fenêtre principale
        if self.connected:
            self.create_texting_gui()
            self.gui_done = True 
            threading.Thread(target=self.receive).start()

    # Création des interfaces

    def create_nickname_choice_gui(self):
        self.win.maxsize(500,290)
        self.logo = tkinter.PhotoImage(file=LOGO_PATH)
        tkinter.Label(image=self.logo,bg=DARK_BLUE).pack()
        self.nickname_frame = tkinter.Frame(self.win,bg=DARK_BLUE)
        self.nickname_label = tkinter.Label(self.nickname_frame,text = "Choisissez un nom",bg=DARK_BLUE,fg=WHITE,font=DEFAULT_FONT)
        self.nickname_entry = tkinter.Entry(self.nickname_frame,font=DEFAULT_FONT)
        self.confirm_button = tkinter.Button(self.nickname_frame,text="Continuer",bg=DARKER_BLUE,fg=WHITE,font=DEFAULT_FONT,command=self.nickname_choice)
        self.error_label = tkinter.Label(self.nickname_frame,bg=WHITE,fg=RED,font=DEFAULT_FONT)

        self.nickname_frame.pack(expand=True,fill=BOTH)
        self.nickname_label.pack(fill=BOTH,padx=10,pady=10)
        self.nickname_entry.pack(fill=BOTH,padx=10,pady=10)
        self.error_label.pack(fill=BOTH,padx=10,pady=10)
        self.confirm_button.pack(fill=BOTH,padx=10,pady=10)

    def create_server_choice_gui(self):
        self.nickname_frame.destroy()
        self.server_frame = tkinter.Frame(self.win,bg=DARK_BLUE)
        self.server_label = tkinter.Label(self.server_frame,text = "IP du serveur :",bg=DARK_BLUE,fg=WHITE,font=DEFAULT_FONT)
        self.server_entry = tkinter.Entry(self.server_frame,font=DEFAULT_FONT)
        self.confirm_button = tkinter.Button(self.server_frame,text="Se connecter",bg=DARKER_BLUE,fg=WHITE,font=DEFAULT_FONT,command=self.server_choice)
        self.error_label = tkinter.Label(self.server_frame,bg=WHITE,fg=RED,font=DEFAULT_FONT)

        self.server_frame.pack(expand=True,fill=BOTH)
        self.server_label.pack(fill=BOTH,padx=10,pady=10)
        self.server_entry.pack(fill=Y,padx=10,pady=10)
        self.error_label.pack(fill=BOTH,padx=10,pady=10)
        self.confirm_button.pack(fill=BOTH,padx=10,pady=10)

    def create_texting_gui(self):
        self.server_frame.destroy() # Effacement du contenu de la fenêtre
        self.win.maxsize(2000,2000)
        self.win.minsize(650,650)
        self.win.state('zoomed') # Plein écran

        self.text_frame = tkinter.Frame(self.win,bg=DARK_BLUE)
        self.text_area = scrolledtext.ScrolledText(self.text_frame,font = MONO_FONT)
        self.input_area = tkinter.Text(self.text_frame,height=3)
        self.send_button = tkinter.Button(self.text_frame,height=3,text="Envoyer",command=self.write)
        
        self.text_frame.pack(expand=True)
        tkinter.Label(self.text_frame,image=self.logo,bg=DARK_BLUE).grid(column=0,row=0,columnspan=2)
        self.text_area.grid(column=0,row=1,columnspan=2,sticky="nesw")    
        self.input_area.grid(column=0,row=2,sticky="nesw")                
        self.send_button.grid(column=1,row=2,sticky="nesw")               

        self.text_area.config(state="disabled")
        self.win.bind("<Control_L><Return>", self.write) # Ctrl+Entrée envoie le message

    # Communication

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
        except Exception as e:
            self.error_label.config(text=f"Impossible de se connecter au serveur\n{self.host}:{self.port}")
            print(e)
            
    def write(self, event = None):
        input = self.input_area.get("1.0","end")
        if len(input.replace(" ","").replace(NEW_LINE_CHAR,"")) != 0:
            message = self.input_area.get("1.0","end")
            self.sock.send(message.encode("utf-8"))
            self.input_area.delete("1.0","end")
    
    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode("utf-8")

                if message == "[asking_nickname]":
                    self.sock.send(self.nickname.encode("utf-8"))
                
                elif message == "[nickname_already_taken]": #FIXME
                    self.log("[Nom déjà pris.\nVeuillez redémarrer l'application]")

                elif message == "[address_banned]":
                    self.log("[Vous avez été banni]")

                elif self.gui_done:
                    self.text_area.config(state="normal")
                    self.log(message)

                    # Ajoute photo de profil 
                    #self.text_area.image_create("end",image=self.profile_pic)
                    # FIXME: La photo de profil du client est affiché sur tous les messages (envoyés ET reçus)
                    # FIXME: La photo de profil doit faire 32x32 peu importe sa taille originale

                    # Surligne mentions et messages informatifs
                    

            except Exception:
                self.sock.close()
                break

    # Fonctions utiles

    def log(self,message):
        if "@" + self.nickname in message:
            self.text_area.insert("end", message,"mention")
                        
        elif message.startswith(self.nickname):
            self.text_area.insert("end", message,"own_msg")

        elif message.startswith("["):
            self.text_area.insert("end", message,"msg_info")
            
        elif message.startswith("*"):
            self.text_area.insert("end",message[1:],"bold")

        elif message.startswith("!"):
            self.text_area.insert("end",message[1:],"big")

        elif message.startswith("_"):
            self.text_area.insert("end",message[1:],"underlined")

        elif message.startswith("-"):
            self.text_area.insert("end",message[1:],"italic")

        elif message.startswith("/!\\"):
            self.text_area.insert("end",message[3:],"warning")

        else:
            self.text_area.insert("end",message)

        self.text_area.tag_config("mention",background=PALE_YELLOW)
        self.text_area.tag_config("msg_info",foreground=DARK_BLUE,font=BOLD_FONT) 
        self.text_area.tag_config("own_msg",background=LIGHT_GRAY)
        self.text_area.tag_config("bold",font=BOLD_FONT)
        self.text_area.tag_config("big",font=BIG_FONT)
        self.text_area.tag_config("underlined",font=UNDERLINED_FONT)
        self.text_area.tag_config("italic",font=ITALIC_FONT)
        self.text_area.tag_config("warning",foreground=RED,font=BIG_FONT)

        self.text_area.yview("end")
        self.text_area.config(state="disabled")

    def is_nickname_valid(self,nickname):
        if len(nickname) < 17 and len(nickname) > 2 and nickname.isalnum(): # alphanumérique et entre 3 et 16 caractères
            return True
        else:
            return False

    def stop(self):
        if messagebox.askokcancel("Quitter", "Voulez vous vraiment quitter ?"):
            self.force_stop()

    def force_stop(self):
        self.win.destroy()
        if self.sock != None:
            self.sock.close()
        self.running = False
        exit(0)




#------------------------------------------------------------------------------------
#                                       CHOIX SERVEUR CLIENT
#------------------------------------------------------------------------------------
update()
window = tkinter.Tk()
window.configure(bg=DARK_BLUE)
window.geometry("400x200")
window.eval("tk::PlaceWindow . center")
window.maxsize(400,200)
window.minsize(400,200)
window.wm_iconbitmap(ICON_PATH)

logo = tkinter.PhotoImage(file=LOGO_PATH)

widgets = [
    tkinter.Label(window,image=logo,bg=DARK_BLUE),
    tkinter.Button(window,text="Créer un serveur",padx=10,pady=10,bg=DARK_BLUE,fg=WHITE,font=DEFAULT_FONT,command=start_server),
    tkinter.Button(window,text="Rejoindre un serveur",padx=10,pady=10,bg=DARK_BLUE,fg=WHITE,font=DEFAULT_FONT,command=start_client)
    ]

for w in widgets:
    w.pack(expand=True,fill=BOTH)

window.mainloop()
