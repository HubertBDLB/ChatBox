
WEBSITE_PATH = "https://hubertbdlb.github.io/chatbox/"

GITHUB_PATH = "https://raw.githubusercontent.com/HubertBDLB/ChatBox/main/"

README_PATH = "https://github.com/HubertBDLB/ChatBox/blob/main/README.md"

RAW_README_PATH = GITHUB_PATH + "README.md"

IMAGES_PATH = "images/"

VERSION = "ChatBox v3.9"

NEW_LINE_CHAR = """
"""

INVITE_MESSAGE = f"Installe {VERSION} depuis {README_PATH}"

HELP_MESSAGE = """Liste des commandes :
/help                       : Affiche ce message
/help2                      : Affiche le message d'aide concernant la syntaxe
/kick <nom>                 : Exclu un client
/ban <nom>                  : Banni un client
/blacklist                  : Affiche la liste des adresse bannies
/broadcast | /br <message>  : Envoie un message à tous les clients
/msg <nom> <message>        : Envoie un message à un client donné
/list                       : Affiche la liste des clients connectés
/stop                       : Eteint le serveur (demande confirmation)
/ip                         : Affiche l'ip et le port du serveur
/invite                     : Copie un message d'invitation dans le presse-papier
"""

SYNTAX_HELP_MESSAGE = """Avec les commandes /broadcast | /br et /msg | /w :
Avant le message :
*   : Gras
_   : Souligné
-   : Italique
[   : Gras et bleu
!   : Gros (16 -> 32)
/!\ : Gros et rouge
&   : Rouge
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
DISABLED = "disabled"
ENABLED = "normal"
END = "end"

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
ERROR_COLOR = "#ffe784"