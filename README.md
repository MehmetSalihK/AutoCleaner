# 🛡️ AutoCleaner Pro v5.2 - Professional Edition

[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**AutoCleaner Pro** est un outil de nettoyage système professionnel pour Windows 10/11, conçu pour optimiser les performances de votre PC en supprimant les fichiers temporaires, caches et données inutiles de manière intelligente et sécurisée.

---

## ✨ Fonctionnalités Principales

### 🧹 Nettoyage Intelligent
- **Système Windows**
  - Fichiers temporaires (%TEMP%, C:\Windows\Temp)
  - Cache Windows et Prefetch
  - Logs système et crash dumps (.dmp)
  - SoftwareDistribution\Download
  
- **Navigateurs Web**
  - Chrome, Edge, Brave
  - Opera, Opera GX, Vivaldi
  - Yandex et autres navigateurs Chromium
  - **Protection** : Préserve mots de passe et favoris

- **Plateformes Gaming**
  - Steam (cache, htmlcache, logs, dumps)
  - Epic Games Launcher
  - Riot Games (League of Legends, Valorant)
  - Discord cache
  - NVIDIA et AMD caches GPU

- **Applications**
  - Spotify, Adobe, Microsoft Teams
  - Caches et fichiers temporaires

### 📊 Surveillance Système en Temps Réel
- **Métriques CPU, RAM, Disque, GPU**
- Graphiques de progression colorés
- Statistiques réseau (Download/Upload)
- Mise à jour automatique toutes les 2 secondes

### ⏱️ Nettoyage Automatique Programmable
- Intervalles configurables : **5, 10, 15, 30, 45 minutes** ou **1, 2, 3 heures**
- Notifications Windows après chaque nettoyage
- Exécution en arrière-plan silencieuse
- Statistiques détaillées (fichiers supprimés, espace libéré)

### 🔔 Notifications Natives Windows
- Intégration complète avec le Centre de notifications Windows
- Notifications après nettoyage automatique
- Alertes de minimisation dans la barre des tâches
- Bouton de test dans les paramètres

### 📜 Historique et Logs Détaillés
- Enregistrement de chaque fichier supprimé
- Informations : chemin, taille, catégorie, timestamp
- Export CSV pour analyse
- Affichage des 100 dernières actions

### 🎨 Interface Moderne et Professionnelle
- Design Fluent inspiré de Windows 11
- Mode sombre/clair
- Cartes avec effets de profondeur
- Animations fluides
- Responsive (1200x800 minimum)

### 🔒 Sécurité et Protection
- **Mode Simulation** : Prévisualisation avant suppression
- Protection des données de connexion (Steam, navigateurs)
- Liste noire de fichiers critiques
- Logs détaillés de toutes les opérations
- Instance unique (pas de doublons)

### 🔧 Paramètres Avancés
- Minimiser dans la barre des tâches (System Tray)
- Démarrage automatique avec Windows
- Mode Furtif (démarrage minimisé)
- Personnalisation des intervalles de nettoyage
- Activation/désactivation des notifications

---

## 📥 Installation

### Option 1 : Exécutable Portable (Recommandé)
1. Téléchargez `AutoCleanerPro_v5.2_Final.exe` depuis le dossier `dist/`
2. Double-cliquez pour lancer (droits administrateur recommandés)
3. Aucune installation requise !

### Option 2 : Depuis le Code Source
```bash
# Cloner le repository
git clone https://github.com/MehmetSalihK/AutoCleaner.git
cd AutoCleaner

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

### Dépendances
- Python 3.8+
- customtkinter >= 5.2.0
- psutil >= 5.9.0
- pystray >= 0.19.4
- Pillow >= 9.0.0
- pywin32 >= 306
- winotify >= 1.1.0

---

## 🚀 Utilisation

### Démarrage Rapide
1. **Lancez l'application** (droits admin recommandés pour un nettoyage complet)
2. **Tableau de Bord** : Visualisez l'état de votre système
3. **Actions Rapides** :
   - 🧹 **Nettoyer Maintenant** : Nettoyage immédiat
   - 🔍 **Analyser (Simulation)** : Prévisualisation sans suppression

### Configuration du Nettoyage Automatique
1. Allez dans **⚙️ Paramètres**
2. Choisissez votre **Intervalle de Nettoyage** (5 min à 3 heures)
3. Activez **Notifications** pour recevoir des alertes
4. Testez avec le bouton **📢 Envoyer une Notification de Test**

### Minimiser dans la Barre des Tâches
1. Activez **Minimiser dans la Tray** dans les Paramètres
2. Fermez la fenêtre → L'app continue en arrière-plan
3. Cliquez sur l'icône près de l'horloge pour rouvrir
4. Clic droit → **Quitter** pour fermer complètement

### Consulter l'Historique
1. Allez dans **📜 Historique**
2. Visualisez les 100 dernières suppressions
3. Cliquez sur **💾 Exporter CSV** pour sauvegarder sur le bureau

---

## 🎯 Fonctionnalités Avancées

### Mode Simulation (Sécurité)
Activez le **Mode Simulation** dans les Paramètres pour :
- Voir ce qui serait supprimé SANS rien toucher
- Tester les règles de nettoyage
- Vérifier l'espace qui serait libéré

### Nettoyage Personnalisé
Dans **🧹 Nettoyage Avancé** :
- Cochez/décochez les catégories à nettoyer
- Système, Navigateurs, Gaming, Applications
- Chaque catégorie est détaillée

### Protection des Données
Par défaut, AutoCleaner Pro **NE SUPPRIME PAS** :
- Mots de passe enregistrés
- Favoris/Marque-pages
- Sessions de connexion (Steam, Epic, etc.)
- Fichiers système critiques (.sys, .dll)

---

## 📊 Statistiques et Performances

### Ce que vous gagnez
- **Espace disque** : Jusqu'à plusieurs Go libérés
- **Performance** : Démarrage plus rapide
- **Stabilité** : Moins de crashs liés aux caches corrompus
- **Vie privée** : Suppression des traces de navigation

### Exemples de Nettoyage
```
✅ Nettoyage réussi !
📁 Fichiers supprimés : 1,247
💾 Espace libéré : 3.42 GB
⚠️ Erreurs : 0
```

---

## 🛠️ Build depuis le Source

### Créer un Exécutable
```bash
# Installer PyInstaller
pip install pyinstaller

# Build
python -m PyInstaller --noconsole --onefile \
  --name="AutoCleanerPro_v5.2_Final" \
  --icon="AutoCleanerLogo.ico" \
  --add-data "AutoCleanerLogo.ico;." \
  --add-data "AutoCleanerLogo.png;." \
  --collect-all customtkinter \
  --collect-all winotify \
  main.py

# L'exécutable sera dans dist/
```

---

## 🐛 Résolution de Problèmes

### L'application ne démarre pas
1. **Vérifiez les logs** : `%USERPROFILE%\autocleaner_v4.log`
2. **Lancez en admin** : Clic droit → Exécuter en tant qu'administrateur
3. **Vérifiez Python** : Version 3.8+ requise

### Les notifications ne s'affichent pas
1. Vérifiez que **winotify** est installé : `pip install winotify`
2. Testez avec le bouton dans les Paramètres
3. Vérifiez le Centre de notifications Windows (coin bas-droit)

### Le Gestionnaire des tâches se ferme
- Utilisez la version **v5.1 Stable** ou supérieure
- Protection anti-crash intégrée

### L'icône tray ne s'affiche pas
- Vérifiez que **pystray** est installé
- L'icône peut prendre 1-2 secondes à apparaître

---

## 📝 Changelog

### v5.2 Final (Décembre 2024)
- ✅ Notifications natives Windows (winotify)
- ✅ Bouton de test de notification
- ✅ Meilleure gestion d'erreur
- ✅ README amélioré

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :
1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👨‍💻 Auteur

**Mehmet Salih K**
- GitHub: [@MehmetSalihK](https://github.com/MehmetSalihK)

---

## ⚠️ Avertissement

- **Utilisez à vos propres risques**
- Toujours faire une **sauvegarde** avant un nettoyage important
- Le **Mode Simulation** est recommandé pour les premiers usages
- Certaines fonctionnalités nécessitent des **droits administrateur**

---

## 🌟 Remerciements

Merci à tous les contributeurs et utilisateurs d'AutoCleaner Pro !

**Aimez-vous AutoCleaner Pro ? Donnez-lui une ⭐ sur GitHub !**

---

<div align="center">
  <strong>AutoCleaner Pro v5.2 - Professional Edition</strong><br>
  <em>Optimisez votre PC Windows en toute sécurité</em>
</div>