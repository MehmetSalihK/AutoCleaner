# 🧹 AutoCleaner

**AutoCleaner** est une application Windows légère et autonome qui nettoie automatiquement les fichiers temporaires, les journaux système et le cache DNS toutes les 5 minutes, en s’exécutant discrètement en arrière-plan.
Un menu accessible depuis la barre des tâches permet de suivre en temps réel les statistiques de nettoyage.

---

## 📚 Table des matières

* [🎯 Objectifs](#-objectifs)
* [✨ Fonctionnalités](#-fonctionnalités)
* [🛠️ Installation](#-installation)
* [📋 Requirements](#-requirements)
* [🚀 Utilisation](#-utilisation)
* [📡 API](#-api)
* [🎁 Bonus](#-bonus)
* [🤝 Contribuer](#-contribuer)
* [📄 Licence](#-licence)

---

## 🎯 Objectifs

AutoCleaner vise à simplifier la maintenance de ton PC en automatisant des tâches souvent fastidieuses, pour :

* Libérer de l’espace disque rapidement
* Améliorer la stabilité et les performances système
* Éviter l’accumulation de fichiers inutiles
* Proposer une interface intuitive et légère

---

## ✨ Fonctionnalités

* ✅ Nettoyage automatique des fichiers temporaires (`%temp%` et `C:\Windows\Temp`)
* ✅ Suppression des journaux Windows (`Application`, `System`, `Security`)
* ✅ Vidage du cache DNS (`ipconfig /flushdns`)
* ✅ Notification Windows après chaque opération de nettoyage
* ✅ Icône dans la barre des tâches avec menu contextuel :

  * Affichage des statistiques en temps réel
  * Nettoyage manuel à la demande
  * Quitter proprement l’application
* ✅ Lancement automatique au démarrage de Windows

---

## 🛠️ Installation

### Pré-requis

* Windows 10 ou 11
* Python 3.8 ou supérieur
* Droits administrateur (nécessaires au premier lancement)

### Étapes

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/ton-utilisateur/AutoCleaner.git
   cd AutoCleaner
   ```

2. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. (Optionnel) Créer un exécutable autonome avec PyInstaller :

   ```bash
   pyinstaller --onefile --noconsole autocleaner.py
   ```

---

## 📋 Requirements

Voici un exemple de contenu pour le fichier `requirements.txt` :

```
psutil>=5.9.0
win10toast-persist>=0.9.4
pywin32>=305
```

* `psutil` : Pour interagir avec les processus et gérer les fichiers système
* `win10toast-persist` : Pour afficher des notifications Windows persistantes
* `pywin32` : Pour accéder aux API Windows (gestion des logs, etc.)

---

## 🚀 Utilisation

### Démarrer le programme

```bash
python autocleaner.py
```

> ⚠️ Le script redémarre automatiquement avec les droits administrateur si nécessaire.

### Interface disponible

* Icône dans la barre des tâches Windows
* Menu contextuel accessible par clic droit :

  * **Statistiques** : affiche le nombre de fichiers supprimés et erreurs rencontrées
  * **Quitter** : ferme l’application

---

## 📡 API

Pas d’API REST ou web, mais une API Python simple à intégrer :

| Fonction                  | Description                        |
| ------------------------- | ---------------------------------- |
| `perform_cleanup()`       | Lance un nettoyage complet         |
| `clear_temp_folder(path)` | Supprime les fichiers d’un dossier |
| `clear_logs()`            | Vide les journaux système          |
| `clear_dns()`             | Vide le cache DNS                  |

Idéal pour automatiser ou étendre la gestion dans d’autres scripts.

---

## 🎁 Bonus

* Fonctionnement multithreadé, sans bloquer l’interface
* Ajout automatique au démarrage de Windows via création de raccourci
* Notifications persistantes grâce à `win10toast_persist`
* Interface graphique simple et efficace en Tkinter

---

## 🤝 Contribuer

Tu souhaites participer ? Voici comment faire :

1. Fork le dépôt
2. Crée ta branche de fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Commit tes changements (`git commit -m "Ajout de ma fonctionnalité"`)
4. Push ta branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvre une Pull Request

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.
Voir le fichier [`LICENSE`](LICENSE) pour les détails.

---

🔒 *Développé avec ❤️ pour que ton PC reste propre sans effort.*

---

Si tu veux, je peux aussi t’aider à générer un `requirements.txt` automatiquement selon tes imports exacts !
