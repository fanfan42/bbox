# bbox
Petit script python3 pour controler l'API bbox (Bouygues Telecom box)

Pour retrouver l'ensemble des fonctions disponibles de l'API, se rendre sur
[API BBox](https://api.bbox.fr/doc/apirouter/)

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

Voir le fichier inventory.example pour voir toutes les possibilites
offertes par cette nouvelle fonctionnalite

Voir egalement le fichier inventory.readme pour avoir toutes les
explications sur la facon de gerer votre propre inventaire et voir
toutes les fonctionnalites deja developpees (ou pas)

# Notes
J'ai commence ce projet en 2021. Au depart, je voulais surtout avoir acces a
quelques commandes sans avoir besoin d'activer le remote sur la BBox (pas secure),
c'est la partie "raw" du script.

J'avais deja dans l'idee de faire comme avec Ansible : avoir 1 inventaire ou
je decris l'etat de mon infra et je l'applique. Mais comme tout geek
normalement constitue, j'ai eu la flemme. Puis, j'ai lu un article du blog de
@Korben en partenariat avec talent.io [voir ici](https://korben.info/articles/astuces-python)
sur les bonnes pratiques de Python. Cela plus la petite etoile qui fait plaisir,
ca m'a donne des ailes pour developper davantage ce script qui est parfait
pour mes besoins. Ah et non, je ne ferai pas comme avec OVH, je ne prevois
pas de developper un module pour Ansible. Surtout parce que je ne souhaite
pas installer Ansible sur la machine qui deploiera cet inventaire.

Je ne suis pas developpeur Python "professionnel", juste sysadmin/devops toujours
passionne par le code. J'ai fait de mon mieux pour faire de ce programme quelque 
chose de propre et facilement maintenable. Mais si vous saignez des yeux en lisant
mon code, toutes mes confuses. N'hesitez pas a faire des PR ou me faire part
de vos commentaires, il est tres probable que ce soit integre dans ce code aussi


