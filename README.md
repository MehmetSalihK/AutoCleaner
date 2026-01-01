# 🛡️ AutoCleaner Demo

<div align="center">
  
  ![Logo](AutoCleanerLogo.ico)
  
  <h3>v1.0 (Ultimate Design)</h3>

  [![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
  [![Python](https://img.shields.io/badge/Python-3.11%2B-green?logo=python)](https://www.python.org/)
  [![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue)](https://github.com/TomSchimansky/CustomTkinter)
  [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
  
</div>

<div align="center">
  <p><em>L'optimiseur système ultime pour Windows avec un design "Surface" moderne et des outils professionnels.</em></p>
</div>

---

## 📋 Table des matières

- [🎯 À propos](#🎯-à-propos)
- [✨ Fonctionnalités Principales](#✨-fonctionnalités-principales)
- [🚀 Installation & Démarrage](#🚀-installation--démarrage)
- [💻 Interface & Design](#💻-interface--design)
- [🛠 Technologies Utilisées](#🛠-technologies-utilisées)
- [⚙️ Configuration](#⚙️-configuration)
- [📦 Compilation (.exe)](#📦-compilation-exe)
- [🤝 Contribution](#🤝-contribution)
- [📄 Licence](#📄-licence)

---

## 🎯 À propos

**AutoCleaner Demo** est une solution de nettoyage et d'optimisation pour Windows 10 et 11. Conçu pour être à la fois puissant et élégant, il permet de libérer de l'espace disque, de gérer les processus gourmands et d'accélérer le démarrage de votre PC, le tout via une interface ultra-moderne.

> **Note** : Cette version "Demo v1.0" présente le design final "Ultimate" et toutes les fonctionnalités avancées.

---

## ✨ Fonctionnalités Principales

### 🧹 Nettoyage Intelligent
- **Système** : Suppression des fichiers temporaires, caches Windows, logs, et crash dumps.
- **Navigateurs** : Nettoyage des caches (Chrome, Edge, Brave, Opera, Vivaldi) sans toucher aux mots de passe.
- **Gaming** : Optimisation pour Steam, Epic Games, Riot Games, et caches GPU (NVIDIA/AMD).
- **Applications** : Support de Discord, Spotify, Adobe, Teams.

### 📊 Surveillance en Temps Réel
- **Dashboard** : Vue d'ensemble CPU, RAM, Disque et GPU.
- **Réseau** : Moniteur de débit (Download/Upload) en direct.
- **Indicateurs visuels** : Jauges de couleur dynamiques.

### 🛠️ Outils Avancés
| Outil | Description |
| :--- | :--- |
| **Gestionnaire de Processus** | Identifiez et tuez les processus gourmands (arborescence incluse). |
| **Gestionnaire de Démarrage** | Supprimez les programmes qui ralentissent le boot. |
| **Désinstalleur d'Apps** | Scannez et désinstallez proprement les logiciels installés. |
| **Optimiseur de RAM** | Libérez la mémoire vive inutilisée en un clic. |
| **Analyseur de Disque** | Trouvez les fichiers volumineux (>100Mo, >1Go). |

---

## 🚀 Installation & Démarrage

### Option 1 : Exécutable Portable (Recommandé)
1.  Allez dans le dossier `dist\AutoCleanerDemo`.
2.  Lancez `AutoCleanerDemo.exe`.
3.  *(Optionnel)* Faites **Clic droit > Épingler au menu Démarrer** pour activer les notifications natives.

### Option 2 : Depuis le code source
Prerequisites : Python 3.11+

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement automatique
run.bat

# Lancement manuel
python main.py
```

---

## 💻 Interface & Design

Cette version introduit le **Ultimate Design** (v6.4) :

- **Thème Sombre Premium** : Palette `#1a1a2e` avec accents `#00d4aa` (Turquoise) et violets profonds.
- **Surface UI** : Les fenêtres de dialogue flottent au-dessus de l'interface avec un effet de profondeur.
- **Ghost Buttons** : Boutons secondaires transparents avec bordures fines pour une hiérarchie visuelle claire.
- **Neumorphism Subtil** : Champs de saisie incrustés pour un look moderne.

---

## 🛠 Technologies Utilisées

*   **Langage** : Python 3.11
*   **Interface (GUI)** : CustomTkinter (basé sur Tkinter)
*   **Système** : `psutil`, `win32api` (pywin32), `ctypes`
*   **Notifications** : `winotify` (Toast Windows 10/11)
*   **Images** : Pillow (PIL)
*   **Tray Icon** : pystray

---

## ⚙️ Configuration

Vous pouvez personnaliser l'expérience via l'onglet **Paramètres** :
- **Mode Furtif** : Lance l'application minimisée dans la barre des tâches.
- **Nettoyage Auto** : Définissez l'intervalle (ex: toutes les 30 min).
- **Notifications** : Activez/Désactivez les alertes Windows.
- **Mode Simulation** : Pour tester sans rien supprimer (Sécurité).

---

## 📦 Compilation (.exe)

Pour créer votre propre exécutable standalone :

```cmd
build.bat
```
*Le fichier `.exe` sera généré dans le dossier `dist/`.*

---

## 🤝 Contribution

Les retours sont les bienvenus !
Utilisez le bouton **"✉️ Donner votre Avis"** directement dans l'application pour envoyer vos suggestions via Discord Webhook.

---

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

<div align="center">
  <br>
  <strong>Créé avec ❤️ par [Mehmet Salih K]</strong>
</div>