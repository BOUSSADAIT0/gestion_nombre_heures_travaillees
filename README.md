# Gestion des Heures Travaillées

Une application simple pour gérer et suivre vos heures de travail.

## Installation

1. Assurez-vous d'avoir Python installé sur votre ordinateur
2. Installez les dépendances requises :
   ```
   pip install -r requirements.txt
   ```

## Utilisation

1. Lancez l'application :
   ```
   python work_hours_improved.py
   ```

2. Fonctionnalités principales :
   - Ajouter une nouvelle entrée : Cliquez sur "➕ Nouvelle entrée"
   - Modifier une entrée : Sélectionnez une entrée et cliquez sur "✏️ Modifier"
   - Supprimer une entrée : Sélectionnez une entrée et cliquez sur "🗑️ Supprimer"
   - Exporter les données : Cliquez sur "📤 Exporter"
   - Vérifier les durées : Cliquez sur "🔍 Vérifier les durées"
   - Voir les statistiques : Cliquez sur "📊 Statistiques"

3. Pour chaque entrée, vous pouvez :
   - Définir la date et l'heure de début
   - Définir la date et l'heure de fin
   - Ajouter une pause (optionnel)
   - Choisir une catégorie de travail
   - Définir un tarif horaire

4. Les données sont automatiquement sauvegardées dans un fichier `work_hours_data.json`

## Raccourcis clavier

- Ctrl + N : Nouvelle entrée
- Ctrl + S : Sauvegarder
- Ctrl + D : Supprimer l'entrée sélectionnée
- Ctrl + E : Exporter
- Ctrl + T : Changer le thème (clair/sombre)

## Fonctionnalités

- **Types de travail**
  - Mode jour (même date de début et de fin)
  - Mode nuit (date de fin = date de début + 1 jour)

- **Calcul automatique**
  - Durée du travail (heures et minutes)
  - Montant total basé sur le taux horaire

- **Interface utilisateur intuitive**
  - Sélecteurs de date avec calendrier en français
  - Menus déroulants pour les heures/minutes
  - Tableau détaillé avec ligne de total
  - Interface adaptée aux conventions françaises

- **Gestion des données**
  - Ajout, modification et suppression d'entrées
  - Filtrage par plage de dates

- **Options d'exportation**
  - Format Excel (.xlsx)
  - Format PDF (.pdf)
  - Format image (.png)

## Structure du code

L'application est organisée autour d'une classe principale `WorkHoursApp` qui gère l'interface utilisateur et la logique métier.

Principales sections :
- **Interface utilisateur** : Création et disposition des widgets
- **Gestion des données** : Ajout, modification et suppression d'entrées
- **Calculs** : Détermination des heures travaillées et des montants
- **Exportation** : Génération de fichiers Excel, PDF et images

## Personnalisation

### Interface utilisateur

L'application utilise `customtkinter` pour une interface moderne, mais fonctionne également avec Tkinter standard si `customtkinter` n'est pas disponible.

### Localisation

L'application est configurée pour l'affichage des dates en français. La localisation peut être modifiée en ajustant les paramètres suivants :

```python
# Pour changer la locale
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')  # Exemple pour l'anglais

# Pour les widgets DateEntry
self.start_date_entry = DateEntry(..., locale='en_US', date_pattern='mm/dd/yyyy')
```

## Dépannage

### Problèmes courants

1. **Erreur "No module named X"** : Installez les dépendances manquantes avec pip.
2. **Locale non disponible** : Assurez-vous que les locales sont correctement installées sur votre système.
3. **Erreur d'exportation** : Vérifiez que les permissions d'écriture sont correctement configurées pour le dossier de destination.

### Support

Pour tout problème ou suggestion, veuillez ouvrir une issue sur le dépôt GitHub.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à proposer des améliorations via des pull requests.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Pushez votre branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Boussad AIT DJOUDI OUFELLA - Développeur initial

---

**Note** : Cette application est conçue spécifiquement pour le calcul des heures travaillées et n'est pas destinée à remplacer les logiciels professionnels de gestion de paie ou de ressources humaines.
