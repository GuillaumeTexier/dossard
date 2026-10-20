---
name: classement-html
description: Génère la page HTML du classement d'une épreuve de dossard (classement-<event_id>.html). À utiliser quand on demande une page, un export HTML ou une version imprimable/publiable du classement d'une épreuve.
---

# Page HTML de classement

Le script `scripts/classement_html.py` appelle `GET /events/{event_id}/ranking` en interne (sans serveur) et écrit `classement-<event_id>.html` dans le répertoire courant : la page reflète exactement la réponse de l'API.

## Étapes

1. Identifier l'`event_id`. S'il n'est pas donné, le chercher via `GET /competitions` et les épreuves de la compétition, ou demander à l'utilisateur.
2. Depuis la racine du dépôt, venv activé :

   ```bash
   python .claude/skills/classement-html/scripts/classement_html.py <event_id>
   ```

3. Vérifier la sortie : `classement-<event_id>.html : N athlètes classés`.
   - « Base introuvable » : lancer `python scripts/seed.py --reset`.
   - « Épreuve introuvable » ou 404 : l'`event_id` n'existe pas.
4. Indiquer à l'utilisateur le chemin du fichier généré.

## Règles

- Ne pas modifier le HTML à la main : relancer le script. Pour changer la mise en page, éditer `render()` dans le script.
- Le fichier généré est un livrable, pas du code : ne pas le committer sans demande.
- Ne pas lire `.env`.
- Le HTML n'affiche que les champs publics du classement (rang, dossard, nom, club, performance) : n'y ajouter ni licence, ni certificat médical, ni date de naissance.
