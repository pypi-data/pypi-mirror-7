testlinkconsole
===============
[![Build Status](https://travis-ci.org/chbrun/testlinkconsole.svg?branch=master)](https://travis-ci.org/chbrun/testlinkconsole)
[![Coverage Status](https://coveralls.io/repos/chbrun/testlinkconsole/badge.png?branch=master)](https://coveralls.io/r/chbrun/testlinkconsole?branch=master)

console d'accès testlink

Installation
============
* Cloner le repo
* configuration dans le fichier testlinkclient.cfg l'url d'acces à testlink et la clé d'API (elle se trouve dans le projet)
* Le projet de test sous testlink doit utiliser les variables personnalisées suivantes dans les testcases :
  * scriptBehat : type string : va contenir le chemin vers le script behat à lancer automatiquement
  * Browsers : type checkbox : sera utilisé par le script pour appeler behat selon le profil. J'utilise un profil par navigateur.

Utilisation
===========
* lancer le script
* utiliser les commandes directement à la console
* afficher l'aide
* la console utiliser la completion des commandes

Commande à la console
=====================
* help : l'aide
* save : sauvegarde les paramètres dans le fichier cfg
* list : liste les objets de testlink (projets, campagnes, tests)
  * A noter que pour lister les campagnes, les tests, il faut setter un projet
* show : affiche les variables de la console
* set  : permet de setter une variable
  * Ex : set projetid 1 
* get  : récupère la valeur d'une variable
* run  : lance la campagne de test à condition d'avoir spécifié le projet et la campagne.

A noter que la console recharge automatiquement le fichier cfg au démarrage, ce qui évite de revaloriser les variables à chaque utilisation


TODO
====
* cmd run : run one test
* add variable UserAgent 
