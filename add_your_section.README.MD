# Comment rajouter une section
## Dans votre inventaire
```sh
[section enable=1 other=onevalue]
name param1=value1 param2=value2
othername param1=othervalue
```
Attention, le parser est sensible aux espaces pour separer les
key=value de chacune des lignes mais aussi de la conf de la
section

## Dans bbox_cli.py
La section se cree dans le dossier bbox/section, mais dans ce
fichier, il faut rajouter l'import avec les autres, ex:
```sh
from bbox.section.dyndns import DyndnsManager
```
A la ligne limits = ('wifi','host', ...),
rajouter le nom de la section, ex: dyndns
​
## Dans le dossier bbox/section
Creer un fichier du nom de votre section, ex: dyndns.py
Il devra etre formate comme suit:
```sh
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
​
from dataclasses import dataclass, asdict
​
# Dataclass definissant un object de la bbox, ex: Host ou Fwv4 definissant une regle de firewall
# Les slots ne sont pas obligatoires, c'est plus leger en memoire mais cette option des dataclasses
# n'arrive qu'a la version Python 3.10 ce qui peut en rebuter certains
@dataclass(slots = True)
class Object:
    # Variables obligatoires
    param1: str
    param2: int
    # Variables optionnelles pouvant s'auto initialiser
    param3: int=1
​
    # Optionnel, seulement si vous avez du post traitement a faire apres l'init de la dataclass
    def __post_init__(self):
        pass
​
    # Une methode create OU create_or_update qui prend en parametre, au moins un objet API et un object logger (voir les fichiers bbox/api.py et bbox/logger.py)
    # le nom n'est pas obligatoire mais c'est plus pour orienter. La methode create fait des POST de creation, elle ne prend pas en compte l'idee
    # qu'un objet equivalent puisse exister (voir bbox/section/fwv4.py). create_or_update fera le traitement pour verifier d'abord si l'element a creer existe
    # avant de le creer/modifier (voir bbox/section/wifi.py)
    def create(self, logger, api):
        pass
​
​
class ObjectManager:
    # l'utilisation des slotted class est preferable pour l'utilisation memoire mais rien ne vous y oblige
    __slots__ = ['logger', 'api', 'conf', 'data']
​
    def __init__(self, logger, api, data):
        self.logger = logger
        self.api = api
        self.conf = rules.pop('conf')
        self.data = data
​
    # Cette methode est obligatoire, elle permet de configurer les options rajoutees a la ligne de votre section, ex: [wifi enable=1 gamer_mode=0 ping_responder=0]
    # Elle ne prend pas de parametres, son role est de prendre les donnees de self.conf et de les traiter
    def conf_section(self):
        pass
​
    # Cette methode est obligatoire, elle permet de deployer vos objets bbox, les lignes de chaque section en somme, ex: machine1 ipaddress=192.168.1.30 macaddress=08:69:69:69:69:69 ...
    # Elle ne prend pas de parametres et se contente de traiter les donnees de self.data
	# Cette fonction cree des Object class pour chaque ligne de la section
	# Elle peut egalement appeler d'autres fonctions (voir bbox/session/device.py)
    def deploy(self):
        pass
```
