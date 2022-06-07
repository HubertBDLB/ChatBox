#_______________________________________________________________________
# Bibliothèque                              | Utilisation               |
#___________________________________________|___________________________|
from constantes import *                    # Constantes                |
from fonctions import *                     # Fonctions                 |
import sys                                  # Quitter app & Chemins     |
import timeit                               # Calcul temps réponse      |
import socket                               # Lien Client - Serveur     |
import threading                            # Séparation des tâches     |
import tkinter                              # Interface                 |
import webbrowser                           # Mode d'emploi             |
from tkinter import simpledialog,scrolledtext,messagebox                #
#___________________________________________|___________________________|

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
        """ Création de la fenêtre """
        # Paramètres de la fenêtre
        self.win = tkinter.Tk()
        self.win.configure(bg=DARK_BLUE)
        self.win.title(VERSION)
        self.win.wm_iconbitmap(ICON_PATH)
        self.win.resizable(False,False)
        self.create_nickname_choice_gui()

        # Début de la boucle principale
        self.win.protocol("WM_DELETE_WINDOW",self.stop)
        self.win.mainloop()


    def nickname_choice(self,event = None):
        self.nickname = ""
        self.nickname = self.nickname_entry.get()
        if not self.is_nickname_valid(self.nickname):
            self.error_label.config(text="Le nom doit faire\nentre 3 et 16 caractères\nalphanumériques")
        else:
            self.create_server_choice_gui()

    def server_choice(self,event = None):
        if len(self.server_entry.get().rstrip()) > 0:
            self.host = self.server_entry.get()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            start = timeit.default_timer()

            self.connect_thread = threading.Thread(target=self.connect)
            self.connect_thread.start()

            while timeit.default_timer()-start < 5 and not self.connected:
                pass
            if timeit.default_timer()-start >= 5 and not self.connected:
                self.error_label.config(text=f"{self.host}:{self.port}\na mis trop de temps\npour répondre")

            # Ouverture de la fenêtre principale
            if self.connected:
                self.create_texting_gui()
                self.gui_done = True 
                threading.Thread(target=self.receive).start()


    # Création des interfaces

    def create_server_choice_gui(self):
        self.nickname_frame.destroy()
        self.server_frame = tkinter.Frame(
            self.win,
            bg=DARK_BLUE
            )

        self.server_choice_frame = tkinter.Frame(
            self.server_frame,
            bg=DARK_BLUE
            )

        self.server_label = tkinter.Label(
            self.server_frame,
            text="IP du serveur :",
            bg=DARK_BLUE,
            fg=WHITE,
            font=DEFAULT_FONT
            )

        self.server_entry = tkinter.Entry(
            self.server_choice_frame,
            font=DEFAULT_FONT
            )

        self.confirm_button = tkinter.Button(
            self.server_frame,
            text="Se connecter",
            bg=DARKER_BLUE,
            fg=WHITE,
            font=DEFAULT_FONT,
            command=self.server_choice
            )   

        self.error_label = tkinter.Label(
            self.server_frame,
            bg=DARK_BLUE,
            fg=ERROR_COLOR,
            font=DEFAULT_FONT
            )       

        # Affichage
   
        self.server_frame.pack(
            expand=True,
            fill=BOTH
            )

        self.server_label.pack(
            fill=BOTH,
            padx=10,pady=10
            )

        self.server_entry.pack(
            fill=BOTH,
            padx=10
            )

        self.server_choice_frame.pack(
            expand=True,
            fill=BOTH
            )

        servers = self.get_servers()
        if servers != ():
            for server in servers:
                tkinter.Button(
                    self.server_choice_frame,
                    text=server[1].rstrip('\n'),
                    command = lambda server = server : self.insert_in_server_entry(server[0]),
                    height=1
                    ).pack(fill=BOTH,padx=10)

        self.error_label.pack(fill=BOTH,padx=10,pady=10)
        self.confirm_button.pack(fill=BOTH,padx=10,pady=10)

        self.server_entry.bind("<Return>", self.server_choice)                                                                                              


    def create_nickname_choice_gui(self):

        self.logo = tkinter.PhotoImage(file=LOGO_PATH)

        self.nickname_frame = tkinter.Frame(
            self.win,
            bg=DARK_BLUE
            )

        self.nickname_label = tkinter.Label(
            self.nickname_frame,
            text = "Choisissez un nom",
            bg=DARK_BLUE,
            fg=WHITE,
            font=DEFAULT_FONT
            )

        self.nickname_entry = tkinter.Entry(
            self.nickname_frame,
            font=DEFAULT_FONT
            )

        self.confirm_button = tkinter.Button(
            self.nickname_frame,
            text="Continuer",
            bg=DARKER_BLUE,
            fg=WHITE,
            font=DEFAULT_FONT,
            command=self.nickname_choice
            )

        self.error_label = tkinter.Label(
            self.nickname_frame,
            bg=DARK_BLUE,
            fg=ERROR_COLOR,
            font=DEFAULT_FONT
            )

        self.nickname_entry.bind("<Return>", self.nickname_choice)

        tkinter.Label(self.nickname_frame,image=self.logo,bg=DARK_BLUE).pack()
        self.nickname_frame.pack(expand=True,fill=BOTH)
        self.nickname_label.pack(fill=BOTH,padx=10,pady=10)
        self.nickname_entry.pack(fill=BOTH,padx=10,pady=10)
        self.error_label.pack(fill=BOTH,padx=10,pady=10)
        self.confirm_button.pack(fill=BOTH,padx=10,pady=10)


    def create_texting_gui(self):
        self.server_frame.destroy()
        self.win.state('zoomed') # Plein écran
        self.win.resizable(True,True)
        self.win.bind("<Control_L><Return>", self.write) # Ctrl+Entrée envoie le message

        # Importance relative des lignes et colonnes
        self.win.grid_rowconfigure(1,weight=1)
        self.win.grid_columnconfigure(0,weight=1)
        self.win.grid_columnconfigure(1,weight=0)

        # Widgets
        self.text_area = scrolledtext.ScrolledText(
            self.win,
            font = DEFAULT_FONT
            )

        self.input_area = tkinter.Text(
            self.win,
            height=3
            )

        self.send_button = tkinter.Button(
            self.win,
            height=3,
            text="Envoyer",
            command=self.write
            )

        self.menu = tkinter.Menu(
            self.win
            )

        self.menu.add_command(
            label="Mode d'emploi",
            command=lambda: webbrowser.open(WEBSITE_PATH)
            )

        if self.host not in self.get_servers(ip_only=True):
            self.menu.add_command(label= "Ajouter aux favoris ☆", command=self.register_server)
        else:
            self.menu.add_command(label= "Supprimer des favoris ★", command=self.unregister_server)

        self.win.config(menu=self.menu)
        
        # Affichage des widgets
        tkinter.Label(self.win,image=self.logo,bg=DARK_BLUE).grid(column=0,row=0,columnspan=2)
        self.text_area.grid(column=0,row=1,columnspan=2,sticky="nesw")    
        self.input_area.grid(column=0,row=2,sticky="nesw")                
        self.send_button.grid(column=1,row=2,sticky="nesw")               

        self.text_area.config(state="disabled")


    # Communication


    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
        except:
            self.error_label.config(text=f"Impossible de se\nconnecter au serveur\n{self.host}:{self.port}")


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

                elif message == "[nickname_already_taken]": #FIXME Redemander nom si invalide
                    self.log("[Nom déjà pris.\nVeuillez redémarrer l'application]")

                elif message == "[address_banned]":
                    self.log("[Vous avez été banni]")

                elif self.gui_done:
                    self.text_area.config(state="normal")
                    self.log(message)

            except Exception:
                self.sock.close()
                break


    # Fonctions utiles


    def insert_in_server_entry(self, ip: str):
        self.server_entry.delete(0, END)
        self.server_entry.insert(0, ip)


    def get_servers(self,ip_only: bool = False) -> list:
        """ Récupère un serveur parmis les favoris """
        with open("servers.txt","r") as f:
            if ip_only:
                ips = []
                for server in f.readlines()[1:]:
                    ips.append(server.split(";")[0])
                return ips
            else:
                servers = []
                for server in f.readlines()[1:]:
                    server_tuple = tuple(server.split(";"))
                    servers.append(server_tuple)
                return servers


    def register_server(self):
        """ Enregistre un serveur aux favoris """
        with open("servers.txt","a") as f:
            if self.host not in self.get_servers(ip_only=True):
                f.write(f"{self.host};{simpledialog.askstring('Ajouter aux favoris','Choisissez un nom pour le serveur')}\n")
                self.log("[Serveur ajouté aux favoris]")
                self.menu.delete(2,2)
                self.menu.add_command(label="Supprimer des favoris ★", command=self.unregister_server)


    def unregister_server(self):
        """ Supprimer un serveur des favoris"""
        with open("servers.txt","r") as f:
            lines = f.readlines()
        
        # Récupère la ligne à supprimer
        for number, line in enumerate(lines):
            if line.split(";")[0] == self.host:
                line_to_remove = number

        # Réécrit tout le fichier sauf la ligne à supprimer
        with open("servers.txt","w") as f:
            for number, line in enumerate(lines):
                if number != line_to_remove:
                    f.write(line)

        self.menu.delete(2,2)
        self.menu.add_command(label="Ajouter aux favoris ☆", command=self.register_server)


    def log(self,message):

        if message.startswith("<"):
            for letter in range(len(message)):
                if message[letter] == ">":
                    break
            self.text_area.insert("end",'\n' + message[1:letter],"bold")
            self.text_area.insert("end",message[letter+1:])
        # FIXME elif "@" + self.nickname in message: self.text_area.insert("end", message,"mention")
        elif message.startswith(self.nickname): self.text_area.insert("end", message,"own_msg")
        elif message.startswith("["): self.text_area.insert("end", message,"msg_info")
        elif message.startswith("*"): self.text_area.insert("end",message[1:],"bold")
        elif message.startswith("!"): self.text_area.insert("end",message[1:],"big")
        elif message.startswith("_"): self.text_area.insert("end",message[1:],"underlined")
        elif message.startswith("-"): self.text_area.insert("end",message[1:],"italic")
        elif message.startswith("/!\\"): self.text_area.insert("end",message[3:],"warning")
        elif message.startswith("&"): self.text_area.insert("end",message[1:],"red")
        else: self.text_area.insert("end",message)

        self.text_area.tag_config("mention",background=PALE_YELLOW)
        self.text_area.tag_config("msg_info",foreground=DARK_BLUE,font=BOLD_FONT) 
        self.text_area.tag_config("own_msg",background=LIGHT_GRAY)
        self.text_area.tag_config("bold",font=BOLD_FONT)
        self.text_area.tag_config("big",font=BIG_FONT)
        self.text_area.tag_config("underlined",font=UNDERLINED_FONT)
        self.text_area.tag_config("italic",font=ITALIC_FONT)
        self.text_area.tag_config("warning",foreground=RED,font=BIG_FONT)
        self.text_area.tag_config("red",foreground=RED)
        self.text_area.yview("end")
        self.text_area.config(state="disabled")

        # Surligne nom
        # start = self.text_area.index('1.0')
        # end = self.text_area.index('end')
        # self.text_area.mark_set("matchStart", start)
        # self.text_area.mark_set("matchEnd", start)
        # self.text_area.mark_set("searchLimit", end)

        # count = tkinter.IntVar()
        # while True:
        #     index = self.text_area.search(
        #         "\\<.*\\>",
        #         "matchEnd",
        #         "searchLimit",
        #         count=count,
        #         regexp=True
        #         )

        #     if index == "": break
        #     if count.get() == 0: break # degenerate pattern which matches zero-length strings
        #     self.text_area.mark_set("matchStart", index)
        #     self.text_area.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
        #     self.text_area.tag_add("bold", "matchStart", "matchEnd")


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
        sys.exit(1)
