#_______________________________________________________________________
# Bibliothèque                              | Utilisation               |
#___________________________________________|___________________________|
from constantes import *                    # Constantes                |
from fonctions import *                     # Fonctions                 |
import sys                                  # Quitter app & Chemins     |
import socket                               # Lien Client - Serveur     |
import threading                            # Séparation des tâches     |
import tkinter                              # Interface                 |
from tkinter import scrolledtext,messagebox #                           |
#___________________________________________|___________________________|

class SERVER:
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.host = s.getsockname()[0]
        s.close()
        self.port = 9090
        self.gui_done = False
        self.running = True

        try: 
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('',self.port))
        except: # Si serveur déjà existant : fermer l'application
            self.stop(force=True)

        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()

        self.server.listen()
        self.blacklist = [] 
        self.clients = {} # dictionnaire socket : surnom 

        while not self.gui_done:
            pass
        if self.gui_done:
            self.log(f"Le serveur {self.host}:{self.port} est en ligne\n")
            self.log(HELP_MESSAGE,"command_result")
            self.receive()


    def gui_loop(self):
        """ Construit l'interface """
        self.win = tkinter.Tk()
        self.win.configure(bg=DARK_BLUE)
        self.win.title(VERSION + " - Hôte")
        self.win.wm_iconbitmap(ICON_PATH)
        self.logo = tkinter.PhotoImage(file=LOGO_PATH)
        self.win.bind("<Control_L><Return>", self.execute) # Ctrl+Entrée envoie le message

        # Importance relative des lignes et colonnes
        self.win.grid_rowconfigure(1,weight=1)
        self.win.grid_columnconfigure(0,weight=1)
        self.win.grid_columnconfigure(1,weight=0)

        # Widgets
        self.text_area = scrolledtext.ScrolledText(
            self.win,
            font = MONO_FONT
            )

        self.input_area = tkinter.Text(
            self.win,
            height=3
            )

        self.send_button = tkinter.Button(
            self.win,
            height=3,
            text="Envoyer",
            command=self.execute,
            width=15)
        
        # Affichage des widgets
        tkinter.Label(
            self.win,
            image=self.logo,
            bg=DARK_BLUE
            ).grid(
                column=0,
                row=0,
                columnspan=2
                )

        self.text_area.grid(
            column=0,
            row=1,
            columnspan=2,
            sticky="nesw"
            )

        self.input_area.grid(
            column=0,
            row=2,
            sticky="nesw"
            )            

        self.send_button.grid(
            column=1,
            row=2,
            sticky="nesw"
            )               

        self.text_area.config(state="disabled")
        self.win.protocol('WM_DELETE_WINDOW',self.stop)
        self.gui_done = True
        self.win.mainloop()


    # Commandes
    

    def execute(self,event = None):
        """ Détecte et execute les commandes """
        message = self.input_area.get('1.0','end')

        # Si une commande
        if message.startswith("/"):
            self.log(message,"command")
            command = message.split()[0][1:]
            parameter = message[(len(command)+2):]
            
            if command in ["help"]:
                try: self.log(HELP_MESSAGE,"command_result")
                except Exception as e: self.log(f"ERREUR : {e}\n","error")

            elif command in ["help2"]:
                try: self.log(SYNTAX_HELP_MESSAGE,"command_result")
                except Exception as e: self.log(f"ERREUR : {e}\n","error")

            elif command in ["kick"]:
                try: self.kick(parameter.replace(NEW_LINE_CHAR,''))
                except Exception as e: self.log(f"ERREUR : {e}\n","error")
                    
            elif command in ["broadcast","br"]:
                try: self.broadcast(parameter)
                except Exception as e: self.log(e,"error")
                
            elif command in ["stop"]:
                try: self.stop()
                except Exception as e: self.log(e,"error")

            elif command in ["list"]:
                try: self.log_online_members()
                except Exception as e: self.log(e,"error")

            elif command in ["ban"]:
                try: self.ban(parameter.split()[0])
                except Exception as e: self.log(e,"error")

            elif command in ["msg"]:
                try: self.msg(parameter.split()[0],parameter[len(parameter.split()[0])+1:])
                except Exception as e: self.log(e,"error")

            elif command in ["ip"]:
                try: self.log(f"{self.host}:{self.port}\n","command_result")
                except Exception as e: self.log(e,"error")

            elif command in ["blacklist"]:
                try: self.log_banned_clients()
                except Exception as e: self.log(e,"error")

            elif command in ["invite"]:
                try: 
                    self.log("L'invitation a été copiée dans le presse-papier\n","command_result")
                    copy_to_clipboard(INVITE_MESSAGE)
                except Exception as e: self.log(e,"error")

            else: # Commande inexistante
                self.log("Cette commande n'existe pas.\nAfficher la liste des commandes : /help\n","command_result")
        else:
            self.broadcast("&[ADMIN]\n" + message)


    def get_socket_from_name(self,name: str) -> socket.socket:
        """ Renvoie un socket a partir du nom du client associé """
        sockets_list = list(self.clients.keys())
        nicknames_list = list(self.clients.values())
        socket = sockets_list[nicknames_list.index(name)]
        return socket  


    def log(self,message: str,message_type: str = None):
        """ Affiche un message dans la zone de texte """
        self.text_area.config(state="normal")

        if message_type == None:
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
    

    def msg(self,name: str,message: str):
        try:
            self.get_socket_from_name(name).send(message.encode("utf-8"))
            self.log(f"Message envoyé\n","command_result")

        except ValueError:
            self.log(f"ERREUR : {name} n'est pas connecté\n","error")

        except IndexError:
            self.log(f"ERREUR : Syntaxe : /msg | /w <nom>\n","error")


    def get_online_members(self,names_only: bool = False):
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


    def log_online_members(self,names_only:bool = False):
        """Affiche la liste des membres connectés"""
        self.log(self.get_online_members(names_only),"command_result")


    def log_banned_clients(self):
        if self.blacklist == []:
            self.log("La liste noire est vide\n","command_result")
        else: 
            self.log(str(self.blacklist) + '\n',"command_result")


    def ban(self,name: str):
        """Kick et refuse les tentatives de connection d'un client donné"""
        client = self.get_socket_from_name(name)
        banned_ip = client.getpeername()[0]

        self.broadcast(f"[{name} a été banni]\n")
        
        self.blacklist.append(banned_ip)
        client.close()
        
        # Ban des doubles comptes
        if self.clients != {}:
            for c in self.clients:
                if c.getpeername()[0] == banned_ip:
                    c.close()


    def kick(self,name: str):
        """Arrête le thread handle d'un client en particulier"""
        socket = self.get_socket_from_name(name)
        socket.send('[Vous avez été exclu]'.encode("utf-8"))
        self.log(f"{name} a été exclu\n","command_result")
        socket.close()


    def stop(self,force: bool = False):
        """Eteint le serveur en demandant confirmation"""
        if force:
            stop = True
        else:
            stop = messagebox.askokcancel("Quitter", "Voulez vous éteindre le serveur ?")

        if stop:
            try: self.broadcast("[Le serveur est fermé]\n")
            except: pass

            try: self.win.destroy()
            except: pass

            self.running = False
            self.server.close()
            sys.exit(1)


    # Communication


    def broadcast(self,message: str):
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
                message = f"<{nom_client}>\n{raw_message}"
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
