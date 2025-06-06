# 🧹 AutoCleaner

**AutoCleaner** est une application Windows légère qui nettoie automatiquement les fichiers temporaires, les logs système, et la mémoire DNS toutes les 5 minutes en tâche de fond. Un menu dans la barre des tâches permet de suivre les statistiques en temps réel.

---

## 📚 Table des Matières

- [🎯 Objectifs](#-objectifs)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🛠️ Installation](#-installation)
- [🚀 Utilisation](#-utilisation)
- [📡 API](#-api)
- [🎁 Bonus](#-bonus)
- [🤝 Contribuer](#-contribuer)
- [📄 Licence](#-licence)

---

## 🎯 Objectifs

L'objectif d'AutoCleaner est d'automatiser les tâches de nettoyage que l'on fait manuellement :
- Gagner de l’espace disque
- Améliorer la stabilité et les performances
- Éviter les fichiers inutiles qui s’accumulent
- Avoir une interface simple et sans prise de tête

---

## ✨ Fonctionnalités

- ✔ Nettoyage automatique des fichiers temporaires (`%temp%` et `C:\Windows\Temp`)
- ✔ Suppression des journaux Windows (`Application`, `System`, `Security`)
- ✔ Vidage du cache DNS (`ipconfig /flushdns`)
- ✔ Notification système après chaque nettoyage
- ✔ Icône dans la barre des tâches avec menu contextuel :
  - Voir les statistiques
  - Lancer un nettoyage manuel
  - Quitter l’application
- ✔ Démarrage automatique avec Windows

---

## 🛠️ Installation

1. **Pré-requis** :
   - Windows 10 ou 11
   - Python 3.8+
   - Être administrateur (requis au premier lancement)

2. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/ton-utilisateur/AutoCleaner.git
   cd AutoCleaner
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **(Facultatif) Créer l’exécutable** :
   ```bash
   pyinstaller --onefile --noconsole autocleaner.py
   ```

---

## 🚀 Utilisation

### ▶ Lancer le script
```bash
python autocleaner.py
```

💡 Un redémarrage en mode administrateur est automatique si nécessaire.

### 📊 Interface disponible
- Icône dans la **barre des tâches**
- Clic droit → **Statistiques** / **Quitter**

---

## 📡 API

AutoCleaner ne fournit pas encore d'API externe, mais voici ce que tu peux intégrer :

| Fonction | Description |
|---------|-------------|
| `perform_cleanup()` | Lance le nettoyage complet |
| `clear_temp_folder(path)` | Supprime les fichiers dans le dossier donné |
| `clear_logs()` | Vide les journaux système |
| `clear_dns()` | Vide le cache DNS |

Tu peux intégrer ces fonctions dans d'autres scripts Python.

---

## 🎁 Bonus

- ✅ Mode **threadé** : tourne en arrière-plan sans bloquer l’interface
- 🛠️ Se recrée automatiquement au démarrage de Windows
- 🔔 Notifications persistantes avec `win10toast_persist`
- 💡 Interface tkinter simple et efficace pour les stats

---

## 🤝 Contribuer

Tu es le·la bienvenu·e ! Voici comment contribuer :

1. Fork le dépôt
2. Crée une branche (`git checkout -b feature/ton-idee`)
3. Commit tes modifications (`git commit -am 'Ajoute une fonctionnalité'`)
4. Push la branche (`git push origin feature/ton-idee`)
5. Crée une **Pull Request**

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [`LICENSE`](LICENSE) pour plus de détails.

---

🔒 *Développé avec ❤️ pour garder ton PC propre sans prise de tête.*