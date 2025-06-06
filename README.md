# 🧹 AutoCleaner

**AutoCleaner** est une application Windows intelligente et discrète qui maintient automatiquement votre système propre en nettoyant les fichiers temporaires, optimisant les performances et protégeant vos données importantes. Fonctionne silencieusement en arrière-plan sans interruption.

[![Windows](https://img.shields.io/badge/Windows-10%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com)

---

## 📚 Table des matières

* [🎯 Objectifs](#-objectifs)
* [✨ Fonctionnalités](#-fonctionnalités)
* [🛡️ Sécurité et Protection](#️-sécurité-et-protection)
* [🛠️ Installation](#️-installation)
* [📋 Requirements](#-requirements)
* [🚀 Utilisation](#-utilisation)
* [⚙️ Configuration](#️-configuration)
* [📊 Monitoring](#-monitoring)
* [🔧 Dépannage](#-dépannage)
* [🎁 Bonus](#-bonus)
* [🤝 Contribuer](#-contribuer)
* [📄 Licence](#-licence)

---

## 🎯 Objectifs

AutoCleaner révolutionne la maintenance PC en automatisant intelligemment les tâches de nettoyage pour :

* ⚡ **Performance** : Libération d'espace disque et optimisation système
* 🛡️ **Sécurité** : Protection des données importantes (navigateurs, profils)
* 🥷 **Discrétion** : Fonctionnement invisible sans interruption
* 🔄 **Automatisation** : Maintenance continue sans intervention

---

## ✨ Fonctionnalités

### 🧹 **Nettoyage Intelligent**
* ✅ Nettoyage automatique des fichiers temporaires (`%temp%`, `C:\Windows\Temp`)
* ✅ Suppression sélective des journaux système (préservation des logs critiques)
* ✅ Vidage optimisé du cache DNS
* ✅ Nettoyage sécurisé du cache navigateur (sans données utilisateur)
* ✅ Filtrage intelligent : préservation des fichiers récents (<24h) et importants

### 🛡️ **Protection Avancée**
* 🔒 **Navigation** : Préservation de l'historique, cookies, mots de passe
* 📁 **Applications** : Protection des profils Chrome, Firefox, Edge
* 🎮 **Gaming** : Sauvegarde des données Steam, Epic Games, Discord
* 💼 **Productivité** : Conservation des paramètres Office, Adobe, Teams

### 🥷 **Mode Furtif**
* 👻 Démarrage silencieux sans fenêtre console
* 🔕 Notifications discrètes et courtes
* ⏰ Nettoyage automatique toutes les 10 minutes
* 🚀 Lancement automatique au démarrage Windows

### 📊 **Interface Intuitive**
* 🖱️ Icône système avec menu contextuel
* 📈 Statistiques en temps réel
* 🧹 Nettoyage manuel à la demande
* ⚙️ Configuration simple

---

## 🛡️ Sécurité et Protection

### **Données Préservées**
```
🌐 Navigateurs Web
├── Chrome : Historique, cookies, mots de passe, favoris
├── Firefox : Profils utilisateur complets
└── Edge : Sessions et données de connexion

💻 Applications Système
├── Windows Explorer : Historique de navigation
├── PowerShell : Historique des commandes
└── Logs critiques : System, Security

🎯 Applications Tierces
├── Gaming : Steam, Epic Games, Discord, Spotify
├── Bureau : Office, Adobe, Teams, Skype
└── Développement : Git, IDE, configurations
```

### **Sécurité Renforcée**
* ⏱️ **Timeout** sur les commandes système (évite les blocages)
* 🔍 **Vérification** de l'âge et taille des fichiers
* 🚫 **Exclusion** des fichiers système critiques (.dll, .exe, .sys)
* 📝 **Logs** des erreurs pour diagnostic

---

## 🛠️ Installation

### **Pré-requis**
* ![Windows](https://img.shields.io/badge/-Windows%2010%2F11-blue?style=flat&logo=windows) 
* ![Python](https://img.shields.io/badge/-Python%203.8%2B-green?style=flat&logo=python)
* 🔑 Droits administrateur (premier lancement uniquement)

### **Installation Rapide**

```bash
# 1. Cloner le projet
git clone https://github.com/votre-nom/AutoCleaner.git
cd AutoCleaner

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le programme
python autocleaner.py
```

### **Création d'un Exécutable**

```bash
# Installation de PyInstaller
pip install pyinstaller

# Génération de l'exécutable (recommandé)
pyinstaller --onefile --noconsole --name="AutoCleaner" autocleaner.py

# L'exécutable sera dans le dossier dist/
```

---

## 📋 Requirements

### **requirements.txt**
```txt
win10toast-persist>=0.9.4
pystray>=0.19.4
Pillow>=9.0.0
pywin32>=305
psutil>=5.9.0
```

### **Dépendances Détaillées**

| Package | Version | Usage |
|---------|---------|--------|
| `win10toast-persist` | ≥0.9.4 | Notifications Windows persistantes |
| `pystray` | ≥0.19.4 | Icône système et menu contextuel |
| `Pillow` | ≥9.0.0 | Génération d'icônes dynamiques |
| `pywin32` | ≥305 | API Windows (registre, raccourcis) |
| `psutil` | ≥5.9.0 | Gestion des processus système |

---

## 🚀 Utilisation

### **Démarrage**
```bash
# Lancement normal
python autocleaner.py

# Ou avec l'exécutable
AutoCleaner.exe
```

> ⚠️ **Note** : Le programme demande automatiquement les droits administrateur si nécessaire

### **Interface Utilisateur**

#### **Icône Système** 🖱️
* **Clic gauche** : Afficher les statistiques
* **Clic droit** : Menu contextuel

#### **Menu Contextuel**
| Option | Action |
|--------|--------|
| 📊 Statistiques | Affiche le nombre de fichiers nettoyés |
| 🧹 Nettoyer maintenant | Lance un nettoyage manuel |
| ❌ Quitter | Ferme l'application |

---

## ⚙️ Configuration

### **Personnalisation du Nettoyage**

Modifiez la liste `EXCLUDED_PATHS` dans le code pour ajouter vos exclusions :

```python
EXCLUDED_PATHS = [
    # Ajouter vos dossiers à protéger
    "MonApplication\\ImportantData",
    "MesDocuments\\Projet"
]
```

### **Fréquence de Nettoyage**

```python
# Dans schedule_cleanup()
time.sleep(600)  # 600 = 10 minutes
                 # 300 = 5 minutes
                 # 1800 = 30 minutes
```

---

## 📊 Monitoring

### **Statistiques Disponibles**
* 📁 **Fichiers supprimés** : Compteur total
* ❌ **Erreurs rencontrées** : Nombre d'échecs
* ⏰ **Dernière exécution** : Timestamp du dernier nettoyage
* 🛡️ **Mode protection** : Status des exclusions

### **Logs et Diagnostic**
Les erreurs sont comptabilisées et affichées dans l'interface statistiques pour un suivi optimal.

---

## 🔧 Dépannage

### **Problèmes Courants**

| Problème | Solution |
|----------|----------|
| ❌ Pas de droits admin | Clic droit → "Exécuter en tant qu'administrateur" |
| 🚫 Notifications non affichées | Vérifier les paramètres de notification Windows |
| ⏸️ Programme ne démarre pas | Vérifier l'installation de Python et des dépendances |
| 🔄 Pas de nettoyage auto | Relancer le programme avec droits admin |

### **Désinstallation**
```bash
# Supprimer du démarrage automatique
# Via les paramètres Windows → Applications → Démarrage
# Ou supprimer la clé registre HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\AutoCleaner
```

---

## 🎁 Bonus

### **Fonctionnalités Avancées**
* 🧵 **Multithreading** : Interface réactive, nettoyage en arrière-plan
* 🔄 **Auto-démarrage** : Ajout automatique au démarrage Windows
* 🎨 **Icône dynamique** : Génération automatique si logo absent
* 💾 **Sauvegarde** : Conservation des données critiques utilisateur
* 🔒 **Mode discret** : Aucune interruption de votre travail

### **Intégration Système**
* ✅ Compatible Windows 10/11
* ✅ Fonctionne sur architectures x64/x86
* ✅ Respect des permissions système
* ✅ Gestion intelligente des erreurs

---

## 🤝 Contribuer

Votre contribution est la bienvenue ! 

### **Comment Participer**
1. 🍴 **Fork** le projet
2. 🌿 **Branche** : `git checkout -b feature/nouvelle-fonctionnalite`
3. ✏️ **Commit** : `git commit -m "Ajout: nouvelle fonctionnalité"`
4. 📤 **Push** : `git push origin feature/nouvelle-fonctionnalite`
5. 🔄 **Pull Request** avec description détaillée

### **Guidelines**
* 📝 Code commenté et documenté
* 🧪 Tests sur Windows 10/11
* 🛡️ Respect des exclusions de sécurité
* 📚 Mise à jour de la documentation

---

## 📄 Licence

```
MIT License

Copyright (c) 2025 AutoCleaner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**Voir le fichier [LICENSE](LICENSE) pour les détails complets.**

---

## 🔗 Liens Utiles

* 📖 [Documentation Complète](https://github.com/votre-nom/AutoCleaner/wiki)
* 🐛 [Signaler un Bug](https://github.com/votre-nom/AutoCleaner/issues)
* 💡 [Demander une Fonctionnalité](https://github.com/votre-nom/AutoCleaner/issues/new)
* 📧 [Contact](mailto:votre-email@domain.com)

---

<div align="center">

**🛡️ Développé avec ❤️ pour maintenir votre PC performant et sécurisé**

![Maintenance](https://img.shields.io/badge/Maintained-Yes-green.svg)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)
![Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

</div>