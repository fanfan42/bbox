# bbox

Petit script python3 pour controler l'API bbox (Bouygues Telecom box)
base sur l'equivalent python2: https://github.com/r3c/bbox.py
Pour retrouver l'ensemble des fonctions disponibles de l'API, se rendre sur
https://api.bbox.fr/doc/apirouter/

# Configuration
Dans le meme dossier que le script bbox.py, creer le fichier .bbox.config et renseigner en JSON les parametres d'acces de la bbox
{"url": "https://mabbox.bytel.fr", "password": "SuperPassword"}

# Exemples:
- Recuperer toutes les regles du firewall : 
bbox.py raw GET api/v1/firewall/rules

- Mettre a jour la regle firewall dont l'id est 5 depuis la commande precedente : 
bbox.py raw PUT api/v1/firewall/rules/5 "srcip=8.8.8.8&srcipnot=0&dstip=192.168.1.66&dstipnot=0&srcports=&srcportnot=0&dstports=22&dstportnot=0&order=5&enable=1&protocols=tcp&description=AllowGoogleFromOutsideToSSH&action=Accept"

- Recuperer les regles NAT: 
bbox.py raw GET api/v1/nat/rules

- Mettre a jour la regle NAT dont l'id est 3 depuis la commande precedente : 
bbox.py raw PUT api/v1/nat/rules/3 "enable=1&ipremote=8.8.8.8"

- Recuperer les machines enregistrees sur la bbox : 
bbox.py raw GET api/v1/hosts

- Reveiller (Wake On Lan) la machine dont l'id est 7 depuis la la commande precedente : 
bbox.py raw POST api/v1/hosts/7?btoken= "action=wakeup"
