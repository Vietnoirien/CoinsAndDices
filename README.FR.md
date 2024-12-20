# Lanceur de Dés et Pièces

Une application desktop complète pour simuler des lancers de dés et de pièces, développée avec wxPython.

## Fonctionnalités

### 1. Dés Standards
- Lancer plusieurs dés simultanément avec notation NdX
- Affichage détaillé des résultats (total, moyenne, min/max)
- Support de multiples groupes de dés

### 2. Pièces
- Lancer jusqu'à 100+ pièces simultanément
- Affichage des statistiques (pile/face)
- Visualisation de la séquence complète

### 3. Dés Personnalisés
- Création de dés avec faces personnalisées
- Sauvegarde permanente des dés créés
- Édition et suppression des dés existants

### 4. Dés Runebound
- Simulation des dés spéciaux du jeu Runebound
- Support de lancers multiples
- Affichage des terrains obtenus

## Installation

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances :
```bash
pip install wxPython
```

## Utilisation

1. Lancez l'application :
```bash
python wx_app.py
```

2. Navigation
- Utilisez le menu principal pour accéder aux différentes fonctionnalités
- Chaque module dispose de son interface dédiée avec des contrôles intuitifs

## Structure du Projet

- `wx_app.py` : Fichier principal contenant toutes les classes de l'interface graphique
  - `HomePage` : Menu principal de l'application
  - `StandardDiceFrame` : Gestion des dés standards
  - `CoinFrame` : Simulation des lancers de pièces
  - `CustomDiceFrame` : Interface des dés personnalisés
  - `RuneboundFrame` : Module spécial pour Runebound

- `custom_dices.json` : Stockage persistant des dés personnalisés

## Architecture

L'application est construite selon une architecture modulaire où chaque fonctionnalité est encapsulée dans sa propre classe Frame. Cela permet :
- Une maintenance facilitée
- Une séparation claire des responsabilités
- Une extensibilité simple pour ajouter de nouvelles fonctionnalités

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur le projet.