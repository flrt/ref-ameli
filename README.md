Vérification de disponibilité des référentiels Ameli CCAM, UCD, LPP
===================================================================

Ce projet permet de
- détecter si une nouvelle version d'un référentiel est disponible
- télécharger les fichiers de données en lien avec la version
- transférer sur un répertoire d'un serveur FTP les fichiers téléchargés
- produire un fichier [XML ATOM](https://tools.ietf.org/html/rfc4287) et de le transférer par FTP sur un serveur
- alerter par mail d'une nouvelle version

# Nomenclatures traitées
- CCAM : [Classification Commune des Actes Médicaux](https://www.ameli.fr/medecin/exercice-liberal/facturation-remuneration/nomenclatures-codage/codage-actes-medicaux-ccam)
- UCD : [médicaments codés en Unités Communes de Dispensation](https://www.ameli.fr/etablissement-de-sante/exercice-professionnel/nomenclatures-codage/medicaments)
- LPP [Liste des produits et prestations](https://www.ameli.fr/etablissement-de-sante/exercice-professionnel/nomenclatures-codage/lpp)

## Flux ATOM XML
- CCAM : [https://www.opikanoba.org/feeds/ameli_ccam.xml](https://www.opikanoba.org/feeds/ameli_ccam.xml)
- UCD : [https://www.opikanoba.org/feeds/ameli_ucd.xml](https://www.opikanoba.org/feeds/ameli_ucd.xml)
- LPP : [https://www.opikanoba.org/feeds/ameli_lpp.xml](https://www.opikanoba.org/feeds/ameli_lpp.xml)

## Validations W3C

| Nomenclature | Résultat |
| ------------ | -------- |
| CCAM | <a href="https://validator.w3.org/feed/check.cgi?url=https%3A//www.opikanoba.org/feeds/ameli_ccam.xml"><img src="valid-atom.png" alt="[Valid Atom 1.0]" title="Valider le flux CCAM" /></a> |
| UCD  | <a href="https://validator.w3.org/feed/check.cgi?url=https%3A//www.opikanoba.org/feeds/ameli_ucd.xml"><img src="valid-atom.png" alt="[Valid Atom 1.0]" title="Valider le flux UCD" /></a> |
| LPP  | <a href="https://validator.w3.org/feed/check.cgi?url=https%3A//www.opikanoba.org/feeds/ameli_lpp.xml"><img src="valid-atom.png" alt="[Valid Atom 1.0]" title="Valider le flux LPP" /></a> |

# Fonctionnement de la détection
La détection de la présence d'une nouvelle version se fait par évaluation prédictive. 
En fonction des réféntiels la méthode est différente :
- pour les LPP, le programme essaie d'accèder à la version suivante (par requete HTPP HEAD)
- pour la CCAM et les UCD, le programme télécharge la page web et l'analyse à la recherche de liens faisant référence à la nouvelle version

# Exécution du programme
Le programme fonctionne avec python 3 et s'éxécute dans un conteneur docker (il est largement possible de l'utiliser sans).

Pour construire le conteneur :

    $ docker build -t py_ameli .

Pour le démarrer le conteneur : 

    $ docker run -it --rm -v "$PWD":/opt -w /opt py_ameli /bin/bash

Pour lancer le programme python :

    $  python check.py -h
    usage: check.py [-h] [-a {feed,download}] [--feedbase FEEDBASE]
                [--feedftp FEEDFTP] [--dataftp DATAFTP] [--mail MAIL]
                [--backupdir BACKUPDIR] [--downdir DOWNDIR]
                {ucd,lpp,ccam}

    positional arguments:
        {ucd,lpp,ccam}        referentiel : ucd | lpp | ccam

    optional arguments:
        -h, --help            show this help message and exit
        -a {feed,download}, --action {feed,download}
                              actions disponibles : <feed> -> produit un fichiers de
                              syndication ATOM, <download> -> télécharge les
                              fichiers
        --feedbase FEEDBASE   URL de base des flux atom, utilisés dans le flux ATOM
                              pour s'autoréférencer (*)
        --feedftp FEEDFTP     configuration FTP pour upload du flux ATOM, format
                              JSON
        --dataftp DATAFTP     configuration FTP pour upload des données, format JSON
        --mail MAIL           configuration Mail pour envoyer une notification,
                              format JSON
        --backupdir BACKUPDIR
                              Répertoire de sauvegarde des pages html
        --downdir DOWNDIR     Répertoire de téléchargements des fichiers de données

    (*) Lien sur le lien autoréférencé dans ATOM :
    https://www.feedvalidator.org/docs/warning/MissingAtomSelfLink.html


Exemple de ligne de commande pour vérifier si une nouvelle version LPP est disponible :

    $ python3 check.py -a feed --feedftp conf/ftp-feed.json \
    --feedbase https://www.opikanoba.org/feeds/ \
    --dataftp conf/ftp-data.json \
    --mail conf/mail.json \
    lpp

# structure du projet
- racine : fichiers python
- backup : répertoire contenant les fichiers html source téléchargés
- conf : répertoire contenant les fichiers de configuration
    - configuration des flux ATOM
    - template html pour les compléments d'informations
    - configuration mail, ftp
- data : données persistantes permettant de connaître les versions actuelles et de générer les flux ATOM
- down : répertoire de téléchargement des données
- feeds : répertoire local contenant les fichiers XML ATOM
- tests : fichiers de tests unitaires

# Licence 

[MIT](LICENSE) pour le code

[CC BY-SA 3.0 FR](https://creativecommons.org/licenses/by-sa/3.0/fr/) pour le contenu ATOM