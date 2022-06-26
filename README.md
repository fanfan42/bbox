# bbox
Petit script python3 pour controler l'API bbox (Bouygues Telecom box)

Pour retrouver l'ensemble des fonctions disponibles de l'API, se rendre sur
https://api.bbox.fr/doc/apirouter/

# Pre requis
Python >= 3.10

# Configuration
A la racine de votre home, creer le fichier .bbox.config et renseigner en INI les parametres d'acces de la bbox
```sh
[info]
url=https://mabbox.bytel.fr
password=SuperPassword
```

NOTE: Vous pouvez laisser le password vide, le programme vous le demandera alors en direct

# Faire des appels brut d'API

base sur l'equivalent python2: https://github.com/r3c/bbox.py
```sh
bbox_cli.py raw METHOD PATH [PARAMS]
```

Exemples:
- Recuperer toutes les regles du firewall : 
```sh
bbox_cli.py raw GET api/v1/firewall/rules
```

- Mettre a jour la regle firewall dont l'id est 5 depuis la commande precedente : 
```sh
bbox_cli.py raw PUT api/v1/firewall/rules/5 
"srcip=8.8.8.8&srcipnot=0&dstip=192.168.1.66&dstipnot=0&srcports=&srcportnot=0&dstports=22&dstportnot=0&order=5&enable=1&protocols=tcp&description=AllowGoogleFromOutsideToSSH&action=Accept"
```

- Recuperer les regles NAT:
```sh
bbox_cli.py raw GET api/v1/nat/rules
```

- Mettre a jour la regle NAT dont l'id est 3 depuis la commande precedente : 
```sh
bbox_cli.py raw PUT api/v1/nat/rules/3 "enable=1&ipremote=8.8.8.8"
```

- Recuperer les machines enregistrees sur la bbox : 
```sh
bbox_cli.py raw GET api/v1/hosts
```

- Reveiller (Wake On Lan) la machine dont l'id est 7 depuis la la commande precedente : 
```sh
bbox_cli.py raw POST api/v1/hosts/7?btoken= "action=wakeup"
```

# Donner un fichier d'inventaire en parametre
```sh
bbox_cli.py apply /root/inventory [-l limit]
```

Voir le fichier inventory.example pour voir toutes les possibilites offertes par cette nouvelle fonctionnalite

Plus de doc a venir sur le sujet


