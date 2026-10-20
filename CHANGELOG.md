# Changelog

## Non publié

- Ajoute `POST /athletes/import` : importe un CSV de licenciés (`text/csv`, `;`, dates `jj/mm/aaaa`) et renvoie `created`, `skipped` et `errors` par ligne (400 `invalid_csv`, `invalid_encoding`). Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajoute `GET /health` : vérifie que l'API répond (`{"status": "ok"}`).
- Ajoute `GET /athletes/{athlete_id}` : détail d'un athlète (404 `not_found` s'il n'existe pas).
