# Gwent Beta Classic 0.8.1 — Français

> La version 0.8.1 pour Next-Gen 5.0+ a été testée en jeu. Classic 1.32 est corrigée et testée séparément ; son archive actuelle est une version de test.

## Important

Sauvegardez vos parties avant l'installation et avant chaque mise à jour. Le mod est en développement actif : utilisez une sauvegarde séparée pour vos premières parties.

Les traductions restent une préversion : les textes des cartes proviennent de la localisation officielle de la bêta, l'interface a été traduite par IA et peut contenir des erreurs. Les nouvelles indications ajoutées depuis la 0.6.6 n'existent pour l'instant qu'en anglais et en russe ; les autres langues les affichent en anglais. Signalez tout ce qui sonne faux.

## À propos

Gwent Beta Classic remplace le Gwynt de The Witcher 3 par les cartes, les règles et le plateau de Gwent Beta 0.9.24 autonome. Les parties restent intégrées au monde du Sorceleur : affrontez des PNJ, accomplissez des quêtes, achetez des tonneaux et construisez vos decks.

## Fonctionnalités

- 479 cartes à collectionner, dont 21 chefs, pour les cinq factions
- Plateau, interface, polices, cadres de cartes, météo et effets de la bêta ; chefs animés
- Éditeur de decks : cinq decks de départ modifiables et huit emplacements personnels, filtres et recherche
- Adversaires avec 46 archétypes de decks de la bêta et trois niveaux de difficulté de l'IA
- Tonneaux à 200 couronnes chez tous les aubergistes, ouverts comme dans la bêta
- Fragments : fabriquez des cartes pour 30 / 80 / 200 / 800 selon la rareté ; les exemplaires en trop sont recyclés automatiquement
- Tutoriel, mulligan, consultation des cimetières et du deck, fiche détaillée des cartes
- Souris, clavier et manette

## Changements depuis la 0.7.3a

- Chaque paquet contient les cinq doublages et les 13 langues de texte. Les téléchargements séparés par doublage ne sont plus nécessaires.
- Deux boutons voisins, Texte et Voix, dans le menu du mod, avec sélection automatique ou manuelle indépendante.
- Détection distincte des langues du texte et des voix du jeu. Une langue non prise en charge utilise l’anglais.
- Les préférences sont enregistrées dans la sauvegarde. L’ancienne sélection manuelle du texte est conservée après mise à jour.
- Définitions des tonneaux et récupération du stock corrigées en Nouvelle partie +. Un ajout échoué n’est plus marqué comme terminé ; le stock vendu ne revient pas à chaque ouverture de la boutique.
- Effets retravaillés pour les trois projectiles de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, les statuts, les compteurs et l’armure.
- Ressources de l’interface réorganisées pour respecter le budget de compilation de 63 Mio sans réduire la résolution des textures. Le chargement des menus et la stabilité restent à valider.

## Langues

Texte : anglais, russe, allemand, français, italien, polonais, espagnol (Espagne), espagnol (Amérique latine), portugais (Brésil), japonais, coréen, chinois simplifié et chinois traditionnel. Changez-la à tout moment avec le bouton de langue du texte en haut à gauche des menus des decks et de la collection, ou dans les paramètres de combat ; le choix est enregistré.

Chaque paquet comprend les voix RU, EN, DE, IT et PT-BR. Choisissez séparément texte et voix avec deux boutons voisins dans le menu des decks/de la collection du mod, ou dans les paramètres de combat. Changer de voix ne demande aucune réinstallation. Automatique suit séparément les langues actuelles du texte et des voix du jeu ; si une langue manque, l’anglais est utilisé. Sauvegardez normalement après le choix : les préférences appartiennent à cette sauvegarde et restent après mise à jour des fichiers. L’ancien choix manuel du texte est conservé. Certaines répliques du troll des tonneaux en DE/IT gardent leur remplacement russe d’origine. Les noms natifs des objets suivent la langue du jeu ; certaines notifications hors de l’interface restent RU/EN.

## Installation

1. Fermez le jeu et sauvegardez vos parties. Téléchargez le paquet pour 1.32 ou Next-Gen (5.0+). N’installez qu’une version de Beta Gwent.

2. Pour une mise à jour, déplacez d’abord l’ancien dossier Beta Gwent hors de Mods. Ne supprimez pas tout le dossier Mods et ne mélangez pas les versions.

3. Copiez Mods depuis l’archive dans le dossier du jeu, à côté de bin et content. Chemin final : Mods/modBetaGwentClassic132/content pour 1.32, Mods/modBetaGwent0924/content pour Next-Gen.

4. Chargez une sauvegarde. Le menu habituel des decks de Gwynt ouvre l’éditeur et les langues ; parlez à un PNJ joueur pour lancer une partie. Sauvegardez normalement pour conserver vos choix.

## Configuration requise

The Witcher 3 sur PC. Choisissez la version distincte pour Classic 1.32 ou Next-Gen (paquet nommé 5.0+). REDkit, Wwise et un installateur EXE ne sont pas nécessaires pour jouer.

## Compatibilité

Supprimez l'ancien dossier modBetaGwentReduxCompat : la couche de compatibilité séparée n'est plus incluse. La compatibilité avec Redux/Redo Expansion n'a pas été confirmée séparément. Les autres refontes du Gwynt et les mods touchant ses menus, les échanges de cartes ou les récompenses peuvent entrer en conflit. Après avoir modifié vos mods, refaites la fusion des scripts avec Script Merger.

## Signaler un bug

Un problème ? Indiquez les versions du mod et du jeu, les langues choisies pour texte et voix (y compris Automatique), Nouvelle partie + ou non, les autres mods, les cartes/chefs et les étapes de reproduction. Une capture et une sauvegarde avant le problème sont utiles. Pour une traduction, précisez langue et écran et proposez une meilleure formulation.

### Activer le journal

1. Ajoutez -debugscripts après le guillemet fermant de la cible d’un raccourci vers witcher3.exe. Steam : Propriétés → Général → Options de lancement. Pour GOG, utilisez un raccourci direct vers witcher3.exe.

2. Lancez le jeu, reproduisez le problème puis fermez-le. Copiez immédiatement scriptslog.txt : le lancement suivant l’écrase. S’il ne contient qu’un en-tête, signalez-le ; une configuration supplémentaire peut être nécessaire.

3. Si Windows a créé un fichier de crash, joignez aussi le dernier .dmp correspondant.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Remerciements

Merci à CD Projekt pour The Witcher et Gwent, à LegacyGwent DIY pour les ressources des cartes et du plateau, à la communauté Beta Gwent pour la préservation des archives et les idées d'archétypes, et à tous ceux qui testent le mod et envoient des rapports détaillés.

Projet de fan non officiel. Le code original du mod est sous licence GPL-3.0-only ; les contenus originaux du jeu appartiennent à leurs propriétaires.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
