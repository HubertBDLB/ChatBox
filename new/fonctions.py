#_______________________________________________________________________
# Bibliothèque                              | Utilisation               |
#___________________________________________|___________________________|
from constantes import *                    # Constantes                |
import sys                                  # Quitter app & Chemins     |
import os                                   # Chemins & Commandes       |
from platform import system                 #                           |
from subprocess import check_call           #                           |
#___________________________________________|___________________________|


def copy_to_clipboard(text: str) -> str:
    """ Copie du texte dans le presse-papier """
    if system() == "Darwin": cmd='echo '+text.strip()+'|pbcopy'
    elif system() == "Windows":cmd='echo '+text.strip()+'|clip'
    return check_call(cmd, shell=True)


def resource_path(relative_path: str) -> str:
    """ Récupère le chemin absolu d'un chemin relatif d'une ressource """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


ICON_PATH = resource_path(IMAGES_PATH + "icon_256.ico")
LOGO_PATH = resource_path(IMAGES_PATH + "logo_192_64.png")
